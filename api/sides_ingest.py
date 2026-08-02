"""Ingest sides from Markdown, PDF, or Final Draft FDX → story markdown for mok-tua."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


def _slug(s: str, n: int = 24) -> str:
    x = re.sub(r"[^a-zA-Z0-9]+", "_", (s or "shot").strip()).strip("_").lower()
    return (x or "shot")[:n]


def markdown_from_plain_sides(
    text: str,
    *,
    title: str = "Sides import",
    style_lock: str = "clean cinematic still, consistent character, storyboard panel",
) -> str:
    """Split plain text into shots by blank lines / scene headers / INT./EXT. lines."""
    lines = [ln.rstrip() for ln in text.splitlines()]
    blocks: list[str] = []
    buf: list[str] = []
    scene_pat = re.compile(r"^(INT\.|EXT\.|I/E\.|SCENE\s+\d+|#\s*Scene)", re.I)
    for ln in lines:
        if scene_pat.match(ln.strip()) and buf:
            blocks.append("\n".join(buf).strip())
            buf = [ln]
        elif not ln.strip() and buf:
            blocks.append("\n".join(buf).strip())
            buf = []
        else:
            if ln.strip():
                buf.append(ln)
    if buf:
        blocks.append("\n".join(buf).strip())
    blocks = [b for b in blocks if b]
    if not blocks:
        blocks = [text.strip() or "Empty sides"]

    parts = [
        "---",
        f'title: "{title}"',
        "type: sides_import",
        f'style_lock: "{style_lock}"',
        "version: 1.0",
        "---",
        "",
        "# Scene 1 – Imported Sides",
        "id: scene_01",
        f"duration: {max(4.0, 3.5 * len(blocks)):.1f}s",
        "location: \"from sides\"",
        "mood: \"as scripted\"",
        "",
    ]
    for i, block in enumerate(blocks, 1):
        first = block.splitlines()[0][:80]
        cam = "static medium close-up" if i % 2 == 0 else "wide establishing"
        cont = f"\n  - continue_from: shot_01_{i-1:02d}" if i > 1 else ""
        parts.extend(
            [
                f"## Shot 1.{i} – {_slug(first, 20)}",
                f"id: shot_01_{i:02d}",
                "duration: 3.5s",
                f'camera: "{cam}"',
                "prompt: >",
                *[f"  {ln}" for ln in block.splitlines()[:12]],
                f"  {style_lock}",
                "seed: " + str(40 + i),
                "consistency:",
                "  - character_lock: primary" + cont,
                "status: pending",
                "",
            ]
        )
    return "\n".join(parts)


def parse_fdx(path: Path | str) -> str:
    """Extract Paragraph text from Final Draft FDX XML."""
    root = ET.parse(Path(path)).getroot()
    # FDX uses Content/Paragraph/Text
    chunks: list[str] = []
    for para in root.iter():
        tag = para.tag.split("}")[-1] if "}" in para.tag else para.tag
        if tag != "Paragraph":
            continue
        texts = []
        for t in para.iter():
            ttag = t.tag.split("}")[-1] if "}" in t.tag else t.tag
            if ttag == "Text" and (t.text or "").strip():
                texts.append(t.text.strip())
        if texts:
            chunks.append(" ".join(texts))
    return "\n\n".join(chunks)


def parse_pdf(path: Path | str) -> str:
    """Extract text from PDF via pypdf or pymupdf if available."""
    p = Path(path)
    try:
        import pypdf  # type: ignore

        reader = pypdf.PdfReader(str(p))
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        return "\n\n".join(pages)
    except Exception:
        pass
    try:
        import fitz  # pymupdf

        doc = fitz.open(str(p))
        return "\n\n".join(page.get_text() for page in doc)
    except Exception as exc:
        raise RuntimeError(
            f"PDF extract failed ({exc}). Install pypdf or pymupdf in mok-tua venv."
        ) from exc


def ingest_sides_file(
    path: Path | str,
    *,
    title: str | None = None,
    style_lock: str = "clean cinematic still, consistent character, storyboard panel",
) -> dict[str, Any]:
    p = Path(path)
    if not p.is_file():
        return {"ok": False, "error": "file_not_found", "path": str(p)}
    suffix = p.suffix.lower()
    raw_title = title or p.stem
    try:
        if suffix in (".md", ".markdown", ".txt"):
            text = p.read_text(encoding="utf-8", errors="replace")
            # if already story schema, pass through
            if re.search(r"^##\s+Shot\s+", text, re.M) or (
                text.lstrip().startswith("---") and "prompt:" in text
            ):
                return {"ok": True, "format": "story_markdown", "markdown": text, "title": raw_title}
            md = markdown_from_plain_sides(text, title=raw_title, style_lock=style_lock)
            return {"ok": True, "format": "md_sides", "markdown": md, "title": raw_title}
        if suffix == ".fdx":
            plain = parse_fdx(p)
            md = markdown_from_plain_sides(plain, title=raw_title, style_lock=style_lock)
            return {"ok": True, "format": "fdx", "markdown": md, "title": raw_title, "chars": len(plain)}
        if suffix == ".pdf":
            plain = parse_pdf(p)
            md = markdown_from_plain_sides(plain, title=raw_title, style_lock=style_lock)
            return {"ok": True, "format": "pdf", "markdown": md, "title": raw_title, "chars": len(plain)}
        return {"ok": False, "error": "unsupported_suffix", "suffix": suffix}
    except Exception as exc:
        return {"ok": False, "error": "ingest_failed", "detail": str(exc), "path": str(p)}


def ingest_sides_bytes(
    data: bytes,
    filename: str,
    *,
    title: str | None = None,
    style_lock: str = "clean cinematic still, consistent character, storyboard panel",
) -> dict[str, Any]:
    import tempfile

    suffix = Path(filename).suffix or ".txt"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(data)
        path = Path(tmp.name)
    try:
        return ingest_sides_file(path, title=title or Path(filename).stem, style_lock=style_lock)
    finally:
        path.unlink(missing_ok=True)
