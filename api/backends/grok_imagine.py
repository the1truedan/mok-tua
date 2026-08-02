"""xAI Grok Imagine still (and optional video) client for mok-tua cloud overflow."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


DEFAULT_BASE = "https://api.x.ai/v1"
DEFAULT_IMAGE_MODEL = "grok-imagine-image"


def _api_key() -> str | None:
    return os.environ.get("XAI_API_KEY") or os.environ.get("GROK_API_KEY")


def available() -> bool:
    return bool(_api_key())


def generate_image(
    prompt: str,
    *,
    model: str | None = None,
    n: int = 1,
    dry_run: bool = True,
    timeout: float = 120.0,
) -> dict[str, Any]:
    """
    Text-to-image via xAI Images API.

    Live path requires XAI_API_KEY. dry_run returns a plan receipt without spend.
    """
    model = model or os.environ.get("MOCK_TUA_GROK_IMAGE_MODEL") or DEFAULT_IMAGE_MODEL
    base = (os.environ.get("XAI_BASE_URL") or DEFAULT_BASE).rstrip("/")
    payload: dict[str, Any] = {
        "provider": "grok_imagine",
        "model": model,
        "prompt_preview": (prompt or "")[:200],
        "n": n,
        "endpoint": f"{base}/images/generations",
    }

    if dry_run:
        payload.update(
            {
                "ok": True,
                "status": "dry_run",
                "note": "Set dry_run=false and XAI_API_KEY for live Grok Imagine",
                "cli_earmark": (
                    f'curl -X POST {base}/images/generations '
                    '-H "Authorization: Bearer $XAI_API_KEY" '
                    '-H "Content-Type: application/json" '
                    f"-d '{{\"model\":\"{model}\",\"prompt\":\"...\"}}'"
                ),
            }
        )
        return payload

    key = _api_key()
    if not key:
        payload.update({"ok": False, "status": "missing_api_key", "error": "XAI_API_KEY not set"})
        return payload

    body = json.dumps({"model": model, "prompt": prompt, "n": n}).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/images/generations",
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
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
            }
        )
        return payload
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        payload.update({"ok": False, "status": "unreachable", "error": str(exc)})
        return payload

    try:
        parsed = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError:
        payload.update(
            {
                "ok": False,
                "status": "invalid_json",
                "http_status": status,
                "raw": raw[:500].decode("utf-8", errors="replace"),
            }
        )
        return payload

    # OpenAI-compatible shape: data[].url or data[].b64_json
    urls: list[str] = []
    data = parsed.get("data") if isinstance(parsed, dict) else None
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item.get("url"):
                urls.append(str(item["url"]))

    payload.update(
        {
            "ok": bool(urls) or status == 200,
            "status": "ok" if urls else "accepted",
            "http_status": status,
            "urls": urls,
            "result": parsed,
        }
    )
    return payload


def generate_video_plan(
    prompt: str,
    *,
    model: str = "grok-imagine-video",
    dry_run: bool = True,
) -> dict[str, Any]:
    """Video path earmark — plan receipt until wired to live video endpoint."""
    return {
        "ok": True if dry_run else False,
        "status": "dry_run" if dry_run else "live_not_implemented",
        "provider": "grok_imagine_video",
        "model": model,
        "prompt_preview": (prompt or "")[:200],
        "note": "Earmark: wire to xAI video generations when productized; prefer local Wan for QQQ0",
    }
