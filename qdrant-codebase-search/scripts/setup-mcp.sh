#!/usr/bin/env bash
set -euo pipefail

# Setup MCP configuration for @mhalder/qdrant-mcp-server
# Usage: setup-mcp.sh --agent claude|codex|qwen [--qdrant-url URL] [--ollama-url URL] [--apply]

AGENT=""
QDRANT_URL="${QDRANT_URL:-http://localhost:6333}"
OLLAMA_URL="${EMBEDDING_BASE_URL:-http://localhost:11434}"
QDRANT_MCP_PACKAGE="${QDRANT_MCP_PACKAGE:-@mhalder/qdrant-mcp-server@3.3.1}"
NODE_PATH=""
APPLY_CHANGES=0

usage() {
    echo "Usage: $0 --agent claude|codex|qwen [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --agent         Agent to configure: claude, codex, qwen"
    echo "  --qdrant-url    Qdrant URL (default: $QDRANT_URL)"
    echo "  --ollama-url    Ollama URL (default: $OLLAMA_URL)"
    echo "  --apply         Actually write config / run agent CLI. Default: print for review only"
    echo "  --node-path     Custom path to node/npx (e.g., /opt/homebrew/opt/node@22/bin)"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --agent) AGENT="$2"; shift 2 ;;
        --qdrant-url) QDRANT_URL="$2"; shift 2 ;;
        --ollama-url) OLLAMA_URL="$2"; shift 2 ;;
        --apply) APPLY_CHANGES=1; shift ;;
        --node-path) NODE_PATH="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

[[ -z "$AGENT" ]] && { echo "Error: --agent is required"; usage; }

# Check prerequisites
check_command() {
    if ! command -v "$1" &>/dev/null; then
        echo "Error: $1 not found. Install Node.js 22+."
        exit 1
    fi
}

NPX_CMD="npx"
if [[ -n "$NODE_PATH" ]]; then
    NPX_CMD="${NODE_PATH}/npx"
    if [[ ! -x "$NPX_CMD" ]]; then
        echo "Error: npx not found at $NPX_CMD"
        exit 1
    fi
else
    check_command npx
fi

# Verify Node.js version >= 22
NODE_CMD="node"
[[ -n "$NODE_PATH" ]] && NODE_CMD="${NODE_PATH}/node"
NODE_VERSION=$("$NODE_CMD" -v 2>/dev/null | sed 's/v//' | cut -d. -f1)
if [[ "$NODE_VERSION" -lt 22 ]]; then
    echo "Error: Node.js 22+ required (found v${NODE_VERSION})"
    echo "Install: brew install node@22"
    echo "Then re-run with: --node-path /opt/homebrew/opt/node@22/bin"
    exit 1
fi

case "$AGENT" in
    claude)
        if [[ "$APPLY_CHANGES" -eq 1 ]]; then
            echo "Applying MCP config to Claude Code..."
            claude mcp add qdrant-mcp \
                -e QDRANT_URL="$QDRANT_URL" \
                -e EMBEDDING_PROVIDER=ollama \
                -e EMBEDDING_BASE_URL="$OLLAMA_URL" \
                -- "$NPX_CMD" -y "$QDRANT_MCP_PACKAGE"
            echo "Done. Verify with: claude mcp list"
        else
            echo "Review the following command, then re-run with --apply if it looks correct:"
            echo "claude mcp add qdrant-mcp \\"
            echo "  -e QDRANT_URL=$QDRANT_URL \\"
            echo "  -e EMBEDDING_PROVIDER=ollama \\"
            echo "  -e EMBEDDING_BASE_URL=$OLLAMA_URL \\"
            echo "  -- $NPX_CMD -y $QDRANT_MCP_PACKAGE"
        fi
        ;;
    codex)
        CONFIG_DIR="${HOME}/.codex"
        CONFIG_FILE="${CONFIG_DIR}/config.json"
        mkdir -p "$CONFIG_DIR"

        MCP_CONFIG=$(cat <<EOF
{
  "mcpServers": {
    "qdrant-mcp": {
      "command": "$NPX_CMD",
      "args": ["-y", "$QDRANT_MCP_PACKAGE"],
      "env": {
        "QDRANT_URL": "$QDRANT_URL",
        "EMBEDDING_PROVIDER": "ollama",
        "EMBEDDING_BASE_URL": "$OLLAMA_URL"
      }
    }
  }
}
EOF
)
        if [[ "$APPLY_CHANGES" -eq 1 && ! -f "$CONFIG_FILE" ]]; then
            echo "$MCP_CONFIG" > "$CONFIG_FILE"
            echo "Written to $CONFIG_FILE"
        else
            [[ -f "$CONFIG_FILE" ]] && echo "Warning: $CONFIG_FILE already exists."
            echo "Review the following MCP config manually:"
            echo "$MCP_CONFIG"
            [[ "$APPLY_CHANGES" -eq 0 ]] && echo "Re-run with --apply to write automatically when the target file does not exist."
        fi
        ;;
    qwen)
        CONFIG_DIR="${HOME}/.qwen-code"
        CONFIG_FILE="${CONFIG_DIR}/mcp.json"
        mkdir -p "$CONFIG_DIR"

        MCP_CONFIG=$(cat <<EOF
{
  "mcpServers": {
    "qdrant-mcp": {
      "command": "$NPX_CMD",
      "args": ["-y", "$QDRANT_MCP_PACKAGE"],
      "env": {
        "QDRANT_URL": "$QDRANT_URL",
        "EMBEDDING_PROVIDER": "ollama",
        "EMBEDDING_BASE_URL": "$OLLAMA_URL"
      }
    }
  }
}
EOF
)
        if [[ "$APPLY_CHANGES" -eq 1 && ! -f "$CONFIG_FILE" ]]; then
            echo "$MCP_CONFIG" > "$CONFIG_FILE"
            echo "Written to $CONFIG_FILE"
        else
            [[ -f "$CONFIG_FILE" ]] && echo "Warning: $CONFIG_FILE already exists."
            echo "Review the following MCP config manually:"
            echo "$MCP_CONFIG"
            [[ "$APPLY_CHANGES" -eq 0 ]] && echo "Re-run with --apply to write automatically when the target file does not exist."
        fi
        ;;
    *)
        echo "Error: Unknown agent '$AGENT'. Use: claude, codex, qwen"
        exit 1
        ;;
esac
