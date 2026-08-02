"""python -m tui [--skin c64|modern] [--repl]"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow `python -m tui` from repo root without install
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tui import DEFAULT_SKIN, SKINS, __version__


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="python -m tui",
        description="mok-tua conductor TUI (C64 or modern skin over CLI verbs)",
    )
    p.add_argument(
        "--skin",
        choices=list(SKINS),
        default=DEFAULT_SKIN,
        help="c64 = PETSCII-style blue canvas; modern = navy ops chrome",
    )
    p.add_argument(
        "--repl",
        action="store_true",
        help="Force stdlib line REPL (no Textual full-screen)",
    )
    p.add_argument(
        "--version",
        action="version",
        version=f"mok-tua-tui {__version__}",
    )
    args = p.parse_args(argv)

    if not args.repl:
        try:
            from tui.app import run_textual, textual_available

            if textual_available():
                return run_textual(args.skin)
        except Exception as exc:  # pragma: no cover - UI path
            print(f"[tui] Textual path failed ({exc}); falling back to REPL", file=sys.stderr)

    from tui.repl import run_repl

    return run_repl(args.skin)


if __name__ == "__main__":
    raise SystemExit(main())
