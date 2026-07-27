"""Cloud overflow estimate stub (HF / RunPod / Vast) — no live spend by default."""

from __future__ import annotations

from typing import Any


def cloud_overflow_receipt(
    shot_id: str,
    *,
    provider: str,
    estimate: dict[str, Any],
    live: bool = False,
) -> dict[str, Any]:
    if live:
        return {
            "ok": False,
            "status": "live_not_implemented",
            "shot_id": shot_id,
            "provider": provider,
            "note": "Set MOCK_TUA_HF_LIVE only after wiring Gradio/HF client; v1 is estimate-only.",
            "estimate": estimate,
        }
    return {
        "ok": True,
        "status": "stub_receipt",
        "shot_id": shot_id,
        "provider": provider,
        "estimate": estimate,
        "charged_usd": 0.0,
    }
