from __future__ import annotations

from collections import Counter
import re

from agent_evolve.engine.base import EvolutionEngine
from agent_evolve.types import StepResult

from .catalog import STOPWORDS, tokenize


BLOCK_START = "<!-- A-EVOLVE-ROUTING-SIGNALS:START -->"
BLOCK_END = "<!-- A-EVOLVE-ROUTING-SIGNALS:END -->"
FRONTMATTER_RE = re.compile(r"^---\s*\n.*?\n---\s*\n?", re.DOTALL)
IGNORE_HEADINGS = {
    "use with companion skills",
    "output pattern",
}
GENERIC_TOKENS = {
    "accessibility",
    "actions",
    "agent",
    "agency",
    "asked",
    "base",
    "clear",
    "coherent",
    "component",
    "components",
    "constraints",
    "default",
    "deliverables",
    "design",
    "guidance",
    "implementation",
    "include",
    "interface",
    "notes",
    "output",
    "outputs",
    "pattern",
    "practical",
    "product",
    "proposal",
    "proposed",
    "recommendations",
    "skills",
    "state",
    "structure",
    "system",
    "task",
    "user",
    "usually",
    "visual",
    "workflow",
    "workflows",
}


class HeuristicRoutingEngine(EvolutionEngine):
    """Mutation engine that improves routing cues without an external LLM."""

    def step(self, workspace, observations, history, trial) -> StepResult:
        mutated_skills: list[str] = []

        for skill in workspace.list_skills():
            original = workspace.read_skill(skill.name)
            updated = self._apply_base_routing_signals(original)
            if updated != original:
                workspace.write_skill(skill.name, updated)
                mutated_skills.append(skill.name)

        for observation in observations:
            if observation.feedback.success:
                continue
            expected_skill = observation.feedback.raw.get("expected_skill")
            if not expected_skill:
                continue
            original = workspace.read_skill(expected_skill)
            extra_tokens = self._extract_failure_tokens(
                observation.task.input,
                observation.task.metadata.get("expected_output", ""),
            )
            updated = self._merge_signal_block(original, extra_tokens)
            if updated != original:
                workspace.write_skill(expected_skill, updated)
                mutated_skills.append(expected_skill)

        mutated_unique = sorted(set(mutated_skills))
        return StepResult(
            mutated=bool(mutated_unique),
            summary=f"heuristic routing engine updated {len(mutated_unique)} skill files",
            metadata={"mutated_skills": mutated_unique},
        )

    def _apply_base_routing_signals(self, content: str) -> str:
        tokens = self._extract_base_signal_tokens(content)
        if not tokens:
            return content
        return self._merge_signal_block(content, tokens)

    def _extract_base_signal_tokens(self, content: str) -> list[str]:
        body = FRONTMATTER_RE.sub("", content, count=1)
        current_heading = ""
        signal_tokens: list[str] = []

        for raw_line in body.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("#"):
                current_heading = line.lstrip("#").strip().lower()
                continue
            if current_heading in IGNORE_HEADINGS:
                continue
            if line.startswith("-") or re.match(r"^\d+\.", line):
                for token in tokenize(line):
                    if token not in GENERIC_TOKENS and token not in signal_tokens:
                        signal_tokens.append(token)
        return signal_tokens[:18]

    def _extract_failure_tokens(self, prompt: str, expected_output: str) -> list[str]:
        combined = " ".join([prompt, expected_output])
        counts = Counter(tokenize(combined))
        ordered = [
            token
            for token, _count in counts.most_common()
            if token not in GENERIC_TOKENS and token not in STOPWORDS
        ]
        return ordered[:16]

    def _merge_signal_block(self, content: str, new_tokens: list[str]) -> str:
        if not new_tokens:
            return content

        existing_tokens = self._read_existing_tokens(content)
        merged_tokens: list[str] = []
        for token in [*existing_tokens, *new_tokens]:
            if token not in merged_tokens:
                merged_tokens.append(token)
        merged_tokens = merged_tokens[:24]
        block = self._render_block(merged_tokens)

        if BLOCK_START in content and BLOCK_END in content:
            pattern = re.compile(
                rf"{re.escape(BLOCK_START)}.*?{re.escape(BLOCK_END)}\n?",
                re.DOTALL,
            )
            return pattern.sub(block, content)

        if content.endswith("\n"):
            return f"{content}\n{block}"
        return f"{content}\n\n{block}"

    def _read_existing_tokens(self, content: str) -> list[str]:
        if BLOCK_START not in content or BLOCK_END not in content:
            return []
        match = re.search(
            rf"{re.escape(BLOCK_START)}\n(.*?)\n{re.escape(BLOCK_END)}",
            content,
            re.DOTALL,
        )
        if not match:
            return []
        return tokenize(match.group(1))

    def _render_block(self, tokens: list[str]) -> str:
        token_line = " ".join(tokens)
        return "\n".join(
            [
                BLOCK_START,
                f"## Routing signals: {token_line}",
                BLOCK_END,
            ]
        ) + "\n"
