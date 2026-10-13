---
name: open-terminal-guide
description: "Complete guide to Open Terminal, a self-hosted terminal REST API for AI agents. Use for any Open Terminal question: API endpoints, deployment (Docker, bare metal), configuration, Open WebUI integration, architecture, debugging, writing client code for Open Terminal. Also use when working on the open-terminal codebase: project structure, runner.py, main.py, MCP server, Jupyter notebooks. Triggers: open-terminal, open terminal, remote terminal API, /execute, /files, sandbox API, terminal sessions, Open WebUI terminal."
---

# Open Terminal — Complete Guide

Open Terminal is a lightweight self-hosted REST API that gives AI agents and automation tools a dedicated environment to run commands, manage files and execute code. It is part of the [Open WebUI](https://github.com/open-webui/open-webui) ecosystem.

## Two modes

| Mode | Description | Security |
|-------|----------|-------------|
| **Docker** | Isolated container with preinstalled Python, Node.js, git, ffmpeg, LaTeX, data science libraries, etc. | Sandbox, safe for AI agents |
| **Bare metal** | `pip install open-terminal` and run directly on the machine | Commands run with the user's privileges — no isolation |

## Quick start

```bash
# Set the key up front via a secret manager or env file
export OPEN_TERMINAL_API_KEY='<random-secret-from-secret-store>'
export OPEN_TERMINAL_IMAGE='ghcr.io/open-webui/open-terminal@sha256:<verified-digest>'

# Docker (recommended)
docker pull "$OPEN_TERMINAL_IMAGE"
docker run -d --name open-terminal --restart unless-stopped \
  -p 127.0.0.1:8000:8000 \
  -v open-terminal:/home/user \
  -e OPEN_TERMINAL_API_KEY="$OPEN_TERMINAL_API_KEY" \
  "$OPEN_TERMINAL_IMAGE"

# Bare metal via uvx (no install)
uvx open-terminal run --host 127.0.0.1 --port 8000 --api-key "$OPEN_TERMINAL_API_KEY"

# Bare metal via pip
pip install open-terminal
open-terminal run --host 127.0.0.1 --port 8000 --api-key "$OPEN_TERMINAL_API_KEY"
```

An API key auto-generated into the logs is only fine for a local throwaway test. For a persistent environment set the key explicitly via an env var or a `_FILE` secret.

## Authentication

All endpoints except `/health` require a Bearer token:

```
Authorization: Bearer $OPEN_TERMINAL_API_KEY
```

WebSocket terminals use **first-message auth** — the first message after connecting must be JSON:
```json
{"type": "auth", "token": "$OPEN_TERMINAL_API_KEY"}
```

## Security Guardrails

- Deploy Open Terminal only behind a VPN, reverse proxy or allowlist ACL. Never expose it directly to the internet without a separate isolation layer.
- In production prefer Docker/VM/a dedicated unprivileged user. Bare metal is acceptable only in a trusted environment.
- Use `/files/upload` with a `url` field, notebook `source` and `/proxy/{port}/{path}` only for trusted sources. Do not download URLs or execute fetched content without manual review.
- If PTY, notebooks or proxy are not needed, disable them via config or at the perimeter.
- Never paste real keys into commands, logs, issue trackers, JSON examples or messages to the agent.

## Main API groups

| Group | Purpose |
|--------|-----------|
| `POST /execute` | Run commands as background processes |
| `GET /execute/{id}/status` | Poll output and status |
| `POST /execute/{id}/input` | Send stdin to the process |
| `DELETE /execute/{id}` | Terminate (kill) the process |
| `GET /files/list` | List a directory |
| `GET /files/read` | Read a file (text/PDF/binary) |
| `POST /files/write` | Write a file |
| `POST /files/replace` | Find-and-replace in a file |
| `GET /files/grep` | Search file contents |
| `GET /files/glob` | Find files by name (glob patterns) |
| `GET /files/display` | Open a file in the user's UI |
| `POST /files/upload` | Upload a file (multipart or URL) |
| `POST /api/terminals` | Create an interactive PTY session |
| `WS /api/terminals/{id}` | WebSocket for the terminal |
| `GET /ports` | Detect listening TCP ports |
| `/proxy/{port}/{path}` | Reverse proxy to localhost:{port} |
| `GET /health` | Health check (no auth) |

Details for every endpoint are in `references/api.md`.

## Command execution model

Commands are started via `POST /execute` as **background processes**:

1. The command is spawned in a PTY (Unix) / WinPTY (Windows) / pipes (fallback)
2. It gets a UUID; output is written to a JSONL log in `LOG_DIR`
3. Status: `running` → `done` (or `killed`)
4. Output is read by polling `GET /execute/{id}/status` with `offset` and `tail`
5. Finished processes are removed automatically 5 minutes after completion

The `wait` parameter (0–300 s) lets you wait for completion inline — handy for short commands.

## Interactive terminals

PTY sessions are managed via REST + WebSocket:

1. `POST /api/terminals` — create a session (limit: `MAX_TERMINAL_SESSIONS`, default 16)
2. `WS /api/terminals/{id}` — connect (first-message auth → binary input/output frames)
3. Resize: a text JSON frame `{"type": "resize", "cols": 120, "rows": 40}`
4. Dead sessions are cleaned up automatically on listing

## Configuration

Precedence (highest to lowest):
1. CLI flags (`--host`, `--port`, `--api-key`)
2. Environment variables (`OPEN_TERMINAL_*`)
3. User config: `~/.config/open-terminal/config.toml`
4. System config: `/etc/open-terminal/config.toml`
5. Built-in defaults

The full table of environment variables and parameters is in `references/configuration.md`.

### Docker-specific variables

| Variable | Description |
|-----------|----------|
| `OPEN_TERMINAL_PACKAGES` | Space-separated apt packages installed at startup |
| `OPEN_TERMINAL_PIP_PACKAGES` | Space-separated pip packages installed at startup |

Handled by `entrypoint.sh` on every container start.

### Docker secrets

The `_FILE` convention is supported (as in PostgreSQL):
- `OPEN_TERMINAL_API_KEY_FILE=/run/secrets/api_key` — the value is read from the file
- `VAR` and `VAR_FILE` cannot be set at the same time

### Docker socket

For Docker CLI access from the container (build images, run containers):
```bash
docker run -d -p 8000:8000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v open-terminal:/home/user \
  "$OPEN_TERMINAL_IMAGE"
```
`entrypoint.sh` adds the user to the socket's group automatically. Mounting the Docker socket is equivalent to root on the host — do it only in a trusted environment.

## Open WebUI integration

Open Terminal integrates with Open WebUI in two ways:

### Direct Connection (from the browser)
The user connects their instance via **User Settings → Integrations → Open Terminal**. Requests go straight from the browser.

### System-Level (via the backend)
The admin configures it via **Admin Settings → Integrations → Open Terminal**. Requests are proxied through the Open WebUI backend. Several terminals can be configured with per-user/group access control.

In both cases the connection is added in the **Open Terminal** section (not as a tool server) — this provides a file sidebar for browsing, uploading and editing files.

## Codebase architecture

For working on the open-terminal source see `references/architecture.md`.

## MCP server

Open Terminal can run as an MCP (Model Context Protocol) server:

```bash
# Requires: pip install open-terminal[mcp]
open-terminal mcp --transport stdio
open-terminal mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

All FastAPI endpoints are exposed as MCP tools automatically via `FastMCP.from_fastapi()`.

## Jupyter Notebooks

Hidden endpoints (not in the OpenAPI schema) for per-cell notebook execution:

1. `POST /notebooks` — create a session (bound to an `.ipynb` file, starts a kernel)
2. `POST /notebooks/{session_id}/execute` — run a cell (by index, optionally overriding source)
3. `GET /notebooks/{session_id}` — session status
4. `DELETE /notebooks/{session_id}` — stop the kernel

Sessions are removed after 30 minutes of inactivity. The notebook is saved to disk after each execution.

<!-- A-EVOLVE-ROUTING-SIGNALS:START -->
## Routing signals: open terminal rest api execute files sessions sandbox command notebook self-hosted terminal api agents open_terminal_api_key
<!-- A-EVOLVE-ROUTING-SIGNALS:END -->

Russian version: [`references/README.ru.md`](references/README.ru.md).
