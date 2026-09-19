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

## Full a-evolve / Skillforge run

Install the PyPI package into the local venv (GitHub clone is optional; `main`
is still `0.1.0`). From the repo root:

```bash
python3 -m venv tools/a_evolve_router/.venv
tools/a_evolve_router/.venv/bin/pip install a-evolve
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 \
  tools/a_evolve_router/.venv/bin/python -m tools.a_evolve_router.run_pilot \
  --reset-workspace --engine none --cycles 1
```

`--engine none` validates the loop without mutating skills. Keep
`--reset-workspace` for a clean catalog copy.

Skillforge (`AEvolveEngine`) over OCX — isolated workspace only:

```bash
# OCX_API_KEY from ~/.hermes/.env, or export it.
# Optional: OCX_BASE_URL, OCX_EVOLVER_MODEL
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 \
  tools/a_evolve_router/.venv/bin/python -m tools.a_evolve_router.run_pilot \
  --reset-workspace --engine skillforge --cycles 1
```

`--engine default` is an alias of `skillforge`. PyPI `a-evolve` 0.1.0 only
runs the bash tool-loop on Bedrock; this repo wraps OCX in
`ocx_provider.py` / `skillforge_engine.py`.

Codex CLI instead of OCX:

```bash
codex login status
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 \
  tools/a_evolve_router/.venv/bin/python -m tools.a_evolve_router.run_pilot \
  --reset-workspace --engine codex --cycles 1
```

Do **not** use `--engine heuristic` on this catalog: it appends generic
routing-signal tokens and collapses discrimination.

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
- `tools/a_evolve_router/catalog.py` keeps the original line-based
  frontmatter parser on purpose. A PyYAML parser was wired in during the
  pilot and tested against the current catalog, but on `main` it
  regresses top-1 accuracy from 0.8364 to 0.7818 (see the pilot-run table
  below) because the heuristic router relies on the first-line-only
  description overlap to discriminate nearby skills. The line-based
  parser is left in place; a future switch to PyYAML should ship with a
  router that consumes the full description body.
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

## Pilot run (2026-09-20)

Catalog after dropping design-agency skills: 26 skills, 48 routing cases.
`telegram-formatting` remains a listed skill but is not in the `ai-tools` bundle.

| Step | Engine | Cycles | top1 acc | avg_score | Notes |
|------|--------|--------|----------|-----------|-------|
| 1. Baseline 2026-09-01 | — | — | 0.8364 (46/55) | 0.8745 | nine description collisions |
| 2. Quoted first-line tokens + `нужно` stopword | — | — | 1.0000 (64/64) | 1.0000 | 2026-09-20 |
| 3. Drop `basic-memory-workflow` | — | — | 1.0000 (63/63) | 1.0000 | |
| 4. Drop `lightpanda-browser` | — | — | 1.0000 (63/63) | 1.0000 | no evals |
| 5. Drop 4 design-agency skills | — | — | **1.0000 (48/48)** | 1.0000 | ui/ux/whimsy |

The former nine collisions (`administering-linux` 1/2, `amnezia-vpn` 1,
`ansible-playbook` 2, `gitlab-ci` 1, `linux-routing` 1,
`incident__neg-security`, `technical-writer__neg-devops`,
`preview-interview__neg-writer`) are closed by quoting `description` as a
single line with discriminating tokens. `>-` folded blocks are invisible to
the line-based parser.

Skillforge is wired for future fail-driven evolution. With top-1 = 1.0 it
correctly applies zero mutations. Do not copy `.workdir/` back into the repo.

### Cross-skill negative cases added to `supplemental_cases.json`

`supplemental_cases.json` keeps cross-skill negatives after dropping design-agency cases.

- `agency-incident-response-commander__neg-sre` (live outage → incident, not SRE)
- `agency-sre__neg-incident` (SLO/alert hygiene → SRE, not incident)
- `agency-devops-automator__neg-ansible` (Terraform/Atlantis → DevOps)
- `ansible-playbook__neg-devops` (Ansible role + molecule → Ansible only)
- `agency-security-engineer__neg-incident` (threat model → security, not incident)
- `agency-incident-response-commander__neg-security` (active token leak → incident commander first)
- `agency-technical-writer__neg-devops` (rewrite runbook → writer, not DevOps)
- `preview-interview__neg-writer` (FAANG STAR rehearsal → interview prep, not docs)
- `telegram-formatting__neg-writer` / `__neg-ui` (Rich Markdown vs docs rewrite)

## Notes

- Default `--engine` is `none` (loop wiring, no mutation).
- `--engine skillforge` / `default` uses Skillforge via OCX (`ocx_provider.py`).
- `--engine heuristic` is net-negative on this catalog — do not run it.
- `--engine codex` uses `codex exec` with the current CLI login.
- Mutations stay under `tools/a_evolve_router/.workdir/` and are safe to delete.
  Never copy that tree back into real skill folders.
