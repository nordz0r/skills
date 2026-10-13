#!/usr/bin/env bash
# graph.json -> validated, rendered SVG + seamless GIF + MP4 per lens.
# usage: pr-lens-build.sh <graph.json> [outDir] [theme: dark|light|both]
#   PALETTE=github (default, renderer colours) | nopaste (paste.goldfinches.ru theme colours)
#   theme=both writes <lens>-dark.* and <lens>-light.*; a single theme writes <lens>.*
set -euo pipefail
GRAPH="$(realpath "${1:?usage: pr-lens-build.sh graph.json [outDir] [dark|light|both]}")"
OUT="$(mkdir -p "${2:-./pr-lens-out}" && realpath "${2:-./pr-lens-out}")"
THEME="${3:-dark}"; FPS="${FPS:-20}"; MIN_WIDTH="${MIN_WIDTH:-1600}"
PR_LENS_HOME="${PR_LENS_HOME:-$HOME/.cache/pr-lens-diagrams}"
HERE="$(cd "$(dirname "$0")" && pwd)"
[ -d "$PR_LENS_HOME/node_modules/@coldtea/pr-lens-cli" ] || bash "$HERE/pr-lens-setup.sh"
PALETTE="${PALETTE:-github}"
case "$THEME" in dark|light|both) ;; *) echo "theme must be dark, light or both" >&2; exit 2;; esac
case "$PALETTE" in github|nopaste) ;; *) echo "PALETTE must be github or nopaste" >&2; exit 2;; esac
cp "$HERE/record.mjs" "$PR_LENS_HOME/record.mjs"   # so `playwright` resolves from PR_LENS_HOME
cd "$PR_LENS_HOME"
npx pr-lens validate "$GRAPH"

# Neutral renderer colours -> palette. Diff colours (added/modified/removed) are kept.
recolor() { # <svg> <theme>
  [ "$PALETTE" = nopaste ] || return 0
  if [ "$2" = dark ]; then
    sed -i -E 's/([=:]["'"'"' ]?)#0d1117/\1#212427/gI; s/([=:]["'"'"' ]?)#1c2128/\1#1a1c1e/gI;
      s/([=:]["'"'"' ]?)#(3d444d|30363d|21262d)/\1#33373b/gI; s/([=:]["'"'"' ]?)#e6edf3/\1#e2e2e6/gI;
      s/([=:]["'"'"' ]?)#9198a1/\1#9ba3af/gI; s/([=:]["'"'"' ]?)#6e7681/\1#8ab4f8/gI' "$1"
  else
    sed -i -E 's/([=:]["'"'"' ]?)#f4f5f7/\1#e6ddd2/gI; s/([=:]["'"'"' ]?)#ffffff/\1#f3eee7/gI;
      s/([=:]["'"'"' ]?)#(d1d9e0|d8dee4)/\1#c9bdaf/gI; s/([=:]["'"'"' ]?)#f1f3f5/\1#e9e2d8/gI;
      s/([=:]["'"'"' ]?)#1f2328/\1#302b25/gI; s/([=:]["'"'"' ]?)#59636e/\1#625951/gI;
      s/([=:]["'"'"' ]?)#8c959f/\1#176b62/gI' "$1"
  fi
}

build_theme() { # <theme> <suffix>
  local theme="$1" sfx="$2" BG
  if [ "$PALETTE" = nopaste ]; then BG='#212427'; [ "$theme" = light ] && BG='#e6ddd2'
  else BG='#0d1117'; [ "$theme" = light ] && BG='#ffffff'; fi
  rm -rf "$OUT/render-$theme"; npx pr-lens render "$GRAPH" -o "$OUT/render-$theme" --theme "$theme" >/dev/null
  for svg in "$OUT"/render-"$theme"/*-"$theme"-*.svg; do
    lens="$(basename "$svg" | sed -E "s/-$theme-[0-9a-f]+\.svg$//")"
    recolor "$svg" "$theme"
    cp "$svg" "$OUT/$lens$sfx.svg"
    vbw="$(grep -o 'viewBox="[^"]*"' "$svg" | head -1 | awk '{print int($3)}')"
    w=$(( vbw > MIN_WIDTH ? vbw : MIN_WIDTH ))
    if [ "$lens" = architecture ]; then
      secs=11.2   # LCM(1.6s pulse, 0.7s hero-train spacing) -> seamless loop
    else
      secs="$(grep -o 'dur="[0-9.]*s"' "$svg" | head -1 | grep -o '[0-9.]*')"; secs="${secs:-8}"
    fi
    frames="$(mktemp -d)"
    node record.mjs "$svg" "$frames" "$secs" "$FPS" "$w" "$BG"
    ffmpeg -y -loglevel error -framerate "$FPS" -i "$frames/f%04d.png" -c:v libx264 -crf 18 -preset slow \
      -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" -movflags +faststart "$OUT/$lens$sfx.mp4"
    ffmpeg -y -loglevel error -framerate "$FPS" -i "$frames/f%04d.png" \
      -vf "scale=$w:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=none:diff_mode=rectangle" \
      -loop 0 "$OUT/$lens$sfx.gif"
    rm -rf "$frames"
    echo "✓ $lens ($theme, $PALETTE): $OUT/$lens$sfx.svg $OUT/$lens$sfx.gif $OUT/$lens$sfx.mp4 (${secs}s @ ${FPS}fps, ${w}px)"
  done
}

if [ "$THEME" = both ]; then build_theme dark -dark; build_theme light -light
else build_theme "$THEME" ""; fi
