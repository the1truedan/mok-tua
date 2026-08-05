"""PETSCII logo / skin / media resolve unit tests (no Textual)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tui import DEFAULT_SKIN, resolve_skin  # noqa: E402
from tui.bridge import resolve_command  # noqa: E402
from tui.petscii import intro_recommendations, loading_screen_text, mok_tua_logo_lines, vic_bar  # noqa: E402


class PetsciiTests(unittest.TestCase):
    def test_logo_has_mok(self) -> None:
        lines = mok_tua_logo_lines()
        self.assertEqual(len(lines), 5)
        joined = "\n".join(lines)
        self.assertIn("█", joined)

    def test_loading_and_intro(self) -> None:
        boot = loading_screen_text("0.5.5", step=8)
        self.assertIn("MOK-TUA", boot)
        self.assertIn("LOADING", boot)
        intro = intro_recommendations()
        self.assertIn("QQQ", intro)
        self.assertIn("FramePack", intro)

    def test_vic_bar(self) -> None:
        self.assertIn("n/a", vic_bar(None))
        b = vic_bar(50.0, width=10)
        self.assertIn("%", b)
        self.assertEqual(b.count("█") + b.count("░"), 10)

    def test_skin_aliases(self) -> None:
        self.assertEqual(DEFAULT_SKIN, "c64")
        self.assertEqual(resolve_skin("1980crt"), "c64")
        self.assertEqual(resolve_skin("tui-c64-mode-default-1980crt-tui"), "c64")
        self.assertEqual(resolve_skin("matrix"), "green")
        self.assertEqual(resolve_skin("paper"), "mono")
        self.assertEqual(resolve_skin("green"), "green")

    def test_show_play_receipt_commands(self) -> None:
        name, argv, err = resolve_command("show /tmp/x.png")
        self.assertEqual(name, "show")
        self.assertEqual(argv, ["show", "/tmp/x.png"])
        self.assertIsNone(err)
        name, argv, err = resolve_command("play clip.mp4")
        self.assertEqual(name, "play")
        name, argv, err = resolve_command("receipt stamp a.png --renderer r")
        self.assertEqual(name, "receipt")
        assert argv is not None
        self.assertEqual(argv[0], "receipt")
        self.assertEqual(argv[1], "stamp")
        name, argv, err = resolve_command("m")
        self.assertEqual(name, "monitor")


if __name__ == "__main__":
    unittest.main()
