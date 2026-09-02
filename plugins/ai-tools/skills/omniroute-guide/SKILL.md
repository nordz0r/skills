---
name: omniroute-guide
description: "Полная справка по OmniRoute — unified AI proxy/router: архитектура, установка, провайдеры, combo/auto-маршрутизация, MCP (94 tools), A2A, API, dashboard, resilience, CLI-интеграции, env-переменные, отладка. Используй при любых вопросах об OmniRoute: как работает, от чего зависит, как управлять, подключить MCP/A2A, настроить провайдер, combo, auto, туннель, API key, resilience, compression, memory, skills. Триггеры: omniroute, AI router, LLM proxy, combo routing, auto-combo, MCP omniroute, A2A, /v1/chat/completions, provider fallback."
---

# OmniRoute — Полная справка (RU)

**OmniRoute** — локальный AI-шлюз и dashboard на Next.js 16. Один OpenAI-совместимый endpoint (`/v1/*`) маршрутизирует запросы через 237 провайдеров с переводом форматов, fallback, OAuth/API-key управлением, usage tracking, MCP (94 tools) и A2A v0.3.

**Версия в репозитории:** 3.8.44 · **Порт по умолчанию:** 20128 · **Runtime:** Node.js `>=22.0.0 <23 || >=24.0.0 <27`

## Структура репозитория

```text
OmniRoute/
├── src/                    # Next.js App Router (dashboard + /api/*)
│   ├── app/api/v1/         # OpenAI-совместимые API routes
│   ├── app/(dashboard)/    # Dashboard UI
│   ├── lib/db/             # SQLite domain modules (95 файлов)
│   ├── server/authz/       # Authorization pipeline
│   └── sse/                # SSE handlers (обёртка open-sse)
├── open-sse/               # Streaming engine (executors, translators, MCP)
│   ├── handlers/           # chatCore, embeddings, search, ...
│   ├── executors/          # Provider-specific HTTP dispatch
│   ├── services/           # combo, compression, rate limits, ...
│   └── mcp-server/         # 94 MCP tools, 3 transports
├── bin/omniroute.mjs       # CLI entry point
├── electron/               # Desktop app
└── docs/                   # Официальная документация
```

## Ключевые возможности

| Подсистема | Что делает |
|------------|------------|
| **V1 API** | `/v1/chat/completions`, `/v1/responses`, embeddings, images, audio, video, music, search, rerank, moderations |
| **Combo routing** | 17 стратегий (priority, auto, fusion, P2C, round-robin, ...) — цепочка fallback по провайдерам |
| **Auto-Combo** | `model: "auto"` / `auto/coding` / `auto/fast` — 12-факторный scoring, автовыбор лучшего провайдера |
| **Resilience** | 3 слоя: provider circuit breaker → connection cooldown → model lockout |
| **MCP Server** | 94 tools, 30 scopes, stdio / SSE / Streamable HTTP |
| **A2A Server** | JSON-RPC 2.0 + SSE, 6 skills, Agent Card at `/.well-known/agent.json` |
| **Memory** | FTS5 + Qdrant, injection/extraction между сессиями |
| **Skills** | Sandbox framework, built-in + custom skills |
| **Compression** | Caveman, RTK, stacked pipelines — сжатие промптов до upstream |
| **Dashboard** | Провайдеры, combos, costs, health, MCP/A2A tabs, playground |

## Навигация по справке

| Тема | Файл | Когда читать |
|------|------|-------------|
| Архитектура и pipeline | `references/architecture.md` | Как устроен запрос, слои, границы |
| API и заголовки | `references/api.md` | Endpoints, auth, custom headers |
| MCP (подключение, tools, scopes) | `references/mcp.md` | IDE config, transports, 94 tools |
| A2A протокол | `references/a2a.md` | Agent Card, JSON-RPC, skills |
| Маршрутизация и Auto-Combo | `references/routing.md` | Combos, strategies, auto variants |
| Resilience (3 слоя) | `references/resilience.md` | Circuit breaker, cooldown, lockout |
| Env и конфигурация | `references/config.md` | DATA_DIR, secrets, ports, feature flags |
| Dashboard | `references/dashboard.md` | Страницы UI, управление |
| CLI-интеграции | `references/cli-tools.md` | setup-*, launch, IDE pointing |
| Провайдеры | `references/providers.md` | OAuth, API-key, free tiers |
| Отладка | `references/troubleshooting.md` | Типичные проблемы и решения |

