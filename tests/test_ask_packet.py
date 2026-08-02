"""Ask-packet emit, PHI refuse, award dry-run."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "api"))


class AskPacketTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.work = Path(self._tmp.name)
        import os

        os.environ["WORK_FALLBACK"] = str(self.work)
        os.environ["MOCK_TUA_CONFIG"] = str(ROOT / "config")
        # re-import modules that cache WORK
        for mod in list(sys.modules):
            if mod in (
                "chains_render",
                "ask_packet",
                "crowd_index",
                "award",
            ):
                del sys.modules[mod]

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_lock_ref_stable(self) -> None:
        import ask_packet

        a = ask_packet.lock_ref_for_tier("T1_vid_gen")
        b = ask_packet.lock_ref_for_tier("T1_vid_gen")
        self.assertEqual(a, b)
        self.assertTrue(a.startswith("T1_vid_gen@"))
        self.assertGreaterEqual(len(a.split("@")[1]), 8)

    def test_phi_emit_forbidden(self) -> None:
        import ask_packet

        with self.assertRaises(ValueError) as ctx:
            ask_packet.emit_packet(op="still", data_class="phi", qqq_floor="QQQ0")
        self.assertIn("phi", str(ctx.exception).lower())

        with self.assertRaises(ValueError) as ctx2:
            ask_packet.emit_packet(
                op="still",
                data_class="phi",
                qqq_floor="QQQ3",
                allow_crowd=True,
            )
        self.assertIn("phi", str(ctx2.exception).lower())

    def test_emit_public_and_award(self) -> None:
        import ask_packet
        import award
        import crowd_index

        crowd_index.seed_lab_nodes(force=True)
        pkt = ask_packet.emit_packet(
            op="still",
            data_class="public",
            qqq_floor="QQQ3",
            allow_crowd=True,
            payload_text='{"prompt":"test panel"}',
        )
        self.assertEqual(pkt["schema"], "ask_packet.v1")
        self.assertEqual(pkt["manifest"]["data_class"], "public")
        self.assertEqual(pkt["custody"]["chain_id"], "mok-tua-render")
        v = ask_packet.validate_packet_shape(pkt)
        self.assertTrue(v["ok"], v)

        res = award.award_packet(pkt, dry_run=True)
        self.assertTrue(res["ok"], res)
        self.assertIsNotNone(res.get("winner"))
        # still prefers desk-host or gpu-host
        self.assertIn(res["winner"]["id"], {"desk-host", "gpu-host", "tower"})

    def test_internal_not_untrusted(self) -> None:
        import ask_packet
        import award
        import crowd_index

        crowd_index.seed_lab_nodes(force=True)
        pkt = ask_packet.emit_packet(
            op="video",
            data_class="internal",
            qqq_floor="QQQ0",
            allow_crowd=False,
        )
        res = award.award_packet(pkt, dry_run=True, prefer_trusted=True)
        self.assertTrue(res["ok"])
        self.assertTrue(res["winner"]["trusted"])

    def test_chains_verify(self) -> None:
        import ask_packet
        import chains_render

        ask_packet.emit_packet(op="still", data_class="internal")
        v = chains_render.verify_chain()
        self.assertTrue(v["ok"], v)
        self.assertGreaterEqual(v["events"], 1)


if __name__ == "__main__":
    unittest.main()
