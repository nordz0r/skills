#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Run NVIDIA SkillEvaluator 0.9.0 Tier 1 on an explicit skill list.

The official reusable workflow is not used: its credential preflight unions
redaction variants across the catalog, and a short password-tail or 8-character
window can collide with skill directory names or with report keys such as
``passed``. This runner uses the same pinned image CLI, then redacts report
values only so schema keys stay intact. Skills in git are not modified.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

WORKSPACE = Path("/workspace")
REPORTS = Path("/reports")
MAX_WORKERS = 16


def _load_paths() -> list[str]:
    paths = [line.strip() for line in os.environ.get("SKILL_PATHS", "").splitlines() if line.strip()]
    if len(paths) != 27 or len(set(paths)) != 27:
        raise SystemExit(f"expected 27 unique skill paths, got {len(paths)}")
    missing = [path for path in paths if not (WORKSPACE / path / "SKILL.md").is_file()]
    if missing:
        raise SystemExit("missing SKILL.md for: " + ", ".join(missing))
    return paths


def _import_redaction():
    sys.path[:0] = ["/ci", "/app/ci", "/opt/ci", "/usr/local/lib/ci"]
    try:
        from secret_redaction import collect_sensitive_values  # type: ignore
    except ImportError:
        try:
            from ci.secret_redaction import collect_sensitive_values  # type: ignore
        except ImportError:
            collect_sensitive_values = None
    try:
        from skillevaluator.utils.secret_redaction import Redactor
    except ImportError:
        Redactor = None
    return collect_sensitive_values, Redactor


def _collect_tokens(paths: list[str], collect_sensitive_values) -> set[str]:
    tokens: set[str] = set()
    if collect_sensitive_values is None:
        return tokens
    for path in paths:
        try:
            tokens.update(collect_sensitive_values(WORKSPACE / path))
        except Exception as exc:
            print(f"SkillEvaluator: credential preflight skipped for {path}: {type(exc).__name__}", flush=True)
    return tokens


def _redact_values(value, redactor):
    if redactor is None:
        return value
    if isinstance(value, str):
        return redactor.text(value)
    if isinstance(value, list):
        return [_redact_values(item, redactor) for item in value]
    if isinstance(value, dict):
        return {key: _redact_values(item, redactor) for key, item in value.items()}
    return value


def _quality(data: dict) -> tuple[object, object]:
    for candidate in data.get("quality_summary") or []:
        if isinstance(candidate, dict) and "overall_score" in candidate:
            return candidate.get("overall_score"), candidate.get("grade")
    for result in data.get("results") or []:
        quality = result.get("quality") if isinstance(result, dict) else None
        if isinstance(quality, dict) and "overall_score" in quality:
            return quality.get("overall_score"), quality.get("grade")
    return None, None


def _high_findings(data: dict) -> list[dict]:
    found = []
    for result in data.get("results") or []:
        if not isinstance(result, dict):
            continue
        validator = result.get("validator") or result.get("name")
        for finding in result.get("findings") or []:
            if not isinstance(finding, dict):
                continue
            severity = str(finding.get("severity") or "").lower()
            if severity not in {"high", "critical"}:
                continue
            found.append(
                {
                    "skill": None,
                    "file": finding.get("file_path") or finding.get("file"),
                    "line": finding.get("line_number") or finding.get("line"),
                    "rule": finding.get("check_name") or finding.get("category") or finding.get("rule"),
                    "category": finding.get("category"),
                    "severity": severity,
                    "validator": validator,
                }
            )
    return found