## Быстрый старт

### Установка

```bash
# npm (рекомендуется)
npm install -g omniroute
omniroute

# Docker
docker run -d --name omniroute -p 20128:20128 diegosouzapw/omniroute:latest

# Из исходников
git clone https://github.com/diegosouzapw/OmniRoute.git && cd OmniRoute
npm install && npm run dev
```

Dashboard: `http://localhost:20128`

### Первичная настройка секретов

```bash
cp .env.example .env
# Обязательно сгенерировать:
openssl rand -base64 48   # JWT_SECRET
openssl rand -hex 32      # API_KEY_SECRET
```

`INITIAL_PASSWORD` — пароль первого входа в dashboard (сменить после login).

### Подключение бесплатного провайдера

Dashboard → **Providers** → Add Provider → **Kiro AI** / **OpenCode Free** / **Pollinations** → Connect (без API key).

### Подключение IDE/CLI

```
Base URL: http://localhost:20128/v1
API Key:  [Dashboard → Endpoints → скопировать ключ]
Model:    auto
```

Проверка:

```bash
curl http://localhost:20128/v1/models -H "Authorization: Bearer YOUR_KEY"
```

### Автонастройка CLI

```bash
omniroute setup-claude
omniroute setup-codex
omniroute setup-opencode --remote http://VPS:20128 --api-key sk-...
omniroute launch          # Claude Code с env
omniroute launch-codex    # Codex CLI
```

## Request Pipeline (кратко)

```
Client → /v1/chat/completions
  → CORS → Zod validation → auth? → policy → prompt injection guard
  → handleChatCore()
    → cache → rate limit → combo routing?
      → resolveComboTargets() → handleSingleModel() per target
    → translateRequest() → getExecutor() → fetch upstream
    → response translation → SSE или JSON
```

Подробнее: `references/architecture.md`

## Auth (два режима)

| Режим | Где | Как |
|-------|-----|-----|
| **API Key** | `/v1/*`, MCP | `Authorization: Bearer <key>` |
| **Dashboard Session** | `/api/*` management | Cookie `auth_token` (JWT) |

Классы маршрутов: `PUBLIC` → `CLIENT_API` → `MANAGEMENT` (fail-closed).

API key с scope `manage` — доступ к management API и remote MCP bypass.

## MCP — быстрое подключение

### stdio (Cursor, Cline)

```json
{
  "mcpServers": {
    "omniroute": {
      "command": "omniroute",
      "args": ["--mcp"],
      "env": {
        "OMNIROUTE_API_KEY": "sk-..."
      }
    }
  }
}
```

### HTTP Streamable (Claude Code)

```bash
claude mcp add-server omniroute --type http --url http://localhost:20128/api/mcp/stream
```

**Включить MCP:** Dashboard → Endpoints → MCP toggle + выбрать transport (`sse` или `streamable-http`).

**Remote access:** Bearer key со scope `manage` — единственный способ к `/api/mcp/*` с non-loopback.

Полная справка: `references/mcp.md`

## A2A — быстрое подключение

```bash
# Agent Card
curl http://localhost:20128/.well-known/agent.json

# Задача
curl -X POST http://localhost:20128/a2a \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"message/send","params":{"skill":"smart-routing","messages":[{"role":"user","content":"Hello"}]}}'
```

Включить: Dashboard → Endpoints → A2A toggle.

Skills: `smart-routing`, `quota-management`, `provider-discovery`, `cost-analysis`, `health-report`, `list-capabilities`.

