# A-Evolve Skill Router Pilot

This experiment turns the repo's skill eval prompts into a small routing benchmark for
[`a-evolve`](https://github.com/A-EVO-Lab/a-evolve).

The target behavior is narrow on purpose:

- input: a user prompt
- output: the single best skill to activate
- evolvable surface: skill texts inside an isolated workspace copy

## What is included

- `benchmark.py`: an `a-evolve` `BenchmarkAdapter` built from top-level `<skill>/evals/evals.json`
- `supplemental_cases.json`: extra ambiguous routing prompts for stress-testing nearby skills
- `agent.py`: a deterministic `SkillRouterAgent` that scores skills by prompt overlap
- `workspace.py`: materializes a separate mutable workspace from the current top-level skills
- `run_pilot.py`: runs the local `a-evolve` loop and prints train/holdout results
- `evaluate_baseline.py`: evaluates the current catalog without installing `a-evolve`

## Why this pilot

It is a low-risk way to try `a-evolve` against this repository:

- no edits to real skill folders during the experiment
- train/holdout split is balanced: `id=1` prompts are `train`, `id=2` prompts are `holdout`
- extra ambiguous benchmark cases live under `tools/a_evolve_router/supplemental_cases.json`
- the benchmark is cheap and deterministic
- improvements should show up as better routing phrasing, not as benchmark-specific code hacks

## Local baseline

From the repo root:

```bash
python3 -m tools.a_evolve_router.evaluate_baseline --split all
```

## Full a-evolve run with `uv`

1. Clone `a-evolve`.
2. Run the pilot from this repo root so the manifest entrypoint
   `tools.a_evolve_router.agent.SkillRouterAgent` is importable.

Example:

```bash
uv venv tools/a_evolve_router/.venv
uv pip install --python tools/a_evolve_router/.venv/bin/python --no-deps -e /path/to/a-evolve
uv pip install --python tools/a_evolve_router/.venv/bin/python pyyaml
PYTHONDONTWRITEBYTECODE=1 uv run --python tools/a_evolve_router/.venv/bin/python \
  -m tools.a_evolve_router.run_pilot --reset-workspace --engine heuristic --cycles 2
```

If you want a clean rerun each time, keep `--reset-workspace`.

To validate only the loop wiring, without LLM-backed mutation:

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --python tools/a_evolve_router/.venv/bin/python \
  -m tools.a_evolve_router.run_pilot --reset-workspace --engine none --cycles 1
```

To drive the evolver through the current logged-in Codex CLI session instead of API keys:

```bash
codex login status
PYTHONDONTWRITEBYTECODE=1 uv run --python tools/a_evolve_router/.venv/bin/python \
  -m tools.a_evolve_router.run_pilot --reset-workspace --engine codex --cycles 1
```

You can also pin a Codex model explicitly:

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --python tools/a_evolve_router/.venv/bin/python \
  -m tools.a_evolve_router.run_pilot --reset-workspace --engine codex \
  --codex-model gpt-5.4 --codex-reasoning-effort medium --cycles 1
```

## Windows / OneDrive notes

A few small adaptations were required to make the pilot run on Windows + OneDrive.
They are environment-only and do not change Linux/macOS behaviour.

- `tools/a_evolve_router/run_pilot.py` reads `AEVOLVE_WORKDIR` from the
  environment. If unset, it falls back to the previous default
  `tools/a_evolve_router/.workdir/evolution_workdir`. Set it to a path on a
  local (non-OneDrive) drive so a-evolve can write per-task patch files.
- `tools/a_evolve_router/workspace.py` reads `AEVOLVE_WORKSPACE` the same way.
- The `codex` engine picks up `CODEX_BIN` from the environment so the wrapper
  can point at the absolute path of `codex.cmd` (subprocess on Windows does
  not always inherit the shell `PATH`).
- `tools/a_evolve_router/catalog.py` uses PyYAML for frontmatter parsing so
  `description: >-` folded blocks load correctly. The line-by-line fallback
  is kept for environments without PyYAML.
- `task_id` is rendered with `__` instead of `::` because a-evolve's observer
  writes `patch_{task_id}.diff` straight to disk and `::` is reserved on
  Windows.

Example wrapper for Windows + Codex CLI:

```bash
set PYTHONDONTWRITEBYTECODE=1
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
set CODEX_BIN=C:\Users\You\AppData\Roaming\npm\codex.cmd
set AEVOLVE_WORKDIR=C:\Users\You\AppData\Local\Temp\a-evolve-pilot\evolution
set AEVOLVE_WORKSPACE=C:\Users\You\AppData\Local\Temp\a-evolve-pilot\skill-router
python -m tools.a_evolve_router.run_pilot --reset-workspace --engine codex --cycles 1
```

## Pilot run (2026-09-01)

What I actually ran, in order, on the current `main` snapshot of this repo
(31 top-level skills, 55 eval cases: 32 train / 23 holdout).

| Step | Engine | Cycles | Train acc@1 | Holdout acc@1 | avg_score | Notes |
|------|--------|--------|-------------|----------------|-----------|-------|
| 1. Baseline (before any change) | — | — | 81.25% | 86.96% | 0.8745 | router sees only the first line of `description:`; folded `>-` blocks read as the literal string `>-`, so 14 of 31 skills had no description. |
| 2. `parse_frontmatter` switched to PyYAML | — | — | 87.50% | 86.96% | 0.9045 | one-line parser fix in `catalog.py`; no `SKILL.md` touched. Train +6.25 pp, holdout stable. |
| 3. Heuristic engine | `heuristic` | 3 | 81.25% | 73.91% | 0.835 | net negative; `_apply_base_routing_signals` pulls every bullet token from every skill into a `Routing signals:` block, drowning the router in shared generic tokens (see failures below). |
| 4. Codex CLI engine | `codex` | 1 | not reached | not reached | — | failed in this environment: ChatGPT-account Codex cannot use `gpt-5`, and the default profile's MCP servers hit an OAuth-protected Cloudflare endpoint. The `--codex` engine is left in the code for Linux/CI runs that have an OpenAI API key. |

### Heuristic-engine failure mode

`_apply_base_routing_signals` in `heuristic_engine.py` walks the bullet list of
each `SKILL.md`, filters only the `GENERIC_TOKENS` blocklist, and appends
everything else (up to 18 tokens) as a `## Routing signals:` line at the bottom
of the file. Every skill then carries the same generic vocabulary ("system",
"design", "process", "structure"), so the router's weighted overlap stops
discriminating.

Per-case deltas after 3 heuristic cycles vs the patched baseline:

- **Holdout: 1 fixed, 4 regressed** (net -3 cases).
  - Regressed: `agency-technical-writer__2`, `agency-ui-designer__2`,
    `agency-ui-designer__supp-holdout-1`, `agency-ui-designer__neg-architect`.
  - Fixed: `ansible-playbook__2`.
- **Train: 5 fixed, 4 regressed** (net +1 case, but at the cost of 4 holdout
  regressions).

**Conclusion**: the heuristic engine as written is net-harmful on the current
skill set. It is left in the codebase because the design (mutate routing cues
in an isolated workspace) is sound; the implementation needs a per-skill
relevance threshold and a holdout-aware penalty before the next run.

### Known router limitations after the parser fix

Seven cases still fail on both train and holdout. They are honest
description-level collisions, not parser bugs:

- `agency-devops-automator::1` → `ansible-playbook` (DevOps description
  contains the word "Ansible").
- `agency-ux-researcher::1` → `nextcloud-admin` (Russian description overlap
  in tokenization).
- `agency-technical-writer::neg-devops` → `agency-incident-response-commander`
  (both mention "runbook").
- `preview-interview::neg-writer` → `agency-ui-designer` (UI designer wins
  on "design"/"system" tokens vs the same score for `preview-interview`).
- `administering-linux::2` → `ansible-playbook` (Russian generic-token
  overlap).
- `agency-technical-writer::2` → `open-terminal-guide` (Russian description
  overlap).
- `agency-incident-response-commander::neg-security` → `basic-memory-workflow`
  (active-leak prompt is correctly identified by humans as incident-class but
  the keyword "rotate keys" is sparse in the incident description).

Fixing these requires either richer routing features (bigrams, weighting by
heading position, or per-skill `negative_cues:` blocks) or hand-editing
descriptions. The pilot leaves them in place and surfaces them here so the
next iteration knows where to invest.

### Cross-skill negative cases added to `supplemental_cases.json`

`supplemental_cases.json` now contains 19 cases (up from 6). The new ones
stress-test the boundaries of skills that frequently confuse the router:

- `agency-incident-response-commander__neg-sre` (live outage → incident, not SRE)
- `agency-sre__neg-incident` (SLO/alert hygiene → SRE, not incident)
- `agency-devops-automator__neg-ansible` (Terraform/Atlantis → DevOps)
- `ansible-playbook__neg-devops` (Ansible role + molecule → Ansible only)
- `agency-security-engineer__neg-incident` (threat model → security, not incident)
- `agency-incident-response-commander__neg-security` (active token leak → incident commander first)
- `agency-ux-architect__neg-ui` (IA + CSS tokens → architect, not UI designer)
- `agency-ui-designer__neg-architect` (settings screen → UI designer, not architect)
- `agency-ux-researcher__neg-architect` (usability test plan → researcher, not architect)
- `agency-technical-writer__neg-devops` (rewrite runbook → writer, not DevOps)
- `basic-memory-workflow__neg-researcher` (save ADR + recall → memory, not research)
- `playwright-skill__neg-lightpanda` (standard Playwright test → playwright)
- `preview-interview__neg-writer` (FAANG STAR rehearsal → interview prep, not docs)

## Notes

- The pilot is tuned for `evolve_skills: true`; prompt and memory mutations are disabled by default.
- The default local path uses `HeuristicRoutingEngine`, which mutates routing cues in skill files
  without requiring API keys. Switch to `--engine default` only when you have a real `a-evolve`
  LLM provider configured.
- `--engine codex` uses `codex exec` with the current CLI login session. It does not need an
  OpenAI API key and does not read `~/.codex/auth.json` directly.
- The baseline agent is intentionally simple. The point is to let `a-evolve` improve the skill
  library's routing surface, not to hide the problem behind a stronger classifier.
- Runtime mutations live under `tools/a_evolve_router/.workdir/` and are safe to delete.
