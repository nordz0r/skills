from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_ROOT = Path(__file__).resolve().parent
AGENCY_GLOB = "agency-*/SKILL.md"
SUPPLEMENTAL_CASES_FILE = EXPERIMENT_ROOT / "supplemental_cases.json"
TOKEN_RE = re.compile(r"[0-9A-Za-zА-Яа-я][0-9A-Za-zА-Яа-я+_-]*")
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
STOPWORDS = {
    "a",
    "an",
    "and",
    "any",
    "be",
    "by",
    "for",
    "from",
    "how",
    "i",
    "if",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "use",
    "when",
    "with",
    "без",
    "в",
    "во",
    "для",
    "и",
    "или",
    "как",
    "на",
    "не",
    "но",
    "нужен",
    "по",
    "под",
    "при",
    "с",
    "со",
    "так",
    "что",
    "это",
}


@dataclass(frozen=True)
class SkillDoc:
    name: str
    description: str
    path: Path
    content: str

    @property
    def body(self) -> str:
        match = FRONTMATTER_RE.match(self.content)
        if not match:
            return self.content
        return self.content[match.end() :]


@dataclass(frozen=True)
class BenchmarkCase:
    task_id: str
    prompt: str
    expected_skill: str
    expected_output: str
    split: str


def tokenize(text: str) -> list[str]:
    tokens = [token.lower() for token in TOKEN_RE.findall(text)]
    return [token for token in tokens if len(token) > 2 and token not in STOPWORDS]


def parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}

    metadata: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"').strip("'")
    return metadata


def load_skill_catalog(repo_root: Path | None = None) -> list[SkillDoc]:
    root = repo_root or REPO_ROOT
    skills: list[SkillDoc] = []
    for skill_file in sorted(root.glob(AGENCY_GLOB)):
        content = skill_file.read_text(encoding="utf-8")
        metadata = parse_frontmatter(content)
        skills.append(
            SkillDoc(
                name=metadata.get("name", skill_file.parent.name),
                description=metadata.get("description", ""),
                path=skill_file,
                content=content,
            )
        )
    return skills


def load_eval_cases(repo_root: Path | None = None) -> list[BenchmarkCase]:
    root = repo_root or REPO_ROOT
    cases: list[BenchmarkCase] = []
    for eval_file in sorted(root.glob("agency-*/evals/evals.json")):
        payload = json.loads(eval_file.read_text(encoding="utf-8"))
        skill_name = payload["skill_name"]
        for item in payload["evals"]:
            split = item.get("split") or ("train" if int(item["id"]) == 1 else "holdout")
            task_id = f"{skill_name}::{item['id']}"
            cases.append(
                BenchmarkCase(
                    task_id=task_id,
                    prompt=item["prompt"],
                    expected_skill=skill_name,
                    expected_output=item.get("expected_output", ""),
                    split=split,
                )
            )

    if SUPPLEMENTAL_CASES_FILE.exists():
        for item in json.loads(SUPPLEMENTAL_CASES_FILE.read_text(encoding="utf-8")):
            cases.append(
                BenchmarkCase(
                    task_id=item["task_id"],
                    prompt=item["prompt"],
                    expected_skill=item["expected_skill"],
                    expected_output=item.get("expected_output", ""),
                    split=item["split"],
                )
            )
    return cases
