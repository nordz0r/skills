#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  ollama-fetch.sh --url <url>
  ollama-fetch.sh --url <url> --json
  ollama-fetch.sh --url <url> --links

Options:
  --url      URL to fetch content from (required)
  --json     Output raw JSON response
  --links    Include discovered links in output
  -h, --help Show this help

Environment:
  OLLAMA_SEARCH_API_KEY Ollama Web Search API key (required)
  OLLAMA_API_KEY        Legacy fallback name for the same key
  OLLAMA_WEB_FETCH_URL  Override fetch endpoint (default: https://ollama.com/api/web_fetch)
EOF
}

api_key="${OLLAMA_SEARCH_API_KEY:-${OLLAMA_API_KEY:-}}"
web_fetch_url="${OLLAMA_WEB_FETCH_URL:-https://ollama.com/api/web_fetch}"
target_url=""
json_output="0"
show_links="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --url)
      [[ $# -ge 2 ]] || { echo "missing value for --url" >&2; exit 2; }
      target_url="$2"
      shift 2
      ;;
    --json)
      json_output="1"
      shift
      ;;
    --links)
      show_links="1"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$api_key" ]]; then
  echo "OLLAMA_SEARCH_API_KEY is not set (OLLAMA_API_KEY is accepted as a legacy fallback)" >&2
  exit 2
fi

if [[ -z "$target_url" ]]; then
  echo "--url is required" >&2
  exit 2
fi

payload="$(jq -n --arg url "$target_url" '{url: $url}')"

response="$(curl -fsS "$web_fetch_url" \
  -H "Authorization: Bearer $api_key" \
  -H "Content-Type: application/json" \
  -d "$payload")"

if [[ "$json_output" == "1" ]]; then
  printf '%s\n' "$response"
  exit 0
fi

# Title
title="$(jq -r '.title // "No title"' <<<"$response")"
echo "=== $title ==="
echo ""

# Content
jq -r '.content // "No content"' <<<"$response"

# Links (optional)
if [[ "$show_links" == "1" ]]; then
  echo ""
  echo "=== Links ==="
  jq -r '(.links // [])[] ' <<<"$response"
fi
