#!/usr/bin/env bash
set -euo pipefail

# Run a locally installed qdrant-mcp-server build.
# This wrapper intentionally avoids `npx -y` so startup does not fetch code
# from the npm registry at runtime.

NODE_CMD="${NODE_CMD:-node}"
QDRANT_MCP_BIN="${QDRANT_MCP_BIN:-}"
QDRANT_MCP_ENTRY="${QDRANT_MCP_ENTRY:-${HOME}/.local/share/qdrant-mcp-server/build/index.js}"

if [[ -n "$QDRANT_MCP_BIN" ]] && command -v "$QDRANT_MCP_BIN" >/dev/null 2>&1; then
    exec "$QDRANT_MCP_BIN" "$@"
fi

if [[ -f "$QDRANT_MCP_ENTRY" ]]; then
    exec "$NODE_CMD" "$QDRANT_MCP_ENTRY" "$@"
fi

cat >&2 <<EOF
Local qdrant-mcp-server build not found.
Install it once and re-run:
  git clone https://github.com/mhalder/qdrant-mcp-server "$HOME/.local/share/qdrant-mcp-server"
  cd "$HOME/.local/share/qdrant-mcp-server"
  npm ci
  npm run build

Then either:
  export QDRANT_MCP_ENTRY="$HOME/.local/share/qdrant-mcp-server/build/index.js"
or:
  export QDRANT_MCP_BIN=/path/to/qdrant-mcp-server
EOF
exit 1
