"""PETSCII / demoscene-style boot art for mok-tua C64 skin.

Uses Unicode block elements (not true C64 ROM font — that is a terminal
font choice). VIC-II palette intent lives in themes/c64.tcss.
"""

from __future__ import annotations

# 5-row block font for letters used in MOK-TUA (demoscene-ish)
_GLYPHS: dict[str, list[str]] = {
    "M": [
        "█  █",
        "██ ██",
        "█ ██ █",
        "█    █",
        "█    █",
    ],
    "O": [
        " ███ ",
        "█   █",
        "█   █",
        "█   █",
        " ███ ",
    ],
    "K": [
        "█  █",
        "█ █ ",
        "██  ",
        "█ █ ",
        "█  █",
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
        "████ ",
        "     ",
        "     ",
    ],
    " ": [
        "  ",
        "  ",
        "  ",
        "  ",
        "  ",
    ],
}


def render_block_word(word: str, gap: str = " ") -> list[str]:
    """Return 5 lines of block art for uppercase word."""
    chars = []
    for ch in word.upper():
        g = _GLYPHS.get(ch) or _GLYPHS.get(" ")
        chars.append(g)
    lines: list[str] = []
    for row in range(5):
        parts = [g[row] for g in chars]
        lines.append(gap.join(parts))
    return lines


def mok_tua_logo_lines() -> list[str]:
    return render_block_word("MOK-TUA", gap=" ")


def loading_screen_text(version: str = "0.5.4", *, step: int = 0) -> str:
    """Full boot splash (plain text; colors via theme)."""
    logo = mok_tua_logo_lines()
    bar_w = 24
    filled = min(bar_w, max(0, step % (bar_w + 1)))
    bar = "█" * filled + "░" * (bar_w - filled)
    lines = [
        "",
        *logo,
        "",
        f" **** MOK-TUA V{version}  CONDUCTOR ****",
        " 64K RAM SYSTEM  38911 BASIC BYTES FREE",
        "",
        f" LOADING  {bar}",
        " PETSCII BOOT · VIC-II PALETTE · READY SOON",
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
