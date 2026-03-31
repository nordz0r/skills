from __future__ import annotations

import shutil
from pathlib import Path

from .catalog import EXPERIMENT_ROOT, REPO_ROOT


WORKSPACE_TEMPLATE = EXPERIMENT_ROOT / "workspace_template"
DEFAULT_WORKDIR = EXPERIMENT_ROOT / ".workdir" / "skill-router"


def materialize_workspace(
    destination: Path | None = None,
    *,
    repo_root: Path | None = None,
    reset: bool = False,
) -> Path:
    repo = (repo_root or REPO_ROOT).resolve()
    target = (destination or DEFAULT_WORKDIR).resolve()

    if reset and target.exists():
        shutil.rmtree(target)

    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(WORKSPACE_TEMPLATE, target, dirs_exist_ok=True)

    skills_dir = target / "skills"
    if skills_dir.exists():
        shutil.rmtree(skills_dir)
    skills_dir.mkdir(parents=True, exist_ok=True)

    for skill_dir in sorted(repo.glob("agency-*")):
        source = skill_dir / "SKILL.md"
        if not source.exists():
            continue
        dest_dir = skills_dir / skill_dir.name
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest_dir / "SKILL.md")

    memory_dir = target / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    episodic_path = memory_dir / "episodic.jsonl"
    episodic_path.touch(exist_ok=True)
    return target
