"""Stdlib line-oriented TUI (no Textual required). C64-ish colors when TTY."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from tui import DEFAULT_SKIN, __version__
from tui.bridge import HELP_TEXT, resolve_command, run_cli
from tui.media import classify, media_status, play_external, render_image_preview
from tui.petscii import disk_directory_menu, loading_screen_text
from tui.workflow import deck_intro_lines, media_ready_block, run_status_snapshot

# VIC-II-ish ANSI (best-effort)
_C64_BG = "\033[48;2;64;49;141m"
_C64_FG = "\033[38;2;165;160;255m"
_C64_HI = "\033[38;2;255;255;255m"
_C64_YL = "\033[38;2;213;223;124m"
_C64_GN = "\033[38;2;92;235;90m"
_C64_RD = "\033[38;2;255;123;123m"
# Inverse boot: light-blue paper + deep ink (matches themes/c64.tcss #boot)
_C64_BOOT_BG = "\033[48;2;165;160;255m"
_C64_BOOT_FG = "\033[38;2;26;20;72m"
_RESET = "\033[0m"
_CLEAR = "\033[2J\033[H"


def _color_ok() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()


def _paint(skin: str, text: str, kind: str = "body") -> str:
    if skin != "c64" or not _color_ok():
        return text
    if kind == "boot":
        # Paint each line so inverse covers the full logo block on the TTY.
        out_lines = []
        for ln in text.splitlines():
            out_lines.append(f"{_C64_BOOT_BG}{_C64_BOOT_FG}{ln}{_RESET}")
        return "\n".join(out_lines)
    palette = {
        "body": _C64_FG,
        "hi": _C64_HI,
        "yl": _C64_YL,
        "gn": _C64_GN,
        "rd": _C64_RD,
    }
    return f"{_C64_BG}{palette.get(kind, _C64_FG)}{text}{_RESET}"


def _resolve_media(raw: str) -> Path:
    path = Path(raw).expanduser()
    if path.is_file():
        return path
    from tui.workflow import ROOT

    alt = ROOT / raw
    return alt if alt.is_file() else path


def run_repl(
    skin: str = DEFAULT_SKIN,
    *,
    seed_prompt: str | None = None,
    preloaded_status: str | None = None,
    preloaded_software: str | None = None,
    auto_status: bool = True,
) -> int:
    """Blocking line REPL. Returns process exit code."""
    c64ish = skin in ("c64", "1980crt", "tui-c64-mode-default-1980crt-tui")
    if c64ish and _color_ok():
        sys.stdout.write(_CLEAR)
        print(_paint(skin, loading_screen_text(__version__, step=12), "boot"))
        print()

    status_text = preloaded_status
    software_text = preloaded_software
    if auto_status and status_text is None:
        print(_paint(skin, "probing stack status…", "yl"))
        status_text, software_text = run_status_snapshot()

    for line in deck_intro_lines(
        skin,
        __version__,
        seed_prompt=seed_prompt,
        status_text=status_text or None,
        software_text=software_text or None,
    ):
        print(_paint(skin, line, "body"))
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
        if name == "menu":
            print(_paint(skin, disk_directory_menu(), "yl"))
            continue
        if name == "media":
            print(_paint(skin, media_ready_block(), "yl"))
            print(_paint(skin, media_status(), "gn"))
            continue
        if name in ("show", "thumb"):
            if not argv or len(argv) < 2:
                print(_paint(skin, "usage: show PATH.jpg|.png|.mp4", "rd"))
                continue
            path = _resolve_media(argv[1])
            if not path.is_file():
                print(_paint(skin, f"missing: {path}", "rd"))
                continue
            kind = classify(path)
            if kind == "video":
                from tui.media import extract_video_thumb

                t = extract_video_thumb(path)
                if t:
                    print(_paint(skin, f"video thumb {t.name}", "yl"))
                    path = t
                else:
                    print(_paint(skin, "no thumb — try: play PATH", "yl"))
                    continue
            print(_paint(skin, f"SHOW {path}", "hi"))
            print(render_image_preview(path, max_width=48 if name == "show" else 28))
            print(_paint(skin, "READY.", "hi"))
            continue
        if name == "play":
            if not argv or len(argv) < 2:
                print(_paint(skin, "usage: play|open PATH.mp4|.png|.jpg", "rd"))
                continue
            path = _resolve_media(argv[1])
            result = play_external(path)
            if result.get("ok"):
                print(_paint(skin, f"PLAY {path} via {result.get('cmd')}", "gn"))
            else:
                print(_paint(skin, f"play failed: {result.get('error')}", "rd"))
            print(_paint(skin, "READY.", "hi"))
            continue

        assert argv is not None
        print(_paint(skin, f"RUN {name.upper()}", "yl"))
        rc, text = run_cli(argv)
        lines = text.splitlines()
        if len(lines) > 80:
            text = "\n".join(lines[:80]) + f"\n… ({len(lines) - 80} more lines)"
        kind = "gn" if rc == 0 else "rd"
        print(_paint(skin, text, kind))
        print()
        print(_paint(skin, "READY.", "hi"))
