---
name: context-audit
description: "Audit agent context composition, token budgets, and static versus dynamic inflation across system prompts, tool schemas, and conversation history. Use when assessing prompt overhead, analyzing session tokens, optimizing tool/skill catalogs, or measuring before/after context reduction. Triggers: context audit, token budget, context inflation, prompt tokens, system prompt overhead, tool schema tokens, context snapshot, context reduction, /dump analysis."
license: MIT
metadata:
  version: "1.0.0"
  source: "https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering, https://github.com/addyosmani/agent-skills"
  upstream_commit: "pinned-upstream-2025"
  upstream_synced: "2026-10-22"
---

# Context Audit

Read-only, evidence-based context auditing and optimization for agent sessions.

## Overview

Context auditing identifies what consumes the context window, distinguishes static prefix overhead (system prompts and tool schemas) from dynamic accumulation (conversation history and tool outputs), and measures actual token changes across iterations without guessing.

Russian reference: [references/methodology.md](references/methodology.md) covers methodology, attribution, and OMP runtime context internals. Additional schema details are documented in [references/omp_schema_evidence.md](references/omp_schema_evidence.md).

## Core Principles

1. **Measure Before and After**: Always establish a concrete baseline before recommending or applying context changes. Never claim savings without comparative measurements from the same workload.
2. **Prefix Caching != Window Reduction**: High prompt-cache hits reduce latency and cost, but do not free context space or reduce attention distraction.
3. **Separate Static Prefix from Dynamic History**: System prompts and tool schemas persist across all turns; message history grows per turn. A 500-token tool schema cut reduces every request, while conversation compaction addresses cumulative growth.
4. **Physical Deduplication Saves Zero Prompt Tokens**: Moving files to symlinks, pruning unread disk folders, or deduplicating storage has zero effect on prompt tokens unless those files were loaded into context or tool definitions.
5. **Protect Critical Working State**: During active debugging, never mask active error messages, failing test outputs, or user constraints. Mask only resolved intermediate steps.
6. **No Silent Mutation**: Context auditing is strictly read-only. Never disable tools or rewrite prompt files automatically.

## CLI Usage

The bundled standard-library script `scripts/audit_context.py` inspects native OMP session JSONL traces and verified `/dump` request sidecars.

### 1. Inspect a Native Session Snapshot

```bash
python3 scripts/audit_context.py inspect /path/to/session.jsonl --snapshot last
```

Select `first`, `last`, or an explicit record ID (`--snapshot 01a16083-322e-7424-8edd-de60baac85fb`).

Output provides:
- `prompt_tokens`: Provider usage-backed prompt counter (`usage.contextTokens ?? (input + cacheRead + cacheWrite)`). Output tokens excluded.
- `non_message_tokens`: Local tokenizer estimate for system prompt and tool schemas.
- `tool_schema_tokens`: Optional local tokenizer estimate for tool schemas (subset of `non_message_tokens`).
- `non_tool_static_tokens`: Derived static remainder (`non_message_tokens - tool_schema_tokens`).
- `provider_anchor_remainder`: Derived residual (`prompt_tokens - non_message_tokens`).

### 2. Compare Two Captures (or First vs Last)

```bash
# Compare first turn vs last turn in the same session
python3 scripts/audit_context.py compare /path/to/session.jsonl /path/to/session.jsonl --before first --after last

# Compare baseline session vs optimized session
python3 scripts/audit_context.py compare baseline.jsonl optimized.jsonl
```

The comparison calculates delta, reduction percentage, direction of change, and issues explicit warnings if models or compaction epochs differ.

### 3. Inspect Local `/dump` Sidecar

For pre-request inspection without session files:
```bash
python3 scripts/audit_context.py inspect /tmp/omp-llm-request-sample.json
```
Measures Unicode characters, UTF-8 bytes, and heuristic character estimates (`chars / 4`) for `systemPrompt`, `tools`, and `messages` without emitting sensitive payload contents. Native metrics and dump heuristics cannot be mixed in comparisons.

## Recommended Workflow

1. **Establish Baseline**: Run `audit_context.py inspect` on an existing session trace or capture `/dump` during a representative run.
2. **Identify Primary Overhead**:
   - If `tool_schema_tokens` dominates static tokens: prune unused tools or adopt progressive skill loading.
   - If `non_tool_static_tokens` dominates: streamline system prompt rules or extract reference docs into on-demand files.
   - If `provider_anchor_remainder` dominates: apply observation masking or trigger compaction on resolved turns.
3. **Apply Targeted Intervention**: Edit one layer at a time.
4. **Remeasure**: Run `audit_context.py compare` against the baseline. If no baseline was captured, explicitly state that savings are unmeasured.
