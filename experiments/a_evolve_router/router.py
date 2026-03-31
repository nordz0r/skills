from __future__ import annotations

from dataclasses import dataclass

from .catalog import SkillDoc, tokenize


@dataclass(frozen=True)
class RankedSkill:
    name: str
    score: float
    overlap_tokens: list[str]


def _build_skill_text(skill: SkillDoc) -> str:
    lines = []
    for line in skill.body.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            lines.append(stripped.lstrip("#").strip())
        if len(lines) >= 12:
            break
    headings = " ".join(lines)
    return " ".join([skill.name, skill.description, headings])


def rank_skills(prompt: str, skills: list[SkillDoc]) -> list[RankedSkill]:
    prompt_tokens = tokenize(prompt)
    prompt_set = set(prompt_tokens)
    ranked: list[RankedSkill] = []

    for skill in skills:
        name_tokens = set(tokenize(skill.name.replace("-", " ")))
        description_tokens = set(tokenize(skill.description))
        heading_tokens = set(tokenize(_build_skill_text(skill)))

        name_overlap = sorted(prompt_set & name_tokens)
        description_overlap = sorted(prompt_set & description_tokens)
        heading_overlap = sorted(prompt_set & heading_tokens)

        score = (
            len(name_overlap) * 4.0
            + len(description_overlap) * 2.5
            + len(heading_overlap) * 1.0
        )
        overlap_tokens = sorted(set(name_overlap + description_overlap + heading_overlap))
        ranked.append(RankedSkill(name=skill.name, score=score, overlap_tokens=overlap_tokens))

    return sorted(ranked, key=lambda item: (-item.score, item.name))
