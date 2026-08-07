"""GPU exclusive prep — free Comfy weights, stop allowlisted competitors.

Never kills unknown PIDs. Dry-run by default.
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

# Role hostnames only in public output; resolve via env for operators.
COMFY_URLS = [
    os.environ.get("COMFY_URL", "http://gpu-host:8188").rstrip("/"),
    "http://127.0.0.1:8188",
]

# Allowlisted stop targets: name → (host, port) probe; optional stop recipe id
VIDEO_PROFILE_STOP: list[dict[str, Any]] = [
    {"id": "framepack", "port": 7864, "host": "127.0.0.1", "note": "FramePack Gradio"},
    {"id": "maestro", "port": 7860, "host": "127.0.0.1", "note": "Maestro if hogging GPU"},
    {"id": "facefusion", "port": 7870, "host": "127.0.0.1", "note": "FaceFusion"},
]


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _tcp_open(host: str, port: int, timeout: float = 0.4) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def comfy_free(
    base_url: str,
    *,
    unload_models: bool = True,
    free_memory: bool = True,
    timeout: float = 30.0,
) -> dict[str, Any]:
    url = f"{base_url.rstrip('/')}/free"
    body = json.dumps(
        {"unload_models": unload_models, "free_memory": free_memory}
    ).encode()
    req = urllib.request.Request(
        url, data=body, method="POST", headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return {"ok": True, "status": resp.status, "url": url}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status": exc.code, "url": url, "error": str(exc)}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"ok": False, "url": url, "error": str(exc)}


def sample_nvidia_ssh(target: str | None = None) -> dict[str, Any]:
    host = target or os.environ.get("MOCK_TUA_SSH_TARGET", "mrgpu")
    try:
        proc = subprocess.run(
            [
                "ssh",
                "-o",
                "BatchMode=yes",
                "-o",
                "ConnectTimeout=6",
                host,
                "nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=12,
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return {"ok": False, "error": (proc.stderr or proc.stdout)[:200], "host": host}
        cols = [c.strip() for c in proc.stdout.strip().splitlines()[0].split(",")]
        used, total, util = float(cols[0]), float(cols[1]), float(cols[2])
        free = total - used
        return {
            "ok": True,
            "host": host,
            "gpu_mem_used_mib": used,
            "gpu_mem_total_mib": total,
            "gpu_mem_free_mib": free,
            "gpu_util_pct": util,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "host": host}


def _try_comfy_free_any() -> list[dict[str, Any]]:
    results = []
    for u in COMFY_URLS:
        r = comfy_free(u)
        results.append(r)
        if r.get("ok"):
            break
    return results


def gpu_prep(
    profile: str = "video",
    *,
    live: bool = False,
    free_comfy: bool = True,
    stop_competitors: bool = False,
    min_free_mib: float = 8000.0,
    ssh_target: str | None = None,
) -> dict[str, Any]:
    """
    Prepare GPU for a exclusive render profile.

    dry-run (live=False): report what would run + current VRAM.
    live=True: POST /free on Comfy; optionally note competitor ports (stop only if wired).
    """
    profile = (profile or "video").strip().lower()
    before = sample_nvidia_ssh(ssh_target)
    actions: list[dict[str, Any]] = []
    peers = []
    for p in VIDEO_PROFILE_STOP:
        up = _tcp_open(p["host"], int(p["port"]))
        peers.append({**p, "listening": up})

    if free_comfy:
        if live:
            actions.append({"action": "comfy_free", "results": _try_comfy_free_any()})
            time.sleep(1.0)
        else:
            actions.append(
                {
                    "action": "comfy_free",
                    "dry_run": True,
                    "urls": COMFY_URLS,
                    "note": "Would POST /free unload_models+free_memory",
                }
            )

    if stop_competitors:
        for p in peers:
            if not p.get("listening"):
                continue
            actions.append(
                {
                    "action": "stop_peer",
                    "id": p["id"],
                    "port": p["port"],
                    "dry_run": not live,
                    "note": (
                        "Allowlisted port is live — operator should stop via "
                        "mok-tua stop <id> or Pinokio; auto-kill not enabled"
                    ),
                }
            )

    after = sample_nvidia_ssh(ssh_target) if live else before
    free_mib = (after or {}).get("gpu_mem_free_mib")
    ready = bool(
        after.get("ok")
        and isinstance(free_mib, (int, float))
        and free_mib >= min_free_mib
    )
    return {
        "ok": True,
        "profile": profile,
        "live": live,
        "ready": ready if live else None,
        "min_free_mib": min_free_mib,
        "before": before,
        "after": after,
        "peers": peers,
        "actions": actions,
        "at": _utc(),
        "law": "no unknown PID kills; comfy /free + allowlisted notes only",
    }
