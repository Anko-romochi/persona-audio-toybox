from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from clip_metadata import basename_for_cut, load_clip_meta


def enrich_cuts_with_metadata(cuts: list[dict[str, Any]], project: str) -> list[dict[str, Any]]:
    meta = load_clip_meta(project)
    enriched: list[dict[str, Any]] = []
    for cut in cuts:
        new_cut = dict(cut)
        basename = basename_for_cut(new_cut)
        new_cut["basename"] = basename
        clip_meta = meta.get(basename, {})
        new_cut["group_id"] = clip_meta.get("group_id")
        new_cut["tags"] = clip_meta.get("tags", [])
        # keep duration contract and all pre-existing fields untouched
        enriched.append(new_cut)
    return enriched


def main() -> None:
    parser = argparse.ArgumentParser(description="Build edit_plan.mv.json with clip metadata")
    parser.add_argument("--project", required=True)
    parser.add_argument("--input", required=True, help="Input JSON file with candidate clips/cuts")
    parser.add_argument("--output", default="edit_plan.mv.json")
    args = parser.parse_args()

    src = json.loads(Path(args.input).read_text(encoding="utf-8"))
    cuts = src["cuts"] if isinstance(src, dict) and "cuts" in src else src
    if not isinstance(cuts, list):
        raise ValueError("input must be a list of cuts or an object with cuts[]")

    output = {
        "project": args.project,
        "cuts": enrich_cuts_with_metadata(cuts, args.project),
    }
    Path(args.output).write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
