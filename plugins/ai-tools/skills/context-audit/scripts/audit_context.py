#!/usr/bin/env python3
"""Read-only context capture inspector. Uses only Python's standard library."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterator

NATIVE_METHOD = "native_provider_prompt_and_local_estimates"
DUMP_METHOD = "dump_unicode_character_heuristic"


class AuditError(Exception):
    pass


def fail(message: str) -> None:
    print(f"context-audit: {message}", file=sys.stderr)
    raise SystemExit(2)


def integer(value: Any, name: str, line: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        where = f" at line {line}" if line else ""
        raise AuditError(f"invalid non-negative integer {name}{where}")
    return value


def optional_integer(value: Any, name: str, line: int | None = None) -> int | None:
    if value is None:
        return None
    return integer(value, name, line)


def json_lines(path: Path) -> Iterator[tuple[int, dict[str, Any]]]:
    try:
        with path.open("r", encoding="utf-8") as stream:
            for number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                try:
                    value = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise AuditError(f"malformed JSONL at line {number}: {exc.msg}") from None
                if not isinstance(value, dict):
                    raise AuditError(f"JSONL record at line {number} is not an object")
                yield number, value
    except OSError as exc:
        raise AuditError(f"cannot read {path}: {exc.strerror}") from None


def native_captures(path: Path) -> list[dict[str, Any]]:
    captures: list[dict[str, Any]] = []
    for line, outer in json_lines(path):
        message = outer.get("message")
        if outer.get("type") != "message" or not isinstance(message, dict):
            continue
        if message.get("role") != "assistant" or "contextSnapshot" not in message:
            continue
        snapshot = message["contextSnapshot"]
        if not isinstance(snapshot, dict):
            raise AuditError(f"contextSnapshot is not an object at line {line}")

        prompt = integer(snapshot.get("promptTokens"), "contextSnapshot.promptTokens", line)
        non_message = integer(snapshot.get("nonMessageTokens"), "contextSnapshot.nonMessageTokens", line)
        schema = optional_integer(snapshot.get("toolSchemaTokens"), "contextSnapshot.toolSchemaTokens", line)
        history_removed = optional_integer(
            snapshot.get("historyRewriteTokensRemoved"), "contextSnapshot.historyRewriteTokensRemoved", line
        )
        compaction_epoch = optional_integer(snapshot.get("compactionEpoch"), "contextSnapshot.compactionEpoch", line)

        record_id = outer.get("id")
        if not isinstance(record_id, str) or not record_id:
            raise AuditError(f"assistant snapshot lacks string outer id at line {line}")
        timestamp = outer.get("timestamp")
        last_msg_ts = snapshot.get("lastMessageTimestamp")
        model = message.get("model", outer.get("model"))

        metrics: dict[str, Any] = {
            "prompt_tokens": prompt,
            "non_message_tokens": non_message,
            "tool_schema_tokens": schema,
            "non_tool_static_tokens": (non_message - schema) if schema is not None else None,
            "provider_anchor_remainder": prompt - non_message,
        }
        if history_removed is not None:
            metrics["history_rewrite_tokens_removed"] = history_removed
            metrics["corrected_provider_prompt"] = max(0, prompt - history_removed)

        captures.append({
            "record_id": record_id,
            "timestamp": timestamp if isinstance(timestamp, str) else None,
            "last_message_timestamp": last_msg_ts if isinstance(last_msg_ts, (int, str)) else None,
            "model": model if isinstance(model, str) else None,
            "compaction_epoch": compaction_epoch,
            "line": line,
            "metrics": metrics,
        })
    if not captures:
        raise AuditError("no assistant.message.contextSnapshot records found")
    return captures


def select(captures: list[dict[str, Any]], selector: str) -> dict[str, Any]:
    if selector == "first":
        return captures[0]
    if selector == "last":
        return captures[-1]
    for capture in captures:
        if capture["record_id"] == selector:
            return capture
    raise AuditError(f"snapshot record id not found: {selector}")


def count_text(value: str) -> dict[str, int | float]:
    chars = len(value)
    return {
        "unicode_characters": chars,
        "utf8_bytes": len(value.encode("utf-8")),
        "chars_divided_by_4_estimate": chars / 4,
    }


def tool_name(tool: Any, index: int) -> str:
    if not isinstance(tool, dict):
        return f"tool[{index}]"
    function = tool.get("function")
    if isinstance(function, dict) and isinstance(function.get("name"), str):
        return function["name"]
    if isinstance(tool.get("name"), str):
        return tool["name"]
    return f"tool[{index}]"


def dump_capture(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise AuditError(f"cannot read {path}: {exc.strerror}") from None
    except json.JSONDecodeError as exc:
        raise AuditError(f"malformed JSON dump: {exc.msg}") from None
    if not isinstance(data, dict):
        raise AuditError("dump must be a JSON object")
    system, tools, messages = data.get("systemPrompt"), data.get("tools"), data.get("messages")
    if not isinstance(system, str) or not isinstance(tools, list) or not isinstance(messages, list):
        raise AuditError("dump must contain systemPrompt (string), tools (array), and messages (array)")

    try:
        tool_text = json.dumps(tools, ensure_ascii=False, separators=(",", ":"))
        message_text = json.dumps(messages, ensure_ascii=False, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        raise AuditError(f"dump tools/messages are not JSON-serializable: {exc}") from None

    components = [
        {"name": "systemPrompt", **count_text(system)},
        {
            "name": "tools",
            **count_text(tool_text),
            "tool_count": len(tools),
            "tool_names": [tool_name(tool, i) for i, tool in enumerate(tools)],
        },
        {"name": "messages", **count_text(message_text), "message_count": len(messages)},
    ]
    largest = sorted(components, key=lambda item: int(item["utf8_bytes"]), reverse=True)
    return {
        "source": {
            "kind": "dump-json",
            "path": str(path),
            "model": data.get("model") if isinstance(data.get("model"), str) else None,
            "scope": {key: data[key] for key in ("thinkingLevel", "serviceTier") if isinstance(data.get(key), str)},
        },
        "method": DUMP_METHOD,
        "capture": {"record_id": None, "timestamp": None, "compaction_epoch": None},
        "metrics": {
            "components": components,
            "total": count_text(system + tool_text + message_text),
            "largest_components": [item["name"] for item in largest],
        },
        "warnings": [
            "Character and UTF-8 byte counts are deterministic sizes, not model token counts.",
            "chars_divided_by_4_estimate is a heuristic only; wire serialization overhead is unknown.",
            "Dump content is intentionally not emitted because it may contain secrets.",
        ],
    }


def inspect(path_text: str, selector: str) -> dict[str, Any]:
    path = Path(path_text)
    if path.suffix.lower() == ".jsonl":
        capture = select(native_captures(path), selector)
        return {
            "source": {
                "kind": "native-jsonl",
                "path": str(path),
                "model": capture["model"],
                "scope": {"compaction_epoch": capture["compaction_epoch"]},
            },
            "method": NATIVE_METHOD,
            "capture": {
                key: capture[key]
                for key in ("record_id", "timestamp", "last_message_timestamp", "compaction_epoch", "line")
                if capture.get(key) is not None
            },
            "metrics": capture["metrics"],
            "metric_notes": {
                "prompt_tokens": "Provider usage-backed prompt counter; omp prioritizes usage.contextTokens and falls back to input + cacheRead + cacheWrite. Output is excluded.",
                "non_message_tokens": "Local tokenizer estimate reported by the runtime for system prompt blocks and eligible wire tools.",
                "tool_schema_tokens": "Optional local tokenizer estimate for tool schemas; included within non_message_tokens, never add it again.",
                "non_tool_static_tokens": "Derived local estimate: non_message_tokens - tool_schema_tokens when tool_schema_tokens is present.",
                "provider_anchor_remainder": "Derived residual: prompt_tokens - non_message_tokens; anchors provider usage against local static estimates but may reflect provider/protocol differences rather than exact history tokens.",
                "corrected_provider_prompt": "Optional field: max(0, prompt_tokens - history_rewrite_tokens_removed) when history rewriting removed prior tokens.",
            },
            "warnings": [
                "One snapshot is a point-in-time composition, not a causal attribution.",
                "Do not sum snapshots or merge compaction epochs; inspect one point in time.",
            ],
        }
    if selector != "last":
        raise AuditError("--snapshot applies only to native JSONL; dump JSON has one capture")
    return dump_capture(path)


def delta(before: int | float | None, after: int | float | None) -> dict[str, Any] | None:
    if before is None or after is None:
        return None
    change = after - before
    return {
        "before": before,
        "after": after,
        "delta": change,
        "reduction_percent": None if before == 0 else (before - after) / before * 100,
        "direction": "increase" if change > 0 else "decrease" if change < 0 else "unchanged",
    }


def compare(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    if before["method"] != after["method"]:
        raise AuditError("incompatible comparison: native reported counters and dump character heuristics cannot be mixed")

    if before["method"] == NATIVE_METHOD:
        keys = (
            "prompt_tokens",
            "non_message_tokens",
            "tool_schema_tokens",
            "non_tool_static_tokens",
            "provider_anchor_remainder",
            "corrected_provider_prompt",
        )
        changes: dict[str, Any] = {}
        for key in keys:
            metric_delta = delta(before["metrics"].get(key), after["metrics"].get(key))
            if metric_delta is not None:
                changes[key] = metric_delta
        warnings = [
            "Totals include changing conversation history; descriptive deltas do not establish cause.",
            "Compare the same workload and model where possible; model or compaction-epoch changes limit inference.",
        ]
        if before["source"]["model"] != after["source"]["model"]:
            warnings.append("Model differs between captures.")
        if before["capture"].get("compaction_epoch") != after["capture"].get("compaction_epoch"):
            warnings.append("Compaction epoch differs between captures; do not treat this as a continuous total.")
    else:
        changes = {
            "total_unicode_characters": delta(
                before["metrics"]["total"]["unicode_characters"], after["metrics"]["total"]["unicode_characters"]
            ),
            "total_utf8_bytes": delta(
                before["metrics"]["total"]["utf8_bytes"], after["metrics"]["total"]["utf8_bytes"]
            ),
            "total_chars_divided_by_4_estimate": delta(
                before["metrics"]["total"]["chars_divided_by_4_estimate"],
                after["metrics"]["total"]["chars_divided_by_4_estimate"],
            ),
        }
        warnings = [
            "Dump comparison is a character-size heuristic, not model token accounting.",
            "Wire serialization overhead is unknown; do not mix this with native counters.",
        ]

    return {
        "method": before["method"],
        "before": {"source": before["source"], "capture": before["capture"]},
        "after": {"source": after["source"], "capture": after["capture"]},
        "changes": changes,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Read-only inspector for OMP native context snapshots or verified /dump JSON."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    inspect_parser = sub.add_parser("inspect")
    inspect_parser.add_argument("input")
    inspect_parser.add_argument("--snapshot", default="last", metavar="first|last|RECORD_ID")

    compare_parser = sub.add_parser("compare")
    compare_parser.add_argument("before_input", metavar="before")
    compare_parser.add_argument("after_input", metavar="after")
    compare_parser.add_argument("--before", dest="before_snapshot", default="last", metavar="first|last|RECORD_ID")
    compare_parser.add_argument("--after", dest="after_snapshot", default="last", metavar="first|last|RECORD_ID")

    args = parser.parse_args()

    try:
        if args.command == "inspect":
            result = inspect(args.input, args.snapshot)
        else:
            before_cap = inspect(args.before_input, args.before_snapshot)
            after_cap = inspect(args.after_input, args.after_snapshot)
            result = compare(before_cap, after_cap)
    except AuditError as exc:
        fail(str(exc))

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
