"""Director stack providers: list, probe, launch, pull, stop.

Reads config/director_stack_catalog.json (+ launch recipes) and runs local
process recipes. Pinokio GUI remains the fallback when a recipe is GUI-only.
"""

from __future__ import annotations

import json
import os
import signal
import socket
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = Path(os.environ.get("MOCK_TUA_CONFIG", ROOT / "config"))
AI_DATA = Path(os.environ.get("AI_DATA_ROOT", "/Volumes/ai-data"))
LAUNCH_DIR = Path(os.environ.get("MOCK_TUA_LAUNCH_DIR", ROOT / "work" / "launches"))
# Shared process registry (NFS-visible on lab hosts) so GUI/CLI agree on pid/port.
RUNTIME_DIR = Path(
    os.environ.get(
        "MOCK_TUA_RUNTIME_DIR",
        str(AI_DATA / "work" / "mok-tua" / "runtime"),
    )
)
# FramePack reserved port (avoid ACE-Step default 7865 collision).
FRAMEPACK_PORT = int(os.environ.get("FRAMEPACK_PORT", "7864"))
FRAMEPACK_BIND = os.environ.get("FRAMEPACK_BIND", "0.0.0.0")
FRAMEPACK_OPEN = os.environ.get(
    "FRAMEPACK_OPEN",
    f"http://gpu-host:{FRAMEPACK_PORT}/",
)


