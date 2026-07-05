# API Reference (краткая справка)

Base URL: `http://localhost:20128/v1` (или custom `PORT` / split-port mode).

Auth: `Authorization: Bearer <api-key>` (когда `REQUIRE_API_KEY` включён).

## Основные endpoints

| Method | Path | Описание |
|--------|------|----------|
| POST | `/v1/chat/completions` | Chat (OpenAI format) |
| POST | `/v1/responses` | Responses API (unified handler) |
| POST | `/v1/embeddings` | Embeddings |
| POST | `/v1/images/generations` | Image generation |
| POST | `/v1/audio/transcriptions` | STT (multipart) |
| POST | `/v1/audio/speech` | TTS (binary audio) |
| POST | `/v1/videos/generations` | Video (ComfyUI/SD WebUI) |
| POST | `/v1/music/generations` | Music (ComfyUI) |
| POST | `/v1/moderations` | Content moderation |
| POST | `/v1/rerank` | Document reranking |
| POST | `/v1/search` | Web search gateway |
| GET | `/v1/models` | Model catalog |
| WS | `/v1/ws` | WebSocket bridge |

Aliases: `/api/v1/*`, `/chat/completions`, `/responses`, `/models`.

## Chat Completions — пример

```bash
curl -X POST http://localhost:20128/v1/chat/completions \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "auto",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": true
  }'
```

## Request Headers

| Header | Назначение |
|--------|------------|
| `X-OmniRoute-No-Cache` | `true` — bypass cache |
| `x-omniroute-no-memory` | `true` — skip memory/skills injection |
| `X-OmniRoute-Progress` | `true` — progress events |
| `X-Session-Id` / `x_session_id` | Sticky session affinity |
| `Idempotency-Key` / `X-Request-Id` | Dedup (5s window) |
| `x-omniroute-compression` | Per-request compression override (`off`, `default`, `engine:rtk`, combo name/id) |
| `x-omniroute-disabled-guardrails` | Opt-out guardrails for request |

## Response Headers (telemetry)

| Header | Описание |
|--------|----------|
| `X-OmniRoute-Cache` | `HIT` / `MISS` |
| `X-OmniRoute-Response-Cost` | USD (10 decimals) |
| `X-OmniRoute-Tokens-In` / `Out` | Token counts |
| `X-OmniRoute-Model` / `Provider` | Resolved routing |
| `X-OmniRoute-Latency-Ms` | Latency |
| `X-OmniRoute-Fallback-Attempts` | Fallback count (if > 0) |
| `X-OmniRoute-Compression` | Applied compression plan |
| `X-OmniRoute-Request-Id` | Correlation ID |
| `X-OmniRoute-Version` | Build version |

Cache HIT: `X-OmniRoute-Response-Cost` = 0, savings in `X-OmniRoute-Cost-Saved`.

## Management API (session или manage-scope key)

| Prefix | Назначение |
|--------|------------|
| `/api/providers/` | Provider CRUD, OAuth, sync models |
| `/api/combos/` | Combo management |
| `/api/settings/` | System settings |
| `/api/keys/` | API key lifecycle |
| `/api/monitoring/health` | Health (public readonly GET) |
| `/api/mcp/*` | MCP status, tools, transports, audit |
| `/api/a2a/*` | A2A status, tasks |

## Model naming

- `auto`, `auto/coding`, `auto/fast`, `auto/cheap`, `auto/smart`, `auto/offline`
- `provider/model` — force specific provider (e.g. `openai/gpt-4o`)
- Combo name as model — route through named combo
- Aliases — cross-proxy normalizations (30+ auto-seeded)

## Webhooks

7 event types, HMAC-signed, exponential backoff, auto-disable after 10 failures.
См. `docs/frameworks/WEBHOOKS.md`.

## OpenAPI

Полная спецификация: `docs/openapi.yaml` + `docs/reference/API_REFERENCE.md`.