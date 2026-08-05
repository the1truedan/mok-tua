"""Media helpers: show images in-TUI, play mp4 via external tools."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}
VIDEO_EXT = {".mp4", ".webm", ".mov", ".mkv"}


def classify(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in IMAGE_EXT:
        return "image"
    if ext in VIDEO_EXT:
        return "video"
    return "other"


def extract_video_thumb(path: Path, dest: Path | None = None) -> Path | None:
    """First frame via ffmpeg if available."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg or not path.is_file():
        return None
    out = dest or path.with_suffix(".thumb.jpg")
    try:
        proc = subprocess.run(
            [
                ffmpeg,
                "-y",
                "-i",
                str(path),
                "-frames:v",
                "1",
                "-q:v",
                "4",
                str(out),
            ],
            capture_output=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out if proc.returncode == 0 and out.is_file() else None


def play_external(path: Path) -> dict[str, Any]:
    """Play video/image with best available tool (mpv → timg → open/xdg)."""
    if not path.is_file():
        return {"ok": False, "error": f"missing: {path}"}
    kind = classify(path)
    candidates: list[list[str]] = []
    if shutil.which("mpv"):
        candidates.append(["mpv", "--force-window=yes", "--really-quiet", str(path)])
    if kind == "video" and shutil.which("timg"):
        candidates.append(["timg", "-pk", str(path)])
    if kind == "image" and shutil.which("timg"):
        candidates.append(["timg", str(path)])
    if shutil.which("open"):  # macOS
        candidates.append(["open", str(path)])
    if shutil.which("xdg-open"):
        candidates.append(["xdg-open", str(path)])
    if not candidates:
        return {
            "ok": False,
            "error": "no player (install mpv, timg, or use OS open)",
        }
    cmd = candidates[0]
    try:
        # non-blocking for long video
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError as exc:
        return {"ok": False, "error": str(exc)}
    return {"ok": True, "cmd": cmd, "kind": kind}


def render_image_preview(path: Path, *, max_width: int = 48) -> str:
    """Return terminal-friendly image preview text.

    Prefer rich-pixels / textual-image when available; else chafa; else path note.
    """
    if not path.is_file():
        return f"(missing image: {path})"

    # chafa unicode
    if shutil.which("chafa"):
        try:
            proc = subprocess.run(
                [
                    "chafa",
                    f"--size={max_width}x18",
                    "--symbols=block",
                    str(path),
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                return proc.stdout.rstrip()
        except (OSError, subprocess.TimeoutExpired):
            pass

    # rich-pixels half-blocks
    try:
        from PIL import Image  # type: ignore
        from rich_pixels import Pixels  # type: ignore
        from rich.console import Console
        from io import StringIO

        img = Image.open(path)
        img.thumbnail((max_width * 2, 36))
        buf = StringIO()
        console = Console(file=buf, width=max_width, force_terminal=True, color_system="truecolor")
        console.print(Pixels.from_image(img))
        text = buf.getvalue()
        if text.strip():
            return text.rstrip()
    except Exception:
        pass

    size = path.stat().st_size
    return (
        f"[image] {path.name}  ({size} bytes)\n"
        f" path: {path}\n"
        " tip: pip install rich-pixels pillow  OR  brew install chafa/timg\n"
        "      play PATH opens external viewer"
    )


def media_status() -> str:
    tools = []
    for name in ("mpv", "timg", "chafa", "ffmpeg", "open"):
        tools.append(f"{name}:{'Y' if shutil.which(name) else 'n'}")
    try:
        import rich_pixels  # noqa: F401

        tools.append("rich-pixels:Y")
    except ImportError:
        tools.append("rich-pixels:n")
    try:
        import textual_image  # noqa: F401

        tools.append("textual-image:Y")
    except ImportError:
        tools.append("textual-image:n")
    return "media " + " ".join(tools)
