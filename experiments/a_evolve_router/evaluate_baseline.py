from __future__ import annotations

import argparse
import json

from .catalog import load_eval_cases, load_skill_catalog
from .router import rank_skills


def evaluate(split: str) -> dict:
    skills = load_skill_catalog()
    cases = [case for case in load_eval_cases() if split == "all" or case.split == split]

    rows = []
    for case in cases:
        ranked = rank_skills(case.prompt, skills)
        selected = ranked[0].name if ranked else None
        top_three = [item.name for item in ranked[:3]]
        score = 1.0 if selected == case.expected_skill else 0.35 if case.expected_skill in top_three else 0.0
        rows.append(
            {
                "task_id": case.task_id,
                "split": case.split,
                "expected_skill": case.expected_skill,
                "selected_skill": selected,
                "top_three": top_three,
                "score": score,
                "expected_output": case.expected_output,
            }
        )

    accuracy = sum(1 for row in rows if row["selected_skill"] == row["expected_skill"]) / len(rows)
    avg_score = sum(row["score"] for row in rows) / len(rows)
    return {
        "split": split,
        "cases": len(rows),
        "top1_accuracy": round(accuracy, 4),
        "avg_score": round(avg_score, 4),
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the current skill-router baseline.")
    parser.add_argument(
        "--split",
        choices=["train", "holdout", "all"],
        default="all",
        help="Dataset split to evaluate.",
    )
    args = parser.parse_args()
    report = evaluate(args.split)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