## Auto-Combo (model: auto)

| Модель | Назначение |
|--------|------------|
| `auto` | Баланс speed/cost/quality |
| `auto/coding` | Код, debugging |
| `auto/fast` | Минимальная latency |
| `auto/cheap` | Минимальная стоимость |
| `auto/smart` | Сложные задачи, exploration |
| `auto/offline` | Максимум доступной ёмкости |

При падении провайдера — автоматический fallback на следующий в combo.

## Resilience — 3 слоя (не путать!)

| Слой | Scope | Когда срабатывает |
|------|-------|-------------------|
| **Provider Circuit Breaker** | Весь провайдер | 408/500/502/503/504 повторно |
| **Connection Cooldown** | Один key/account | 401/403/429 на конкретном ключе |
| **Model Lockout** | Provider+connection+model | 429 per-model, 404 missing model |

Отладка: `/dashboard/health`, `omniroute_get_health` (MCP), `GET /api/monitoring/health`.

## Важные env-переменные

| Variable | Default | Назначение |
|----------|---------|------------|
| `DATA_DIR` | `~/.omniroute/` | SQLite DB, backups |
| `PORT` | `20128` | Dashboard + API (single-port) |
| `JWT_SECRET` | — | Dashboard JWT (обязателен) |
| `API_KEY_SECRET` | — | Шифрование API keys в DB |
| `REQUIRE_API_KEY` | feature flag | Требовать Bearer на `/v1/*` |
| `OMNIROUTE_API_KEY` | — | Passthrough key для MCP internal calls |

Полный список: `references/config.md` (синхронизирован с `.env.example`).

## CLI команды

```bash
omniroute                    # Запуск сервера
omniroute --mcp              # MCP stdio transport
omniroute --port 3000        # Другой порт
omniroute --no-open          # Без автооткрытия браузера
omniroute doctor             # Диагностика
omniroute setup --non-interactive --password "$PASS"
omniroute provider list      # Список провайдеров
```

## Security Guardrails (для агента)

- **PII redaction** — opt-in (`PII_REDACTION_ENABLED`, `PII_RESPONSE_SANITIZATION` = `false` по умолчанию). Не включать без явного запроса оператора.
- **Error sanitization** — ответы через `buildErrorBody()` / `sanitizeErrorMessage()`, никогда raw stack.
- **LOCAL_ONLY routes** — `/api/mcp/`, `/api/services/`, `/api/cli-tools/runtime/` только loopback (или `manage` scope для MCP).
- **Public upstream OAuth creds** — только через `resolvePublicCred()`, не string literals.

## Официальная документация (source of truth)

При расхождении со skill — верить репозиторию:

| Тема | Путь в репо |
|------|------------|
| Architecture | `docs/architecture/ARCHITECTURE.md` |
| MCP | `docs/frameworks/MCP-SERVER.md` |
| A2A | `docs/frameworks/A2A-SERVER.md` |
| API | `docs/reference/API_REFERENCE.md` |
| Env | `docs/reference/ENVIRONMENT.md` |
| Auto-Combo | `docs/routing/AUTO-COMBO.md` |
| Resilience | `docs/architecture/RESILIENCE_GUIDE.md` |
| AuthZ | `docs/architecture/AUTHZ_GUIDE.md` |
| Setup | `docs/guides/SETUP_GUIDE.md` |

## Workflow для агента

1. **Вопрос "как подключить X"** → `references/cli-tools.md` или `references/mcp.md`
2. **Ошибка маршрутизации** → `references/resilience.md` + `references/routing.md`
3. **Настройка env/deploy** → `references/config.md`
4. **API интеграция** → `references/api.md`
5. **Dashboard "где найти"** → `references/dashboard.md`
6. **Не работает** → `references/troubleshooting.md` + `omniroute doctor`

Перед утверждением фактов о коде — grep по `src/`, `open-sse/`, `bin/`. Если 0 hits — не документировать.