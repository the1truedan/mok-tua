"""Live Headroom / OpenAI-compatible chat for S0 script expansion."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


def chat_completions(
    base_url: str,
    *,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    max_tokens: int = 2048,
    temperature: float = 0.4,
    timeout: float = 120.0,
) -> dict[str, Any]:
    url = base_url.rstrip("/") + "/chat/completions"
    body = json.dumps(
        {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {"ok": True, "data": data}
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")[:800]
        return {"ok": False, "status": exc.code, "error": err_body}
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)}


def expand_script_to_shots(
    script: str,
    *,
    base_url: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    base = base_url or os.environ.get("HEADROOM_BASE", "http://127.0.0.1:8787/v1")
    key = api_key or os.environ.get("LITELLM_MASTER_KEY", "")
    mdl = model or os.environ.get("LLM_MODEL", "manager-auto")
    if dry_run or not key:
        return {
            "ok": True,
            "status": "dry_run" if dry_run else "no_api_key",
            "shots": [
                {
                    "id": "shot_auto_01",
                    "duration": 5.0,
                    "prompt": script[:400] or "instructor establishes calm technical presence",
                }
            ],
            "note": "dry_run or missing LITELLM_MASTER_KEY — synthetic single shot",
        }
    system = (
        "You are MOCK-TUA shot lister. Given a short script, return ONLY valid JSON: "
        '{"shots":[{"id":"shot_01","duration":5.0,"prompt":"...","camera":"..."}]} '
        "Max 8 shots. No markdown fences."
    )
    result = chat_completions(
        base,
        api_key=key,
        model=mdl,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": script[:6000]},
        ],
    )
    if not result.get("ok"):
        return {"ok": False, "status": "llm_failed", **result}
    content = ""
    try:
        content = result["data"]["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return {"ok": False, "status": "bad_response", "raw": result}
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return {"ok": False, "status": "json_parse_failed", "content": content[:1000]}
    shots = parsed.get("shots") if isinstance(parsed, dict) else None
    if not isinstance(shots, list):
        return {"ok": False, "status": "missing_shots", "parsed": parsed}
    return {"ok": True, "status": "ok", "shots": shots, "model": mdl}
