from __future__ import annotations

import json

from agent_evolve.protocol.base_agent import BaseAgent
from agent_evolve.types import Task, Trajectory

from .catalog import SkillDoc
from .router import rank_skills


class SkillRouterAgent(BaseAgent):
    """Deterministic skill router over the current workspace skill library."""

    def solve(self, task: Task) -> Trajectory:
        skill_docs = [
            SkillDoc(
                name=skill.name,
                description=skill.description,
                path=self.workspace.root / skill.path / "SKILL.md",
                content=self.get_skill_content(skill.name),
            )
            for skill in self.skills
        ]

        ranked = rank_skills(task.input, skill_docs)
        selected = ranked[0] if ranked else None

        payload = {
            "selected_skill": selected.name if selected else None,
            "ranked_skills": [
                {
                    "name": item.name,
                    "score": item.score,
                    "overlap_tokens": item.overlap_tokens,
                }
                for item in ranked[:5]
            ],
        }
        steps = [
            {
                "event": "rank_skill",
                "skill": item.name,
                "score": item.score,
                "overlap_tokens": item.overlap_tokens,
            }
            for item in ranked[:5]
        ]
        return Trajectory(task_id=task.id, output=json.dumps(payload, ensure_ascii=False), steps=steps)
