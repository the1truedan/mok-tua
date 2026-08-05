"""T0–T4 version lock + loading profiles for scale/repro bring-up."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = Path(os.environ.get("MOCK_TUA_CONFIG", ROOT / "config"))
LOCK_PATH = CONFIG_DIR / "tier_lock_T0-T4.json"
AI_DATA = Path(os.environ.get("AI_DATA_ROOT", "/Volumes/ai-data"))
WORK = Path(os.environ.get("WORK_FALLBACK", ROOT / "work"))

DEFAULT_LOADING = {
    "demo": ["mok_tua", "sm_comfy", "directors_console"],
    "full_local": [
        "mok_tua",
        "sm_comfy",
        "directors_console",
        "wan2gp",
        "ace_step",
        "tts_story",
        "facefusion",
    ],
    "video_mrgpu": ["sm_comfy", "wan2gp"],
    "face": ["facefusion", "dreamtalk"],
    "audio": ["ace_step", "tts_story"],
    "body": ["freemocap"],
}

MOK_TUA_VERSION = "0.3.0"


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _git_sha(path: Path) -> str | None:
    git_dir = path / ".git"
    repo = path
    if not git_dir.is_dir() and (path / "app" / ".git").is_dir():
        repo = path / "app"
    if not (repo / ".git").exists() and not git_dir.is_dir():
        # bare path may itself be git
        try:
            proc = subprocess.run(
                ["git", "-C", str(path), "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if proc.returncode == 0:
                return proc.stdout.strip()[:12]
        except Exception:
            return None
        return None
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if proc.returncode == 0:
            return proc.stdout.strip()[:12]
    except Exception:
        return None
    return None


def _git_dirty(path: Path) -> bool:
    repo = path
    if not (path / ".git").is_dir() and (path / "app" / ".git").is_dir():
        repo = path / "app"
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return bool((proc.stdout or "").strip())
    except Exception:
        return False


def write_lock(
    *,
    smoke_ref: str | None = None,
    host_profiles: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from providers import load_catalog, resolve_app_path

    cat = load_catalog()
    tiers_map: dict[str, list[dict[str, Any]]] = {
        "T0_orchestrators": [],
        "T1_vid_gen": [],
        "T2_audio_music": [],
        "T3_face_body": [],
        "T4_comfy_graphs": [],
    }
    for app in cat.get("apps") or []:
        tier = str(app.get("tier") or "")
        if tier not in tiers_map:
            continue
        path = resolve_app_path(app)
        entry = {
            "id": app.get("id"),
            "name": app.get("name"),
            "path": str(path) if path else app.get("path"),
            "path_ok": bool(path and path.exists()),
            "sha": _git_sha(path) if path and path.exists() else None,
            "dirty": _git_dirty(path) if path and path.exists() else None,
            "priority": app.get("priority"),
            "bleeding_edge": bool(app.get("bleeding_edge")),
            "ports": app.get("ports"),
            "status": app.get("status"),
        }
        tiers_map[tier].append(entry)

    # T4 pins
    wf_root = AI_DATA / "stability-matrix/mac-Data/Workflows"
    pin_rows = []
    for g in cat.get("sm_workflow_pins_bleed") or []:
        hits = list(wf_root.glob(g)) if wf_root.is_dir() else []
        pin_rows.append({
            "glob": g,
            "status": "present" if hits else "missing",
            "sample": hits[0].name if hits else None,
        })
    tiers_map["T4_comfy_graphs"] = pin_rows

    lock = {
        "version": 1,
        "locked_at": _utc(),
        "mok_tua_version": MOK_TUA_VERSION,
        "host_profiles": host_profiles or {
            "m4rv": {"role": "stills", "comfy": COMFY_HINT_LOCAL()},
            "mrgpu": {
                "role": "video",
                "host": os.environ.get("MRGPU_HOST", "gpu-host"),
                "comfy_url": os.environ.get("COMFY_MRGPU_URL", "http://gpu-host:8188"),
                "gpu": "RTX 4060 Ti 16G",
            },
        },
        "tiers": tiers_map,
        "loading": DEFAULT_LOADING,
        "smoke_ref": smoke_ref,
        "policy": {
            "dirty_pinokio_wrapper": "prefer_nested_app_git",
            "conflict": "skip_until_repair",
            "qqq_smoke": "dry_run_only",
        },
    }
    LOCK_PATH.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "path": str(LOCK_PATH), "lock": lock}


def COMFY_HINT_LOCAL() -> str:
    return os.environ.get("COMFY_LOCAL_URL", "http://127.0.0.1:8188")


def load_lock() -> dict[str, Any]:
    if not LOCK_PATH.is_file():
        return {"ok": False, "error": "no_lock", "path": str(LOCK_PATH)}
    data = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    return {"ok": True, "path": str(LOCK_PATH), "lock": data}


def loading_profiles() -> dict[str, list[str]]:
    loaded = load_lock()
    if loaded.get("ok"):
        return dict((loaded["lock"] or {}).get("loading") or DEFAULT_LOADING)
    return dict(DEFAULT_LOADING)


def load_profile(
    profile: str,
    *,
    dry_run: bool = True,
    monitor: str | None = None,
) -> dict[str, Any]:
    """Launch providers in lock loading order with progress bars."""
    from host_monitor import progress_bar, run_with_monitor
    from providers import launch_provider

    profiles = loading_profiles()
    ids = profiles.get(profile)
    if not ids:
        return {"ok": False, "error": "unknown_profile", "profiles": list(profiles.keys())}

    results = []
    total = len(ids)

    def _run_all() -> list[dict[str, Any]]:
        out = []
        for i, aid in enumerate(ids, 1):
            # strip @host annotation
            pure = aid.split("@")[0]
            print(f"{progress_bar(i - 1, total)} loading {pure}…")
            r = launch_provider(pure, dry_run=dry_run)
            out.append({"id": pure, "result": r})
            print(f"{progress_bar(i, total)} {pure}: {r.get('status') or r.get('error')}")
        return out

    if monitor:
        results, mon = run_with_monitor(_run_all, node=monitor, label=f"load:{profile}")
    else:
        results, mon = _run_all(), None

    ok = all((r.get("result") or {}).get("ok") for r in results)
    return {
        "ok": ok,
        "profile": profile,
        "dry_run": dry_run,
        "results": results,
        "monitor": mon,
        "profiles": list(profiles.keys()),
    }
