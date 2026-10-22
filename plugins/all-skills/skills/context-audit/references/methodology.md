# Context Engineering and Optimization Methodology

This document outlines the context auditing and optimization methodology used by the `context-audit` skill. It combines empirical measurement on agent runtime traces with principles adapted from upstream context engineering research.

## Upstream Attribution & Licenses

### 1. Agent Skills for Context Engineering (`context-optimization`)
- **Source**: [muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) (`skills/context-optimization/SKILL.md`)
- **License**: MIT
- **Copyright**: (c) 2025 Context Engineering Agent Skills Contributors
- **Notice**:
```text
MIT License

Copyright (c) 2025 Context Engineering Agent Skills Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 2. Agent Skills (`context-engineering`)
- **Source**: [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) (`skills/context-engineering/SKILL.md`)
- **License**: MIT
- **Copyright**: (c) 2025 Addy Osmani
- **Notice**:
```text
MIT License

Copyright (c) 2025 Addy Osmani

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Core Principles

1. **Measure Before and After on the Same Workload**
   Never claim token savings without comparing a verified before capture to an after capture under the same task requirements.
2. **Distinguish Prefix Caching from Total Context Size**
   A high prompt-cache hit rate lowers latency and token billing, but does not shrink the active context window or alleviate attention pressure.
3. **Separate Static Prefix from History**
   System prompts, tool schemas, and persistent instructions occupy a fixed prefix. Conversation history, tool inputs, and tool outputs grow dynamically. Optimizations that trim static overhead (such as compact tool schemas or progressive skill loading) reduce every turn's baseline, while conversation compaction reduces dynamic growth.
4. **Physical Deduplication Saves Zero Prompt Tokens by Itself**
   Deduplicating files on disk, creating symlinks, or archiving unused files does not change context usage unless those items were loaded into the prompt, tool catalog, or system instructions.
5. **Protect Critical Context Elements**
   When compacting or masking, never discard active error messages, failing test outputs, or user constraints for ongoing debugging. Mask or summarize resolved intermediate steps first.

---

## Metric Definitions and Verification

### Native JSONL Session Capture (`contextSnapshot`)
- Pinned implementation: `oh-my-pi` `v18.12.6` (`agent-session.ts`, `compaction.ts`, `ai/types.ts`).
- `promptTokens`: Provider usage-backed counter. omp prioritizes reported `usage.contextTokens` and falls back to `input + cacheRead + cacheWrite`. Output tokens are excluded.
- `nonMessageTokens`: Local tokenizer estimate calculated by the runtime across system prompt blocks and eligible wire tools.
- `toolSchemaTokens`: Optional local tokenizer estimate for tool schemas. When present, it is already included inside `nonMessageTokens` and must not be added to it.
- `non_tool_static_tokens`: Derived estimate: `nonMessageTokens - toolSchemaTokens`.
- `provider_anchor_remainder`: Derived residual: `promptTokens - nonMessageTokens`. This residual anchors provider-reported prompt usage against local static estimates; it reflects conversation history plus any protocol or provider-specific accounting differences.
- `historyRewriteTokensRemoved`: Optional counter present when history rewriting stripped tokens.
- `corrected_provider_prompt`: Derived field `max(0, promptTokens - historyRewriteTokensRemoved)` when history rewrite tokens are reported.

### Verified Dump JSON (`/dump`)
- Pinned implementation: `oh-my-pi` `v18.12.6` interactive mode `/dump` writing `/tmp/omp-llm-request-<id>.json`.
- Shape: Verified JSON object containing `systemPrompt` (string), `tools` (array), and `messages` (array).
- Character and UTF-8 byte sizes are deterministic measurements of the serialized components.
- `chars_divided_by_4_estimate` is a simple heuristic ratio, never an exact model tokenizer calculation.
- Wire serialization framing overhead is unknown and provider-dependent.
- Native counters and dump estimates must never be mixed in a single comparison.
