# Конфигурация и Environment Variables

Source of truth: `docs/reference/ENVIRONMENT.md` + `.env.example` (sync enforced by `npm run check:env-doc-sync`).

## Обязательные секреты (первый запуск)

| Variable | Generate | Purpose |
|----------|----------|---------|
| `JWT_SECRET` | `openssl rand -base64 48` | Dashboard session JWT |
| `API_KEY_SECRET` | `openssl rand -hex 32` | AES encryption API keys in SQLite |
| `INITIAL_PASSWORD` | manual | First dashboard login password |
| `OMNIROUTE_WS_BRIDGE_SECRET` | `openssl rand -base64 32` | WS bridge (required in production) |

```bash
echo "JWT_SECRET=$(openssl rand -base64 48)"
echo "API_KEY_SECRET=$(openssl rand -hex 32)"
echo "OMNIROUTE_WS_BRIDGE_SECRET=$(openssl rand -base64 32)"
```

## Storage & Database

| Variable | Default | Notes |
|----------|---------|-------|
| `DATA_DIR` | `~/.omniroute/` | SQLite DB root |
| `STORAGE_ENCRYPTION_KEY` | disabled | Full DB encryption at rest |
| `DISABLE_SQLITE_AUTO_BACKUP` | `false` | Skip pre-migration backup |
| `OMNIROUTE_SKIP_DB_HEALTHCHECK` | `0` | Skip integrity check |

**Docker:** `DATA_DIR=/data` + volume mount.

**CI/Test:** `DATA_DIR=/tmp/omniroute-test`.

DB file: `${DATA_DIR}/omniroute.db` (WAL journaling).

## Network & Ports

### Single-port (default)

```
PORT=20128
→ Dashboard: http://localhost:20128
→ API:       http://localhost:20128/v1/chat/completions
```

### Split-port

```
API_PORT=20131      # /v1/* only
DASHBOARD_PORT=20130  # UI only
```

### Other ports

| Variable | Default | Service |
|----------|---------|---------|
| `LIVE_WS_PORT` | `20129` | Real-time monitoring WS |
| `OMNIROUTE_BASE_PATH` | empty | Subpath behind reverse proxy |

## Security & Auth

| Variable | Default | Notes |
|----------|---------|-------|
| `REQUIRE_API_KEY` | feature flag | DB override > env > default |
| `OMNIROUTE_API_KEY` | unset | Passthrough persistent key |
| `ROUTER_API_KEY` | unset | Alias for above |

Feature flags: `src/shared/constants/featureFlagDefinitions.ts` + DB override via dashboard.

**PII (opt-in only, default OFF):**
- `PII_REDACTION_ENABLED` = `false`
- `PII_RESPONSE_SANITIZATION` = `false`

## MCP-specific

| Variable | Default |
|----------|---------|
| `OMNIROUTE_BASE_URL` | `http://localhost:20128` |
| `OMNIROUTE_MCP_ENFORCE_SCOPES` | `false` |
| `OMNIROUTE_MCP_SCOPES` | empty |
| `MCP_TOOL_DENY` / `MCP_TOOL_ALLOW` | unset |

## Logging

| Variable | Default |
|----------|---------|
| `APP_LOG_LEVEL` | `info` |
| `APP_LOG_TO_FILE` | `false` |

## Outbound Proxy

Upstream requests через HTTP/SOCKS proxy — dashboard Settings → Proxy или env vars.
См. `docs/ops/PROXY_GUIDE.md`.

## Tunnels

Cloudflare Quick/Named, ngrok, Tailscale Funnel.
См. `docs/ops/TUNNELS_GUIDE.md`.

Remote MCP: tunnel + `manage` scope key.

## Deployment Scenarios

| Scenario | Key settings |
|----------|-------------|
| Local dev | defaults, no encryption |
| Docker prod | `DATA_DIR=/data`, secrets via env |
| VPS | `HOST=0.0.0.0`, tunnel optional |
| Electron | `OMNIROUTE_PORT` takes precedence |

## Setup headless

```bash
omniroute setup --non-interactive --password "$OMNIROUTE_PASSWORD"
omniroute setup --non-interactive --add-provider --provider openai --api-key "$OPENAI_API_KEY"
omniroute doctor
```

## Node.js Runtime

Supported: `>=22.0.0 <23 || >=24.0.0 <27`.

Recommended: Node 24.x LTS.

```bash
node --version  # must be in supported range
```