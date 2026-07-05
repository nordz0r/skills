# Troubleshooting

## Quick Reference (90% проблем)

| Симптом | Причина | Решение |
|---------|---------|---------|
| Can't connect | Сервер не запущен | `omniroute` или `docker restart omniroute` |
| Invalid API key | Неверный/истёкший ключ | Перекопировать из Dashboard → Endpoints |
| Rate limit exceeded | Слишком много запросов | Подождать 1 мин или `model: auto` |
| Quota exceeded | Квота исчерпана | Больше провайдеров / free tiers (Kiro, Pollinations) |
| Slow responses | Provider busy | `model: auto/fast` или Groq/Cerebras |
| Wrong provider | auto выбрал другой | Нормально; force: `openai/gpt-4o` |
| 502 Bad Gateway | Provider down | Retry или `model: auto` |
| 401 Unauthorized | Bad credentials | Проверить key / re-OAuth |
| 429 Too Many Requests | Rate limited | Wait или больше providers |

## Quick Fixes

| Problem | Solution |
|---------|----------|
| First login fails | Set `INITIAL_PASSWORD` in `.env` |
| Wrong port | `PORT=20128`, `NEXT_PUBLIC_BASE_URL=http://localhost:20128` |
| No log files | `APP_LOG_TO_FILE=true` |
| EACCES permission | `DATA_DIR=/writable/path` |
| Login crash / blank | Node.js version — см. ниже |
| macOS dlopen error | `cd $(npm root -g)/omniroute/app && npm rebuild better-sqlite3` |
| Proxy fetch failed | Proxy config level — см. PROXY_GUIDE |

## Node.js Compatibility

**Supported:** `>=22.22.2 <23` or `>=24.0.0 <27`.

```bash
nvm install 24 && nvm use 24
node --version
npm install -g omniroute
omniroute
```

Symptoms of bad Node: blank login, `Module did not self-register`, native binding errors.

## MCP Issues

| Problem | Check |
|---------|-------|
| MCP tools not listed | MCP enabled in Dashboard → Endpoints |
| 400 wrong transport | Match `mcpTransport` setting (sse vs streamable-http) |
| 403 LOCAL_ONLY | Remote needs `manage` scope key |
| scope_denied | API key missing required scope |
| stdio not connecting | `which omniroute`, PATH in IDE config |
| Heartbeat offline | `${DATA_DIR}/runtime/mcp-heartbeat.json`, PID alive |

```bash
omniroute --mcp   # test stdio
curl http://localhost:20128/api/mcp/status  # needs dashboard session
npm run test:protocols:e2e
```

## Routing Issues

| Problem | Debug |
|---------|-------|
| Provider skipped | `/dashboard/health` — circuit breaker OPEN? |
| One key fails | Connection cooldown (`rateLimitedUntil`) |
| One model fails | Model lockout |
| auto picks wrong | `omniroute_explain_route` (MCP) |
| Combo all fail | Check all targets, `omniroute_test_combo` |

## A2A Issues

| Problem | Check |
|---------|-------|
| 503 on /a2a | A2A disabled — enable in Endpoints |
| Skill not found | Valid skill ID from Agent Card |
| Task timeout | Default 5min TTL |

```bash
curl http://localhost:20128/.well-known/agent.json
curl http://localhost:20128/api/a2a/status
```

## Database Issues

```bash
omniroute doctor
# MCP: omniroute_db_health_check
```

- WAL mode default
- Migrations on startup (110 files)
- Mass pending migrations guard: `OMNIROUTE_MAX_PENDING_MIGRATIONS=50`

## Diagnostics Commands

```bash
omniroute doctor
curl http://localhost:20128/api/monitoring/health
curl http://localhost:20128/v1/models -H "Authorization: Bearer KEY"
```

## Logs

Dashboard → `/dashboard/logs` (request, proxy, audit, console).

Env: `APP_LOG_LEVEL=debug`, `APP_LOG_TO_FILE=true`.

## Community

- Discord: https://discord.gg/EkzRkpzKYt
- GitHub Issues: https://github.com/diegosouzapw/OmniRoute/issues

## macOS Native Module Rebuild

```
dlopen ... slice is not valid mach-o file
```

```bash
cd $(npm root -g)/omniroute/app
npm rebuild better-sqlite3
omniroute
```