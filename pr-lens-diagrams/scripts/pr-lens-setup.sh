#!/usr/bin/env bash
# Install PR Lens CLI + Playwright Chromium into a local tool dir (no global installs, no `npx skills add`).
set -euo pipefail
PR_LENS_HOME="${PR_LENS_HOME:-$HOME/.cache/pr-lens-diagrams}"
PR_LENS_CLI_VERSION="${PR_LENS_CLI_VERSION:-0.13.0}"
PLAYWRIGHT_VERSION="${PLAYWRIGHT_VERSION:-1.64.0}"
node -e 'const [a,b]=process.versions.node.split(".").map(Number);if(a<20||(a===20&&b<11)){console.error("Node >= 20.11 required, have "+process.versions.node);process.exit(1)}'
command -v ffmpeg >/dev/null || { echo "ffmpeg not found: install it (apt install ffmpeg / brew install ffmpeg)" >&2; exit 1; }
mkdir -p "$PR_LENS_HOME"; cd "$PR_LENS_HOME"
[ -f package.json ] || npm init -y >/dev/null
npm install --no-fund --no-audit "@coldtea/pr-lens-cli@${PR_LENS_CLI_VERSION}" "playwright@${PLAYWRIGHT_VERSION}"
# On a bare Linux host add system libs: npx playwright install --with-deps chromium (needs root)
npx playwright install chromium
echo "PR Lens tools ready in $PR_LENS_HOME"
