from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from agent_evolve.config import EvolveConfig
from agent_evolve.contract.workspace import AgentWorkspace
from agent_evolve.engine.base import EvolutionEngine
from agent_evolve.engine.history import EvolutionHistory
from agent_evolve.engine.trial import TrialRunner
from agent_evolve.types import Observation, StepResult
from agent_evolve.algorithms.skillforge.prompts import (
    DEFAULT_EVOLVER_SYSTEM_PROMPT,
    build_evolution_prompt,
)


class CodexCliEngine(EvolutionEngine):
    """Run one evolution step through the local Codex CLI session."""

    def __init__(
        self,
        config: EvolveConfig,
        *,
        model: str | None = None,
        reasoning_effort: str = "medium",
        codex_bin: str = "codex",
        timeout_seconds: int = 900,
    ) -> None:
        self.config = config
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.codex_bin = codex_bin
        self.timeout_seconds = timeout_seconds

    def step(
        self,
        workspace: AgentWorkspace,
        observations: list[Observation],
        history: EvolutionHistory,
        trial: TrialRunner,
    ) -> StepResult:
        recent_logs = history.get_observations(last_n_cycles=2)
        cycle_num = history.latest_cycle + 1

        skills_before = [skill.name for skill in workspace.list_skills()]
        drafts = workspace.list_drafts()
        before_paths = self._list_changed_paths(workspace.root)

        prompt = build_evolution_prompt(
            workspace,
            recent_logs,
            drafts,
            cycle_num,
            evolve_prompts=self.config.evolve_prompts,
            evolve_skills=self.config.evolve_skills,
            evolve_memory=self.config.evolve_memory,
            evolve_tools=self.config.evolve_tools,
            trajectory_only=self.config.trajectory_only,
            max_skills=self.config.extra.get("max_skills", 5),
            solver_proposed=self.config.extra.get("solver_proposed", False),
            prompt_only=self.config.extra.get("prompt_only", False),
            protect_skills=self.config.extra.get("protect_skills", False),
        )
        final_message = self._run_codex(self._build_prompt(prompt), workspace.root)

        skills_after = [skill.name for skill in workspace.list_skills()]
        after_paths = self._list_changed_paths(workspace.root)
        changed_paths = sorted(set(after_paths) - set(before_paths))
        allowed_paths, reverted_paths = self._split_paths(changed_paths)
        if reverted_paths:
            self._restore_paths(reverted_paths, workspace.root)
        workspace.clear_drafts()

        if reverted_paths:
            skills_after = [skill.name for skill in workspace.list_skills()]

        new_skills = len(set(skills_after) - set(skills_before))
        mutated = bool(allowed_paths) or set(skills_after) != set(skills_before)

        summary = f"codex cli engine updated {len(allowed_paths)} files"
        if final_message:
            summary = f"{summary}: {final_message.splitlines()[0][:180]}"
        if reverted_paths:
            summary = f"{summary} (reverted {len(reverted_paths)} disallowed paths)"

        return StepResult(
            mutated=mutated,
            summary=summary,
            metadata={
                "evo_number": cycle_num,
                "tasks_analyzed": len(recent_logs),
                "drafts_reviewed": len(drafts),
                "skills_before": len(skills_before),
                "skills_after": len(skills_after),
                "new_skills": new_skills,
                "changed_paths": allowed_paths,
                "reverted_paths": reverted_paths,
                "codex_model": self.model or "default",
                "codex_reasoning_effort": self.reasoning_effort,
                "codex_summary": final_message,
            },
        )

    def _build_prompt(self, evolution_prompt: str) -> str:
        return (
            "Treat the current repository as the mutable agent workspace for one A-Evolve cycle.\n"
            "Do not access files outside the current workspace.\n"
            "Do not read or depend on external auth, config, or home-directory secrets.\n"
            "Do not use the network.\n"
            "Only edit workspace files under prompts/, skills/, memory/, or tools/.\n"
            "The Permissions section below is strict: if a surface is not explicitly allowed there, do not modify it.\n"
            "Inspect files first, make precise edits, and verify with `git diff --stat` before finishing.\n\n"
            "Reference A-Evolve evolver system prompt:\n"
            f"{DEFAULT_EVOLVER_SYSTEM_PROMPT}\n\n"
            "Evolution task:\n"
            f"{evolution_prompt}\n\n"
            "Finish with a concise summary of the changes you made and why."
        )

    def _run_codex(self, prompt: str, workspace_root: Path) -> str:
        with tempfile.TemporaryDirectory(prefix="codex-evolve-") as tmpdir:
            output_path = Path(tmpdir) / "last_message.txt"
            command = [
                self.codex_bin,
                "exec",
                "-C",
                str(workspace_root),
                "--skip-git-repo-check",
                "--ephemeral",
                "--color",
                "never",
                "-s",
                "workspace-write",
                "-c",
                'approval_policy="never"',
                "-c",
                f'model_reasoning_effort="{self.reasoning_effort}"',
                "--output-last-message",
                str(output_path),
            ]
            if self.model:
                command.extend(["-m", self.model])
            command.append("-")

            result = subprocess.run(
                command,
                input=prompt,
                text=True,
                capture_output=True,
                cwd=workspace_root,
                timeout=self.timeout_seconds,
                check=False,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    "codex exec failed with exit code "
                    f"{result.returncode}\nSTDOUT:\n{self._tail(result.stdout)}\nSTDERR:\n{self._tail(result.stderr)}"
                )
            if output_path.exists():
                return output_path.read_text().strip()
            return ""

    def _list_changed_paths(self, workspace_root: Path) -> list[str]:
        changed = self._run_git(["diff", "--name-only", "--relative", "HEAD"], workspace_root)
        untracked = self._run_git(
            ["ls-files", "--others", "--exclude-standard"],
            workspace_root,
        )
        paths = [line.strip() for line in changed.splitlines() if line.strip()]
        paths.extend(line.strip() for line in untracked.splitlines() if line.strip())
        return sorted(set(paths))

    def _split_paths(self, paths: list[str]) -> tuple[list[str], list[str]]:
        allowed_prefixes: list[str] = []
        if self.config.evolve_prompts:
            allowed_prefixes.append("prompts/")
        if self.config.evolve_skills:
            allowed_prefixes.append("skills/")
        if self.config.evolve_memory:
            allowed_prefixes.append("memory/")
        if self.config.evolve_tools:
            allowed_prefixes.append("tools/")

        allowed: list[str] = []
        reverted: list[str] = []
        for path in paths:
            if any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in allowed_prefixes):
                allowed.append(path)
            else:
                reverted.append(path)
        return allowed, reverted

    def _restore_paths(self, paths: list[str], workspace_root: Path) -> None:
        tracked = [path for path in paths if self._is_tracked(path, workspace_root)]
        untracked = [path for path in paths if path not in tracked]
        if tracked:
            self._run_git(["restore", "--worktree", "--source=HEAD", "--", *tracked], workspace_root)
        for path in untracked:
            full_path = workspace_root / path
            if full_path.is_dir():
                shutil.rmtree(full_path, ignore_errors=True)
            elif full_path.exists():
                full_path.unlink()

    def _is_tracked(self, path: str, workspace_root: Path) -> bool:
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", path],
            text=True,
            capture_output=True,
            cwd=workspace_root,
            check=False,
        )
        return result.returncode == 0

    def _run_git(self, args: list[str], workspace_root: Path) -> str:
        result = subprocess.run(
            ["git", *args],
            text=True,
            capture_output=True,
            cwd=workspace_root,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(
                "git command failed: "
                f"{' '.join(args)}\nSTDOUT:\n{self._tail(result.stdout)}\nSTDERR:\n{self._tail(result.stderr)}"
            )
        return result.stdout

    def _tail(self, text: str, limit: int = 1200) -> str:
        text = text.strip()
        if len(text) <= limit:
            return text
        return text[-limit:]