def _evaluate_one(index: int, path: str, min_score: str) -> dict:
    output = REPORTS / f"skill-{index:03d}"
    output.mkdir(parents=True, exist_ok=True)
    argv = [
        "skillevaluator",
        "tier1",
        str(WORKSPACE / path),
        "--no-llm",
        "--profile",
        "default",
        "--min-score",
        min_score,
        "-r",
        "json,markdown,sarif",
        "-o",
        str(output),
    ]
    log = output / "stderr.log"
    try:
        proc = subprocess.run(
            argv,
            cwd=WORKSPACE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=3000,
        )
        log.write_bytes(proc.stderr)
        (output / "stdout.log").write_bytes(proc.stdout)
        report = output / "skillevaluator-tier1.json"
        if not report.is_file():
            return {
                "path": path,
                "report_dir": output.name,
                "exit_code": proc.returncode,
                "overall_status": "error",
                "passed": False,
                "error": "Evaluator execution failed or its JSON report was missing, unreadable, or invalid.",
            }
        data = json.loads(report.read_text(encoding="utf-8"))
        score, grade = _quality(data)
        highs = _high_findings(data)
        for item in highs:
            item["skill"] = path
        return {
            "path": path,
            "report_dir": output.name,
            "exit_code": proc.returncode,
            "overall_status": data.get("overall_status") or ("passed" if data.get("overall_passed") else "failed"),
            "overall_passed": data.get("overall_passed"),
            "passed": bool(data.get("overall_passed")) and proc.returncode == 0,
            "incomplete_scans": data.get("incomplete_scans") or [],
            "total_errors": data.get("total_errors"),
            "total_warnings": data.get("total_warnings"),
            "severity_counts": data.get("severity_counts") or {},
            "quality_score": score,
            "grade": grade,
            "high_findings": highs,
            "error": None,
        }
    except subprocess.TimeoutExpired:
        return {
            "path": path,
            "report_dir": output.name,
            "exit_code": None,
            "overall_status": "error",
            "passed": False,
            "error": "Scan time limit reached; this skill did not finish.",
        }
    except Exception:
        log.write_text(traceback.format_exc(), encoding="utf-8")
        return {
            "path": path,
            "report_dir": output.name,
            "exit_code": None,
            "overall_status": "error",
            "passed": False,
            "error": "Evaluator execution failed or its JSON report was missing, unreadable, or invalid.",
        }


