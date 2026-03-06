#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  ollama-search.sh --query <text>
  ollama-search.sh --query <text> --max-results <n>
  ollama-search.sh --query <text> --json

Options:
  --query         Search query (required)
  --max-results   Number of results, 1-10 (default: 5)
  --json          Output raw JSON instead of table
  -h, --help      Show this help

Environment:
  OLLAMA_API_KEY         Ollama API key (required)
  OLLAMA_WEB_SEARCH_URL  Override search endpoint (default: https://ollama.com/api/web_search)
EOF
}

api_key="${OLLAMA_API_KEY:-}"
web_search_url="${OLLAMA_WEB_SEARCH_URL:-https://ollama.com/api/web_search}"
query=""
max_results="5"
json_output="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --query)
      [[ $# -ge 2 ]] || { echo "missing value for --query" >&2; exit 2; }
      query="$2"
      shift 2
      ;;
    --max-results)
      [[ $# -ge 2 ]] || { echo "missing value for --max-results" >&2; exit 2; }
      max_results="$2"
      shift 2
      ;;
    --json)
      json_output="1"
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
  echo "OLLAMA_API_KEY is not set" >&2
  exit 2
fi

if [[ -z "$query" ]]; then
  echo "--query is required" >&2
  exit 2
fi

case "$max_results" in
  ''|*[!0-9]*)
    echo "--max-results must be a positive integer" >&2
    exit 2
    ;;
esac

if (( max_results < 1 || max_results > 10 )); then
  echo "--max-results must be between 1 and 10" >&2
  exit 2
fi

payload="$(jq -n --arg query "$query" --argjson max_results "$max_results" \
  '{query: $query, max_results: $max_results}')"

response="$(curl -fsS "$web_search_url" \
  -H "Authorization: Bearer $api_key" \
  -H "Content-Type: application/json" \
  -d "$payload")"

if [[ "$json_output" == "1" ]]; then
  printf '%s\n' "$response"
  exit 0
fi

jq -r '
  if (.results | length) == 0 then
    "No search results"
  else
    (
      ["TITLE\tURL\tCONTENT"],
      (
        .results[]
        | [
            .title // "-",
            .url // "-",
            ((.content // "-") | gsub("[\r\n\t]+"; " ") | .[0:220])
          ]
        | @tsv
      )
    )
  end
  | .[]
' <<<"$response"
