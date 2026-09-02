# CLI-интеграции

## Два flow

### Consumption (CLI → OmniRoute → Provider)

```
Claude Code / Codex / Cursor / Cline / Continue / OpenCode / ...
        ↓
http://YOUR_SERVER:20128/v1
        ↓
OmniRoute routes → Anthropic / OpenAI / Gemini / ...
```

### Reverse spawn (ACP Agents)

```
Client → OmniRoute → spawns CLI via stdio/ACP → response
```

Dashboard: `/dashboard/acp-agents`.

## Dashboard Pages

| Page | Route | Count |
|------|-------|-------|
| CLI Code's | `/dashboard/cli-code` | 20 |
| CLI Agents | `/dashboard/cli-agents` | 6 |
| ACP Agents | `/dashboard/acp-agents` | registry |

## Базовая конфигурация (любой OpenAI-compatible tool)

```
Base URL: http://localhost:20128/v1
API Key:  [from Dashboard → Endpoints]
Model:    auto
```

⚠️ Некоторые tools требуют `/v1` suffix, другие — нет. См. таблицу в `docs/guides/CLI-INTEGRATIONS.md`.

## setup-* commands (автонастройка)

```bash
omniroute setup-codex
omniroute setup-claude
omniroute setup-opencode
omniroute setup-cline
omniroute setup-kilo
omniroute setup-continue
omniroute setup-cursor
omniroute setup-roo
omniroute setup-crush
omniroute setup-goose
omniroute setup-qwen
omniroute setup-aider
```

### Flags

| Flag | Purpose |
|------|---------|
| `--remote <url>` | Configure local CLI against remote OmniRoute |
| `--api-key <key>` | API key for remote |
| `--dry-run` | Preview without writing |
| `--port <n>` | OmniRoute port (default 20128) |
| `--model <id>` | For tools without auto-discovery |
| `--yes` | Non-interactive |

### Remote example

```bash
omniroute setup-claude --remote http://192.168.0.15:20128 --api-key sk-...
```

## Launch commands (no config write)

```bash
omniroute launch          # Claude Code with injected env
omniroute launch-codex    # Codex CLI
```

## Claude Code

```bash
# API routing
omniroute setup-claude

# MCP (HTTP transport)
claude mcp add-server omniroute --type http --url http://localhost:20128/api/mcp/stream
```

## Cursor

Settings → Models → Override OpenAI Base URL:
`http://localhost:20128/v1`

MCP: см. `references/mcp.md` — stdio config.

## Codex CLI

```bash
omniroute setup-codex
# or
omniroute launch-codex
```

## Continue / Cline / Roo

Dashboard → CLI Code's → select tool → copy generated config or run `setup-*`.

## Source of Truth

Catalog: `src/shared/constants/cliTools.ts` (`CLI_TOOLS`).

Schema: `src/shared/schemas/cliCatalog.ts`.

Full table: `docs/guides/CLI-INTEGRATIONS.md`, `docs/reference/CLI-TOOLS.md`.

## Benefits

- One API key for all tools
- Unified cost tracking in dashboard
- Model switching without reconfiguring each CLI
- Works local, VPS, Docker, tunnel