from __future__ import annotations

import json
from pathlib import Path
from typing import Any


META_FILENAME = "clip_meta.json"


def clip_meta_path(project: str) -> Path:
    """SSOT path for clip metadata."""
    return Path("assets") / project / "clips" / META_FILENAME


def load_clip_meta(project: str) -> dict[str, dict[str, Any]]:
    path = clip_meta_path(project)
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must be a JSON object keyed by clip basename")

    normalized: dict[str, dict[str, Any]] = {}
    for basename, meta in data.items():
        if not isinstance(meta, dict):
            raise ValueError(f"metadata for {basename} must be an object")
        group_id = meta.get("group_id")
        tags = meta.get("tags", [])
        source = meta.get("source")
        notes = meta.get("notes")

        if group_id is not None and not isinstance(group_id, str):
            raise ValueError(f"group_id for {basename} must be a string or null")
        if not isinstance(tags, list) or any(not isinstance(t, str) for t in tags):
            raise ValueError(f"tags for {basename} must be an array of strings")
        if source is not None and not isinstance(source, str):
            raise ValueError(f"source for {basename} must be a string or null")
        if notes is not None and not isinstance(notes, str):
            raise ValueError(f"notes for {basename} must be a string or null")

        normalized[basename] = {
            "group_id": group_id,
            "tags": tags,
            "source": source,
            "notes": notes,
        }
    return normalized


def basename_for_cut(cut: dict[str, Any]) -> str:
    if "basename" in cut and isinstance(cut["basename"], str):
        return cut["basename"]
    clip = cut.get("clip")
    if isinstance(clip, str):
        return Path(clip).name
    raise KeyError("cut must include basename or clip")
