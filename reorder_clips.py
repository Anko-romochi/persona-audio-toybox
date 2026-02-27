from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

# R1 extension scoring:
# - distance := absolute cut index difference
# - same basename at distance 1 is prohibited (very large penalty)
# - same group_id within distance <= 2 gets high penalty
# - same tag at distance 1 gets small penalty

PENALTY_BASENAME_ADJACENT = 10**9
PENALTY_GROUP_DISTANCE_2 = 100
PENALTY_TAG_ADJACENT = 10
PENALTY_TAG_BIAS = 2


def _overlap_count(tags_a: list[str], tags_b: list[str]) -> int:
    return len(set(tags_a).intersection(tags_b))


def score_candidate(sequence: list[dict[str, Any]], candidate: dict[str, Any], insert_index: int) -> int:
    score = 0

    for idx, prev in enumerate(sequence):
        distance = abs(insert_index - idx)

        if distance == 1 and prev.get("basename") == candidate.get("basename"):
            score += PENALTY_BASENAME_ADJACENT

        group_a = prev.get("group_id")
        group_b = candidate.get("group_id")
        if group_a and group_b and group_a == group_b and distance <= 2:
            score += PENALTY_GROUP_DISTANCE_2

        if distance == 1:
            score += PENALTY_TAG_ADJACENT * _overlap_count(prev.get("tags", []), candidate.get("tags", []))

    # small bias penalty: avoid over-concentrating tags in the last 4 cuts
    recent = sequence[max(0, insert_index - 4):insert_index]
    recent_tags: dict[str, int] = {}
    for cut in recent:
        for tag in cut.get("tags", []):
            recent_tags[tag] = recent_tags.get(tag, 0) + 1
    for tag in candidate.get("tags", []):
        score += PENALTY_TAG_BIAS * recent_tags.get(tag, 0)

    return score


def reorder_cuts(cuts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not cuts:
        return []

    remaining = [dict(c) for c in cuts]
    sequence = [remaining.pop(0)]

    while remaining:
        best_idx = 0
        best_score = None
        for i, cand in enumerate(remaining):
            s = score_candidate(sequence, cand, len(sequence))
            if best_score is None or s < best_score:
                best_score = s
                best_idx = i
        sequence.append(remaining.pop(best_idx))

    return sequence


def main() -> None:
    parser = argparse.ArgumentParser(description="Reorder cuts with metadata-aware penalties")
    parser.add_argument("--input", default="edit_plan.mv.json")
    parser.add_argument("--output", default="edit_plan.mv.json")
    args = parser.parse_args()

    plan = json.loads(Path(args.input).read_text(encoding="utf-8"))
    cuts = plan.get("cuts", [])
    if not isinstance(cuts, list):
        raise ValueError("edit plan must include cuts[]")

    plan["cuts"] = reorder_cuts(cuts)
    Path(args.output).write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
