"""Stdlib line-oriented TUI (no Textual required). C64-ish colors when TTY."""

from __future__ import annotations

import os
import sys

from tui import DEFAULT_SKIN, __version__
from tui.bridge import HELP_TEXT, boot_banner, resolve_command, run_cli

# VIC-II-ish ANSI (best-effort)
_C64_BG = "\033[48;2;64;49;141m"
_C64_FG = "\033[38;2;165;160;255m"
_C64_HI = "\033[38;2;255;255;255m"
_C64_YL = "\033[38;2;213;223;124m"
_C64_GN = "\033[38;2;92;235;90m"
_C64_RD = "\033[38;2;255;123;123m"
_RESET = "\033[0m"
_CLEAR = "\033[2J\033[H"


def _color_ok() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()


def _paint(skin: str, text: str, kind: str = "body") -> str:
    if skin != "c64" or not _color_ok():
        return text
    palette = {
        "body": _C64_FG,
        "hi": _C64_HI,
        "yl": _C64_YL,
        "gn": _C64_GN,
        "rd": _C64_RD,
    }
    return f"{_C64_BG}{palette.get(kind, _C64_FG)}{text}{_RESET}"


def run_repl(skin: str = DEFAULT_SKIN) -> int:
    """Blocking line REPL. Returns process exit code."""
    if skin == "c64" and _color_ok():
        sys.stdout.write(_CLEAR)
        sys.stdout.write(f"{_C64_BG}{_C64_FG}")
        # Fill a few screen lines for CRT feel
        cols = 40
        rows = 12
        for _ in range(rows):
            sys.stdout.write(" " * cols + "\n")
        sys.stdout.write(_CLEAR)

    print(_paint(skin, boot_banner(skin, __version__.rsplit(".", 1)[0])))
    print()

    while True:
        try:
            prompt = "READY.\n> " if skin == "c64" else "mok-tua> "
            line = input(_paint(skin, prompt, "hi") if skin == "c64" else prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            print(_paint(skin, "BREAK.", "yl"))
            return 0

        name, argv, err = resolve_command(line)
        if not name:
            continue
        if err:
            print(_paint(skin, err, "rd"))
            continue
        if name == "quit":
            print(_paint(skin, "READY.", "hi"))
            return 0
        if name == "help":
            print(_paint(skin, HELP_TEXT, "yl"))
            continue

        assert argv is not None
        print(_paint(skin, f"RUN {name.upper()}", "yl"))
        rc, text = run_cli(argv)
        # Clamp very long dumps for terminal readability
        lines = text.splitlines()
        if len(lines) > 80:
            text = "\n".join(lines[:80]) + f"\n… ({len(lines) - 80} more lines)"
        kind = "gn" if rc == 0 else "rd"
        print(_paint(skin, text, kind))
        print()
        print(_paint(skin, "READY.", "hi"))
