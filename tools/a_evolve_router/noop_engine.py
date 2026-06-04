from __future__ import annotations

from agent_evolve.engine.base import EvolutionEngine
from agent_evolve.types import StepResult


class NoMutationEngine(EvolutionEngine):
    """Minimal engine for validating the a-evolve loop without an LLM."""

    def step(self, workspace, observations, history, trial) -> StepResult:
        return StepResult(
            mutated=False,
            summary=f"no-op engine: observed {len(observations)} tasks, applied 0 mutations",
            metadata={"tasks_analyzed": len(observations)},
        )
