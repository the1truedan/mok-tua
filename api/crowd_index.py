"""Trusted federation node index (file-backed). Not a public marketplace."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = Path(os.environ.get("MOCK_TUA_CONFIG", ROOT / "config"))
NODES_PATH = CONFIG_DIR / "crowd_nodes.json"


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_nodes() -> dict[str, Any]:
    if not NODES_PATH.is_file():
        return {"schema": "crowd_nodes.v1", "nodes": [], "path": str(NODES_PATH)}
    data = json.loads(NODES_PATH.read_text(encoding="utf-8"))
    data["path"] = str(NODES_PATH)
    return data


def save_nodes(data: dict[str, Any]) -> None:
    out = {k: v for k, v in data.items() if k != "path"}
    NODES_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")


def seed_lab_nodes(*, force: bool = False) -> dict[str, Any]:
    """Seed m4rv / mrgpu / tower from tier_lock if missing."""
    from ask_packet import lock_ref_for_tier

    data = load_nodes()
    existing = {n.get("id") for n in data.get("nodes") or []}
    if existing and not force:
        return {"ok": True, "seeded": 0, "nodes": data.get("nodes"), "note": "already seeded"}

    t0 = lock_ref_for_tier("T0_orchestrators")
    t1 = lock_ref_for_tier("T1_vid_gen")
    t2 = lock_ref_for_tier("T2_audio_music")
    t3 = lock_ref_for_tier("T3_face_body")

    seeds = [
        {
            "schema": "node_advertisement.v1",
            "id": "m4rv",
            "pubkey": None,
            "endpoint": "http://127.0.0.1:8188",
            "lock_hashes_resident": [t0, t1],
            "models_digest_set": ["qwen_edit_2509_fp8", "multi_angles"],
            "vram_gb": 36.0,
            "arch": "mps_unified",
            "driver": "mps",
            "bandwidth_mbps": 10000,
            "uptime_score": 0.95,
            "price_hint_usd": 0.0,
            "data_classes_accepted": ["public", "internal"],
            "roles": ["still", "expand", "llm"],
            "last_heartbeat": _utc(),
            "trusted": True,
            "notes": "M4RV SM Comfy — stills preferred",
        },
        {
            "schema": "node_advertisement.v1",
            "id": "mrgpu",
            "pubkey": None,
            "endpoint": os.environ.get("COMFY_MRGPU_URL", "http://gpu-host:8188"),
            "lock_hashes_resident": [t0, t1, t2, t3],
            "models_digest_set": ["wan22", "qwen_edit_2509_fp8", "animatediff"],
            "vram_gb": 16.0,
            "arch": "cuda_sm89",
            "driver": "cuda",
            "bandwidth_mbps": 1000,
            "uptime_score": 0.9,
            "price_hint_usd": 0.0,
            "data_classes_accepted": ["public", "internal"],
            "roles": ["still", "i2v", "video", "face", "tts"],
            "last_heartbeat": _utc(),
            "trusted": True,
            "notes": "MRGPU Comfy — video / Wan preferred",
        },
        {
            "schema": "node_advertisement.v1",
            "id": "tower",
            "pubkey": None,
            "endpoint": "http://control-host:8799",
            "lock_hashes_resident": [t0],
            "models_digest_set": [],
            "vram_gb": 0.0,
            "arch": "cpu",
            "driver": "none",
            "bandwidth_mbps": 1000,
            "uptime_score": 0.99,
            "price_hint_usd": 0.0,
            "data_classes_accepted": ["public", "internal"],
            "roles": ["stitch", "expand"],
            "last_heartbeat": _utc(),
            "trusted": True,
            "notes": "Tower control / CPU — no GPU video",
        },
    ]
    if force:
        data["nodes"] = seeds
    else:
        nodes = list(data.get("nodes") or [])
        for s in seeds:
            if s["id"] not in existing:
                nodes.append(s)
        data["nodes"] = nodes
    data["schema"] = "crowd_nodes.v1"
    data["updated"] = _utc()
    save_nodes(data)
    return {"ok": True, "seeded": len(seeds), "path": str(NODES_PATH), "nodes": data["nodes"]}


def heartbeat(node_id: str, **updates: Any) -> dict[str, Any]:
    data = load_nodes()
    found = False
    for n in data.get("nodes") or []:
        if n.get("id") == node_id:
            n["last_heartbeat"] = _utc()
            for k, v in updates.items():
                if v is not None and k not in ("id",):
                    n[k] = v
            found = True
            break
    if not found:
        return {"ok": False, "error": "unknown_node", "id": node_id}
    data["updated"] = _utc()
    save_nodes(data)
    return {"ok": True, "id": node_id, "last_heartbeat": _utc()}


def list_nodes(*, trusted_only: bool = False, role: str | None = None) -> dict[str, Any]:
    data = load_nodes()
    rows = []
    for n in data.get("nodes") or []:
        if trusted_only and not n.get("trusted"):
            continue
        if role and role not in (n.get("roles") or []):
            continue
        rows.append(n)
    return {"ok": True, "count": len(rows), "nodes": rows, "path": data.get("path")}