def _sanitize_files(tokens: set[str], Redactor) -> None:
    redactor = Redactor(tokens) if Redactor is not None and tokens else None
    withhold = "Raw scanner log withheld while credential redaction is active. See the structured reports.\n"
    for path in REPORTS.rglob("*"):
        if not path.is_file():
            continue
        if path.name in {"stdout.log", "stderr.log"}:
            if tokens:
                path.write_text(withhold, encoding="utf-8")
            continue
        if redactor is None:
            continue
        suffix = path.suffix.lower()
        if suffix not in {".json", ".md", ".sarif"} and not path.name.endswith(".json"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if path.name.endswith(".json"):
            data = _redact_values(json.loads(text), redactor)
            path.write_text(json.dumps(data, ensure_ascii=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        else:
            path.write_text(redactor.text(text), encoding="utf-8")


def _write_reports(rows: list[dict], *, min_score: int, enforcement: str) -> dict:
    scores = [row["quality_score"] for row in rows if isinstance(row.get("quality_score"), (int, float))]
    highs = [item for row in rows for item in row.get("high_findings") or []]
    runtime_errors = [row for row in rows if row.get("error")]
    if runtime_errors:
        overall_status = "error"
    elif all(row.get("passed") for row in rows):
        overall_status = "passed"
    else:
        overall_status = "failed"
    summary = {
        "total": len(rows),
        "passed": sum(1 for row in rows if row.get("passed")),
        "failed": sum(1 for row in rows if not row.get("passed") and not row.get("error")),
        "incomplete": len(runtime_errors),
        "overall_passed": overall_status == "passed",
        "overall_status": overall_status,
        "min_score": min_score,
        "quality_scores": scores,
        "severity_counts": {
            "critical": sum(int((row.get("severity_counts") or {}).get("critical") or 0) for row in rows),
            "high": sum(int((row.get("severity_counts") or {}).get("high") or 0) for row in rows),
            "medium": sum(int((row.get("severity_counts") or {}).get("medium") or 0) for row in rows),
            "low": sum(int((row.get("severity_counts") or {}).get("low") or 0) for row in rows),
        },
        "high_findings": highs,
        "skills": rows,
        "execution": {
            "llm_enabled": False,
            "run_url": os.environ.get("REPORT_RUN_URL", ""),
            "commit": os.environ.get("REPORT_COMMIT", ""),
        },
        "enforcement": {
            "mode": enforcement,
            "downgraded": enforcement == "advisory" and overall_status != "passed",
        },
    }
    (REPORTS / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=True, indent=2, default=str) + "\n", encoding="utf-8"
    )

    lines = [
        "# Skill scan",
        "",
        f"**Tier 1 scan result: {overall_status.upper()}**",
        "",
        f"{summary['total']} skills · {summary['passed']} passed · {summary['failed']} failed · {summary['incomplete']} incomplete",
        "",
        f"Quality threshold (configured, not enforced in advisory mode): {min_score}.",
        "",
        "Tier 1 only · Tier 2: Not run · Tier 3: Not run. LLM checks disabled; no model-backed evaluation requested.",
        "",
        "## Skills and scores",
        "",
        "| Skill | Status | Quality / 100 | Grade | Errors | Warnings | HIGH | CRITICAL |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        score = row.get("quality_score")
        score_s = "" if score is None else str(score)
        sev = row.get("severity_counts") or {}
        status = "ERROR" if row.get("error") else str(row.get("overall_status") or "").upper()
        lines.append(
            f"| {row['path']} | {status} | {score_s} | {row.get('grade') or ''} | "
            f"{row.get('total_errors') if row.get('total_errors') is not None else ''} | "
            f"{row.get('total_warnings') if row.get('total_warnings') is not None else ''} | "
            f"{sev.get('high', '')} | {sev.get('critical', '')} |"
        )
    lines.extend(["", "## HIGH and CRITICAL findings", ""])
    if not highs:
        lines.append("No HIGH or CRITICAL findings in the structured reports.")
    else:
        lines.append("Values of secrets and PII are not listed; only file, line, and rule.")
        lines.append("")
        lines.append("| Skill | File | Line | Rule | Severity |")
        lines.append("| --- | --- | --- | --- | --- |")
        for item in highs:
            lines.append(
                f"| {item.get('skill') or ''} | {item.get('file') or ''} | "
                f"{item.get('line') if item.get('line') is not None else ''} | "
                f"{item.get('rule') or ''} | {item.get('severity') or ''} |"
            )
    if runtime_errors:
        lines.extend(["", "## Runtime errors", ""])
        for row in runtime_errors:
            lines.append(f"- `{row['path']}`: {row.get('error')}")
    run_url = os.environ.get("REPORT_RUN_URL")
    if run_url:
        lines.extend(["", f"[Workflow run and logs]({run_url})"])
    markdown = "\n".join(lines) + "\n"
    (REPORTS / "summary.md").write_text(markdown, encoding="utf-8")
    (REPORTS / "details.md").write_text(markdown, encoding="utf-8")
    return summary


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    paths = _load_paths()
    min_score = os.environ.get("MIN_SCORE", "70")
    if not min_score.isdigit() or int(min_score) > 100:
        raise SystemExit("MIN_SCORE must be an integer between 0 and 100.")
    enforcement = os.environ.get("ENFORCEMENT_MODE", "advisory")
    if enforcement not in {"strict", "advisory"}:
        raise SystemExit("ENFORCEMENT_MODE must be strict or advisory")
    workers = int(os.environ.get("SCAN_WORKERS", "4") or "4")
    workers = max(1, min(workers, MAX_WORKERS, len(paths)))

    collect_sensitive_values, Redactor = _import_redaction()
    tokens = _collect_tokens(paths, collect_sensitive_values)
    print(f"SkillEvaluator: scanning {len(paths)} skills, up to {workers} at a time.", flush=True)

    rows: list[dict | None] = [None] * len(paths)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_evaluate_one, index, path, min_score): index for index, path in enumerate(paths, 1)}
        for future in as_completed(futures):
            index = futures[future]
            row = future.result()
            rows[index - 1] = row
            print(f"Skill result: {row['path']} — {str(row.get('overall_status') or 'error').upper()}", flush=True)

    completed = [row for row in rows if row is not None]
    _sanitize_files(tokens, Redactor)
    summary = _write_reports(completed, min_score=int(min_score), enforcement=enforcement)
    print(f"SkillEvaluator finished: {summary['passed']} of {summary['total']} skills passed.", flush=True)

    runtime_failed = summary["incomplete"] > 0
    policy_failed = summary["overall_status"] != "passed"
    below = any(
        isinstance(row.get("quality_score"), (int, float)) and row["quality_score"] < int(min_score)
        for row in completed
    )
    has_high = bool(summary["high_findings"]) or (
        summary["severity_counts"]["high"] + summary["severity_counts"]["critical"]
    ) > 0
    if runtime_failed:
        return 1
    if enforcement == "advisory":
        return 0
    return 1 if policy_failed or below or has_high else 0


if __name__ == "__main__":
    raise SystemExit(main())
