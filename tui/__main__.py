"""python -m tui [--skin c64|green|mono|modern|…] [--prompt TEXT] [--repl]"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow `python -m tui` from repo root without install
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tui import DEFAULT_SKIN, SKINS, __version__, resolve_skin


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="python -m tui",
        description="mok-tua conductor TUI (C64 default · green/mono · modern)",
    )
    p.add_argument(
        "--skin",
        default=DEFAULT_SKIN,
        help=(
            "c64 (default / 1980crt / tui-c64-mode-default-1980crt-tui) · "
            "green (matrix) · mono (paper) · modern"
        ),
    )
    p.add_argument(
        "--prompt",
        default=None,
        help="Seed left-pane launch intro with this prompt text",
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
    skin = resolve_skin(args.skin)
    if args.skin and args.skin.lower() not in {s.lower() for s in SKINS} and skin == DEFAULT_SKIN:
        # unknown skin string that resolve_skin fell back on — warn
        if args.skin.lower() not in ("c64",):
            print(f"[tui] unknown skin {args.skin!r}; using {skin}", file=sys.stderr)

    if not args.repl:
        try:
            from tui.app import run_textual, textual_available

            if textual_available():
                return run_textual(skin, seed_prompt=args.prompt)
        except Exception as exc:  # pragma: no cover - UI path
            print(f"[tui] Textual path failed ({exc}); falling back to REPL", file=sys.stderr)

    from tui.repl import run_repl

    return run_repl(skin, seed_prompt=args.prompt)


if __name__ == "__main__":
    raise SystemExit(main())
