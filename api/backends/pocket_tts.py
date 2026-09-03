"""PocketTTS local voice-clone TTS client.

PocketTTS is a Pinokio app (Gradio-based), not a ComfyUI custom node -- same
outside_comfy_G pattern as ace_step.py. api_name="/generate" takes text,
preset_voice (one of 8 named presets), and custom_voice_file (an Audio
filepath for zero-shot voice cloning -- pass None to use preset_voice only).

Verified 2026-09-02 against a live instance on mrgpu (:42050): a real
2.48s wav was produced with preset_voice="Alba", custom_voice_file=None.
"""

from __future__ import annotations

from typing import Any

PRESET_VOICES = (
    "Alba",
    "Marius",
    "Javert",
    "Jean",
    "Fantine",
    "Cosette",
    "Eponine",
    "Azelma",
)


def generate_speech(
    base_url: str,
    text: str,
    *,
    preset_voice: str = "Alba",
    custom_voice_file: str | None = None,
) -> dict[str, Any]:
    """Generate speech via a running PocketTTS instance.

    base_url: e.g. "http://127.0.0.1:42050" (mrgpu's PocketTTS port).
    custom_voice_file: local path to a short (~10s) reference clip for
    zero-shot cloning; None uses preset_voice instead.

    Returns {ok, audio_path, status} on success, {ok: False, error} on failure.
    """
    try:
        from gradio_client import Client
    except ImportError as exc:
        return {"ok": False, "error": f"gradio_client not installed: {exc}"}

    try:
        client = Client(base_url)
        audio_path, status = client.predict(
            text=text,
            preset_voice=preset_voice,
            custom_voice_file=custom_voice_file,
            api_name="/generate",
        )
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

    return {"ok": True, "audio_path": audio_path, "status": status}
