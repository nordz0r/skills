# OMP Runtime Context Schema Evidence

This reference documents the empirical and source-pinned context measurement schema in `oh-my-pi` (`v18.12.6`).

## 1. Native JSONL Context Snapshot

OMP stores interactive session traces as JSONL. Each record is an object with top-level attributes:
- `type`: record discriminator (e.g. `"message"`).
- `id`: unique record identifier string.
- `timestamp`: ISO-8601 string.
- `message`: nested message payload.

When `message.role === "assistant"`, the runtime attaches `message.contextSnapshot`:

```typescript
export interface ContextSnapshot {
  promptTokens: number;
  nonMessageTokens: number;
  toolSchemaTokens?: number;
  historyRewriteTokensRemoved?: number;
  compactionEpoch?: number;
  lastMessageTimestamp?: number | string;
}
```

### Source Mechanics
- `promptTokens`: Sourced from provider usage reporting. The runtime evaluates `usage.contextTokens ?? (input + cacheRead + cacheWrite)`. Generated completion tokens are strictly excluded.
- `nonMessageTokens`: Calculated by OMP's local tokenizer over active system prompt blocks and eligible wire tools.
- `toolSchemaTokens`: Optional local tokenizer calculation of tool declarations (names, descriptions, schemas, and examples). When present, it is an internal component of `nonMessageTokens`.
- `compactionEpoch`: Increments whenever the session history undergoes lossy compaction or summarization.

### Important Invariants
1. `toolSchemaTokens` is part of `nonMessageTokens`. Adding them together double-counts the tool schema footprint.
2. `nonMessageTokens` can occasionally exceed `promptTokens` in edge cases (e.g., mismatched local tokenizer rules vs provider token accounting).
3. The derived residual `promptTokens - nonMessageTokens` is labeled `provider_anchor_remainder`. It combines conversational messages, tool inputs/outputs, and provider protocol framing; it must not be treated as an exact message-token count.

---

## 2. Interactive `/dump` Payload

The OMP interactive slash command `/dump` captures the verbatim LLM request payload before sending and writes it to a local temporary file (typically `/tmp/omp-llm-request-<id>.json`).

### Verified Structure
```json
{
  "model": "model-identifier-string",
  "thinkingLevel": "off|low|medium|high",
  "serviceTier": "auto|default|flex|scale|priority|ultrafast",
  "systemPrompt": "full system instructions...",
  "tools": [
    {
      "name": "read",
      "description": "...",
      "parameters": { ... }
    }
  ],
  "messages": [
    {
      "role": "user",
      "content": "..."
    }
  ]
}
```

### Security and Sensitivity
- Dump files contain verbatim user prompts, credentials loaded into system instructions, and tool results.
- `context-audit` inspects size metrics (Unicode characters, UTF-8 bytes, heuristic character ratios) and component rankings, but deliberately omits message text and parameter definitions from audit reports.
- Dump inspection is strictly local; never upload or share dump payloads.
