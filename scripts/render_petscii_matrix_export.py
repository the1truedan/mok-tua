#!/usr/bin/env python3
"""Render the PETSCII Matrix brand short (procedural PIL + ffmpeg).

Identity + conductor onboarding export — not a face demo.

Beat sheet (v4):
  1. C64 loader — LOADING bar fills in character cells
  2. µ rain → glyphs resolve into PETSCII MOK-TUA
  3. Rain stops; MOK-TUA brightens (hold)
  4. CRT TV turn-off blip (collapse to center line → black)
  5. tmux pane: mok-tua orchestrator CLI prompt
  6. Old-school C64 disk-in-drive LOAD menu — args, prompt types, caps

Usage:
  python3 scripts/render_petscii_matrix_export.py --procedural-boot
  python3 scripts/render_petscii_matrix_export.py --out work/brand_export/v4
"""

from __future__ import annotations

import argparse
import random
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tui.petscii import mok_tua_logo_lines  # noqa: E402

# --- canvas / palette -------------------------------------------------------
W, H = 1280, 720
FPS = 24
DURATION_S = 28.0  # longer narrative for menu
N_FRAMES = int(DURATION_S * FPS)  # 672

C64_BG = (64, 49, 141)  # #40318D
C64_PANEL = (160, 160, 255)
C64_INK = (32, 24, 80)
C64_TITLE = (255, 255, 255)
C64_LIGHT = (170, 170, 255)
C64_CURSOR = (255, 255, 255)

MATRIX_BG = (0, 0, 0)
MATRIX_MID = (0, 160, 50)
MATRIX_HI = (140, 255, 160)
MATRIX_LOGO = (180, 255, 200)
MATRIX_BRIGHT = (220, 255, 230)
FOOT_DIM = (40, 90, 50)

# tmux / terminal
TERM_BG = (12, 14, 18)
TERM_FG = (200, 220, 200)
TERM_DIM = (90, 110, 90)
TERM_ACCENT = (80, 200, 120)
TMUX_BAR = (40, 50, 70)
TMUX_ACTIVE = (60, 140, 90)

CELL = 16
BAR_CELLS = 24


def _font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Courier New Bold.ttf",
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
        "/System/Library/Fonts/Supplemental/Andale Mono.ttf",
        "/Library/Fonts/Courier New.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ]
    for p in candidates:
        if Path(p).is_file():
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    return ImageFont.load_default()


def progress_fill(t: float, cells: int = BAR_CELLS) -> int:
    t = max(0.0, min(1.0, t))
    eased = 1.0 - (1.0 - t) ** 2.4
    return int(round(eased * cells))


