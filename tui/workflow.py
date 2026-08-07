"""Launch workflow: PETSCII intro → CLI help → status → media-ready deck.

Used by Textual TUI and stdlib REPL so both paths share one sequence.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from tui import __version__
from tui.bridge import HELP_TEXT, boot_banner, run_cli
from tui.media import list_recent_media, media_status
from tui.petscii import (
    cli_args_menu,
    disk_directory_menu,
    intro_recommendations,
    intro_with_prompt,
    loading_screen_text,
)

ROOT = Path(__file__).resolve().parents[1]


def petscii_boot_frames(version: str = __version__, *, steps: int = 12) -> list[str]:
    """Animated LOADING bar frames for CLI pre-TUI intro."""
    return [loading_screen_text(version, step=i) for i in range(steps + 1)]


def print_petscii_intro(version: str = __version__, *, steps: int = 12) -> None:
    """Print PETSCII loader to stdout (CLI preflight before Textual)."""
    import sys
    import time

    tty = sys.stdout.isatty()
    frames = petscii_boot_frames(version, steps=steps)
    for i, fr in enumerate(frames):
        if tty and i > 0:
            # move up enough lines to rewrite splash in place
            n = fr.count("\n") + 1
            sys.stdout.write(f"\033[{n}A")
        print(fr)
        if tty:
            sys.stdout.flush()
            time.sleep(0.06)
    if tty:
        print()


def cli_help_snapshot() -> str:
    """Compact CLI argument / capability menu (C64 disk style + help)."""
    return (
        "**** CLI ARGUMENTS · TYPE help IN TUI ****\n"
        + cli_args_menu()
        + "\n"
        + "Full verb help: python3 scripts/mok_tua_cli.py --help\n"
        + "Same verbs work at READY. (D doctor · P providers · …)\n"
    )


def run_status_snapshot(*, timeout: float = 45.0) -> tuple[str, str]:
    """Run status + software probes; return (status_text, software_text)."""
    rc_s, status = run_cli(["status"], timeout=timeout)
    if rc_s != 0 and not status.strip():
        status = f"(status exit {rc_s})"
    rc_w, software = run_cli(["software"], timeout=timeout)
    if rc_w != 0 and not software.strip():
        software = f"(software exit {rc_w})"
    return status, software


def media_ready_block() -> str:
    """How to open outputs + recent export paths if present."""
    lines = [
        "**** MEDIA · SHOW / PLAY OUTPUTS ****",
        "  show PATH.png|.jpg   preview still in left pane",
        "  play PATH.mp4|.png   external player (mpv / open)",
        "  open PATH            alias of play",
        "  thumb PATH           mini preview",
        f"  {media_status()}",
        "",
    ]
    recent = list_recent_media(ROOT)
    if recent:
        lines.append("  Recent exports (type: show <path>  or  play <path>):")
        for p in recent[:8]:
            try:
                rel = p.relative_to(ROOT)
            except ValueError:
                rel = p
            lines.append(f"    {rel}")
    else:
        lines.append("  tip: after run/receipt, show work/*.png or play docs/assets/exports/*.mp4")
    lines.append("")
    return "\n".join(lines)


def deck_intro_lines(
    skin: str,
    version: str = __version__,
    *,
    seed_prompt: str | None = None,
    status_text: str | None = None,
    software_text: str | None = None,
    include_disk_menu: bool = True,
) -> list[str]:
    """Full left-pane sequence after PETSCII splash ends."""
    out: list[str] = []
    out.extend(boot_banner(skin, version).splitlines())
    out.append("")
    out.extend(cli_help_snapshot().splitlines())
    out.append("")
    if include_disk_menu:
        out.extend(disk_directory_menu().splitlines())
        out.append("")
    if status_text is not None:
        out.append("**** STACK STATUS ****")
        out.extend(_clamp_lines(status_text, 40))
        out.append("")
    if software_text is not None:
        out.append("**** SOFTWARE DISKS ****")
        out.extend(_clamp_lines(software_text, 30))
        out.append("")
    out.extend(media_ready_block().splitlines())
    if seed_prompt:
        out.extend(intro_with_prompt(seed_prompt).splitlines())
    else:
        out.extend(intro_recommendations().splitlines())
    out.append("")
    out.append("READY.  type H · status · software · show PATH · play PATH")
    return out


def _clamp_lines(text: str, max_lines: int) -> list[str]:
    lines = (text or "").splitlines()
    if len(lines) <= max_lines:
        return lines or ["(empty)"]
    return lines[:max_lines] + [f"… ({len(lines) - max_lines} more — type status / software)"]


def preflight_cli_intro(
    *,
    version: str = __version__,
    skip_status: bool = False,
    quiet: bool = False,
) -> dict[str, str]:
    """CLI-side intro before launching Textual: PETSCII + help (+ optional status).

    Returns dict with status/software strings for the TUI to reuse (avoid double probe).
    """
    if not quiet:
        print_petscii_intro(version)
        print(cli_help_snapshot())
        print(disk_directory_menu())
        print()
        print("launching conductor TUI…")
        print()

    result = {"status": "", "software": ""}
    if not skip_status:
        st, sw = run_status_snapshot()
        result["status"] = st
        result["software"] = sw
        if not quiet:
            print("**** STACK STATUS ****")
            print("\n".join(_clamp_lines(st, 25)))
            print()
            print("**** SOFTWARE DISKS ****")
            print("\n".join(_clamp_lines(sw, 20)))
            print()
            print(media_ready_block())
    return result
