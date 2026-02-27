from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from kubo_report import compute_metrics
from reorder_clips import reorder_cuts
from select_clips import enrich_cuts_with_metadata


class PipelineTests(unittest.TestCase):
    def test_select_embeds_metadata_and_preserves_duration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "assets" / "proj" / "clips").mkdir(parents=True)
            (root / "assets" / "proj" / "clips" / "clip_meta.json").write_text(
                json.dumps(
                    {
                        "CUT001.mp4": {
                            "group_id": "g_intro",
                            "tags": ["wide"],
                            "source": "x",
                            "notes": "",
                        }
                    }
                ),
                encoding="utf-8",
            )

            cuts = [{"clip": "media/CUT001.mp4", "duration_sec": 1.23}]
            old = Path.cwd()
            try:
                # Functions resolve SSOT relative to cwd.
                import os
                os.chdir(root)
                enriched = enrich_cuts_with_metadata(cuts, "proj")
            finally:
                os.chdir(old)

            self.assertEqual(enriched[0]["group_id"], "g_intro")
            self.assertEqual(enriched[0]["tags"], ["wide"])
            self.assertEqual(enriched[0]["duration_sec"], 1.23)

    def test_reorder_reduces_group_near_violations(self) -> None:
        cuts = [
            {"basename": "A.mp4", "group_id": "g1", "tags": ["t1"], "duration_sec": 1},
            {"basename": "B.mp4", "group_id": "g1", "tags": ["t1"], "duration_sec": 1},
            {"basename": "C.mp4", "group_id": "g2", "tags": ["t2"], "duration_sec": 1},
            {"basename": "D.mp4", "group_id": "g1", "tags": ["t3"], "duration_sec": 1},
        ]
        before = compute_metrics(cuts)["GROUP_NEAR_VIOLATIONS"]
        after_cuts = reorder_cuts(cuts)
        after = compute_metrics(after_cuts)["GROUP_NEAR_VIOLATIONS"]
        self.assertLessEqual(after, before)
        self.assertEqual(sum(c["duration_sec"] for c in after_cuts), 4)

    def test_report_metric_definitions(self) -> None:
        cuts = [
            {"basename": "A", "group_id": "g1", "tags": ["t1"]},
            {"basename": "B", "group_id": None, "tags": []},
            {"basename": "C", "group_id": "g1", "tags": ["t2"]},
        ]
        metrics = compute_metrics(cuts)
        self.assertEqual(metrics["CUT_COUNT"], 3)
        self.assertAlmostEqual(metrics["TAG_COVERAGE"], 2 / 3)
        self.assertAlmostEqual(metrics["GROUP_COVERAGE"], 2 / 3)
        self.assertEqual(metrics["GROUP_NEAR_VIOLATIONS"], 1)


if __name__ == "__main__":
    unittest.main()
