"""Parse MOCK-TUA story elements markdown (export schema)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore


FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
SCENE_RE = re.compile(r"^#\s+Scene\s+(.+)$", re.M)
SHOT_RE = re.compile(r"^##\s+Shot\s+(.+)$", re.M)


def _parse_kv_block(text: str) -> dict[str, Any]:
    """Parse simple key: value / multiline prompt: > blocks."""
    out: dict[str, Any] = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        if ":" not in line:
            i += 1
            continue
        key, _, rest = line.partition(":")
        key = key.strip()
        rest = rest.strip()
        if rest == ">" or rest == "|":
            buf: list[str] = []
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if nxt and not nxt.startswith(" ") and not nxt.startswith("\t") and ":" in nxt:
                    # next key at indent 0
                    if not nxt.startswith(" ") and re.match(r"^[a-zA-Z_][\w]*:", nxt):
                        break
                if nxt.startswith("  ") or nxt.startswith("\t") or not nxt.strip():
                    buf.append(nxt.strip() if nxt.strip() else "")
                    i += 1
                    continue
                # indented content without being a key
                if nxt.startswith(" "):
                    buf.append(nxt.strip())
                    i += 1
                    continue
                break
            out[key] = "\n".join(x for x in buf if x).strip()
            continue
        if rest == "":
            # possible nested list
            items: list[Any] = []
            i += 1
            while i < len(lines) and (lines[i].startswith("  ") or lines[i].startswith("\t") or lines[i].startswith("-")):
                raw = lines[i].strip()
                if raw.startswith("- "):
                    item = raw[2:].strip()
                    if ":" in item and not item.startswith("http"):
                        # character_lock: instructor style
                        k2, _, v2 = item.partition(":")
                        items.append({k2.strip(): v2.strip()})
                    else:
                        items.append(item)
                i += 1
            out[key] = items
            continue
        # scalar
        if rest.lower() in ("true", "false"):
            out[key] = rest.lower() == "true"
        elif rest.lower() == "null":
            out[key] = None
        else:
            try:
                if "." in rest:
                    out[key] = float(rest)
                else:
                    out[key] = int(rest)
            except ValueError:
                out[key] = rest.strip('"').strip("'")
        i += 1
    return out


def parse_story_markdown(text: str) -> dict[str, Any]:
    """Return {meta, scenes:[{id, fields, shots:[{id, fields}]}]}."""
    meta: dict[str, Any] = {}
    body = text
    m = FRONT_MATTER_RE.match(text)
    if m:
        fm = m.group(1)
        if yaml is not None:
            loaded = yaml.safe_load(fm)
            if isinstance(loaded, dict):
                meta = loaded
        else:
            meta = _parse_kv_block(fm)
        body = text[m.end() :]

    scene_headers = list(SCENE_RE.finditer(body))
    scenes: list[dict[str, Any]] = []

    if not scene_headers:
        # single implicit scene from remaining shots
        shots = _parse_shots(body)
        scenes.append({"id": "scene_00", "title": "default", "fields": {}, "shots": shots})
        return {"meta": meta, "scenes": scenes, "shot_count": sum(len(s["shots"]) for s in scenes)}

    for idx, sm in enumerate(scene_headers):
        start = sm.end()
        end = scene_headers[idx + 1].start() if idx + 1 < len(scene_headers) else len(body)
        chunk = body[start:end]
        title = sm.group(1).strip()
        # split fields before first shot
        first_shot = SHOT_RE.search(chunk)
        if first_shot:
            field_text = chunk[: first_shot.start()]
            shot_text = chunk[first_shot.start() :]
        else:
            field_text = chunk
            shot_text = ""
        fields = _parse_kv_block(field_text)
        scene_id = str(fields.get("id") or f"scene_{idx + 1:02d}")
        scenes.append(
            {
                "id": scene_id,
                "title": title,
                "fields": fields,
                "shots": _parse_shots(shot_text),
            }
        )

    return {
        "meta": meta,
        "scenes": scenes,
        "shot_count": sum(len(s["shots"]) for s in scenes),
        "title": meta.get("title") or (scenes[0]["title"] if scenes else "untitled"),
    }


def _parse_shots(text: str) -> list[dict[str, Any]]:
    headers = list(SHOT_RE.finditer(text))
    shots: list[dict[str, Any]] = []
    for idx, hm in enumerate(headers):
        start = hm.end()
        end = headers[idx + 1].start() if idx + 1 < len(headers) else len(text)
        chunk = text[start:end]
        fields = _parse_kv_block(chunk)
        shot_title = hm.group(1).strip()
        shot_id = str(fields.get("id") or f"shot_{idx + 1:02d}")
        shots.append({"id": shot_id, "title": shot_title, "fields": fields})
    return shots


def parse_story_file(path: Path | str) -> dict[str, Any]:
    p = Path(path)
    return parse_story_markdown(p.read_text(encoding="utf-8"))


def duration_seconds(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip().lower().rstrip("s")
    if ":" in s:
        parts = s.split(":")
        try:
            parts_f = [float(x) for x in parts]
        except ValueError:
            return 0.0
        if len(parts_f) == 2:
            return parts_f[0] * 60 + parts_f[1]
        if len(parts_f) == 3:
            return parts_f[0] * 3600 + parts_f[1] * 60 + parts_f[2]
    try:
        return float(s)
    except ValueError:
        return 0.0
