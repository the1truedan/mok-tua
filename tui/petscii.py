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


def demoscene_filter(line: str, width: int = 40) -> str:
    """Strip secrets/paths/ANSI; fit ~40 cols for C64 spirit log tail."""
    import re

    s = line.replace("\r", " ").replace("\t", " ")
    s = re.sub(r"\x1b\[[0-9;]*m", "", s)
    s = re.sub(r"https?://192\.168\.\d+\.\d+", "http://gpu-host", s)
    s = re.sub(r"/Users/[^/\s]+", "~", s)
    s = re.sub(r"/mnt/ai-data", "nas:", s)
    s = re.sub(r"/Volumes/ai-data", "nas:", s)
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) > width:
        return s[: width - 1] + "…"
    return s


def disk_insert_banner(label: str, title: str = "", *, state: str = "READY") -> str:
    """INSERT DISK metaphor for a software catalog entry."""
    lab = (label or "UNKNOWN").upper()[:12]
    tit = (title or "SOFTWARE").upper()[:16]
    st = (state or "READY").upper()[:14]
    lines = [
        "╔══════════════════════════════════════╗",
        f"║  INSERT DISK: {lab:<22} ║",
        f"║  TITLE: {tit:<28} ║",
        f"║  STATUS: {st:<27} ║",
        "║  LOADING PROGRAM  *******************║",
        "╚══════════════════════════════════════╝",
        "  PRESS PLAY ON TAPE · OR TYPE launch",
    ]
    return "\n".join(lines)


def loading_screen_for(tool_id: str, version: str = "0.5.8", *, step: int = 0) -> str:
    """Per-tool demoscene load screen (extends boot splash)."""
    tid = (tool_id or "mok_tua").lower()
    table = {
        "sm_comfy": ("COMFYUI", "NODE GRAPH ENGINE"),
        "comfy": ("COMFYUI", "NODE GRAPH ENGINE"),
        "directors_console": ("DIRECTORS", "CONSOLE ORCHESTRA"),
        "directors": ("DIRECTORS", "CONSOLE ORCHESTRA"),
        "framepack_studio": ("FRAMEPACK", "LONG VIDEO STUDIO"),
        "framepack": ("FRAMEPACK", "LONG VIDEO STUDIO"),
        "wan2gp": ("WAN2GP", "VIDEO GENERATION"),
        "wan": ("WAN", "VIDEO GENERATION"),
        "ace_step": ("ACE-STEP", "MUSIC GENERATION"),
        "pocket_tts": ("POCKET-TTS", "VOICE CLONE TTS"),
        "dramabox": ("DRAMABOX", "EXPRESSIVE TTS"),
        "facefusion": ("FACEFUSION", "FACE PIPELINE"),
        "qwen_edit": ("QWEN-EDIT", "STORYBOARD PAUSED"),
        "mok_tua": ("MOK-TUA", "CONDUCTOR CORE"),
    }
    label, subtitle = table.get(tid, (tid.upper()[:12], "SOFTWARE DISK"))
    boot = loading_screen_text(version, step=step)
    extra = (
        f"\n  DISK  {label}\n"
        f"  {subtitle}\n"
        f"  GPU-PREP RECOMMENDED BEFORE RENDER\n"
    )
    return boot + extra


def intro_recommendations() -> str:
    return (
        "LAUNCH INTRO — prompt recommendations\n"
        "─────────────────────────────────────\n"
        "  · Still: local Comfy DreamShaper (QQQ0)\n"
        "  · Storyboard LoRAs: multi-angle / next-scene (Qwen weights staged;\n"
        "    sampling PAUSED on 16GB — use when VRAM allows)\n"
        "  · Short loop: AnimateDiff on gpu-host\n"
        "  · Motion sizzle: WAN 2.2 I2V or AnimateDiff (not slideshow)\n"
        "  · Longer I2V: FramePack :7864  (receipt required)\n"
        "  · Cloud I2V: grok_imagine only with QQQ1 + label\n"
        "  · Every clip: renderer · qqq · gpu_evidence\n"
        "  · Disk catalog: software · disk COMFYUI · gpu-prep\n"
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


def cli_args_menu() -> str:
    """Compact argument / verb list for boot → CLI help handoff."""
    return (
        "  models:  inventory · stage\n"
        "  story:   sides PATH · run PATH · batch PATHS…\n"
        "  stack:   providers · doctor · launch ID · stop ID · pull\n"
        "  disks:   software · disk COMFYUI|FRAMEPACK|DIRECTORS · gpu-prep\n"
        "  process: discover · audit · smoke · lock show|write|load\n"
        "  fed:     packet emit · nodes list · chains tip\n"
        "  media:   show PATH.jpg|.png · play PATH.mp4 · open PATH\n"
        "  proof:   receipt show|stamp PATH --renderer … --qqq QQQ0\n"
        "  ui:      tui [--skin c64|green|mono|modern] [--prompt TEXT]\n"
        "\n"
        "  prompt types: still · multi-angle · Next Scene: · i2v sizzle\n"
        "  caps: storyboard · video segments · music/voice · federation\n"
    )


def disk_directory_menu() -> str:
    """Old-school C64 LOAD\"$\",8 style software catalog (text)."""
    return (
        '**** MOK-TUA DISK DIRECTORY ****\n'
        ' 0 "MOK-TUA CONDUCTOR "  00 2A\n'
        " DRIVE 8  ·  UNIT 0  ·  QQQ0 LOCAL\n"
        "\n"
        ' 1  "SOFTWARE"              PRG  LIST GAME DISKS\n'
        ' 2  "DISK COMFYUI --SPLASH"  PRG  INSERT + LOAD SCRN\n'
        ' 3  "DISK FRAMEPACK"        PRG  LONG I2V STUDIO\n'
        ' 4  "DISK DIRECTORS"        PRG  CONSOLE ORCHESTRA\n'
        ' 5  "GPU-PREP --LIVE"       PRG  FREE VRAM /FREE\n'
        ' 6  "RUN STORY.MD"          PRG  STORY→SHOTS→STILLS\n'
        ' 7  "SIDES SCRIPT.PDF"      PRG  INGEST PDF/FDX\n'
        ' 8  "DOCTOR"                PRG  STACK HEALTH\n'
        ' 9  "TUI --SKIN C64"        PRG  CONDUCTOR DECK\n'
        '10  "SHOW OUT.PNG"          PRG  PREVIEW STILL\n'
        '11  "PLAY OUT.MP4"          PRG  EXTERNAL PLAYER\n'
        '12  "RECEIPT STAMP"         PRG  PROVENANCE SIDECAR\n'
        '13  "PROMPTS: STILL"        SEQ  DREAMSHAPER / FLUX\n'
        '14  "PROMPTS: MULTI-ANGLE"  SEQ  CAMERA GRAMMAR\n'
        '15  "PROMPTS: NEXT SCENE:"  SEQ  CONTINUITY LOCK\n'
        '16  "PROMPTS: I2V SIZZLE"   SEQ  ANIMATEDIFF / WAN\n'
        "\n"
        ' EXAMPLE:  show docs/assets/exports/mok-tua-petscii-matrix-poster.png\n'
        ' EXAMPLE:  play docs/assets/exports/mok-tua-petscii-matrix-export.mp4\n'
        " BLOCKS FREE: 664  ·  TYPE software | disk ID | show PATH\n"
    )