# Explicit launch recipes (shell-level). Prefer these over parsing pinokio start.js.
LAUNCH_RECIPES: dict[str, dict[str, Any]] = {
    "mok_tua": {
        "kind": "lab",
        "probe": [{"type": "http", "url": "http://127.0.0.1:8799/healthz"}],
        "open": "http://127.0.0.1:8799/v1/info",
        "cmd": None,  # already this process when API serves
        "note": "API is this service; CLI: scripts/run_host.sh",
    },
    "sm_comfy": {
        "kind": "stability_matrix",
        "probe": [
            {"type": "http", "url": "http://127.0.0.1:8188/system_stats"},
            {"type": "http", "url": "http://gpu-host:8188/system_stats", "label": "gpu-host"},
        ],
        "open": "http://127.0.0.1:8188",
        "cwd": str(AI_DATA / "stability-matrix/mac-Data/Packages/ComfyUI"),
        "cmd": [
            "python",
            "main.py",
            "--listen",
            "0.0.0.0",
            "--port",
            "8188",
        ],
        "env_extra": {"PYTORCH_MPS_HIGH_WATERMARK_RATIO": "0.0"},
        "prefer_script": str(Path.home() / "grokcode/scripts/comfy_launch_shared.sh"),
        "note": "Uses SM ComfyUI package; GPU-host via comfy_gpu_host_runtime.sh",
    },
    "directors_console": {
        "kind": "pinokio",
        "probe": [
            {"type": "tcp", "host": "127.0.0.1", "port": 9820},
            {"type": "tcp", "host": "127.0.0.1", "port": 9800},
            {"type": "tcp", "host": "127.0.0.1", "port": 5173},
        ],
        "open": "http://127.0.0.1:5173",
        "multi": [
            {
                "name": "orchestrator",
                "cwd_rel": "app/Orchestrator",
                "cmd": [
                    "bash",
                    "-lc",
                    "source venv/bin/activate 2>/dev/null; python -m uvicorn orchestrator.api:app --host 127.0.0.1 --port 9820",
                ],
            },
            {
                "name": "cpe",
                "cwd_rel": "app/CinemaPromptEngineering",
                "cmd": [
                    "bash",
                    "-lc",
                    "source venv/bin/activate 2>/dev/null; python -m uvicorn api.main:app --host 127.0.0.1 --port 9800",
                ],
            },
            {
                "name": "frontend",
                "cwd_rel": "app/CinemaPromptEngineering/frontend",
                "cmd": ["npm", "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173"],
            },
        ],
        "app_root": "pinokio/api/directorsconsole.pinokio.git",
        "note": "Or Pinokio → Director's Console → Start",
    },
    "wan2gp": {
        "kind": "pinokio",
        "probe": [{"type": "http_any", "ports": list(range(7860, 7880))}],
        "app_root": "pinokio/api/wan2gp.git",
        "cwd_rel": "app",
        "cmd": [
            "bash",
            "-lc",
            "source env/bin/activate 2>/dev/null || source .venv/bin/activate 2>/dev/null; "
            "python wgp.py --multiple-images --server-name 127.0.0.1 --server-port ${PORT:-7860}",
        ],
        "default_port": 7860,
        "note": "Gradio Wan2GP; or Pinokio Start",
    },
    "pinokio_comfy": {
        "kind": "pinokio",
        "probe": [{"type": "http", "url": "http://127.0.0.1:8188/system_stats"}],
        "app_root": "pinokio/api/comfyui.pinokio.git",
        "cwd_rel": "ComfyUI",
        "cmd": [
            "bash",
            "-lc",
            "source env/bin/activate 2>/dev/null; python main.py --listen 0.0.0.0 --port 8188",
        ],
        "open": "http://127.0.0.1:8188",
        "note": "Conflicts with SM Comfy on same port — pick one",
    },
    "ace_step": {
        "kind": "pinokio",
        "probe": [
            {"type": "http", "url": "http://127.0.0.1:7865/", "label": "ace_local"},
            {"type": "http", "url": "http://gpu-host:7865/", "label": "ace_lan"},
        ],
        "app_root": "pinokio/api/ace-step.pinokio.git",
        "cwd_rel": "app",
        "cmd": [
            "bash",
            "-lc",
            "uv run acestep --port ${PORT:-7865}",
        ],
        "default_port": 7865,
        "open": "http://gpu-host:7865/",
        "note": "Music gen Gradio/API; port 7865 reserved (FramePack uses 7864)",
    },
    "facefusion": {
        "kind": "pinokio",
        "probe": [{"type": "http_any", "ports": list(range(7860, 7900))}],
        "app_root": "pinokio/api/facefusion-pinokio.git",
        "cwd_rel": "facefusion",
        "cmd": [
            "bash",
            "-lc",
            "source ../.env/bin/activate 2>/dev/null; python facefusion.py run",
        ],
        "note": "FaceFusion UI; prefer Pinokio if conda env path differs",
    },
    "freemocap": {
        "kind": "pinokio",
        "probe": [{"type": "process", "match": "freemocap"}],
        "app_root": "pinokio/api/FreeMoCap.pinokio.git",
        "cwd_rel": "app",
        "cmd": ["bash", "-lc", "uv run freemocap"],
        "note": "Desktop mocap app",
    },
    "dreamtalk": {
        "kind": "pinokio",
        "probe": [{"type": "http_any", "ports": list(range(7860, 7900))}],
        "app_root": "pinokio/api/dreamtalk.git",
        "cwd_rel": ".",
        "cmd": ["bash", "-lc", "python app.py"],
        "note": "Talking head Gradio",
    },
    "tts_story": {
        "kind": "pinokio",
        "probe": [{"type": "http_any", "ports": list(range(7860, 7900))}],
        "app_root": "pinokio/api/TTS-Story.git",
        "cwd_rel": ".",
        "cmd": ["bash", "-lc", "python app.py"],
        "note": "Multi-voice story TTS",
    },
    "pocket_tts": {
        "kind": "pinokio",
        "probe": [{"type": "http", "url": "http://127.0.0.1:42050/", "label": "pocket_tts_local"}],
        "app_root": "pinokio/api/pocket-tts-pinokio.git",
        "cwd_rel": "app",
        "cmd": ["bash", "-lc", "PORT=${PORT:-42050} env/bin/python app.py"],
        "default_port": 42050,
        "note": "Lightweight CPU-capable voice-clone TTS (Kyutai PocketTTS); added 2026-09-02, real /generate call verified against a live instance",
    },
    "dramabox": {
        "kind": "pinokio",
        "probe": [{"type": "http", "url": "http://127.0.0.1:42051/", "label": "dramabox_local"}],
        "app_root": "pinokio/api/DramaBox-TTS-Pinokio.git",
        "cwd_rel": "app",
        "cmd": [
            "bash",
            "-lc",
            "GRADIO_SERVER_PORT=${PORT:-42051} MMGP_PROFILE=auto "
            "PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True env/bin/python ../launch_low_vram.py",
        ],
        "default_port": 42051,
        "note": "Expressive prompt-directed TTS w/ voice clone (Resemble AI, LTX-2.3-based); low-VRAM/MMGP path. Generation-verified 2026-09-02 (real wav produced), but ONLY with the GPU near-exclusive — OOMs alongside even idle ace-step-ui (~2.66GB). Do not launch concurrently with other GPU apps; see api/backends/dramabox.py docstring.",
    },

    # ---- kind: "hf_space" — public Hugging Face Spaces, earmarked 2026-09-02 -----
    # Cloud call targets, not local launches: launch_provider() short-circuits to
    # status="cloud_hosted" for this kind (nothing to spawn). Call via gradio_client
    # against "open" (owner/space form resolves fine) from a backends/*.py module,
    # same pattern as ace_step.py/pocket_tts.py/dramabox.py. Sourced from
    # config/hf_spaces_by_category.generated.json (scripts/sync_hf_spaces_by_category.py).
    # Real caveats, not local-GPU ones: most run on shared ZeroGPU (queue + cold-start
    # unpredictability, no SLA), a public Space can go offline/rate-limit/change its API
    # signature without notice, and nothing here should be a default/blocking dependency
    # for an unattended orchestration run — treat as overflow/comparison/gap-fill only.
    # Only hf_luxtts has a written+verified backends/*.py so far; the rest are
    # registered-but-uncalled candidates, verify before relying on them.
    "hf_luxtts": {
        "kind": "hf_space",
        "probe": [{"type": "http", "url": "https://huggingface.co/spaces/YatharthS/LuxTTS"}],
        "open": "YatharthS/LuxTTS",
        "note": "Hosted LuxTTS — 150x realtime voice-clone TTS. Would-be direct workaround "
        "for the local LuxTTS-Pinokio install, which is permanently blocked by an upstream "
        "tokenizers==0.10.3 Rust-toolchain deadlock (LinaCodec pins ancient transformers). "
        "Checked 2026-09-02: this specific Space is currently DOWN "
        "(gradio_client: 'RUNTIME_ERROR' — owner-side crash, not a caller-side problem). "
        "No verified backend module written — nothing to verify against. Re-check "
        "before relying on this; if it stays down, search for another LuxTTS-hosting Space.",
    },
    "hf_xtts": {
        "kind": "hf_space",
        "probe": [{"type": "http", "url": "https://huggingface.co/spaces/coqui/xtts"}],
        "open": "coqui/xtts",
        "note": "Coqui XTTS-v2 — real gap vs. local roster (no XTTS locally). 2766 likes, "
        "widely used. Not yet call-verified.",
    },
    "hf_openvoice": {
        "kind": "hf_space",
        "probe": [{"type": "http", "url": "https://huggingface.co/spaces/myshell-ai/OpenVoiceV2"}],
        "open": "myshell-ai/OpenVoiceV2",
        "note": "MyShell OpenVoice V2 — distinct voice-clone architecture, real gap vs. "
        "local roster. Checked 2026-09-02: Space is UP, but its legacy `fn_index`/"
        "websocket-queue API is incompatible with current gradio_client (2.6.0 raised "
        "'Unknown protocol: ws') — needs an older gradio_client pin or a direct HTTP "
        "call to work, not a simple Client().predict(). Not generation-verified.",
    },
    "hf_rvc": {
        "kind": "hf_space",
        "probe": [{"type": "http", "url": "https://huggingface.co/spaces/r3gm/rvc_zero"}],
        "open": "r3gm/rvc_zero",
        "note": "RVC (VITS-based) voice CONVERSION — a capability the local roster has "
        "none of at all (convert existing audio to a different voice, not text-to-speech). "
        "Not yet call-verified.",
    },
    "hf_musicgen": {
        "kind": "hf_space",
        "probe": [{"type": "http", "url": "https://huggingface.co/spaces/facebook/MusicGen"}],
        "open": "facebook/MusicGen",
        "note": "Meta MusicGen, official space, 5088 likes — distinct architecture from "
        "local ACE-Step. Checked 2026-09-02: Space is UP, modern named api_name "
        "('/predict_batched') API confirmed via view_api() — but a test call with "
        "melodies=None raised AppError('Internal Gradio error'); the 'required' Audio "
        "param likely can't actually be omitted despite what the signature implies. "
        "Retry with a real reference clip before relying on this.",
    },
    "hf_stable_audio": {
        "kind": "hf_space",
        "probe": [{"type": "http", "url": "https://huggingface.co/spaces/stabilityai/stable-audio-3"}],
        "open": "stabilityai/stable-audio-3",
        "note": "Stability AI's official Stable Audio 3 (music + SFX from text). "
        "Not yet call-verified.",
    },
    "hf_liveportrait": {
        "kind": "hf_space",
        "probe": [{"type": "http", "url": "https://huggingface.co/spaces/KlingTeam/LivePortrait"}],
        "open": "KlingTeam/LivePortrait",
        "note": "LivePortrait — applies a driving video's motion to a portrait. 3785 "
        "likes, distinct from local DreamTalk. Not yet call-verified.",
    },
    "hf_sadtalker": {
        "kind": "hf_space",
        "probe": [{"type": "http", "url": "https://huggingface.co/spaces/vinthony/SadTalker"}],
        "open": "vinthony/SadTalker",
        "note": "SadTalker — talking-face video from a single image + audio, distinct "
        "architecture from local DreamTalk. Not yet call-verified.",
    },
    "hf_magicanimate": {
        "kind": "hf_space",
        "probe": [{"type": "http", "url": "https://huggingface.co/spaces/zcxu-eric/magicanimate"}],
        "open": "zcxu-eric/magicanimate",
        "note": "MagicAnimate — animated video from images + a motion sequence. "
        "Not yet call-verified.",
    },
    "hf_latentsync": {
        "kind": "hf_space",
        "probe": [{"type": "http", "url": "https://huggingface.co/spaces/fffiloni/LatentSync"}],
        "open": "fffiloni/LatentSync",
        "note": "LatentSync — audio-conditioned lipsync via latent diffusion; "
        "complements local FaceFusion's lipsync mode rather than duplicating it. "
        "Not yet call-verified.",
    },
    "hf_minimax_h3": {
        "kind": "hf_space",
        "probe": [{"type": "http", "url": "https://huggingface.co/spaces/MiniMaxAI/MiniMax-H3-Turbo-Lora"}],
        "open": "MiniMaxAI/MiniMax-H3-Turbo-Lora",
        "note": "Official MiniMax H3 space (video + synchronized soundtrack) — same "
        "family of tech as Maestro's local H3 Sol Engine; useful as an official-source "
        "comparison point. Not yet call-verified.",
    },
    # ---- end kind: "hf_space" -------------------------------------------------

    "framepack_studio": {
        "kind": "stability_matrix",
        "probe": [
            {
                "type": "http",
                "url": f"http://127.0.0.1:{FRAMEPACK_PORT}/",
                "label": "framepack_local",
            },
            {
                "type": "http",
                "url": f"http://gpu-host:{FRAMEPACK_PORT}/",
                "label": "framepack_lan",
            },
            {
                "type": "path",
                "path": str(AI_DATA / "stability-matrix/Data/Packages/FramePack Studio"),
                "label": "linux_sm_pkg",
                "live": False,
            },
            {
                "type": "path",
                "path": str(AI_DATA / "stability-matrix/mac-Data/Packages/FramePack Studio"),
                "label": "mac_sm_pkg",
                "live": False,
            },
        ],
        "open": FRAMEPACK_OPEN,
        "prefer_script": str(ROOT / "scripts" / "run_framepack_shared_models.sh"),
        # No forced --offline: launcher auto-offline when shared Hunyuan hub present.
        # First seed: FRAMEPACK_ALLOW_DOWNLOAD=1 (writes into shared hf_hub only).
        "prefer_script_args": [
            "--server",
            FRAMEPACK_BIND,
            "--port",
            str(FRAMEPACK_PORT),
        ],
        "default_port": FRAMEPACK_PORT,
        "cmd": None,
        "note": (
            "Shared-models launcher (hf_hub symlink + host venv). "
            "LAN Gradio at open URL. SM GUI after --install-deps. Port 7864. "
            "First hub seed: FRAMEPACK_ALLOW_DOWNLOAD=1 (shared hub only)."
        ),
    },
}


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_catalog() -> dict[str, Any]:
    path = CONFIG_DIR / "director_stack_catalog.json"
    if not path.is_file():
        return {"apps": [], "error": f"missing {path}"}
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_app_path(app: dict[str, Any]) -> Path | None:
    raw = str(app.get("path") or "")
    if raw.startswith("~/"):
        p = Path.home() / raw[2:]
        return p if p.exists() else Path(raw.replace("~", str(Path.home())))
    if raw.startswith("/"):
        return Path(raw)
    # relative to ai-data
    p = AI_DATA / raw
    if p.exists():
        glob_pat = app.get("path_glob")
        if glob_pat and p.is_dir():
            hits = sorted(p.glob(str(glob_pat)))
            if hits:
                return hits[0]
        return p
    # pinokio path style in catalog
    if raw.startswith("pinokio/"):
        return AI_DATA / raw
    if raw.startswith("stability-matrix/"):
        return AI_DATA / raw
    if raw.startswith("models/"):
        return AI_DATA / raw
    return p


