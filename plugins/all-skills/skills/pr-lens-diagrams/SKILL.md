---
name: pr-lens-diagrams
description: "Animated architecture and data-flow diagrams with PR Lens (@coldtea/pr-lens-cli): hand-write graph.json, validate it, render an animated SVG and record a seamless GIF/MP4 for chats (Telegram). Use when asked to draw a diagram, схему, архитектуру, связи сервисов или ботов, sequence/data-flow, animated diagram. Triggers: pr lens, prlens, диаграмма, схема, нарисуй, architecture diagram, data flow, animated svg, gif."
license: MIT
metadata:
  version: "1.0.0"
  author: "NorD (nordz0r)"
  platforms: "linux,macos"
  hermes:
    tags: [diagrams, pr-lens, architecture, data-flow, svg, gif]
---

# PR Lens diagrams

Russian version: [references/README.ru.md](references/README.ru.md).

[PR Lens](https://github.com/coldteadotai/pr-lens) (MIT, https://prlens.dev) renders a JSON graph document into a self-contained **animated SVG** (SMIL `<animateMotion>`, no scripts). A model key is only needed for `analyze` (graph from a git diff); for an arbitrary diagram the agent writes the JSON itself.

## Quick start

```bash
# deps: Node >= 20.11, npm, ffmpeg; Chromium is installed by the setup script
bash scripts/pr-lens-setup.sh                      # into $PR_LENS_HOME (default ~/.cache/pr-lens-diagrams)
bash scripts/pr-lens-build.sh my.graph.json out/   # → out/architecture.{svg,gif,mp4}, out/data-flow.{svg,gif,mp4}
```

- Start from `examples/bots.graph.json` (4 lanes, 12 nodes, 12 edges, 1 flow).
- The build validates, renders (`dark` by default, `light` as the 3rd arg), records frames with Playwright at `deviceScaleFactor: 2`, and encodes a non-dithered GIF and an MP4 (`crf 18`).
- Env: `PR_LENS_HOME`, `FPS` (20), `MIN_WIDTH` (1600), `PR_LENS_CLI_VERSION`, `PLAYWRIGHT_VERSION`.
- `npx skills add coldteadotai/pr-lens` crashes on Node 20 (`fs/promises` has no `glob`); not required. Version-matched docs: `npx pr-lens skill` / `npx pr-lens skill references` inside `$PR_LENS_HOME`.
- **Never publish without explicit user consent**: `pr-lens canvas push` puts the diagram on prlens.dev behind a view link anyone holding it can open.

## Document (schemaVersion 0.2.0)

Required: `schemaVersion, kind: "graph", title, lenses, provenance, lanes, nodes`; plus `edges`, `flows`.
- `provenance` is required even without a repo (dummy owner/name, 40-zero sha).
- `lanes` are **columns, left to right** by `order`; there is no "top" — the leftmost lane is the start.
- Node kinds: `service|app|module|function|route|job|queue|datastore|cache|external|ui|config|test|package|other`. Edge kinds: `call|http|rpc|event|queue|data|dependency|render|other`; `emphasis: normal|hero|muted`; `animated: true`.
- Use `delta: "unchanged"` everywhere for a plain diagram.
- `layout: { direction, laneOrder, rank }` are hints, never coordinates.

## How the animation works

1. Architecture: `animated` edges carry a dot (1.6 s). `hero` edges carry a 3-dot train (2.1 s, 0.7 s spacing) plus glow. Seamless loop = LCM(1.6, 0.7) = **11.2 s**.
2. Data-flow: add `"data-flow"` to `lenses` and `flows[]` (participants = node ids; messages `sync|async|return|self`). Steps light up in array order; loop length = `dur` in the SVG (7 steps → 9.8 s, max 16 s).
3. `walkthrough` and `payload` only play on a prlens.dev canvas.
4. Rasterizers (resvg, cairosvg, rsvg) ignore SMIL; capture in a browser with `pauseAnimations()` + `setCurrentTime(t)` (`scripts/record.mjs`).

## Beauty and quality lessons

- ≤ 10–12 nodes, ~12 edges. Merge similar things into group nodes; list members in `subtitle`. Express "everyone → X" in X's subtitle or via one aggregate node.
- 3–4 lanes, flow left → right (input → orchestrator → workers → output), no empty or overloaded lanes.
- One card per row: same-rank nodes in a lane are seated side by side, narrow and truncated. Give each node in a lane its own `layout.rank`. Rank is a floor (≥ predecessor + 1), so use a staircase 0,1,2,3…; rows are shared across lanes, so give linked neighbours the same rank for straight edges.
- Short labels: subtitle ~20 chars on a narrow card, ~45 on a wide one.
- `hero` only for 1–2 key paths; rare edges `muted`; no labels on obvious edges.
- Data-flow width ≈ 320 px per participant; keep ≤ 6–7 participants.
- Dark theme on `#0d1117` reads best in chats.
- Record at DPR 2, CSS width ≥ viewBox width and ≥ 1600 px, 20 fps.
- GIF: `palettegen=max_colors=128:stats_mode=diff` + `paletteuse=dither=none:diff_mode=rectangle`, lanczos to CSS width (~1 MB for 11 s). MP4 at full 2x.
- Telegram and most chats don't animate SVG — send GIF/MP4. GitHub PR comments do show animated SVG.
- Before delivery, crop a GIF frame at 1:1 and look at it; downscaled previews hide blur.
- `render` output names carry a hash; the build copies them to stable `<lens>.svg`.

## Agent workflow

1. List the entities and group them down to 10–12 nodes. Decide which 1–2 paths are the main ones (`hero`).
2. Copy `examples/bots.graph.json` and edit it: `lanes`, `nodes` with a `layout.rank` staircase, `edges`, and `flows` if needed.
3. Run `bash scripts/pr-lens-build.sh graph.json out/`. If `validate` names a wrong field, fix it.
4. Check the frames: no truncated labels, no paired cards, no crossings. Adjust ranks and labels if needed.
5. Hand the user the GIF or MP4, the `graph.json` source and the SVG.
