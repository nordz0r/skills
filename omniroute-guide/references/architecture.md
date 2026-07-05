# Архитектура OmniRoute

## Executive Summary

OmniRoute — локальный AI routing gateway на Next.js 16. Один OpenAI-совместимый endpoint проксирует трафик через множество upstream провайдеров с translation, fallback, token refresh и usage tracking.

## Слои системы

| Слой | Путь | Назначение |
|------|------|------------|
| API Routes | `src/app/api/v1/` | Entry points (chat, embeddings, ...) |
| Handlers | `open-sse/handlers/` | Request processing |
| Executors | `open-sse/executors/` | Provider-specific HTTP dispatch |
| Translators | `open-sse/translator/` | OpenAI ↔ Claude ↔ Gemini |
| Transformer | `open-sse/transformer/` | Responses API ↔ Chat Completions |
| Services | `open-sse/services/` | Combo, rate limits, cache, compression |
| Database | `src/lib/db/` | SQLite (95 modules, 110 migrations) |
| Domain/Policy | `src/domain/` | Policy engine, cost rules, fallback |
| MCP | `open-sse/mcp-server/` | 94 tools, 3 transports |
| A2A | `src/lib/a2a/` | JSON-RPC 2.0 agent protocol |

## Request Pipeline

```
Client Request
  → src/app/api/v1/.../route.ts
    → CORS → Zod body validation
    → Optional auth (extractApiKey/isValidApiKey)
    → API key policy (enforceApiKeyPolicy)
    → Handler delegation (open-sse)
      → handleChatCore()
        → Semantic/signature cache check
        → Rate limit (rateLimitManager)
        → Combo routing? → handleComboChat()
          → resolveComboTargets() → handleSingleModel() per target
        → translateRequest() → getExecutor() → executor.execute()
          → fetch() upstream → retry w/ backoff
        → Response translation → SSE stream or JSON
        → Responses API: responsesTransformer TransformStream
```

**Нет глобального Next.js middleware** — interception route-specific.

## Combo Routing

`open-sse/services/combo.ts` — 17 стратегий:

`priority`, `weighted`, `fill-first`, `round-robin`, `P2C`, `random`, `least-used`, `cost-optimized`, `reset-aware`, `reset-window`, `headroom`, `strict-random`, `auto`, `lkgp`, `context-optimized`, `context-relay`, `fusion`.

- Каждый target → `handleSingleModel()` (обёртка `handleChatCore()` + circuit breaker)
- `fusion` — параллельный fan-out к панели моделей + judge synthesizes ответ

## System Context

```
[Claude Code, Codex, Cursor, Cline, Custom clients, Browser Dashboard]
        ↓
[OmniRoute Local Process]
  ├── V1 API /v1/*
  ├── Dashboard + Management /api/*
  ├── SSE Core (open-sse + src/sse)
  ├── SQLite (storage.sqlite)
  └── Usage tables + logs
        ↓
[Upstream: OAuth / API-key / Self-hosted providers]
```

## In Scope / Out of Scope

**In scope:** локальный gateway, dashboard APIs, OAuth/token refresh, translation/SSE, persistence, optional cloud sync.

**Out of scope:** cloud service за `NEXT_PUBLIC_CLOUD_URL`, SLA провайдеров, внешние CLI binaries.

## Monorepo layout

- `src/` — Next.js 16 app
- `open-sse/` — streaming engine workspace package
- `electron/` — desktop app
- `tests/` — unit/integration/e2e
- `bin/` — CLI (`omniroute.mjs`)

## Path aliases

- `@/*` → `src/`
- `@omniroute/open-sse` → `open-sse/`

## Runtime

- Node.js `>=22.0.0 <23 || >=24.0.0 <27` (единственный runtime для CLI/server/tests)
- Bun 1.3.10 — только dev gate scripts, не runtime
- Default port: 20128
- Data: `DATA_DIR` (default `~/.omniroute/`)

## Authorization Pipeline

```
Incoming → src/proxy.ts → runAuthzPipeline()
  1. Strip trusted internal headers
  2. classifyRoute() → PUBLIC | CLIENT_API | MANAGEMENT
  3. POLICIES[routeClass].evaluate(ctx)
     allow → stamp x-omniroute-auth-* → next()
     reject → JSON error / 302 login
```

См. `references/config.md` для auth env и `AUTHZ_GUIDE.md` в репо.