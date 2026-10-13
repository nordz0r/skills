#!/usr/bin/env bash
# graph.json -> validated, rendered SVG + seamless GIF + MP4 per lens.
# usage: pr-lens-build.sh <graph.json> [outDir] [theme: dark|light]
set -euo pipefail
GRAPH="$(realpath "${1:?usage: pr-lens-build.sh graph.json [outDir] [dark|light]}")"
OUT="$(mkdir -p "${2:-./pr-lens-out}" && realpath "${2:-./pr-lens-out}")"
THEME="${3:-dark}"; FPS="${FPS:-20}"; MIN_WIDTH="${MIN_WIDTH:-1600}"
PR_LENS_HOME="${PR_LENS_HOME:-$HOME/.cache/pr-lens-diagrams}"
HERE="$(cd "$(dirname "$0")" && pwd)"
[ -d "$PR_LENS_HOME/node_modules/@coldtea/pr-lens-cli" ] || bash "$HERE/pr-lens-setup.sh"
BG='#0d1117'; [ "$THEME" = light ] && BG='#ffffff'
cp "$HERE/record.mjs" "$PR_LENS_HOME/record.mjs"   # so `playwright` resolves from PR_LENS_HOME
cd "$PR_LENS_HOME"
npx pr-lens validate "$GRAPH"
rm -rf "$OUT/render"; npx pr-lens render "$GRAPH" -o "$OUT/render" --theme "$THEME" >/dev/null
for svg in "$OUT"/render/*-"$THEME"-*.svg; do
  lens="$(basename "$svg" | sed -E "s/-$THEME-[0-9a-f]+\.svg$//")"
  cp "$svg" "$OUT/$lens.svg"
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
    -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" -movflags +faststart "$OUT/$lens.mp4"
  ffmpeg -y -loglevel error -framerate "$FPS" -i "$frames/f%04d.png" \
    -vf "scale=$w:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=none:diff_mode=rectangle" \
    -loop 0 "$OUT/$lens.gif"
  rm -rf "$frames"
  echo "✓ $lens: $OUT/$lens.svg $OUT/$lens.gif $OUT/$lens.mp4 (${secs}s @ ${FPS}fps, ${w}px)"
done