def _tcp_open(host: str, port: int, timeout: float = 0.4) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _http_ok(url: str, timeout: float = 2.0) -> dict[str, Any]:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return {"ok": 200 <= resp.status < 400, "status": resp.status, "url": url}
    except Exception as exc:
        return {"ok": False, "url": url, "error": str(exc)[:160]}


def _probe_one(spec: dict[str, Any]) -> dict[str, Any]:
    t = spec.get("type")
    # live=False probes report install presence only (do not mark provider live).
    contributes_live = bool(spec.get("live", True))
    if t == "http":
        r = _http_ok(str(spec["url"]))
        r["label"] = spec.get("label") or spec["url"]
        r["contributes_live"] = contributes_live
        return r
    if t == "tcp":
        host = str(spec.get("host") or "127.0.0.1")
        port = int(spec["port"])
        ok = _tcp_open(host, port)
        return {
            "ok": ok,
            "label": f"{host}:{port}",
            "type": "tcp",
            "contributes_live": contributes_live,
        }
    if t == "http_any":
        ports = spec.get("ports") or []
        for port in ports:
            if _tcp_open("127.0.0.1", int(port)):
                return {
                    "ok": True,
                    "label": f"127.0.0.1:{port}",
                    "port": int(port),
                    "contributes_live": contributes_live,
                }
        return {
            "ok": False,
            "label": f"ports {ports[0]}-{ports[-1]}" if ports else "none",
            "contributes_live": contributes_live,
        }
    if t == "path":
        p = Path(str(spec["path"]))
        return {
            "ok": p.exists(),
            "label": str(p),
            "type": "path",
            "contributes_live": contributes_live,
        }
    if t == "process":
        match = str(spec.get("match") or "")
        try:
            out = subprocess.check_output(["pgrep", "-fl", match], text=True, stderr=subprocess.DEVNULL)
            return {
                "ok": bool(out.strip()),
                "label": match,
                "sample": out.strip()[:120],
                "contributes_live": contributes_live,
            }
        except Exception:
            return {"ok": False, "label": match, "contributes_live": contributes_live}
    return {"ok": False, "error": f"unknown_probe:{t}", "contributes_live": False}


