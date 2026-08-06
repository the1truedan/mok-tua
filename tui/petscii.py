"""PETSCII / demoscene-style boot art for mok-tua C64 skin.

Uses Unicode full-block cells (not true C64 ROM font — that is a terminal
font choice). VIC-II palette intent lives in themes/c64.tcss.

Glyphs are fixed-width (5 columns × 5 rows) so CLI/Textual monospaced
render stays aligned. Prefer inverse boot colors in c64.tcss for contrast.
"""

from __future__ import annotations

# Fixed 5×5 block font — every row of every glyph is exactly 5 cells.
# Only FULL BLOCK (█) and SPACE; avoids half-block double-width footguns.
_GLYPHS: dict[str, list[str]] = {
    "M": [
        "█   █",
        "██ ██",
        "█ █ █",
        "█   █",
        "█   █",
    ],
    "O": [
        " ███ ",
        "█   █",
        "█   █",
        "█   █",
        " ███ ",
    ],
    "K": [
        "█   █",
        "█  █ ",
        "███  ",
        "█  █ ",
        "█   █",
    ],
    "T": [
        "█████",
        "  █  ",
        "  █  ",
        "  █  ",
        "  █  ",
    ],
    "U": [
        "█   █",
        "█   █",
        "█   █",
        "█   █",
        " ███ ",
    ],
    "A": [
        " ███ ",
        "█   █",
        "█████",
        "█   █",
        "█   █",
    ],
    "-": [
        "     ",
        "     ",
        " ███ ",
        "     ",
        "     ",
    ],
    " ": [
        "     ",
        "     ",
        "     ",
        "     ",
        "     ",
    ],
}

_GLYPH_W = 5
_GLYPH_H = 5


def _assert_glyphs() -> None:
    for ch, rows in _GLYPHS.items():
        if len(rows) != _GLYPH_H:
            raise ValueError(f"glyph {ch!r}: expected {_GLYPH_H} rows, got {len(rows)}")
        for i, row in enumerate(rows):
            if len(row) != _GLYPH_W:
                raise ValueError(
                    f"glyph {ch!r} row {i}: expected {_GLYPH_W} cols, got {len(row)} ({row!r})"
                )


_assert_glyphs()


def render_block_word(word: str, gap: str = " ") -> list[str]:
    """Return 5 equal-length lines of block art for uppercase word."""
    chars: list[list[str]] = []
    for ch in word.upper():
        g = _GLYPHS.get(ch) or _GLYPHS[" "]
        chars.append(g)
    lines: list[str] = []
    for row in range(_GLYPH_H):
        parts = [g[row] for g in chars]
        lines.append(gap.join(parts))
    # pad all lines to max width (should already match)
    width = max((len(ln) for ln in lines), default=0)
    return [ln.ljust(width) for ln in lines]


def mok_tua_logo_lines() -> list[str]:
    return render_block_word("MOK-TUA", gap=" ")


def _center_block(lines: list[str], width: int | None = None) -> list[str]:
    """Left-pad lines so the block is centered in *width* (default: max line)."""
    if not lines:
        return lines
    content_w = max(len(ln) for ln in lines)
    box = width if width is not None else content_w
    if box < content_w:
        box = content_w
    pad = max(0, (box - content_w) // 2)
    return [(" " * pad) + ln.ljust(content_w) for ln in lines]


def loading_screen_text(version: str = "0.5.4", *, step: int = 0) -> str:
    """Full boot splash (plain text; inverse colors via theme #boot).

    Layout stays within ~40 columns (C64 spirit) so narrow terminals
    do not wrap and shatter the logo.
    """
    logo = _center_block(mok_tua_logo_lines())
    # frame width = logo width (stable across rows)
    frame_w = max(len(ln) for ln in logo) if logo else 40
    bar_w = min(24, max(8, frame_w - 10))
    filled = min(bar_w, max(0, step % (bar_w + 1)))
    # solid vs light shade — high contrast on inverse boot panel
    bar = "█" * filled + "░" * (bar_w - filled)

    title = f"**** MOK-TUA V{version}  CONDUCTOR ****"
    mem = "64K RAM SYSTEM  38911 BASIC BYTES FREE"
    load = f"LOADING  {bar}"
    foot = "PETSCII BOOT · VIC-II · READY SOON"

    def _fit(s: str) -> str:
        if len(s) <= frame_w:
            return s.center(frame_w)
        return s[:frame_w]

    lines = [
        "",
        *logo,
        "",
        _fit(title),
        _fit(mem),
        "",
        _fit(load),
        _fit(foot),
        "",
    ]
    return "\n".join(lines)


def intro_recommendations() -> str:
    return (
        "LAUNCH INTRO — prompt recommendations\n"
        "─────────────────────────────────────\n"
        "  · Still: local Comfy DreamShaper / Qwen edit (QQQ0)\n"
        "  · Short loop: local_animatediff on gpu-host\n"
        "  · Longer I2V: FramePack :7864  (receipt required)\n"
        "  · Cloud I2V: grok_imagine only with QQQ1 + label\n"
        "  · Every clip: renderer · qqq · gpu_evidence\n"
        "\n"
        "Shortcuts: [D]octor [P]roviders [R]un [S]moke\n"
        "           [L]ock [T]status [M]onitor [H]elp [Q]uit\n"
        "Media:     show PATH · play PATH · thumb PATH\n"
        "Receipt:   receipt show PATH · receipt stamp PATH …\n"
        "\n"
        "Type a command at READY. or paste a story path after run\n"
    )


def intro_with_prompt(prompt: str) -> str:
    body = prompt.strip()
    if len(body) > 1200:
        body = body[:1200] + "\n… (truncated)"
    return (
        "LAUNCH INTRO — CLI prompt seed\n"
        "─────────────────────────────────────\n"
        f"{body}\n"
        "\n"
        "Use: run PATH · packet emit · providers\n"
        "After generate: show/play artifact · receipt stamp\n"
        "\n"
        + intro_recommendations().split("LAUNCH INTRO", 1)[0]
        + "Shortcuts: [D] [P] [R] [S] [H] [Q] · show · play · receipt\n"
    )


def vic_bar(pct: float | None, width: int = 10) -> str:
    """VIC-II style filled bar from 0–100 percent."""
    if pct is None:
        return "░" * width + "  n/a"
    p = max(0.0, min(100.0, float(pct)))
    filled = int(round((p / 100.0) * width))
    return "█" * filled + "░" * (width - filled) + f" {p:5.1f}%"
