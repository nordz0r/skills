"""Skillforge (AEvolveEngine) with an OCX tool loop.

Upstream ``AEvolveEngine._run_llm`` only runs ``converse_loop`` for Bedrock.
OCX is OpenAI-compatible, so this subclass routes ``OcxProvider`` through the
same bash-tool loop against the isolated workspace.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_evolve.algorithms.skillforge.engine import AEvolveEngine
from agent_evolve.algorithms.skillforge.prompts import DEFAULT_EVOLVER_SYSTEM_PROMPT
from agent_evolve.algorithms.skillforge.tools import BASH_TOOL_SPEC, make_workspace_bash

from .ocx_provider import OcxProvider


class SkillforgeEngine(AEvolveEngine):
    """AEvolveEngine that can mutate the workspace via OCX tool calls."""

    def _run_llm(self, prompt: str, workspace_root: Path) -> dict[str, Any]:
        if isinstance(self.llm, OcxProvider):
            bash_fn = make_workspace_bash(workspace_root)
            response = self.llm.converse_loop(
                system_prompt=DEFAULT_EVOLVER_SYSTEM_PROMPT,
                user_message=prompt,
                tools=[BASH_TOOL_SPEC],
                tool_executor={"workspace_bash": lambda command: bash_fn(command)},
                max_tokens=self.config.evolver_max_tokens,
            )
            return {"content": response.content, "usage": response.usage}
        return super()._run_llm(prompt, workspace_root)
