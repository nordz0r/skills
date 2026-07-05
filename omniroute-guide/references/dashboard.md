# Dashboard — страницы и управление

URL: `http://localhost:20128/dashboard` (redirect from `/`).

Auth: login with `INITIAL_PASSWORD` → JWT cookie `auth_token`.

## Основные страницы

| Route | Назначение |
|-------|------------|
| `/dashboard` | Quick start + provider overview |
| `/dashboard/endpoint` | API endpoints, MCP, A2A, keys, context sources |
| `/dashboard/providers` | Provider connections, OAuth, API keys |
| `/dashboard/combos` | Combo builder, strategies, routing rules |
| `/dashboard/auto-combo` | Auto-Combo scoring, mode packs, telemetry |
| `/dashboard/costs` | Cost aggregation, pricing |
| `/dashboard/analytics` | Usage, evals, combo target health |
| `/dashboard/limits` | Quota/rate controls |
| `/dashboard/cli-code` | CLI coding tools setup (20 tools) |
| `/dashboard/cli-agents` | CLI agent tools (6 tools) |
| `/dashboard/acp-agents` | ACP reverse-spawn agents |
| `/dashboard/agents` | → redirects to acp-agents |
| `/dashboard/cloud-agents` | Codex Cloud, Devin, Jules tasks |
| `/dashboard/skills` | A2A skill registry, sandbox |
| `/dashboard/memory` | Conversational memory inspection |
| `/dashboard/webhooks` | Webhook subscriptions |
| `/dashboard/batch` | Batch jobs |
| `/dashboard/cache` | Semantic + reasoning cache stats |
| `/dashboard/playground` | Interactive chat test |
| `/dashboard/health` | Circuit breakers, uptime, quotas |
| `/dashboard/logs` | Request/proxy/audit logs |
| `/dashboard/settings` | General, routing, resilience, feature flags |
| `/dashboard/context/caveman` | Caveman compression rules |
| `/dashboard/context/rtk` | RTK filters |
| `/dashboard/context/combos` | Compression pipeline combos |
| `/dashboard/compression` | Compression analytics |
| `/dashboard/api-manager` | API key lifecycle, scopes, permissions |
| `/dashboard/media` | Image/video/music playground |
| `/dashboard/search-tools` | Search provider testing |
| `/dashboard/translator` | Format conversion preview |
| `/dashboard/audit` | Compliance audit log |
| `/dashboard/usage` | Per-request usage browser |
| `/dashboard/onboarding` | First-run wizard |
| `/dashboard/system` | Runtime diagnostics, version |
| `/dashboard/changelog` | In-app CHANGELOG.md viewer |

Legacy redirects: `/dashboard/cli-tools` → `/dashboard/cli-code`.

## Endpoints Tab (ключевой для интеграций)

`/dashboard/endpoint` содержит:

- **API Keys** — create, scopes, manage toggle
- **Base URL** — copy for IDE config
- **MCP** — enable, transport select, status, audit
- **A2A** — enable, Agent Card link
- **Context Sources** — Notion, Obsidian tokens

## API Key Scopes (для MCP)

При создании ключа — toggle scopes или `manage` для full management access.

Для remote MCP через tunnel: обязательно `manage` scope.

## Settings Tabs

- **General** — system name, base URL
- **Routing** — default combo, strategy
- **Resilience** — circuit breaker thresholds, presets
- **Feature Flags** — REQUIRE_API_KEY, PII, compression toggles
- **Security** — password change, IP allowlist
- **Proxy** — outbound proxy config
- **Compression** — global mode, engines, MCP description compression

## Monitoring

- `/dashboard/health` — real-time
- Live WS: port 20129 (`LIVE_WS_PORT`), dashboard hooks via `useLiveDashboard`
- Public health: `GET /api/monitoring/health` (no auth, GET only)

## Provider Management Flow

1. Providers → Add Provider
2. Select type (OAuth / API Key / Self-hosted)
3. Connect (OAuth flow or paste key)
4. Test connection
5. Sync models (automatic or manual)
6. Add to combo or use `auto`

## First-run

`/dashboard/onboarding` wizard или:

```bash
omniroute setup --non-interactive --password "$PASS"
```