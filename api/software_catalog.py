"""C64 software catalog — insert disk = path + port probe."""

from __future__ import annotations

import json
import os
import socket
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = Path(os.environ.get("MOCK_TUA_CONFIG", ROOT / "config"))
def _ai_data() -> Path | None:
    env = (os.environ.get("AI_DATA_ROOT") or "").strip()
    candidates = []
    if env:
        candidates.append(Path(env))
    candidates.extend([Path("/Volumes/ai-data"), Path("/mnt/ai-data")])
    for p in candidates:
        try:
            if p.is_dir() and (p / "models").exists():
                return p
        except OSError:
            continue
    for p in candidates:
        try:
            if p.is_dir():
                return p
        except OSError:
            continue
    return None


def load_catalog(path: Path | str | None = None) -> dict[str, Any]:
    p = Path(path) if path else CONFIG_DIR / "c64_software_catalog.json"
    if not p.is_file():
        return {"version": 0, "disks": [], "error": f"missing:{p}"}
    data = json.loads(p.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {"disks": []}


def _tcp(host: str, port: int, timeout: float = 0.35) -> bool:
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True
    except OSError:
        return False


def _resolve_hint(hint: str, ai: Path | None) -> Path | None:
    h = hint.replace("~", str(Path.home()))
    p = Path(h)
    if p.is_file() or p.is_dir():
        return p
    if ai is not None and not p.is_absolute():
        q = ai / h
        if q.is_file() or q.is_dir():
            return q
        # glob last segment
        if "*" in h:
            parent = ai / Path(h).parent
            if parent.is_dir():
                matches = list(parent.glob(Path(h).name))
                if matches:
                    return matches[0]
    return None


def probe_disk(disk: dict[str, Any]) -> dict[str, Any]:
    ai = _ai_data()
    paths_found: list[str] = []
    for hint in disk.get("path_hints") or []:
        r = _resolve_hint(str(hint), ai)
        if r is not None:
            # role-safe relative if under ai-data
            if ai and str(r).startswith(str(ai)):
                paths_found.append(str(r.relative_to(ai)))
            else:
                paths_found.append(r.name if r.is_file() else str(r))
    ports = []
    any_port = False
    extra_hosts = ["127.0.0.1", "gpu-host"]
    # Operator may set COMFY_URL=http://gpu-host:8188 (or LAN IP) — use host for probes only
    comfy = (os.environ.get("COMFY_URL") or "").strip()
    if "://" in comfy:
        try:
            from urllib.parse import urlparse

            h = urlparse(comfy).hostname
            if h:
                extra_hosts.append(h)
        except Exception:
            pass
    for port in disk.get("ports") or []:
        live = False
        for host in extra_hosts:
            if _tcp(host, int(port)):
                live = True
                break
        any_port = any_port or live
        ports.append({"port": int(port), "live": live})

    path_ok = bool(paths_found) or disk.get("kind") == "lab"
    if disk.get("kind") == "comfy_model":
        path_ok = bool(paths_found)

    if any_port:
        state = "RUNNING"
    elif path_ok:
        state = "DISK_READY"
    else:
        state = "DISK_NOT_FOUND"

    return {
        "id": disk.get("id"),
        "label": disk.get("label"),
        "title": disk.get("title"),
        "kind": disk.get("kind"),
        "tier": disk.get("tier"),
        "state": state,
        "paths_found": paths_found,
        "ports": ports,
        "recipe": disk.get("recipe"),
        "splash": disk.get("splash"),
        "status_note": disk.get("status_note"),
    }


def list_software(*, catalog_path: Path | str | None = None) -> dict[str, Any]:
    cat = load_catalog(catalog_path)
    disks = [probe_disk(d) for d in cat.get("disks") or [] if isinstance(d, dict)]
    return {
        "ok": True,
        "count": len(disks),
        "disks": disks,
        "catalog_version": cat.get("version"),
    }


def insert_disk(tool_id: str, *, catalog_path: Path | str | None = None) -> dict[str, Any]:
    """Probe one tool — 'insert disk' metaphor (no spawn)."""
    cat = load_catalog(catalog_path)
    tid = tool_id.strip().lower().replace(" ", "_")
    # allow label match
    found = None
    for d in cat.get("disks") or []:
        if not isinstance(d, dict):
            continue
        if str(d.get("id", "")).lower() == tid or str(d.get("label", "")).lower() == tid.upper() or str(d.get("label", "")).lower() == tid:
            found = d
            break
        if str(d.get("label", "")).upper() == tid.upper():
            found = d
            break
    if not found:
        return {"ok": False, "error": "unknown_disk", "id": tool_id}
    probe = probe_disk(found)
    return {
        "ok": True,
        "action": "insert_disk",
        "probe": probe,
        "message": {
            "DISK_READY": "Disk ready — launch with: launch {id} --live",
            "RUNNING": "Already running — open ports or stop first",
            "DISK_NOT_FOUND": "Disk not found — install via Pinokio/SM or stage models",
        }.get(probe["state"], probe["state"]).format(id=probe["id"]),
    }