def app_by_id(app_id: str) -> dict[str, Any] | None:
    cat = load_catalog()
    for a in cat.get("apps") or []:
        if a.get("id") == app_id:
            return a
    return None


def list_providers(
    *,
    tier: str | None = None,
    role: str | None = None,
    bleeding_only: bool = False,
    probe: bool = True,
) -> dict[str, Any]:
    cat = load_catalog()
    rows = []
    for app in cat.get("apps") or []:
        if tier and app.get("tier") != tier:
            continue
        if role and role not in (app.get("roles") or []):
            continue
        if bleeding_only and not app.get("bleeding_edge"):
            continue
        aid = str(app.get("id"))
        recipe = LAUNCH_RECIPES.get(aid, {})
        path = resolve_app_path(app)
        path_ok = bool(path and path.exists())
        probes = []
        live = False
        if probe and recipe.get("probe"):
            for spec in recipe["probe"]:
                pr = _probe_one(spec)
                probes.append(pr)
                if pr.get("ok") and pr.get("contributes_live", True):
                    live = True
        elif probe and app.get("ports"):
            for name, port in (app.get("ports") or {}).items():
                ok = _tcp_open("127.0.0.1", int(port))
                probes.append({"ok": ok, "label": f"{name}:{port}", "contributes_live": True})
                live = live or ok
        state = load_launch_state(aid)
        runtime = load_runtime_state(aid)
        rows.append(
            {
                "id": aid,
                "name": app.get("name"),
                "tier": app.get("tier"),
                "kind": app.get("kind"),
                "roles": app.get("roles"),
                "priority": app.get("priority"),
                "bleeding_edge": bool(app.get("bleeding_edge")),
                "path": str(path) if path else app.get("path"),
                "path_ok": path_ok,
                "live": live,
                "probes": probes,
                "launchable": bool(recipe) and not recipe.get("gui_only"),
                "gui_only": bool(recipe.get("gui_only")),
                "open": recipe.get("open") or (runtime or {}).get("open"),
                "note": recipe.get("note") or app.get("mok_tua_hook"),
                "launched_pid": (state or runtime or {}).get("pid"),
                "launched_at": (state or runtime or {}).get("started_at"),
                "runtime_owner": (runtime or {}).get("owner") or ((state or {}).get("owner")),
                "runtime_port": (runtime or {}).get("port") or recipe.get("default_port"),
            }
        )
    rows.sort(key=lambda r: (r.get("priority") if r.get("priority") is not None else 99, r.get("id") or ""))
    live_n = sum(1 for r in rows if r.get("live"))
    return {
        "ok": True,
        "count": len(rows),
        "live": live_n,
        "ai_data": str(AI_DATA),
        "providers": rows,
        "ts": _utc(),
    }


