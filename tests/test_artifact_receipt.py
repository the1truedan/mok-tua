"""Unit tests for artifact provenance receipts."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "api"))

import artifact_receipt  # noqa: E402


class ArtifactReceiptTests(unittest.TestCase):
    def test_build_and_caption(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "still.png"
            p.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 32)
            rec = artifact_receipt.build_receipt(
                p,
                renderer="gpu_comfy_animatediff",
                model="DreamShaper_8",
                host_role="gpu-host",
                qqq="QQQ0",
                prompt="indie developer vibe coding",
                wall_clock_s=48.2,
                tokens={"input": None, "output": None, "total": None, "note": "n/a local"},
                gpu={"peak_util_pct": 100.0, "gpu_temp_c": 72.0},
                cpu={"load1": 2.1},
            )
            self.assertEqual(rec["schema"], artifact_receipt.SCHEMA)
            self.assertEqual(rec["artifact"]["kind"], "image")
            self.assertTrue(rec["artifact"]["sha256"])
            self.assertIn("gpu_comfy_animatediff", rec["caption_line"])
            self.assertIn("gpu-host", rec["caption_line"])
            side = artifact_receipt.write_receipt(rec, chain=False)
            self.assertTrue(side.is_file())
            loaded = artifact_receipt.load_receipt(p)
            self.assertEqual(loaded["renderer"], "gpu_comfy_animatediff")

    def test_redact_unknown_host(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "x.jpg"
            p.write_bytes(b"jpeg")
            rec = artifact_receipt.build_receipt(
                p,
                renderer="grok_imagine_i2v",
                cloud_or_local="cloud",
                host_role="unknown-lab-box",
                qqq="QQQ1",
            )
            self.assertEqual(rec["host_role"], "host-redacted")
            self.assertEqual(rec["gpu_evidence"], "n/a cloud")

    def test_vic_caption_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "v.mp4"
            p.write_bytes(b"ftyp")
            rec = artifact_receipt.build_receipt(
                p,
                renderer="grok_imagine_i2v",
                cloud_or_local="cloud",
                model="grok-imagine",
                host_role="cloud",
                tokens={"input": 10, "output": 20, "total": 30, "note": None},
                wall_clock_s=12.5,
            )
            self.assertIn("tok 30", rec["caption_line"])
            self.assertEqual(rec["artifact"]["kind"], "video")


if __name__ == "__main__":
    unittest.main()
