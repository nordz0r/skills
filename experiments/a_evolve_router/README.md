# A-Evolve Skill Router Pilot

This experiment turns the repo's `agency-*` eval prompts into a small routing benchmark for
[`a-evolve`](https://github.com/A-EVO-Lab/a-evolve).

The target behavior is narrow on purpose:

- input: a user prompt
- output: the single best `agency-*` skill to activate
- evolvable surface: skill texts inside an isolated workspace copy

## What is included

- `benchmark.py`: an `a-evolve` `BenchmarkAdapter` built from `agency-*/evals/evals.json`
- `supplemental_cases.json`: extra ambiguous routing prompts for stress-testing nearby skills
- `agent.py`: a deterministic `SkillRouterAgent` that scores skills by prompt overlap
- `workspace.py`: materializes a separate mutable workspace from the current `agency-*` skills
- `run_pilot.py`: runs the local `a-evolve` loop and prints train/holdout results
- `evaluate_baseline.py`: evaluates the current catalog without installing `a-evolve`

## Why this pilot

It is a low-risk way to try `a-evolve` against this repository:

- no edits to real skill folders during the experiment
- train/holdout split is balanced: `id=1` prompts are `train`, `id=2` prompts are `holdout`
- extra ambiguous benchmark cases live under `experiments/a_evolve_router/supplemental_cases.json`
- the benchmark is cheap and deterministic
- improvements should show up as better routing phrasing, not as benchmark-specific code hacks

## Local baseline

From the repo root:

```bash
python3 -m experiments.a_evolve_router.evaluate_baseline --split all
```

## Full a-evolve run with `uv`

1. Clone `a-evolve`.
2. Run the pilot from this repo root so the manifest entrypoint
   `experiments.a_evolve_router.agent.SkillRouterAgent` is importable.

Example:

```bash
uv venv experiments/a_evolve_router/.venv
uv pip install --python experiments/a_evolve_router/.venv/bin/python --no-deps -e /path/to/a-evolve
uv pip install --python experiments/a_evolve_router/.venv/bin/python pyyaml
PYTHONDONTWRITEBYTECODE=1 uv run --python experiments/a_evolve_router/.venv/bin/python \
  -m experiments.a_evolve_router.run_pilot --reset-workspace --engine heuristic --cycles 2
```

If you want a clean rerun each time, keep `--reset-workspace`.

To validate only the loop wiring, without LLM-backed mutation:

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --python experiments/a_evolve_router/.venv/bin/python \
  -m experiments.a_evolve_router.run_pilot --reset-workspace --engine none --cycles 1
```

To drive the evolver through the current logged-in Codex CLI session instead of API keys:

```bash
codex login status
PYTHONDONTWRITEBYTECODE=1 uv run --python experiments/a_evolve_router/.venv/bin/python \
  -m experiments.a_evolve_router.run_pilot --reset-workspace --engine codex --cycles 1
```

You can also pin a Codex model explicitly:

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --python experiments/a_evolve_router/.venv/bin/python \
  -m experiments.a_evolve_router.run_pilot --reset-workspace --engine codex \
  --codex-model gpt-5.4 --codex-reasoning-effort medium --cycles 1
```

## Notes

- The pilot is tuned for `evolve_skills: true`; prompt and memory mutations are disabled by default.
- The default local path uses `HeuristicRoutingEngine`, which mutates routing cues in skill files
  without requiring API keys. Switch to `--engine default` only when you have a real `a-evolve`
  LLM provider configured.
- `--engine codex` uses `codex exec` with the current CLI login session. It does not need an
  OpenAI API key and does not read `~/.codex/auth.json` directly.
- The baseline agent is intentionally simple. The point is to let `a-evolve` improve the skill
  library's routing surface, not to hide the problem behind a stronger classifier.
- Runtime mutations live under `experiments/a_evolve_router/.workdir/` and are safe to delete.
