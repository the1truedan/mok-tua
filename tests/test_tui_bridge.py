"""Unit tests for TUI command resolution (no Textual / no live stack)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tui.bridge import HELP_TEXT, boot_banner, resolve_command  # noqa: E402


class TuiBridgeTests(unittest.TestCase):
    def test_shortcuts(self) -> None:
        name, argv, err = resolve_command("d")
        self.assertEqual(name, "doctor")
        self.assertEqual(argv, ["doctor"])
        self.assertIsNone(err)

        name, argv, err = resolve_command("p")
        self.assertEqual(name, "providers")
        self.assertEqual(argv, ["providers"])

        name, argv, err = resolve_command("s")
        self.assertEqual(name, "smoke")

        name, argv, err = resolve_command("l")
        self.assertEqual(argv, ["lock", "show"])

    def test_help_quit(self) -> None:
        name, argv, err = resolve_command("h")
        self.assertEqual(name, "help")
        self.assertIsNone(argv)
        name, argv, err = resolve_command("quit")
        self.assertEqual(name, "quit")
        self.assertIsNone(argv)

    def test_run_default_fixture(self) -> None:
        name, argv, err = resolve_command("run")
        self.assertEqual(name, "run")
        self.assertIsNone(err)
        assert argv is not None
        self.assertEqual(argv[0], "run")
        self.assertTrue(argv[1].endswith("sample_instructor_story.md"))

    def test_run_path(self) -> None:
        name, argv, err = resolve_command("run fixtures/foo.md --live-still")
        self.assertEqual(name, "run")
        assert argv is not None
        self.assertEqual(argv[1], "fixtures/foo.md")
        self.assertIn("--live-still", argv)

    def test_unknown(self) -> None:
        name, argv, err = resolve_command("xyzzy")
        self.assertIsNone(argv)
        self.assertIsNotNone(err)

    def test_banner_and_help(self) -> None:
        b = boot_banner("c64", "0.5")
        self.assertIn("MOK-TUA", b)
        self.assertIn("READY.", b)
        self.assertIn("doctor", HELP_TEXT)

    def test_nodes_chains_defaults(self) -> None:
        _, argv, _ = resolve_command("nodes")
        self.assertEqual(argv, ["nodes", "list"])
        _, argv, _ = resolve_command("chains")
        self.assertEqual(argv, ["chains", "tip"])


if __name__ == "__main__":
    unittest.main()
