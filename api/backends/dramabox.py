"""DramaBox local expressive TTS / voice-clone client.

DramaBox is a Pinokio app (Gradio-based, LTX-2.3-derived, low-VRAM/MMGP
offload path), not a ComfyUI custom node -- same outside_comfy_G pattern as
ace_step.py / pocket_tts.py. api_name="/on_generate" requires prompt and
audio_ref (a short reference clip for voice cloning, ~10s recommended);
other params have sane UI defaults.

Verified 2026-09-02 against a live instance on mrgpu (:42051): a real wav
was produced -- but ONLY after freeing VRAM by stopping the idle ace-step-ui
process first. See the VRAM note below before calling this in an
orchestration context where other GPU apps may be resident.

*** VRAM WARNING -- confirmed via live testing, not theoretical ***
mrgpu's card is 16.4GB. DramaBox's low-VRAM/MMGP path loads Gemma-3-12B
(4-bit, ~7.8GB) + the 3.3B DiT/VAE/decoder stack (~11-12GB resident total)
and OOMs during actual inference (needed ~368MB more than was free) when
ANY other GPU app is also resident -- even a modest one (ace-step-ui's idle
API server alone was holding 2.66GB). The same call succeeded cleanly once
ace-step-ui was stopped. Treat DramaBox as needing the GPU close to
exclusive: check headroom (or proactively stop other idle GPU apps) before
calling this, the same way scripts/mrgpu_steam_prep.sh gates exclusive CUDA
work elsewhere in this project. Do not add DramaBox to a default "audio"
launch_chain that runs concurrently with ace_step/other GPU apps
without addressing this.
"""

from __future__ import annotations

from typing import Any


def generate_speech(
    base_url: str,
    prompt: str,
    audio_ref_path: str,
    *,
    cfg: float = 2.5,
    stg: float = 1.5,
    dur_mult: float = 1.1,
    gen_dur: float = 0.0,
    ref_dur: float = 10.0,
    seed: float = 42,
    denoise_ref: bool = True,
    max_chunk_s: float = 45.0,
    target_chunk_s: float = 37.0,
    crossfade_ms: float = 50.0,
) -> dict[str, Any]:
    """Generate expressive speech via a running DramaBox instance.

    base_url: e.g. "http://127.0.0.1:42051" (mrgpu's DramaBox port).
    prompt: screenplay-style direction, e.g. "[calm] Hello there.".
    audio_ref_path: local path to a short (~10s) reference voice clip --
    required, unlike PocketTTS's optional preset-voice path.

    Returns {ok, audio_path} on success, {ok: False, error} on failure
    (including CUDA OOM -- see the module docstring's VRAM warning).
    """
    try:
        from gradio_client import Client, handle_file
    except ImportError as exc:
        return {"ok": False, "error": f"gradio_client not installed: {exc}"}

    try:
        client = Client(base_url)
        audio_path = client.predict(
            prompt=prompt,
            audio_ref=handle_file(audio_ref_path),
            cfg=cfg,
            stg=stg,
            dur_mult=dur_mult,
            gen_dur=gen_dur,
            ref_dur=ref_dur,
            seed=seed,
            denoise_ref=denoise_ref,
            max_chunk_s=max_chunk_s,
            target_chunk_s=target_chunk_s,
            crossfade_ms=crossfade_ms,
            api_name="/on_generate",
        )
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

    return {"ok": True, "audio_path": audio_path}