def draw_char_progress(
    draw: ImageDraw.ImageDraw,
    *,
    cx: int,
    y: int,
    filled: int,
    cells: int = BAR_CELLS,
    cell: int = CELL,
    label: str = "LOADING",
    ink=C64_INK,
    track=(140, 140, 220),
    fill=C64_INK,
    font: ImageFont.ImageFont | None = None,
) -> None:
    font = font or _font(22)
    tw = draw.textlength(label, font=font) if hasattr(draw, "textlength") else len(label) * 12
    lx = int(cx - (cells * cell) // 2 - tw - 16)
    draw.text((lx, y + (cell - 22) // 2), label, fill=ink, font=font)
    bx = int(cx - (cells * cell) // 2)
    for i in range(cells):
        x0 = bx + i * cell
        draw.rectangle(
            [x0 + 1, y + 1, x0 + cell - 2, y + cell - 2],
            fill=fill if i < filled else track,
            outline=ink,
        )
    draw.rectangle(
        [bx - 2, y - 2, bx + cells * cell + 1, y + cell + 1],
        outline=ink,
        width=2,
    )


def draw_matrix_char_progress(
    draw: ImageDraw.ImageDraw,
    *,
    cx: int,
    y: int,
    filled: int,
    cells: int = BAR_CELLS,
    cell: int = CELL,
    label: str = "LOADING",
) -> None:
    font = _font(20)
    if label:
        tw = draw.textlength(label, font=font) if hasattr(draw, "textlength") else len(label) * 11
        lx = int(cx - (cells * cell) // 2 - tw - 14)
        draw.text((lx, y + (cell - 18) // 2), label, fill=MATRIX_HI, font=font)
    bx = int(cx - (cells * cell) // 2)
    for i in range(cells):
        x0 = bx + i * cell
        col = MATRIX_HI if i < filled else (20, 40, 20)
        draw.rectangle(
            [x0 + 1, y + 1, x0 + cell - 2, y + cell - 2],
            fill=col,
            outline=MATRIX_MID,
        )
    draw.rectangle(
        [bx - 2, y - 2, bx + cells * cell + 1, y + cell + 1],
        outline=MATRIX_MID,
        width=2,
    )
    pct = int(100 * filled / max(1, cells))
    draw.text(
        (bx + cells * cell + 12, y + (cell - 18) // 2),
        f"{pct:3d}%",
        fill=MATRIX_MID,
        font=font,
    )


def render_logo_bitmap(
    cell: int = 18,
    color: tuple[int, int, int] = MATRIX_LOGO,
    bg: tuple[int, int, int] | None = None,
    brightness: float = 1.0,
) -> Image.Image:
    """Rasterize petscii block MOK-TUA. brightness multiplies RGB (can >1)."""
    lines = mok_tua_logo_lines()
    rows = len(lines)
    cols = max(len(ln) for ln in lines)
    im = Image.new("RGBA", (cols * cell, rows * cell), (*bg, 255) if bg else (0, 0, 0, 0))
    px = im.load()
    base = tuple(max(0, min(255, int(c * brightness))) for c in color)
    for r, ln in enumerate(lines):
        for c, ch in enumerate(ln):
            if not ch.strip():
                continue
            x0, y0 = c * cell, r * cell
            for yy in range(cell):
                for xx in range(cell):
                    if yy % 2 == 1:
                        col = tuple(max(0, v - 28) for v in base)
                    else:
                        col = base
                    px[x0 + xx, y0 + yy] = (*col, 255)
    return im


# ---------------------------------------------------------------------------
# Scene 1 — C64 loader
# ---------------------------------------------------------------------------
def boot_frame(step: int, bar_cells: int = BAR_CELLS) -> Image.Image:
    im = Image.new("RGB", (W, H), C64_BG)
    d = ImageDraw.Draw(im)
    margin_x, margin_y = 80, 60
    d.rectangle([margin_x, margin_y, W - margin_x, H - margin_y], fill=C64_PANEL)

    title_f = _font(22)
    body_f = _font(20)
    d.text(
        (W // 2, 28),
        "**** MOK-TUA V0.5.9  CONDUCTOR · SKIN=C64 ****",
        fill=C64_TITLE,
        font=title_f,
        anchor="mt",
    )

    logo = render_logo_bitmap(cell=22, color=C64_INK, bg=C64_PANEL)
    lx = (W - logo.width) // 2
    ly = 110
    im.paste(logo.convert("RGB"), (lx, ly))

    d.text(
        (W // 2, ly + logo.height + 28),
        "**** MOK-TUA V0.5.9  CONDUCTOR ****",
        fill=C64_INK,
        font=body_f,
        anchor="mt",
    )
    d.text(
        (W // 2, ly + logo.height + 56),
        "64K RAM SYSTEM  38911 BASIC BYTES FREE",
        fill=C64_INK,
        font=body_f,
        anchor="mt",
    )

    filled = progress_fill(step / max(1, bar_cells), bar_cells)
    draw_char_progress(
        d,
        cx=W // 2 + 30,
        y=ly + logo.height + 100,
        filled=filled,
        cells=bar_cells,
        cell=CELL,
        label="LOADING",
        ink=C64_INK,
        track=(140, 140, 220),
        fill=C64_INK,
        font=_font(24),
    )
    d.text(
        (W // 2, ly + logo.height + 100 + CELL + 28),
        "PETSCII BOOT · VIC-II · SEARCHING FOR MOK-TUA",
        fill=C64_INK,
        font=body_f,
        anchor="mt",
    )
    return im


# ---------------------------------------------------------------------------
# Scene 2–4 — Matrix rain → logo → brighten
# ---------------------------------------------------------------------------
def _init_columns(n_cols: int, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    cols = []
    for i in range(n_cols):
        cols.append(
            {
                "x": i,
                "y": rng.uniform(-30, 0),
                "speed": rng.uniform(0.35, 1.15),
                "len": rng.randint(6, 18),
                "glyphs": [rng.choice("µµµµ01█▓░╬") for _ in range(40)],
            }
        )
    return cols


def matrix_frame(
    frame_i: int,
    cols: list[dict],
    *,
    logo_alpha: float = 0.0,
    rain_alpha: float = 1.0,
    logo_brightness: float = 1.0,
    foot: str = "mok-tua · PETSCII · conductor identity export · QQQ0",
) -> Image.Image:
    im = Image.new("RGB", (W, H), MATRIX_BG)
    d = ImageDraw.Draw(im)
    font = _font(16)
    cell_h = 20
    n_cols = len(cols)

    if rain_alpha > 0.02:
        for c in cols:
            head = c["y"] + frame_i * c["speed"]
            trail = c["len"]
            for k in range(trail):
                gy = head - k
                py = int(gy * cell_h) % (H + 40 * cell_h) - 20 * cell_h
                px = 40 + c["x"] * ((W - 80) // max(1, n_cols - 1))
                if py < -cell_h or py > H:
                    continue
                ch = c["glyphs"][(frame_i + k) % len(c["glyphs"])]
                if k == 0:
                    col = MATRIX_HI
                elif k < 3:
                    col = MATRIX_MID
                else:
                    f = max(0.15, 1.0 - k / trail)
                    col = tuple(int(v * f) for v in MATRIX_MID)
                col = tuple(int(v * rain_alpha) for v in col)
                d.text((px, py), ch, fill=col, font=font)

    if logo_alpha > 0.01:
        color = MATRIX_BRIGHT if logo_brightness >= 1.15 else MATRIX_LOGO
        logo = render_logo_bitmap(cell=20, color=color, brightness=logo_brightness)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        lx = (W - logo.width) // 2
        ly = (H - logo.height) // 2 - 20
        a = max(0, min(255, int(logo_alpha * 255)))
        bands = logo.split()
        if len(bands) == 4:
            r, g, b, al = bands
            al = al.point(lambda p: int(p * a / 255))
            logo2 = Image.merge("RGBA", (r, g, b, al))
        else:
            logo2 = logo
        layer.paste(logo2, (lx, ly), logo2)
        im = Image.alpha_composite(im.convert("RGBA"), layer).convert("RGB")
        d = ImageDraw.Draw(im)

    if foot and rain_alpha > 0.05:
        d.text((24, H - 28), foot, fill=FOOT_DIM, font=_font(14))
    return im


# ---------------------------------------------------------------------------
# Scene 5 — CRT TV turn-off
# ---------------------------------------------------------------------------
def crt_off_frame(t: float, source: Image.Image) -> Image.Image:
    """t in [0,1]: collapse image to horizontal center line, then black blip.

    Classic CRT power-off: vertical squash → bright line → flash → black.
    """
    t = max(0.0, min(1.0, t))
    if t < 0.45:
        # squash toward horizontal midline
        u = t / 0.45
        u = u * u  # accelerate
        scale_y = max(0.02, 1.0 - u)
        nh = max(2, int(H * scale_y))
        mid = Image.new("RGB", (W, H), (0, 0, 0))
        # brighten slightly as it collapses
        bright = ImageEnhance.Brightness(source).enhance(1.0 + 0.8 * u)
        scaled = bright.resize((W, nh), Image.Resampling.BILINEAR)
        y0 = (H - nh) // 2
        mid.paste(scaled, (0, y0))
        # horizontal bloom on the band
        if nh < H // 4:
            d = ImageDraw.Draw(mid)
            glow = min(255, int(180 + 75 * u))
            d.rectangle([0, y0 - 2, W, y0 + nh + 2], outline=(glow, glow, glow))
        return mid
    if t < 0.62:
        # bright white horizontal line
        u = (t - 0.45) / 0.17
        im = Image.new("RGB", (W, H), (0, 0, 0))
        d = ImageDraw.Draw(im)
        thick = max(1, int(8 * (1.0 - u) + 1))
        cy = H // 2
        # line shortens toward center
        half = int((W // 2) * (1.0 - u * 0.85))
        glow = min(255, int(255 * (1.0 - 0.3 * u)))
        d.rectangle(
            [W // 2 - half, cy - thick, W // 2 + half, cy + thick],
            fill=(glow, glow, min(255, glow + 20)),
        )
        return im
    if t < 0.78:
        # center blip / spark
        u = (t - 0.62) / 0.16
        im = Image.new("RGB", (W, H), (0, 0, 0))
        d = ImageDraw.Draw(im)
        r = max(1, int(14 * (1.0 - u)))
        g = int(255 * (1.0 - u))
        d.ellipse(
            [W // 2 - r, H // 2 - r, W // 2 + r, H // 2 + r],
            fill=(g, g, min(255, g + 30)),
        )
        return im
    # black settle
    return Image.new("RGB", (W, H), (0, 0, 0))


# ---------------------------------------------------------------------------
# Scene 6 — tmux CLI orchestrator
# ---------------------------------------------------------------------------
def tmux_cli_frame(t: float, *, blink: bool = True) -> Image.Image:
    """Fake tmux session with mok-tua CLI help / prompt typing in.

    t: 0..1 progress through the scene (line reveal + typewriter).
    """
    im = Image.new("RGB", (W, H), TERM_BG)
    d = ImageDraw.Draw(im)
    mono = _font(17)
    small = _font(14)
    mono_b = _font(18)

    # tmux status bar top
    d.rectangle([0, 0, W, 28], fill=TMUX_BAR)
    d.rectangle([4, 4, 160, 24], fill=TMUX_ACTIVE)
    d.text((12, 6), "0:mok-tua*", fill=(240, 255, 240), font=small)
    d.text((170, 6), "1:comfy  2:logs  3:shell", fill=(140, 150, 170), font=small)
    d.text((W - 12, 6), "gpu-host · QQQ0", fill=(140, 150, 170), font=small, anchor="ra")

    # left gutter like pane border
    d.line([(0, 28), (0, H - 24)], fill=(50, 60, 80), width=2)

    lines_full = [
        ("dim", "last login: local · conductor session"),
        ("dim", "cd ~/mok-tua && source .venv/bin/activate"),
        ("fg", "$ python3 scripts/mok_tua_cli.py --help"),
        ("accent", "mok-tua v0.5.9 — director stack process"),
        ("dim", "  models: inventory | stage"),
        ("dim", "  story:  sides | run | batch"),
        ("dim", "  stack:  providers | doctor | launch | stop | pull"),
        ("dim", "  disks:  software | disk | gpu-prep"),
        ("dim", "  ui:     tui (--skin c64|green|mono|modern)"),
        ("fg", "$ python3 scripts/mok_tua_cli.py doctor"),
        ("ok", "  stack grade: B+ · comfy: up · headroom: up"),
        ("fg", "$ python3 scripts/mok_tua_cli.py software"),
        ("ok", "  DISK  COMFYUI     RUNNING   :8188"),
        ("ok", "  DISK  FRAMEPACK   READY     :7864"),
        ("ok", "  DISK  DIRECTORS   READY     :5173"),
        ("fg", ""),
    ]

    # reveal lines over time
    n_show = max(1, int(t * (len(lines_full) + 2)))
    y = 40
    lh = 22
    for i, (kind, text) in enumerate(lines_full):
        if i >= n_show:
            break
        if kind == "dim":
            col = TERM_DIM
        elif kind == "accent":
            col = TERM_ACCENT
        elif kind == "ok":
            col = (120, 200, 140)
        else:
            col = TERM_FG
        # typewriter on last visible command line
        if i == n_show - 1 and text.startswith("$") and t < 0.95:
            chars = int(len(text) * min(1.0, (t * len(lines_full) - i) * 2))
            text = text[: max(1, chars)]
        d.text((16, y), text, fill=col, font=mono)
        y += lh

    # READY prompt with cursor
    if n_show >= len(lines_full) - 1:
        prompt = "READY.  "
        d.text((16, y + 8), prompt, fill=TERM_ACCENT, font=mono_b)
        typed = "disk COMFYUI --splash"
        # type the example command
        type_t = max(0.0, (t - 0.72) / 0.28)
        n = int(len(typed) * min(1.0, type_t))
        d.text((16 + 90, y + 8), typed[:n], fill=TERM_FG, font=mono_b)
        if blink and (int(t * 20) % 2 == 0):
            cx = 16 + 90 + n * 10
            d.rectangle([cx, y + 10, cx + 10, y + 26], fill=TERM_ACCENT)

    # bottom tmux bar
    d.rectangle([0, H - 24, W, H], fill=TMUX_BAR)
    d.text(
        (12, H - 20),
        "[tmux] 0:mok-tua*  \"insert disk\"  |  C-b d detach",
        fill=(160, 170, 190),
        font=small,
    )
    return im


# ---------------------------------------------------------------------------
# Scene 7 — C64 disk load menu
# ---------------------------------------------------------------------------
# Menu content: real CLI verbs + prompt types + capabilities
DISK_MENU_HEADER = [
    "     **** MOK-TUA  DISK DIRECTORY ****",
    "  0 \"MOK-TUA CONDUCTOR \"  00 2A",
    "  DRIVE 8  ·  UNIT 0  ·  QQQ0 LOCAL",
    "",
]

DISK_MENU_ENTRIES = [
    #  id   blocks  name                  type note
    ('1', 'PRG', 'LOAD"*",8,1           ', 'BOOT LOADER'),
    ('2', 'PRG', 'SOFTWARE              ', 'LIST GAME DISKS'),
    ('3', 'PRG', 'DISK COMFYUI --SPLASH ', 'INSERT + LOAD SCRN'),
    ('4', 'PRG', 'DISK FRAMEPACK        ', 'LONG I2V STUDIO'),
    ('5', 'PRG', 'DISK DIRECTORS        ', 'CONSOLE ORCHESTRA'),
    ('6', 'PRG', 'GPU-PREP --LIVE       ', 'FREE VRAM /FREE'),
    ('7', 'PRG', 'RUN STORY.MD          ', 'STORY→SHOTS→STILLS'),
    ('8', 'PRG', 'SIDES SCRIPT.PDF      ', 'INGEST PDF/FDX'),
    ('9', 'PRG', 'BATCH WORK/*.MD       ', 'MULTI-STORY RUN'),
    ('10', 'PRG', 'LAUNCH SM_COMFY       ', 'START PROVIDER'),
    ('11', 'PRG', 'PULL --TIER T0        ', 'ORCHESTRATOR PULLS'),
    ('12', 'PRG', 'DOCTOR                ', 'STACK HEALTH'),
    ('13', 'PRG', 'TUI --SKIN C64        ', 'CONDUCTOR DECK'),
    ('14', 'PRG', 'RECEIPT STAMP OUT.MP4 ', 'PROVENANCE SIDECAR'),
    ('15', 'SEQ', 'PROMPTS: STILL        ', 'DREAMSHAPER / FLUX'),
    ('16', 'SEQ', 'PROMPTS: MULTI-ANGLE  ', 'CAMERA GRAMMAR'),
    ('17', 'SEQ', 'PROMPTS: NEXT SCENE:  ', 'CONTINUITY LOCK'),
    ('18', 'SEQ', 'PROMPTS: I2V SIZZLE   ', 'ANIMATEDIFF / WAN'),
    ('19', 'USR', 'CAP: STORYBOARD       ', 'FACEID + PANELS'),
    ('20', 'USR', 'CAP: VIDEO SEGMENTS   ', 'STITCH SHORT CLIPS'),
    ('21', 'USR', 'CAP: MUSIC / VOICE    ', 'ACE-STEP · TTS'),
    ('22', 'USR', 'CAP: FEDERATION       ', 'ASK_PACKET.V1'),
]

DISK_MENU_FOOTER = [
    "",
    "  BLOCKS FREE: 664  ·  PRESS 1-22 OR LOAD\"$\"",
    "  EXAMPLE:  LOAD\"7\",8,1   →  run story.md",
    "  EXAMPLE:  LOAD\"3\",8,1   →  disk comfyui --splash",
    "  EXAMPLE:  LOAD\"18\",8,1  →  i2v sizzle (not slideshow)",
    "",
    "READY.",
]


def disk_menu_frame(t: float, *, cursor_row: int = 0, blink: bool = True) -> Image.Image:
    """Classic C64 LOAD\"$\",8 directory listing aesthetic."""
    im = Image.new("RGB", (W, H), C64_BG)
    d = ImageDraw.Draw(im)
    mono = _font(16)
    mono_sm = _font(14)

    # outer border
    d.rectangle([40, 30, W - 40, H - 30], outline=C64_LIGHT, width=2)
    d.rectangle([44, 34, W - 44, H - 34], outline=C64_PANEL, width=1)

    y = 44
    lh = 18

    # header always
    for line in DISK_MENU_HEADER:
        d.text((60, y), line, fill=C64_LIGHT, font=mono)
        y += lh

    # progressive reveal of entries
    n_entries = len(DISK_MENU_ENTRIES)
    n_show = max(1, int(t * (n_entries + 3)))
    n_show = min(n_entries, n_show)

    # highlight selection once mostly revealed
    select_idx = min(n_entries - 1, max(0, cursor_row))
    if t > 0.85:
        # cycle selection slowly
        select_idx = int((t - 0.85) / 0.15 * 6) % min(8, n_entries)

    for i, (num, ftype, name, note) in enumerate(DISK_MENU_ENTRIES):
        if i >= n_show:
            break
        # C64 directory style:  "NAME"  PRG   note
        line = f' {num:>2}  "{name.strip()}"  {ftype}  {note}'
        # pad / fit
        if len(line) > 72:
            line = line[:71] + "…"
        if i == select_idx and t > 0.5:
            # inverse video selection bar
            d.rectangle([56, y - 1, W - 56, y + lh - 2], fill=C64_LIGHT)
            d.text((60, y), line, fill=C64_BG, font=mono_sm)
        else:
            d.text((60, y), line, fill=C64_LIGHT, font=mono_sm)
        y += lh

    # footer after entries mostly in
    if n_show >= n_entries - 2:
        for line in DISK_MENU_FOOTER:
            col = C64_TITLE if line.startswith("READY") else C64_LIGHT
            d.text((60, y), line, fill=col, font=mono_sm)
            y += lh
        # blinking cursor after READY.
        if blink and (int(t * 16) % 2 == 0):
            d.rectangle([60 + 7 * 10, y - lh + 2, 60 + 7 * 10 + 10, y - 4], fill=C64_LIGHT)

    # side label
    d.text(
        (W - 48, H // 2),
        "DISK",
        fill=C64_PANEL,
        font=_font(12),
        anchor="mm",
    )
    return im


def insert_disk_splash(t: float) -> Image.Image:
    """Brief INSERT DISK banner between tmux and full directory."""
    im = Image.new("RGB", (W, H), C64_BG)
    d = ImageDraw.Draw(im)
    mono = _font(22)
    big = _font(28)
    box = [
        "╔══════════════════════════════════════════╗",
        "║   INSERT DISK: MOK-TUA                   ║",
        "║   TITLE: CONDUCTOR SOFTWARE CATALOG      ║",
        "║   STATUS: DRIVE 8  SPINNING…             ║",
        "║   LOADING PROGRAM  *******************   ║",
        "╚══════════════════════════════════════════╝",
        "     PRESS PLAY ON TAPE · OR TYPE LOAD\"$\"",
    ]
    y0 = H // 2 - len(box) * 16
    filled = progress_fill(t, 20)
    for i, line in enumerate(box):
        if "LOADING PROGRAM" in line:
            stars = "*" * filled + "." * (20 - filled)
            line = f"║   LOADING PROGRAM  {stars:<20} ║"
        d.text((W // 2, y0 + i * 32), line, fill=C64_LIGHT, font=mono, anchor="mm")
    d.text(
        (W // 2, y0 + len(box) * 32 + 20),
        f"{int(100 * t)}%",
        fill=C64_TITLE,
        font=big,
        anchor="mm",
    )
    return im


# ---------------------------------------------------------------------------
# Timeline
# ---------------------------------------------------------------------------
def build_timeline() -> list[Image.Image]:
    """Assemble full v4 narrative (~28s @ 24fps).

    Timing (frames @ 24fps):
       0– 47  C64 loader bar 0→100%              (2.0s)
      48– 59  black beat / SEARCHING              (0.5s)
      60–131  µ rain only                         (3.0s)
     132–179  rain + logo fade in                 (2.0s)
     180–203  rain stops, logo holds              (1.0s)
     204–251  logo brightens                      (2.0s)
     252–287  CRT TV turn-off blip                (1.5s)
     288–311  black settle                        (1.0s)
     312–407  tmux CLI prompt + type              (4.0s)
     408–431  INSERT DISK splash                  (1.0s)
     432–671  C64 disk directory menu             (10.0s)
    """
    frames: list[Image.Image] = []
    cols = _init_columns(48, seed=7)

    # 1) C64 loader
    BOOT_N = 48
    for i in range(BOOT_N):
        step = int(round((i / max(1, BOOT_N - 1)) * BAR_CELLS))
        frames.append(boot_frame(step, BAR_CELLS))

    # 1b) brief black / ready flash
    for i in range(12):
        im = Image.new("RGB", (W, H), C64_BG)
        d = ImageDraw.Draw(im)
        d.text(
            (W // 2, H // 2),
            "SEARCHING FOR MOK-TUA" if i % 4 < 2 else "LOADING",
            fill=C64_LIGHT,
            font=_font(28),
            anchor="mm",
        )
        frames.append(im)

    # 2) Pure rain
    RAIN_N = 72
    for i in range(RAIN_N):
        frames.append(matrix_frame(i, cols, logo_alpha=0.0, rain_alpha=1.0))

    # 3) Logo fade-in through rain
    FADE_IN = 48
    for i in range(FADE_IN):
        a = ((i + 1) / FADE_IN) ** 1.5
        frames.append(
            matrix_frame(
                RAIN_N + i,
                cols,
                logo_alpha=a,
                rain_alpha=1.0 - 0.4 * a,
                logo_brightness=1.0,
            )
        )

    # 4) Rain stops (freeze rain alpha → 0), logo solid
    STOP_N = 24
    last_rain_frame = RAIN_N + FADE_IN
    for i in range(STOP_N):
        rain_a = max(0.0, 1.0 - 0.4 - (i / STOP_N) * 0.6)
        frames.append(
            matrix_frame(
                last_rain_frame,  # freeze column motion
                cols,
                logo_alpha=1.0,
                rain_alpha=rain_a,
                logo_brightness=1.0,
                foot="" if rain_a < 0.2 else "mok-tua · PETSCII · conductor identity export · QQQ0",
            )
        )

    # 5) MOK-TUA brightens
    BRIGHT_N = 48
    for i in range(BRIGHT_N):
        b = 1.0 + 0.85 * ((i + 1) / BRIGHT_N)  # up to ~1.85×
        frames.append(
            matrix_frame(
                last_rain_frame,
                cols,
                logo_alpha=1.0,
                rain_alpha=0.0,
                logo_brightness=b,
                foot="",
            )
        )

    # capture bright logo for CRT source
    bright_src = frames[-1].copy()

    # 6) CRT turn-off
    CRT_N = 36
    for i in range(CRT_N):
        frames.append(crt_off_frame((i + 1) / CRT_N, bright_src))

    # 7) black settle
    for _ in range(24):
        frames.append(Image.new("RGB", (W, H), (0, 0, 0)))

    # 8) tmux CLI
    TMUX_N = 96
    for i in range(TMUX_N):
        frames.append(tmux_cli_frame((i + 1) / TMUX_N, blink=True))

    # 9) INSERT DISK splash
    INS_N = 24
    for i in range(INS_N):
        frames.append(insert_disk_splash((i + 1) / INS_N))

    # 10) Disk directory menu — fill remaining
    remaining = N_FRAMES - len(frames)
    if remaining < 48:
        remaining = 120
    for i in range(remaining):
        t = (i + 1) / remaining
        frames.append(disk_menu_frame(t, blink=True))

    if len(frames) > N_FRAMES:
        frames = frames[:N_FRAMES]
    while len(frames) < N_FRAMES:
        frames.append(frames[-1].copy())
    return frames


def encode_mp4(frame_dir: Path, out_mp4: Path, fps: int = FPS) -> None:
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-framerate",
        str(fps),
        "-i",
        str(frame_dir / "f%04d.png"),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-crf",
        "18",
        "-movflags",
        "+faststart",
        str(out_mp4),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {r.stderr[-800:]}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--out",
        type=Path,
        default=ROOT / "work" / "brand_export" / "v4",
    )
    ap.add_argument("--publish", action="store_true", default=True)
    ap.add_argument("--no-publish", action="store_false", dest="publish")
    # keep flag for CLI compat; v4 always procedural boot
    ap.add_argument("--procedural-boot", action="store_true", default=True)
    args = ap.parse_args()

    out: Path = args.out
    frame_dir = out / "frames"
    frame_dir.mkdir(parents=True, exist_ok=True)

    print(f"rendering {N_FRAMES} frames @ {FPS}fps (~{DURATION_S:.0f}s) …")
    frames = build_timeline()
    for i, fr in enumerate(frames):
        fr.save(frame_dir / f"f{i:04d}.png")
        if i % 80 == 0:
            print(f"  wrote f{i:04d}.png")

    mp4 = out / "mok_tua_petscii_matrix_export.mp4"
    print(f"encoding {mp4} …")
    encode_mp4(frame_dir, mp4)

    # poster = full disk directory (end of catalog reveal)
    poster_idx = min(len(frames) - 1, max(0, len(frames) - 24))
    poster = out / "mok_tua_petscii_matrix_poster.png"
    frames[poster_idx].save(poster)
    # also keep a bright-logo still as alternate
    frames[min(250, len(frames) - 1)].save(out / "poster_logo_bright.png")
    print(f"poster: {poster} (frame {poster_idx})")

    if args.publish:
        dest_dir = ROOT / "docs" / "assets" / "exports"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_mp4 = dest_dir / "mok-tua-petscii-matrix-export.mp4"
        dest_poster = dest_dir / "mok-tua-petscii-matrix-poster.png"
        dest_mp4.write_bytes(mp4.read_bytes())
        dest_poster.write_bytes(poster.read_bytes())
        brand = ROOT / "work" / "brand_export"
        brand.mkdir(parents=True, exist_ok=True)
        (brand / "mok_tua_petscii_matrix_export.mp4").write_bytes(mp4.read_bytes())
        print(f"published → {dest_mp4}")
        print(f"published → {dest_poster}")

    print("done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
