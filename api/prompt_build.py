"""Camera / next-scene prompt builder for robust storyboard panels."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = Path(os.environ.get("MOCK_TUA_CONFIG", ROOT / "config"))


def load_camera_config() -> dict[str, Any]:
    path = CONFIG_DIR / "camera_angles.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def resolve_camera_instruction(camera: str | None, cfg: dict[str, Any] | None = None) -> str:
    """Map free-text camera field or preset id to natural-language instruction."""
    if not camera or not str(camera).strip():
        return ""
    cam = str(camera).strip()
    data = cfg if cfg is not None else load_camera_config()
    phrases = data.get("camera_phrases") or {}
    # exact phrase match
    if cam in phrases:
        return str(phrases[cam])
    # case-insensitive phrase
    lower = cam.lower()
    for key, val in phrases.items():
        if key.lower() == lower:
            return str(val)
    # preset id
    for preset in data.get("presets") or []:
        if str(preset.get("id") or "").lower() == lower:
            return str(preset.get("natural") or cam)
        # also match "size height direction" composite
    # partial key containment (longest match)
    best_key = ""
    best_val = ""
    for key, val in phrases.items():
        if key.lower() in lower and len(key) > len(best_key):
            best_key = key
            best_val = str(val)
    if best_val:
        return best_val
    # pass through as natural instruction
    return cam


def sks_token(direction: str, height: str, size: str) -> str:
    """StoryboardUI2 / fal multi-angle token format."""
    return f"<sks> {direction} {height} shot {size}"


def build_panel_prompt(
    base_prompt: str,
    *,
    camera: str | None = None,
    continue_from: str | None = None,
    next_scene: bool | None = None,
    style_lock: str | None = None,
    use_sks: bool = False,
    sks_parts: dict[str, str] | None = None,
) -> str:
    """
    Assemble panel prompt with optional Next Scene prefix + camera grammar.

    When continue_from is set, next_scene defaults True (cinematic continuity).
    """
    cfg = load_camera_config()
    ns_cfg = cfg.get("next_scene") or {}
    if next_scene is None:
        next_scene = bool(continue_from) and bool(ns_cfg.get("enabled_default", True))

    parts: list[str] = []
    if next_scene:
        prefix = str(ns_cfg.get("prefix") or "Next Scene:").strip()
        parts.append(prefix)

    cam_inst = resolve_camera_instruction(camera, cfg)
    if use_sks and sks_parts:
        parts.append(
            sks_token(
                sks_parts.get("direction") or "front",
                sks_parts.get("height") or "eye-level",
                sks_parts.get("size") or "medium shot",
            )
        )
    elif cam_inst:
        parts.append(cam_inst)

    body = (base_prompt or "").strip()
    if body:
        parts.append(body)

    if style_lock:
        parts.append(str(style_lock).strip())

    if continue_from:
        parts.append(f"(visual continuity from {continue_from})")

    return " ".join(p for p in parts if p).strip()


def continuity_from_fields(fields: dict[str, Any]) -> str | None:
    """Extract continue_from from shot consistency list or field."""
    if fields.get("continue_from"):
        return str(fields["continue_from"])
    consistency = fields.get("consistency")
    if isinstance(consistency, list):
        for item in consistency:
            if isinstance(item, dict) and item.get("continue_from"):
                return str(item["continue_from"])
            if isinstance(item, str) and item.startswith("continue_from:"):
                return item.split(":", 1)[-1].strip()
    if isinstance(consistency, dict) and consistency.get("continue_from"):
        return str(consistency["continue_from"])
    return None
