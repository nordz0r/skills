from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil

import agent_evolve as ae

from .agent import SkillRouterAgent
from .benchmark import SkillRouterBenchmark
from .catalog import EXPERIMENT_ROOT, REPO_ROOT
from .codex_cli_engine import CodexCliEngine
from .heuristic_engine import HeuristicRoutingEngine
from .noop_engine import NoMutationEngine
from .workspace import DEFAULT_WORKDIR, materialize_workspace


AEVOLVE_WORKDIR = EXPERIMENT_ROOT / ".workdir" / "evolution_workdir"


def _evaluate_split(agent: SkillRouterAgent, benchmark: SkillRouterBenchmark, split: str) -> dict:
    tasks = benchmark.get_tasks(split=split, limit=100)
    rows = []
    for task in tasks:
        trajectory = agent.solve(task)
        feedback = benchmark.evaluate(task, trajectory)
        rows.append(
            {
                "task_id": task.id,
                "expected_skill": task.metadata["expected_skill"],
                "score": feedback.score,
                "success": feedback.success,
                "selected_skill": feedback.raw.get("selected_skill"),
            }
        )

    accuracy = sum(1 for row in rows if row["success"]) / len(rows) if rows else 0.0
    avg_score = sum(row["score"] for row in rows) / len(rows) if rows else 0.0
    return {
        "split": split,
        "cases": len(rows),
        "top1_accuracy": round(accuracy, 4),
        "avg_score": round(avg_score, 4),
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local a-evolve skill-router pilot.")
    parser.add_argument(
        "--workspace",
        type=Path,
        default=DEFAULT_WORKDIR,
        help="Isolated workspace directory used by a-evolve.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=EXPERIMENT_ROOT / "pilot_config.yaml",
        help="Path to the a-evolve config YAML.",
    )
    parser.add_argument("--cycles", type=int, default=None, help="Override cycle count.")
    parser.add_argument(
        "--engine",
        choices=["default", "heuristic", "none", "codex"],
        default="heuristic",
        help="Use the default a-evolve engine, a local heuristic engine, a Codex CLI engine, or a no-mutation engine.",
    )
    parser.add_argument(
        "--codex-model",
        default=None,
        help="Optional model name passed through to `codex exec`, for example `gpt-5.4`.",
    )
    parser.add_argument(
        "--codex-reasoning-effort",
        choices=["low", "medium", "high"],
        default="medium",
        help="Reasoning effort passed through to `codex exec`.",
    )
    parser.add_argument(
        "--reset-workspace",
        action="store_true",
        help="Rebuild the isolated workspace from the current agency-* skills.",
    )
    args = parser.parse_args()

    workspace_path = materialize_workspace(args.workspace, repo_root=REPO_ROOT, reset=args.reset_workspace)
    if args.reset_workspace and AEVOLVE_WORKDIR.exists():
        shutil.rmtree(AEVOLVE_WORKDIR)
    benchmark = SkillRouterBenchmark(repo_root=REPO_ROOT)
    resolved_config = ae.EvolveConfig.from_yaml(args.config)
    if args.engine == "default":
        engine = None
    elif args.engine == "heuristic":
        engine = HeuristicRoutingEngine()
    elif args.engine == "codex":
        engine = CodexCliEngine(
            resolved_config,
            model=args.codex_model,
            reasoning_effort=args.codex_reasoning_effort,
        )
    else:
        engine = NoMutationEngine()

    evolver = ae.Evolver(
        agent=workspace_path,
        benchmark=benchmark,
        config=resolved_config,
        engine=engine,
        work_dir=AEVOLVE_WORKDIR,
    )
    result = evolver.run(cycles=args.cycles)

    evolved_workspace = evolver.agent.workspace.root
    agent = SkillRouterAgent(evolved_workspace)
    evaluation = {
        "train": _evaluate_split(agent, benchmark, "train"),
        "holdout": _evaluate_split(agent, benchmark, "holdout"),
    }
    print(
        json.dumps(
            {
                "workspace": str(workspace_path),
                "evolved_workspace": str(evolved_workspace),
                "cycles_completed": result.cycles_completed,
                "final_score": result.final_score,
                "score_history": result.score_history,
                "converged": result.converged,
                "evaluation": evaluation,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
