from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def compute_group_near_violations(cuts: list[dict[str, Any]], max_distance: int = 2) -> int:
    violations = 0
    for i, cut in enumerate(cuts):
        gid = cut.get("group_id")
        if not gid:
            continue
        for j in range(i + 1, min(len(cuts), i + max_distance + 1)):
            if cuts[j].get("group_id") == gid:
                violations += 1
    return violations


def compute_metrics(cuts: list[dict[str, Any]]) -> dict[str, Any]:
    cut_count = len(cuts)
    if cut_count == 0:
        return {
            "CUT_COUNT": 0,
            "TAG_COVERAGE": 0.0,
            "GROUP_COVERAGE": 0.0,
            "GROUP_NEAR_VIOLATIONS": 0,
        }

    tag_covered = sum(1 for c in cuts if c.get("tags"))
    group_covered = sum(1 for c in cuts if c.get("group_id"))

    return {
        "CUT_COUNT": cut_count,
        "TAG_COVERAGE": tag_covered / cut_count,
        "GROUP_COVERAGE": group_covered / cut_count,
        "GROUP_NEAR_VIOLATIONS": compute_group_near_violations(cuts, max_distance=2),
    }


def format_report(metrics: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# kubo_report.latest",
            f"CUT_COUNT: {metrics['CUT_COUNT']}",
            f"TAG_COVERAGE: {metrics['TAG_COVERAGE'] * 100:.1f}%",
            f"GROUP_COVERAGE: {metrics['GROUP_COVERAGE'] * 100:.1f}%",
            f"GROUP_NEAR_VIOLATIONS: {metrics['GROUP_NEAR_VIOLATIONS']}",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate kubo_report.latest.md")
    parser.add_argument("--input", default="edit_plan.mv.json")
    parser.add_argument("--output", default="kubo_report.latest.md")
    args = parser.parse_args()

    plan = json.loads(Path(args.input).read_text(encoding="utf-8"))
    cuts = plan.get("cuts", [])
    metrics = compute_metrics(cuts)
    Path(args.output).write_text(format_report(metrics), encoding="utf-8")


if __name__ == "__main__":
    main()
