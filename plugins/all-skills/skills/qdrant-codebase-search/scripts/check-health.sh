#!/usr/bin/env bash
set -euo pipefail

# Health check for Qdrant + Ollama infrastructure
# Usage: check-health.sh [--qdrant-url URL] [--ollama-url URL] [--model MODEL]

QDRANT_URL="${QDRANT_URL:-http://localhost:6333}"
OLLAMA_URL="${EMBEDDING_BASE_URL:-http://localhost:11434}"
EMBEDDING_MODEL="${EMBEDDING_MODEL:-nomic-embed-text}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --qdrant-url) QDRANT_URL="$2"; shift 2 ;;
        --ollama-url) OLLAMA_URL="$2"; shift 2 ;;
        --model) EMBEDDING_MODEL="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: $0 [--qdrant-url URL] [--ollama-url URL] [--model MODEL]"
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

ERRORS=0

echo "=== Qdrant Codebase Search — Health Check ==="
echo ""

# Check Qdrant
echo -n "Qdrant ($QDRANT_URL): "
if QDRANT_RESP=$(curl -sf --max-time 5 "${QDRANT_URL}/healthz" 2>/dev/null); then
    echo "OK"
    # Show collections count
    COLLECTIONS=$(curl -sf --max-time 5 "${QDRANT_URL}/collections" 2>/dev/null)
    if [[ -n "$COLLECTIONS" ]]; then
        COUNT=$(echo "$COLLECTIONS" | grep -o '"name"' | wc -l | tr -d ' ')
        echo "  Collections: $COUNT"
    fi
else
    echo "FAILED"
    echo "  Cannot connect to Qdrant at $QDRANT_URL"
    echo "  Start with: docker run -d -p 6333:6333 -v qdrant_data:/qdrant/storage qdrant/qdrant"
    ERRORS=$((ERRORS + 1))
fi

echo ""

# Check Ollama
echo -n "Ollama ($OLLAMA_URL): "
if curl -sf --max-time 5 "${OLLAMA_URL}/api/version" >/dev/null 2>&1; then
    echo "OK"

    # Check embedding model
    echo -n "  Model ($EMBEDDING_MODEL): "
    MODELS=$(curl -sf --max-time 10 "${OLLAMA_URL}/api/tags" 2>/dev/null)
    if [[ -n "$MODELS" ]] && echo "$MODELS" | grep -q "$EMBEDDING_MODEL"; then
        echo "OK"
    else
        echo "NOT FOUND"
        echo "  Pull with: ollama pull $EMBEDDING_MODEL"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "FAILED"
    echo "  Cannot connect to Ollama at $OLLAMA_URL"
    echo "  Start with: ollama serve"
    ERRORS=$((ERRORS + 1))
fi

echo ""

# Check Node.js
echo -n "Node.js: "
if command -v node &>/dev/null; then
    NODE_VERSION=$(node -v 2>/dev/null | sed 's/v//' | cut -d. -f1)
    if [[ "$NODE_VERSION" -ge 22 ]]; then
        echo "OK (v$(node -v 2>/dev/null | sed 's/v//'))"
    else
        echo "v${NODE_VERSION} (need 22+)"
        echo "  Install: brew install node@22"
        ERRORS=$((ERRORS + 1))
    fi
else
    # Check homebrew node@22
    if [[ -x "/opt/homebrew/opt/node@22/bin/node" ]]; then
        echo "OK (/opt/homebrew/opt/node@22/bin/node)"
        echo "  Note: not in PATH, use --node-path in setup-mcp.sh"
    else
        echo "NOT FOUND"
        echo "  Install: brew install node@22"
        ERRORS=$((ERRORS + 1))
    fi
fi

echo ""

# Check npx
echo -n "npx: "
if command -v npx &>/dev/null; then
    echo "OK"
elif [[ -x "/opt/homebrew/opt/node@22/bin/npx" ]]; then
    echo "OK (/opt/homebrew/opt/node@22/bin/npx)"
else
    echo "NOT FOUND"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "=== Result ==="
if [[ $ERRORS -eq 0 ]]; then
    echo "All checks passed. Ready to use."
else
    echo "$ERRORS check(s) failed. Fix the issues above."
    exit 1
fi
