"""Run mok-tua CLI verbs and return captured output (TUI ↔ CLI seam)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "mok_tua_cli.py"

# Safe default story for demo RUN from the TUI
DEFAULT_STORY = ROOT / "fixtures" / "sample_instructor_story.md"

# Built-in help (shown without spawning CLI)
HELP_TEXT = """\
**** MOK-TUA CONDUCTOR TUI ****
Commands (type name or shortcut):

  D  doctor      Full stack health board
  P  providers   Director-stack provider table
  S  smoke       T0–T4 smoke scorecard (safe)
  T  status      Providers + doctor grade
  L  lock        Show T0–T4 version lock
  R  run         Dry-run sample story (or: run PATH)
  B  batch       Dry-run batch on fixtures
  I  inventory   Model stage inventory
  N  nodes       Federation node list
  C  chains      CHAINS tip / verify (chains tip)
  M  monitor     One-shot gpu-host sample
  show PATH      Preview still / video thumb in left pane
  play PATH      External mpv/timg/open for media
  thumb PATH     Mini preview (alias of show)
  receipt …      show PATH | stamp PATH --renderer … [--burn-caption]
  H  help        This screen
  Q  quit        Exit TUI

Skins: c64 (default) | 1980crt | green | mono | modern
Same verbs as: python3 scripts/mok_tua_cli.py <cmd>
API always available on :8799 when host is up.
"""

# Map single-letter + aliases → argv list for mok_tua_cli.py
# Values may be callables taking rest tokens → list[str]
CommandSpec = list[str]


def resolve_command(line: str) -> tuple[str, list[str] | None, str | None]:
    """
    Parse a prompt line into (name, argv_or_None, error_or_None).
    argv is relative to mok_tua_cli (no python/path).
    Special: help/quit return name with argv None (handled by shell).
    """
    raw = (line or "").strip()
    if not raw:
        return ("", None, None)

    parts = raw.split()
    head = parts[0].lower()
    rest = parts[1:]

    # Single-letter shortcuts (C64 menu style)
    shortcuts = {
        "d": "doctor",
        "p": "providers",
        "s": "smoke",
        "t": "status",
        "l": "lock",
        "r": "run",
        "b": "batch",
        "i": "inventory",
        "n": "nodes",
        "c": "chains",
        "m": "monitor",
        "h": "help",
        "q": "quit",
        "?": "help",
    }
    if head in shortcuts:
        head = shortcuts[head]
        # for multi-word originals, rest stays

    if head in ("help", "quit", "exit", "q"):
        return (head if head != "exit" else "quit", None, None)

    if head == "doctor":
        return ("doctor", ["doctor"], None)

    if head == "providers":
        argv = ["providers"]
        if rest:
            argv.extend(rest)
        return ("providers", argv, None)

    if head == "smoke":
        argv = ["smoke"]
        if rest:
            argv.extend(rest)
        return ("smoke", argv, None)

    if head == "status":
        return ("status", ["status"], None)

    if head == "lock":
        # default show
        if not rest:
            return ("lock", ["lock", "show"], None)
        return ("lock", ["lock", *rest], None)

    if head == "run":
        path = rest[0] if rest else str(DEFAULT_STORY)
        # always dry unless user passes --no-dry-run / --live-still in rest[1:]
        extra = rest[1:] if rest else []
        argv = ["run", path, *extra]
        return ("run", argv, None)

    if head == "batch":
        paths = rest if rest else [str(DEFAULT_STORY)]
        return ("batch", ["batch", *paths], None)

    if head == "inventory":
        return ("inventory", ["inventory", *rest], None)

    if head == "nodes":
        if not rest:
            return ("nodes", ["nodes", "list"], None)
        return ("nodes", ["nodes", *rest], None)

    if head == "chains":
        if not rest:
            return ("chains", ["chains", "tip"], None)
        return ("chains", ["chains", *rest], None)

    if head == "monitor":
        return ("monitor", ["monitor", *rest], None)

    if head in ("show", "thumb", "play"):
        if not rest:
            return (head, None, f"usage: {head} PATH")
        # local TUI handlers use argv form [verb, path]
        return (head, [head, *rest], None)

    if head == "receipt":
        if not rest:
            return ("receipt", None, "usage: receipt show PATH | receipt stamp PATH …")
        return ("receipt", ["receipt", *rest], None)

    if head == "launch":
        if not rest:
            return ("launch", None, "usage: launch <provider|chain:demo|…> [--live]")
        return ("launch", ["launch", *rest], None)

    # pass-through for power users: full CLI verbs already known
    known = {
        "inventory",
        "stage",
        "sides",
        "run",
        "batch",
        "providers",
        "doctor",
        "launch",
        "stop",
        "pull",
        "status",
        "discover",
        "audit",
        "stage-app",
        "smoke",
        "lock",
        "monitor",
        "packet",
        "nodes",
        "chains",
        "receipt",
    }
    if head in known:
        return (head, [head, *rest], None)

    return (head, None, f"unknown command: {head}  (type H for help)")


def run_cli(
    argv: Sequence[str],
    *,
    timeout: float = 120.0,
    env: dict[str, str] | None = None,
) -> tuple[int, str]:
    """Spawn scripts/mok_tua_cli.py with argv; return (rc, combined text)."""
    if not CLI.is_file():
        return (127, f"CLI missing: {CLI}")

    cmd = [sys.executable, str(CLI), *argv]
    merged = os.environ.copy()
    if env:
        merged.update(env)
    # Prefer JSON-ish / plain text; avoid interactive prompts
    merged.setdefault("PYTHONUNBUFFERED", "1")

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=merged,
        )
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or "") + (exc.stderr or "")
        return (124, (out + f"\n[timeout after {timeout}s]").strip())
    except OSError as exc:
        return (126, f"spawn failed: {exc}")

    chunks = []
    if proc.stdout:
        chunks.append(proc.stdout.rstrip())
    if proc.stderr:
        # demote noise but keep errors
        err = proc.stderr.rstrip()
        if err:
            chunks.append(err)
    text = "\n".join(chunks).strip() or f"(exit {proc.returncode}, no output)"
    return (proc.returncode, text)


def boot_banner(skin: str = "c64", version: str = "0.5") -> str:
    c64ish = skin in (
        "c64",
        "1980crt",
        "tui-c64-mode-default-1980crt-tui",
        "green",
        "matrix",
        "mono",
        "paper",
    )
    if c64ish:
        return (
            f" **** MOK-TUA V{version}  CONDUCTOR ****\n"
            " 64K RAM SYSTEM  38911 BASIC BYTES FREE\n"
            "\n"
            "READY.\n"
            "\n"
            " [D]OCTOR [P]ROVIDERS [R]UN [S]MOKE\n"
            " [L]OCK   [T]STATUS  [M]ONITOR [H]ELP [Q]UIT\n"
            " show/play PATH · receipt stamp PATH\n"
            "\n"
            "READY."
        )
    return (
        f"mok-tua conductor TUI v{version}  skin={skin}\n"
        "Type help · shortcuts D/P/R/S/L/T/M/H/Q · same verbs as CLI\n"
        "READY."
    )
