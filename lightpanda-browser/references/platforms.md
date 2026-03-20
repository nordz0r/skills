# Platforms

## Supported targets

Use this skill for:

- Linux with a local `lightpanda` binary or Docker.
- macOS 13+ with a local `lightpanda` binary or Docker.
- Windows 10+/Server 2016+ with Docker or a manually installed binary.
- WSL as a Linux environment; if the browser runs in WSL, CDP clients may still run on the Windows host.

Official docs list Debian 12, Ubuntu 22.04/24.04, macOS 13+, Windows 10+, Windows Server 2016+, and WSL as supported environments.

## Runtime priority

Resolve runtime in this order:

1. Explicit cloud endpoint via `LIGHTPANDA_CDP_URL` or `LIGHTPANDA_MCP_URL`
2. Local binary via `LIGHTPANDA_BIN` or `lightpanda` in `PATH`
3. Docker image `lightpanda/browser:nightly`
4. Derived cloud endpoint from `LIGHTPANDA_TOKEN` and optional `LIGHTPANDA_CLOUD_REGION`

## Environment variables

- `LIGHTPANDA_BIN`: absolute path to the local binary.
- `LIGHTPANDA_CDP_URL`: remote CDP endpoint such as `wss://euwest.cloud.lightpanda.io/ws?token=...`.
- `LIGHTPANDA_MCP_URL`: remote MCP SSE endpoint such as `https://euwest.cloud.lightpanda.io/mcp/sse?token=...`.
- `LIGHTPANDA_TOKEN`: cloud token used to derive endpoints when explicit URLs are absent.
- `LIGHTPANDA_CLOUD_REGION`: `euwest` or `uswest`; defaults to `euwest`.
- `LIGHTPANDA_DOCKER_IMAGE`: override the default Docker image.
- `LIGHTPANDA_DISABLE_TELEMETRY`: set to `true` by default in local launch helpers.

## Windows and WSL notes

- Prefer Docker or cloud on native Windows unless a tested local binary is already installed.
- Prefer Linux-style local runtime inside WSL.
- Prefer writing temporary automation tasks into the system temp directory from Node (`os.tmpdir()`), not hard-coded `/tmp`, so the same workflow works on Windows, macOS, Linux, and WSL.
