from __future__ import annotations

import json
from pathlib import Path

from agent_evolve.benchmarks.base import BenchmarkAdapter
from agent_evolve.types import Feedback, Task, Trajectory

from .catalog import BenchmarkCase, REPO_ROOT, load_eval_cases


class SkillRouterBenchmark(BenchmarkAdapter):
    """Balanced routing benchmark built from the repo's skill eval prompts."""

    def __init__(self, repo_root: Path | None = None):
        self.repo_root = (repo_root or REPO_ROOT).resolve()
        self.cases = load_eval_cases(self.repo_root)

    def get_tasks(self, split: str = "train", limit: int = 10) -> list[Task]:
        selected_cases = [case for case in self.cases if case.split == split]
        return [
            Task(
                id=case.task_id,
                input=case.prompt,
                metadata={
                    "expected_skill": case.expected_skill,
                    "expected_output": case.expected_output,
                    "split": case.split,
                },
            )
            for case in selected_cases[:limit]
        ]

    def evaluate(self, task: Task, trajectory: Trajectory) -> Feedback:
        expected = task.metadata["expected_skill"]
        payload = self._parse_output(trajectory.output)
        selected = payload.get("selected_skill")
        ranked = payload.get("ranked_skills", [])
        ranked_names = [item.get("name") for item in ranked if item.get("name")]

        success = selected == expected
        if success:
            score = 1.0
        elif expected in ranked_names[:3]:
            score = 0.35
        else:
            score = 0.0

        detail = self._format_detail(
            task_id=task.id,
            prompt=task.input,
            expected=expected,
            selected=selected,
            ranked_names=ranked_names,
            expected_output=task.metadata.get("expected_output", ""),
        )
        return Feedback(
            success=success,
            score=score,
            detail=detail,
            raw={
                "expected_skill": expected,
                "selected_skill": selected,
                "ranked_skills": ranked,
                "prompt": task.input,
            },
        )

    @staticmethod
    def _parse_output(raw_output: str) -> dict:
        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            return {"selected_skill": None, "ranked_skills": []}

    @staticmethod
    def _format_detail(
        *,
        task_id: str,
        prompt: str,
        expected: str,
        selected: str | None,
        ranked_names: list[str],
        expected_output: str,
    ) -> str:
        top_three = ", ".join(ranked_names[:3]) if ranked_names else "none"
        return "\n".join(
            [
                f"Task: {task_id}",
                f"Prompt: {prompt}",
                f"Expected skill: {expected}",
                f"Selected skill: {selected or 'none'}",
                f"Top candidates: {top_three}",
                f"Expected behavior: {expected_output}",
                "Focus on trigger phrasing and routing-specific signal instead of broad generic language.",
            ]
        )


def get_case_map(repo_root: Path | None = None) -> dict[str, BenchmarkCase]:
    return {case.task_id: case for case in load_eval_cases(repo_root or REPO_ROOT)}