def doctor() -> dict[str, Any]:
    """Full stack health: providers + model inventory + orchestration defaults."""
    prov = list_providers(probe=True)
    try:
        from stage_models import inventory_status

        inv = inventory_status()
    except Exception as exc:
        inv = {"ok": False, "error": str(exc)}
    orch_path = CONFIG_DIR / "orchestration.json"
    orch = {}
    if orch_path.is_file():
        orch = json.loads(orch_path.read_text(encoding="utf-8")).get("defaults") or {}
    critical = ["mok_tua", "sm_comfy", "directors_console", "wan2gp"]
    crit_status = {c: next((p for p in prov["providers"] if p["id"] == c), None) for c in critical}
    score = 0
    max_score = 0
    for p in prov["providers"]:
        max_score += 2
        if p.get("path_ok"):
            score += 1
        if p.get("live"):
            score += 1
    return {
        "ok": True,
        "score": score,
        "max_score": max_score,
        "grade": "S" if score >= max_score * 0.75 else "A" if score >= max_score * 0.5 else "B",
        "defaults": orch,
        "critical": {
            k: {
                "live": (v or {}).get("live"),
                "path_ok": (v or {}).get("path_ok"),
                "open": (v or {}).get("open"),
            }
            for k, v in crit_status.items()
        },
        "providers_live": prov["live"],
        "providers_count": prov["count"],
        "model_inventory": {
            "ok": inv.get("ok"),
            "present": inv.get("present"),
            "failed": inv.get("failed"),
            "count": inv.get("count"),
        },
        "ts": _utc(),
    }


def load_launch_state(app_id: str) -> dict[str, Any] | None:
    path = LAUNCH_DIR / f"{app_id}.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def load_runtime_state(app_id: str) -> dict[str, Any] | None:
    """Shared NFS runtime registry (dual lifecycle: mok-tua + SM/external)."""
    path = RUNTIME_DIR / f"{app_id}.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def save_runtime_state(app_id: str, state: dict[str, Any]) -> None:
    """Best-effort shared registry write (NFS may be missing on pure desk dev)."""
    try:
        RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema": "mok_tua_runtime.v1",
            "id": app_id,
            **state,
            "updated_at": _utc(),
        }
        (RUNTIME_DIR / f"{app_id}.json").write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )
    except OSError:
        pass


def clear_runtime_state(app_id: str) -> None:
    path = RUNTIME_DIR / f"{app_id}.json"
    try:
        if path.is_file():
            path.unlink()
    except OSError:
        pass


