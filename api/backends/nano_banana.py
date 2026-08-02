"""Nano Banana (Gemini image) cloud still client + CLI earmark for mok-tua."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


def _api_key() -> str | None:
    return (
        os.environ.get("GOOGLE_API_KEY")
        or os.environ.get("GEMINI_API_KEY")
        or os.environ.get("NANO_BANANA_API_KEY")
    )


def available() -> bool:
    return bool(_api_key()) or bool(os.environ.get("COMFY_API_KEY"))


def cli_earmark(prompt: str, *, out: str = "panel.png") -> str:
    safe = (prompt or "storyboard panel").replace("'", "'\\''")[:120]
    return f"comfy generate nano-banana --prompt '{safe}' --download {out}"


def generate_image(
    prompt: str,
    *,
    model: str | None = None,
    dry_run: bool = True,
    timeout: float = 120.0,
) -> dict[str, Any]:
    """
    Generate a still via Gemini-compatible generateContent when GOOGLE_API_KEY is set.

    dry_run always succeeds with a CLI earmark for ops smoke without spend.
    Live path is best-effort against Gemini image models; Comfy partner nodes
    remain the preferred production path when using Comfy Cloud.
    """
    model = model or os.environ.get("MOCK_TUA_NANO_BANANA_MODEL") or "nano-banana"
    payload: dict[str, Any] = {
        "provider": "nano_banana",
        "model": model,
        "prompt_preview": (prompt or "")[:200],
        "cli_earmark": cli_earmark(prompt),
    }

    if dry_run:
        payload.update(
            {
                "ok": True,
                "status": "dry_run",
                "note": (
                    "Ops: comfy generate nano-banana; or set GOOGLE_API_KEY for live "
                    "Gemini image path. Prefer Comfy partner nodes on cloud hosts."
                ),
            }
        )
        return payload

    key = _api_key()
    if not key:
        payload.update(
            {
                "ok": False,
                "status": "missing_api_key",
                "error": "GOOGLE_API_KEY / GEMINI_API_KEY not set",
                "cli_earmark": cli_earmark(prompt),
            }
        )
        return payload

    # Gemini native generateContent (image models vary by account availability)
    gemini_model = os.environ.get("MOCK_TUA_GEMINI_IMAGE_MODEL") or "gemini-2.0-flash-preview-image-generation"
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{gemini_model}:generateContent?key={key}"
    )
    body = json.dumps(
        {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            status = resp.status
    except urllib.error.HTTPError as exc:
        err_body = exc.read() if hasattr(exc, "read") else b""
        payload.update(
            {
                "ok": False,
                "status": "http_error",
                "http_status": exc.code,
                "error": err_body[:800].decode("utf-8", errors="replace"),
                "cli_earmark": cli_earmark(prompt),
                "note": "If Gemini image model id changed, set MOCK_TUA_GEMINI_IMAGE_MODEL or use comfy-cli",
            }
        )
        return payload
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        payload.update({"ok": False, "status": "unreachable", "error": str(exc)})
        return payload

    try:
        parsed = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError:
        payload.update({"ok": False, "status": "invalid_json", "http_status": status})
        return payload

    payload.update(
        {
            "ok": status == 200,
            "status": "ok" if status == 200 else "accepted",
            "http_status": status,
            "result": parsed,
        }
    )
    return payload
