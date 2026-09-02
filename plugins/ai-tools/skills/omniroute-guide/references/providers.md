# Провайдеры

237 provider entries. Registry: `src/shared/constants/providers.ts` (Zod-validated at load).

## Категории

| Категория | Count | Примеры |
|-----------|-------|---------|
| **Free** | 3 | Qoder AI, Qwen Code, Kiro AI |
| **OAuth** | 14+ | Claude Code, Codex, Gemini, GitHub Copilot, Cursor, Kimi, Kiro, Antigravity, Windsurf, GitLab Duo |
| **API Key** | 120+ | OpenAI, Anthropic, DeepSeek, Groq, xAI, Mistral, Fireworks, Cohere, NVIDIA, OpenRouter, ... |
| **Self-Hosted** | 8+ | LM Studio, vLLM, Ollama Cloud, Xinference, Lemonade, Triton |
| **Custom** | prefixes | `openai-compatible-*`, `anthropic-compatible-*` |

Auto-generated catalog: `docs/reference/PROVIDER_REFERENCE.md` (`npm run gen:provider-reference`).

## Бесплатные провайдеры (без credit card)

| Provider | Models | Auth |
|----------|--------|------|
| **Kiro AI** | Claude models | OAuth, no key |
| **OpenCode Free** | Multiple | No auth |
| **Pollinations** | GPT-5, Claude, Gemini, ... | No key |

Dashboard → Providers → Add → Connect.

## OAuth провайдеры

Flow через dashboard OAuth wizard. Modules: `src/lib/oauth/providers/` (16+ modules).

Public upstream client_id/secret (Gemini/Antigravity-style) — **только** через `resolvePublicCred()` (`open-sse/utils/publicCreds.ts`), never string literals.

### OAuth repair

```bash
# Dashboard → Settings или
omniroute doctor   # checks OAuth env
```

## API Key провайдеры

1. Dashboard → Providers → Add Provider
2. Paste API key
3. Test connection
4. Sync models

Keys encrypted at rest (AES-256-GCM, `API_KEY_SECRET`).

## Self-Hosted

OpenAI-compatible endpoint URL + optional key.

Examples: LM Studio (`http://localhost:1234/v1`), vLLM, Ollama Cloud.

## Adding Provider (dev)

1. Register in `src/shared/constants/providers.ts`
2. Executor in `open-sse/executors/` (if custom)
3. Translator in `open-sse/translator/` (if non-OpenAI)
4. OAuth in `src/lib/oauth/constants/oauth.ts`
5. Models in `open-sse/config/providerRegistry.ts`
6. Tests in `tests/unit/`

## Model Sync

Automatic on connect + manual sync from dashboard.

Dev: env vars in `docs/reference/ENVIRONMENT.md` § Model Sync.

## Provider Resilience (per-provider)

- Circuit breaker — whole provider
- Connection cooldown — per key/account
- Model lockout — per model on connection

См. `references/resilience.md`.

## Pricing

Synced from LiteLLM via `src/lib/pricingSync.ts`.

MCP: `omniroute_sync_pricing` (scope `pricing:write`).

Dashboard → Costs.

## Quota

Preflight check before dispatch. P2C account selection quota-aware.

MCP: `omniroute_check_quota`.

Dashboard → Limits.

## CLI Provider command

```bash
omniroute provider list
omniroute provider add --provider openai --api-key sk-...
omniroute provider test --provider openai
omniroute provider remove --provider openai
```

## Free Tiers Guide

`docs/getting-started/FREE-TIERS-GUIDE.md` — detailed free tier matrix.

## Provider-specific docs

- Claude Web: `docs/providers/CLAUDE_WEB.md`
- AgentRouter: `docs/providers/AGENTROUTER.md`