def save_launch_state(app_id: str, state: dict[str, Any]) -> None:
    LAUNCH_DIR.mkdir(parents=True, exist_ok=True)
    if "owner" not in state:
        state = {**state, "owner": "mok_tua"}
    (LAUNCH_DIR / f"{app_id}.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    # Mirror to shared registry for SM/browser operators on LAN.
    save_runtime_state(app_id, state)


def clear_launch_state(app_id: str) -> None:
    path = LAUNCH_DIR / f"{app_id}.json"
    if path.is_file():
        path.unlink()
    clear_runtime_state(app_id)


def _spawn(cmd: list[str], *, cwd: Path, env: dict[str, str] | None, log_path: Path) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    log_f = open(log_path, "a", encoding="utf-8")
    log_f.write(f"\n--- spawn {_utc()} cwd={cwd} cmd={cmd}\n")
    log_f.flush()
    proc = subprocess.Popen(
        cmd,
        cwd=str(cwd),
        env=full_env,
        stdout=log_f,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    return int(proc.pid)


def launch_provider(
    app_id: str,
    *,
    dry_run: bool = True,
    force: bool = False,
    port: int | None = None,
) -> dict[str, Any]:
    app = app_by_id(app_id)
    recipe = LAUNCH_RECIPES.get(app_id)
    if not recipe:
        return {
            "ok": False,
            "error": "no_recipe",
            "id": app_id,
            "hint": "Use Pinokio/SM GUI or add LAUNCH_RECIPES entry",
            "catalog": app,
        }
    if recipe.get("gui_only"):
        return {
            "ok": True,
            "status": "gui_only",
            "id": app_id,
            "note": recipe.get("note"),
            "open": recipe.get("open"),
        }

    if recipe.get("kind") == "hf_space":
        return {
            "ok": True,
            "status": "cloud_hosted",
            "id": app_id,
            "note": recipe.get("note") or "Public HF Space — nothing to launch locally; call via its backends/* module.",
            "open": recipe.get("open"),
        }

    # already live?
    if not force:
        status = list_providers(probe=True)
        row = next((p for p in status["providers"] if p["id"] == app_id), None)
        if row and row.get("live"):
            return {
                "ok": True,
                "status": "already_live",
                "id": app_id,
                "open": row.get("open") or recipe.get("open"),
                "probes": row.get("probes"),
            }

    if app_id == "mok_tua":
        return {
            "ok": True,
            "status": "self",
            "id": app_id,
            "open": recipe.get("open"),
            "note": "mok-tua API is the control plane",
        }

    app_root = None
    if recipe.get("app_root"):
        app_root = AI_DATA / str(recipe["app_root"])
    elif app:
        app_root = resolve_app_path(app)

    if recipe.get("prefer_script"):
        script = Path(str(recipe["prefer_script"]))
        use_port = port or recipe.get("default_port")
        script_args = [str(a) for a in (recipe.get("prefer_script_args") or [])]
        if use_port is not None:
            # Allow --port N override when caller passes port=
            if "--port" in script_args:
                i = script_args.index("--port")
                if i + 1 < len(script_args):
                    script_args[i + 1] = str(use_port)
            env_port = {"PORT": str(use_port), "FRAMEPACK_PORT": str(use_port)}
        else:
            env_port = None
        open_url = recipe.get("open")
        if use_port is not None and app_id == "framepack_studio":
            open_url = f"http://gpu-host:{use_port}/"
        cmd = ["bash", str(script), *script_args]
        if dry_run:
            return {
                "ok": True,
                "status": "dry_run",
                "id": app_id,
                "cmd": cmd,
                "script_exists": script.is_file(),
                "open": open_url,
                "note": recipe.get("note"),
            }
        if not script.is_file():
            return {
                "ok": False,
                "error": "prefer_script_missing",
                "path": str(script),
                "hint": "Run from a checkout that has scripts/run_framepack_shared_models.sh",
            }
        log = LAUNCH_DIR / f"{app_id}.log"
        pid = _spawn(cmd, cwd=script.parent, env=env_port, log_path=log)
        state = {
            "id": app_id,
            "pid": pid,
            "started_at": _utc(),
            "cmd": cmd,
            "log": str(log),
            "owner": "mok_tua",
            "bind": FRAMEPACK_BIND if app_id == "framepack_studio" else None,
            "port": int(use_port) if use_port is not None else None,
            "open": open_url,
            "host_role": "gpu-host",
        }
        save_launch_state(app_id, state)
        return {"ok": True, "status": "spawned", **state, "open": open_url}

    # multi-process (Director's Console)
    if recipe.get("multi"):
        if dry_run:
            return {
                "ok": True,
                "status": "dry_run",
                "id": app_id,
                "app_root": str(app_root),
                "steps": recipe["multi"],
                "open": recipe.get("open"),
            }
        if not app_root or not app_root.is_dir():
            return {"ok": False, "error": "app_root_missing", "path": str(app_root)}
        pids = []
        for step in recipe["multi"]:
            cwd = app_root / str(step.get("cwd_rel") or ".")
            if not cwd.is_dir():
                return {"ok": False, "error": "cwd_missing", "cwd": str(cwd), "step": step.get("name")}
            log = LAUNCH_DIR / f"{app_id}_{step.get('name')}.log"
            pid = _spawn(list(step["cmd"]), cwd=cwd, env=None, log_path=log)
            pids.append({"name": step.get("name"), "pid": pid, "log": str(log)})
            time.sleep(0.5)
        # brief readiness wait for multi-service stacks (CPE/orch bind slowly)
        time.sleep(2.5)
        probes_after = []
        for spec in recipe.get("probe") or []:
            probes_after.append(_probe_one(spec))
        state = {
            "id": app_id,
            "pids": pids,
            "started_at": _utc(),
            "open": recipe.get("open"),
            "probes": probes_after,
        }
        save_launch_state(app_id, state)
        return {"ok": True, "status": "spawned_multi", **state}

    cmd = recipe.get("cmd")
    if not cmd:
        return {"ok": False, "error": "no_cmd", "note": recipe.get("note"), "id": app_id}

    cwd = Path(str(recipe.get("cwd") or app_root or ROOT))
    if recipe.get("cwd_rel") and app_root:
        cwd = app_root / str(recipe["cwd_rel"])
    if not cwd.is_dir() and not dry_run:
        return {"ok": False, "error": "cwd_missing", "cwd": str(cwd)}

    env = dict(recipe.get("env_extra") or {})
    use_port = port or recipe.get("default_port")
    if use_port:
        env["PORT"] = str(use_port)
        # expand ${PORT} in bash -lc strings
        cmd = [c.replace("${PORT:-7860}", str(use_port)).replace("${PORT:-7865}", str(use_port)).replace("${PORT}", str(use_port)) for c in cmd]

    if dry_run:
        return {
            "ok": True,
            "status": "dry_run",
            "id": app_id,
            "cwd": str(cwd),
            "cmd": cmd,
            "env": env,
            "open": recipe.get("open"),
            "note": recipe.get("note"),
        }

    log = LAUNCH_DIR / f"{app_id}.log"
    pid = _spawn(list(cmd), cwd=cwd, env=env or None, log_path=log)
    state = {
        "id": app_id,
        "pid": pid,
        "started_at": _utc(),
        "cmd": cmd,
        "cwd": str(cwd),
        "log": str(log),
        "open": recipe.get("open"),
    }
    save_launch_state(app_id, state)
    return {"ok": True, "status": "spawned", **state}


def stop_provider(app_id: str) -> dict[str, Any]:
    state = load_launch_state(app_id) or load_runtime_state(app_id)
    if not state:
        return {
            "ok": False,
            "error": "no_launch_state",
            "id": app_id,
            "hint": "Only stops processes recorded in work/launches or shared runtime registry",
        }
    owner = str(state.get("owner") or "mok_tua")
    # Allow mok_tua to stop what it spawned; external/sm need explicit override.
    if owner not in ("mok_tua", "sm_via_wrapper", "external_registered") and not state.get("force_stop"):
        return {
            "ok": False,
            "error": "foreign_owner",
            "id": app_id,
            "owner": owner,
            "hint": "Set force_stop on runtime record or stop from the owning surface",
        }
    killed = []
    pids = []
    if state.get("pid"):
        pids.append(int(state["pid"]))
    for item in state.get("pids") or []:
        if item.get("pid"):
            pids.append(int(item["pid"]))
    for pid in pids:
        try:
            os.killpg(pid, signal.SIGTERM)
            killed.append(pid)
        except ProcessLookupError:
            try:
                os.kill(pid, signal.SIGTERM)
                killed.append(pid)
            except ProcessLookupError:
                pass
        except PermissionError as exc:
            return {"ok": False, "error": str(exc), "pid": pid}
    clear_launch_state(app_id)
    return {"ok": True, "status": "stopped", "id": app_id, "killed": killed, "owner": owner}


def _git_root_for_pull(path: Path, *, prefer_nested: bool = True) -> Path | None:
    """Prefer nested app/.git for pinokio wrappers when outer tree is dirty."""
    outer = path / ".git"
    nested = path / "app" / ".git"
    if prefer_nested and nested.is_dir():
        return path / "app"
    if outer.is_dir() or outer.is_file():
        return path
    if nested.is_dir():
        return path / "app"
    # facefusion-style: facefusion/ subdir
    for sub in ("facefusion", "ComfyUI", "app"):
        if (path / sub / ".git").exists():
            return path / sub
    return None


def _git_sha_short(repo: Path) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--short=12", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if proc.returncode == 0:
            return (proc.stdout or "").strip()
    except Exception:
        return None
    return None


def _git_pull_preflight(repo: Path) -> dict[str, Any]:
    try:
        porc = subprocess.run(
            ["git", "-C", str(repo), "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        lines = [ln for ln in (porc.stdout or "").splitlines() if ln.strip()]
        unmerged = [ln for ln in lines if ln[:2] in ("UU", "AA", "DD", "AU", "UA", "DU", "UD")]
        dirty = len(lines)
        wrapper_only = dirty > 0 and all(
            any(x in ln for x in ("install.js", "reset.js", "start.js", "pinokio.js", "icon.png", "README.md", ".github/"))
            for ln in lines
        )
        try:
            behind_proc = subprocess.run(
                ["git", "-C", str(repo), "rev-list", "--count", "HEAD..@{u}"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            behind = int((behind_proc.stdout or "0").strip()) if behind_proc.returncode == 0 else None
        except Exception:
            behind = None
        return {
            "dirty": dirty,
            "unmerged": unmerged,
            "wrapper_only_dirty": wrapper_only,
            "behind": behind,
            "sha_before": _git_sha_short(repo),
        }
    except Exception as exc:
        return {"error": str(exc), "dirty": -1, "unmerged": [], "wrapper_only_dirty": False}


def pull_provider(
    app_id: str,
    *,
    dry_run: bool = True,
    prefer_nested: bool = True,
    force: bool = False,
) -> dict[str, Any]:
    """git pull --ff-only with dirty/conflict safety. Never hard-resets."""
    app = app_by_id(app_id)
    if not app:
        return {"ok": False, "error": "unknown_app", "id": app_id}
    if app.get("kind") == "models":
        return {"ok": True, "status": "skip_models", "id": app_id, "note": "models pool — use stage CLI"}
    if app.get("kind") == "lab" and app_id == "mok_tua":
        return {"ok": True, "status": "skip_self", "id": app_id, "note": "mok-tua repo managed separately"}
    path = resolve_app_path(app)
    if not path or not path.is_dir():
        return {"ok": False, "error": "path_missing", "path": str(path), "id": app_id}

    repo = _git_root_for_pull(path, prefer_nested=prefer_nested)
    # If outer has git and nested preferred failed dirty policy: try nested first then outer
    if repo is None:
        return {
            "ok": False,
            "error": "not_a_git_repo",
            "path": str(path),
            "id": app_id,
            "note": "Use Pinokio Update",
        }

    pre = _git_pull_preflight(repo)
    if pre.get("unmerged") and not force:
        return {
            "ok": False,
            "status": "skipped_conflict",
            "id": app_id,
            "path": str(repo),
            "preflight": pre,
            "note": "Resolve UU conflicts (e.g. install.js) before pull",
        }
    if pre.get("dirty", 0) > 0 and not force:
        # try nested if we used outer and nested exists
        nested = path / "app"
        if prefer_nested and repo == path and (nested / ".git").exists():
            repo = nested
            pre = _git_pull_preflight(repo)
            if pre.get("unmerged") and not force:
                return {
                    "ok": False,
                    "status": "skipped_conflict",
                    "id": app_id,
                    "path": str(repo),
                    "preflight": pre,
                }
        if pre.get("dirty", 0) > 0 and not force:
            # very dirty (e.g. TTS-Story) → skip
            if pre.get("dirty", 0) > 40:
                return {
                    "ok": True,
                    "status": "skipped_very_dirty",
                    "id": app_id,
                    "path": str(repo),
                    "preflight": pre,
                    "note": "Too dirty for safe ff-only pull",
                }
            if not pre.get("wrapper_only_dirty"):
                return {
                    "ok": True,
                    "status": "skipped_dirty",
                    "id": app_id,
                    "path": str(repo),
                    "preflight": pre,
                    "note": "Working tree dirty; use --force only if intentional",
                }
            # wrapper-only dirty on outer: if we are still on outer, skip
            if repo == path:
                return {
                    "ok": True,
                    "status": "skipped_wrapper_dirty",
                    "id": app_id,
                    "path": str(repo),
                    "preflight": pre,
                    "note": "Pinokio wrapper dirty; nested clean pull preferred when available",
                }

    cmd = ["git", "-C", str(repo), "pull", "--ff-only"]
    if dry_run:
        return {
            "ok": True,
            "status": "dry_run",
            "id": app_id,
            "cmd": cmd,
            "path": str(repo),
            "preflight": pre,
        }
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "status": "timeout",
            "id": app_id,
            "path": str(repo),
            "sha_before": pre.get("sha_before"),
        }
    sha_after = _git_sha_short(repo)
    return {
        "ok": proc.returncode == 0,
        "status": "pulled" if proc.returncode == 0 else "pull_failed",
        "id": app_id,
        "path": str(repo),
        "sha_before": pre.get("sha_before"),
        "sha_after": sha_after,
        "changed": pre.get("sha_before") != sha_after,
        "stdout": (proc.stdout or "")[-800:],
        "stderr": (proc.stderr or "")[-400:],
        "preflight": pre,
    }


def pull_tier(
    tier: str | None = None,
    *,
    bleeding_only: bool = False,
    dry_run: bool = True,
    monitor: str | None = None,
    force: bool = False,
    priority_max: int | None = 2,
) -> dict[str, Any]:
    """Pull all apps in a tier (or all bleeding_edge) with progress + optional gpu-host monitor."""
    from host_monitor import format_sample_line, progress_bar, HostMonitor

    cat = load_catalog()
    apps = []
    for app in cat.get("apps") or []:
        if tier and app.get("tier") != tier:
            continue
        if bleeding_only and not app.get("bleeding_edge"):
            continue
        if app.get("kind") in ("models",):
            continue
        if app.get("id") == "mok_tua":
            continue
        pri = app.get("priority")
        if priority_max is not None and pri is not None and int(pri) > priority_max:
            continue
        apps.append(app)
    apps.sort(key=lambda a: (a.get("priority") if a.get("priority") is not None else 99, a.get("id") or ""))

    mon: HostMonitor | None = None
    if monitor and not dry_run:
        mon = HostMonitor(node=monitor)

        def _cb(sample: dict[str, Any]) -> None:
            print(f"\r{format_sample_line(sample, pull_label='gpu-host'):<110}", end="", flush=True)

        mon.on_sample = _cb
        mon.start()

    results = []
    total = len(apps)
    try:
        for i, app in enumerate(apps, 1):
            aid = str(app.get("id"))
            print(f"{progress_bar(i - 1, total)} pull {aid}…")
            r = pull_provider(aid, dry_run=dry_run, force=force)
            results.append(r)
            st = r.get("status") or r.get("error")
            print(f"{progress_bar(i, total)} {aid}: {st}")
    finally:
        mon_summary = mon.stop() if mon else None
        if mon:
            print()

    ok_n = sum(1 for r in results if r.get("ok"))
    pulled = sum(1 for r in results if r.get("status") == "pulled")
    skipped = sum(1 for r in results if str(r.get("status") or "").startswith("skipped"))
    return {
        "ok": ok_n == total,
        "tier": tier,
        "bleeding_only": bleeding_only,
        "dry_run": dry_run,
        "total": total,
        "ok_count": ok_n,
        "pulled": pulled,
        "skipped": skipped,
        "results": results,
        "monitor": mon_summary,
        "ts": _utc(),
    }


def launch_chain(
    chain: str = "demo",
    *,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Named stacks for one-shot director bring-up."""
    chains = {
        "demo": ["mok_tua", "sm_comfy", "directors_console"],
        "video": ["sm_comfy", "wan2gp"],
        "face": ["facefusion", "dreamtalk"],
        # dramabox deliberately excluded -- confirmed 2026-09-02 it needs the
        # GPU close to exclusive (OOMs alongside even idle ace-step-ui,
        # ~2.66GB); launch it individually, never as part of this chain.
        "audio": ["ace_step", "tts_story", "pocket_tts"],
        "body": ["freemocap"],
        "full": [
            "mok_tua",
            "sm_comfy",
            "directors_console",
            "wan2gp",
            "ace_step",
            "tts_story",
            "facefusion",
        ],
    }
    ids = chains.get(chain)
    if not ids:
        return {"ok": False, "error": "unknown_chain", "chains": list(chains.keys())}
    results = []
    for aid in ids:
        results.append(launch_provider(aid, dry_run=dry_run))
    return {
        "ok": all(r.get("ok") for r in results),
        "chain": chain,
        "dry_run": dry_run,
        "results": results,
        "chains": list(chains.keys()),
    }


def format_table(providers: list[dict[str, Any]]) -> str:
    """Plain-text status board for CLI (no extra deps)."""
    lines = []
    lines.append(f"{'ID':<22} {'LIVE':<5} {'PATH':<5} {'TIER':<18} {'NAME'}")
    lines.append("-" * 78)
    for p in providers:
        live = "YES" if p.get("live") else "no"
        path = "ok" if p.get("path_ok") else "MISS"
        bleed = "*" if p.get("bleeding_edge") else " "
        lines.append(
            f"{bleed}{p.get('id') or '':<21} {live:<5} {path:<5} {str(p.get('tier') or ''):<18} {p.get('name') or ''}"
        )
    lines.append("")
    lines.append("* = bleeding_edge   LIVE=port/http probe   PATH=on-disk under ai-data")
    return "\n".join(lines)
