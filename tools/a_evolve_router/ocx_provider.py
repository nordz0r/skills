"""OpenAI-compatible LLM provider for Skillforge via OCX.

PyPI ``a-evolve`` 0.1.0 only runs the Skillforge bash tool-loop on Bedrock.
This provider talks to an OpenAI-compatible ``/v1/chat/completions`` endpoint
(OCX) and implements ``converse_loop`` so ``AEvolveEngine`` can mutate the
isolated workspace.
"""

from __future__ import annotations

import json
import os
import ssl
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from agent_evolve.config import EvolveConfig
from agent_evolve.llm.base import LLMMessage, LLMProvider, LLMResponse


def _read_dotenv_value(path: Path, key: str) -> str | None:
    if not path.exists():
        return None
    prefix = f"{key}="
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(prefix):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def resolve_ocx_credentials() -> tuple[str, str] | None:
    """Return (base_url, api_key) or None. Never logs the key."""
    base = (
        os.environ.get("OCX_BASE_URL")
        or os.environ.get("OPENAI_BASE_URL")
        or _read_dotenv_value(Path("/root/.hermes/.env"), "OCX_BASE_URL")
        or "https://ocx.goldfinches.ru/v1"
    )
    key = (
        os.environ.get("OCX_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
        or _read_dotenv_value(Path("/root/.hermes/.env"), "OCX_API_KEY")
        or _read_dotenv_value(Path("/root/.hermes/profiles/nord/.env"), "OCX_API_KEY")
    )
    if not key:
        return None
    return base.rstrip("/"), key


def _to_openai_tools(tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    converted = []
    for tool in tools:
        if tool.get("type") == "function" and "function" in tool:
            converted.append(tool)
            continue
        converted.append(
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("input_schema") or tool.get("parameters") or {"type": "object"},
                },
            }
        )
    return converted


class OcxProvider(LLMProvider):
    """Chat Completions client with an OpenAI-style tool loop."""

    def __init__(self, model: str, base_url: str, api_key: str, timeout: int = 180):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self._api_key = api_key
        self.timeout = timeout
        self._ctx = ssl.create_default_context()

    def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=data,
            method="POST",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=self._ctx) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")[:800]
            raise RuntimeError(f"OCX HTTP {exc.code}: {body}") from exc

    def complete(
        self,
        messages: list[LLMMessage],
        max_tokens: int = 4096,
        temperature: float = 0.0,
        **kwargs,
    ) -> LLMResponse:
        raw = self._post(
            {
                "model": self.model,
                "messages": [{"role": m.role, "content": m.content} for m in messages],
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
        )
        choice = raw["choices"][0]["message"]
        usage = raw.get("usage") or {}
        return LLMResponse(
            content=choice.get("content") or "",
            usage={
                "input_tokens": usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
            },
            raw=raw,
        )

    def complete_with_tools(
        self,
        messages: list[LLMMessage],
        tools: list[dict[str, Any]],
        max_tokens: int = 4096,
        **kwargs,
    ) -> LLMResponse:
        raw = self._post(
            {
                "model": self.model,
                "messages": [{"role": m.role, "content": m.content} for m in messages],
                "max_tokens": max_tokens,
                "tools": _to_openai_tools(tools),
            }
        )
        choice = raw["choices"][0]["message"]
        usage = raw.get("usage") or {}
        return LLMResponse(
            content=choice.get("content") or "",
            usage={
                "input_tokens": usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
            },
            raw=raw,
        )

    def converse_loop(
        self,
        system_prompt: str,
        user_message: str,
        tools: list[dict[str, Any]],
        tool_executor: dict[str, Any],
        max_tokens: int = 16384,
        max_turns: int = 20,
    ) -> LLMResponse:
        messages: list[dict[str, Any]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_message})
        openai_tools = _to_openai_tools(tools)
        name_by_openai = {
            item["function"]["name"]: item["function"]["name"] for item in openai_tools
        }

        total_in = 0
        total_out = 0
        texts: list[str] = []
        last_raw: Any = None

        for _ in range(max_turns):
            raw = self._post(
                {
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "tools": openai_tools,
                }
            )
            last_raw = raw
            usage = raw.get("usage") or {}
            total_in += usage.get("prompt_tokens", 0)
            total_out += usage.get("completion_tokens", 0)
            message = raw["choices"][0]["message"]
            content = message.get("content") or ""
            if content:
                texts.append(content)
            tool_calls = message.get("tool_calls") or []
            messages.append(
                {
                    "role": "assistant",
                    "content": content or None,
                    "tool_calls": tool_calls or None,
                }
            )
            if not tool_calls:
                break
            for call in tool_calls:
                fn = call.get("function") or {}
                name = fn.get("name") or ""
                raw_args = fn.get("arguments") or "{}"
                try:
                    args = json.loads(raw_args) if isinstance(raw_args, str) else (raw_args or {})
                except json.JSONDecodeError:
                    args = {"command": raw_args}
                executor = tool_executor.get(name) or tool_executor.get(name_by_openai.get(name, ""))
                if executor is None:
                    result_text = f"ERROR: Unknown tool '{name}'"
                else:
                    try:
                        result_text = executor(**args) if isinstance(args, dict) else executor(args)
                    except Exception as exc:  # noqa: BLE001 — tool sandbox
                        result_text = f"ERROR: {exc}"
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.get("id", name),
                        "content": str(result_text),
                    }
                )

        return LLMResponse(
            content="\n".join(texts),
            usage={"input_tokens": total_in, "output_tokens": total_out},
            raw=last_raw,
        )


def make_ocx_provider(config: EvolveConfig) -> OcxProvider | None:
    creds = resolve_ocx_credentials()
    if creds is None:
        return None
    base, key = creds
    model = os.environ.get("OCX_EVOLVER_MODEL") or config.evolver_model
    return OcxProvider(model=model, base_url=base, api_key=key)
