# A2A Server — Agent-to-Agent Protocol v0.3

## Overview

- **JSON-RPC 2.0** at `POST /a2a` (`src/app/a2a/route.ts`)
- **REST** at `/api/a2a/*` (status, task list, cancel)
- **Agent Card** at `GET /.well-known/agent.json`
- Task TTL: 5 minutes (default), `A2ATaskManager`

## Enablement

Dashboard → **Endpoints** → A2A toggle (disabled by default).

When disabled: `POST /a2a` → HTTP 503, JSON-RPC `-32000`.

## Authentication

```
Authorization: Bearer YOUR_OMNIROUTE_API_KEY
```

Если API key не настроен на сервере — auth bypassed.

## Agent Discovery

```bash
curl http://localhost:20128/.well-known/agent.json
```

Returns: capabilities, skills, version (from `package.json`), auth requirements.

## Skills (6)

| Skill ID | Назначение |
|----------|------------|
| `smart-routing` | Рекомендация routing для задачи |
| `quota-management` | Сводка квот |
| `provider-discovery` | Доступные провайдеры/модели |
| `cost-analysis` | Анализ затрат |
| `health-report` | Health/circuit breaker status |
| `list-capabilities` | Список возможностей агента |

Handlers: `A2A_SKILL_HANDLERS` in `src/lib/a2a/taskExecution.ts`.

## JSON-RPC Methods

### message/send (sync)

```bash
curl -X POST http://localhost:20128/a2a \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_KEY" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "message/send",
    "params": {
      "skill": "smart-routing",
      "messages": [{"role": "user", "content": "Write hello world in Python"}],
      "metadata": {"model": "auto", "combo": "fast-coding"}
    }
  }'
```

Response includes: `task`, `artifacts`, `metadata` (routing_explanation, cost_envelope, resilience_trace, policy_verdict).

### message/stream (SSE)

```bash
curl -N -X POST http://localhost:20128/a2a \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_KEY" \
  -d '{"jsonrpc":"2.0","id":"1","method":"message/stream","params":{"skill":"smart-routing","messages":[{"role":"user","content":"Explain quantum computing"}]}}'
```

Events: working chunks → completed + metadata. Heartbeat comments between events.

### tasks/get

Query task status by ID.

### tasks/cancel

Cancel in-flight task.

## REST Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/a2a/status` | GET | online/disabled, version |
| `/api/a2a/tasks` | GET | List recent tasks |
| `/api/a2a/tasks/[id]` | GET | Task detail |
| `/api/a2a/tasks/[id]/cancel` | POST | Cancel task |

## Task Lifecycle

```
submitted → working → completed | failed | canceled
```

TTL cleanup automatic.

## vs MCP

| | MCP | A2A |
|---|-----|-----|
| Protocol | MCP JSON-RPC | A2A JSON-RPC v0.3 |
| Focus | Tool invocation (94 tools) | Skill-based agent tasks |
| Discovery | tools/list | Agent Card |
| Transport | stdio/SSE/HTTP | HTTP + SSE |

Оба протокола доступны с Dashboard → Endpoints.