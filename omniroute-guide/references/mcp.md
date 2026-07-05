# MCP Server — полная справка

OmniRoute MCP встроен. **94 tools**, **30 scopes**, **3 transports**.

Source of truth: `open-sse/mcp-server/server.ts`, `schemas/tools.ts`.

## Запуск

```bash
# stdio (IDE integrations)
omniroute --mcp

# HTTP — нужен running server + включён MCP в dashboard
omniroute          # затем Dashboard → Endpoints → MCP ON
```

## Transports

| Transport | Endpoint / Command | Когда использовать |
|-----------|-------------------|-------------------|
| **stdio** | `omniroute --mcp` | Cursor, Cline, Claude Desktop |
| **sse** | `GET/POST /api/mcp/sse` | Browser/agent SSE clients |
| **streamable-http** | `POST/GET/DELETE /api/mcp/stream` | Claude Code HTTP, multi-session (`mcp-session-id`) |

Активный HTTP transport выбирается настройкой `mcpTransport`. Переключение закрывает сессии на другом transport.

## IDE Configuration

### Cursor / Cline / VS Code MCP

```json
{
  "mcpServers": {
    "omniroute": {
      "command": "omniroute",
      "args": ["--mcp"],
      "env": {
        "OMNIROUTE_API_KEY": "sk-your-key",
        "OMNIROUTE_BASE_URL": "http://localhost:20128"
      }
    }
  }
}
```

### Claude Code (HTTP)

```bash
claude mcp add-server omniroute --type http --url http://localhost:20128/api/mcp/stream
```

### Remote через tunnel

Non-loopback доступ к `/api/mcp/*` **только** с Bearer key + scope `manage`:

```bash
curl -i \
  -H "Authorization: Bearer sk-..." \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"client","version":"0"}}}' \
  https://your-host.example/api/mcp/stream
```

Без `manage` scope → `403 LOCAL_ONLY`.

## Включение в Dashboard

1. Dashboard → **Endpoints** → вкладка MCP
2. Toggle **MCP Enabled**
3. Выбрать transport: `sse` или `streamable-http`
4. API key со нужными scopes (или `*` / `read:*`)

## Tool Categories (94 total)

| Категория | Count | Примеры |
|-----------|-------|---------|
| Core (Phase 1) | 8 | `get_health`, `list_combos`, `route_request`, `check_quota` |
| Search | 1 | `web_search` |
| Advanced (Phase 2) | 11 | `simulate_route`, `explain_route`, `test_combo` |
| Cache | 2 | `cache_stats`, `cache_flush` |
| Compression | 5 | `compression_status`, `set_compression_engine` |
| 1Proxy | 3 | `oneproxy_fetch`, `oneproxy_rotate` |
| Memory | 3 | `memory_search`, `memory_add`, `memory_clear` |
| Skills | 4 | `skills_list`, `skills_execute` |
| Agent Skills Catalog | 3 | `agent_skills_list`, `agent_skills_get` |
| Pool | 6 | Connection pool management |
| Gamification | 8 | Levels, badges, leaderboard |
| Plugin | 8 | Marketplace install/enable |
| Notion | 6 | Context source CRUD |
| Obsidian | 22 | Vault search, notes, WebDAV |

Все tool names с префиксом `omniroute_` (кроме notion/obsidian tools).

## Essential Tools (стартовый набор)

```
omniroute_get_health          # Uptime, circuit breakers, cache
omniroute_list_combos         # Active combos + strategies
omniroute_check_quota         # Quota used/total, reset time
omniroute_route_request       # Chat через routing
omniroute_cost_report         # Cost by period
omniroute_list_models_catalog # Full model catalog
omniroute_switch_combo        # Activate/deactivate combo
omniroute_get_combo_metrics   # Combo performance
```

## Scopes (30)

| Scope | Tools |
|-------|-------|
| `read:health` | health, metrics, simulate, explain |
| `read:combos` | list_combos, get_combo_metrics |
| `write:combos` | switch_combo, set_routing_strategy |
| `read:quota` | check_quota |
| `execute:completions` | route_request, test_combo |
| `execute:search` | web_search |
| `read:usage` | cost_report, session_snapshot |
| `read:models` | list_models_catalog |
| `write:budget` | set_budget_guard |
| `write:resilience` | set_resilience_profile |
| `read:cache` / `write:cache` | cache tools |
| `read:compression` / `write:compression` | compression tools |
| `read:memory` / `write:memory` | memory tools |
| `read:skills` / `write:skills` / `execute:skills` | skill tools |
| `read:notion` / `write:notion` | notion tools |
| `read:catalog` | agent skills catalog |

Wildcards: `read:*` = all read scopes, `*` = full access.

## MCP Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `OMNIROUTE_BASE_URL` | `http://localhost:20128` | Internal API base |
| `OMNIROUTE_API_KEY` | empty | Bearer for internal calls |
| `OMNIROUTE_MCP_ENFORCE_SCOPES` | `false` | `"true"` — deny missing scopes |
| `OMNIROUTE_MCP_SCOPES` | empty | Default scope allowlist |
| `MCP_TOOL_DENY` | unset | Blacklist tools from `tools/list` |
| `MCP_TOOL_ALLOW` | unset | Allow-list only these tools |
| `OMNIROUTE_MCP_COMPRESS_DESCRIPTIONS` | on | Disable with `false` |

## REST Endpoints (management)

| Endpoint | Method | Auth |
|----------|--------|------|
| `/api/mcp/status` | GET | Management session |
| `/api/mcp/tools` | GET | Management |
| `/api/mcp/sse` | GET/POST | API key + scopes |
| `/api/mcp/stream` | POST/GET/DELETE | API key + scopes |
| `/api/mcp/audit` | GET | Management |
| `/api/mcp/audit/stats` | GET | Management |

## Audit

Каждый tool call → SQLite `mcp_tool_audit`. Scope denials → `scope_denied:<reason>`.

Dashboard: Endpoints → MCP → Audit tab.

## Heartbeat (stdio)

Файл: `${DATA_DIR}/runtime/mcp-heartbeat.json` (каждые 5s). Dashboard `/api/mcp/status` читает для `online`.

## Tool Cardinality Reduction

Уменьшение числа tools в `tools/list` для экономии контекста:

```bash
MCP_TOOL_DENY="omniroute_get_health,omniroute_list_combos" omniroute --mcp
MCP_TOOL_ALLOW="omniroute_route_request,omniroute_check_quota" omniroute --mcp
```

## MCP Accessibility Filter (v3.8+)

Post-execution filter сжимает browser/accessibility tool results (≥2000 chars). Не отдельный tool — прозрачный. Config: `compression.mcpAccessibility`.

## Validation

```bash
npm run test:protocols:e2e   # Full MCP+A2A E2E suite
```