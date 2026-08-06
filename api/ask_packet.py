"""Emit / validate ask_packet.v1 from story shots + tier_lock + pricing.

PHI and phi-adjacent data_class cannot emit crowd-routable packets
(qqq_floor QQQ3 with crowd providers). Local QQQ0 packets may still be built
for internal/lab use with data_class internal.
"""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = Path(os.environ.get("MOCK_TUA_CONFIG", ROOT / "config"))
WORK = Path(os.environ.get("WORK_FALLBACK", ROOT / "work"))

PHI_CLASSES = frozenset({"phi", "phi-adjacent"})
CROWD_QQQ = frozenset({"QQQ3"})  # only public overflow may target crowd


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(name: str) -> dict[str, Any]:
    path = CONFIG_DIR / name
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _load_pricing() -> dict[str, Any]:
    path = CONFIG_DIR / "pricing.yaml"
    if not path.is_file():
        return {}
    try:
        import yaml  # type: ignore

        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def lock_ref_for_tier(tier: str = "T1_vid_gen") -> str:
    """BLAKE2b over tier slice from tier_lock (stdlib; stable join key)."""
    lock_path = CONFIG_DIR / "tier_lock_T0-T4.json"
    if not lock_path.is_file():
        raw = tier.encode("utf-8")
        return f"{tier}@{hashlib.blake2b(raw, digest_size=8).hexdigest()}"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    slice_ = (lock.get("tiers") or {}).get(tier) or []
    # include mok_tua_version + locked_at for stability across inventory noise
    material = {
        "mok_tua_version": lock.get("mok_tua_version"),
        "locked_at": lock.get("locked_at"),
        "tier": tier,
        "ids": [
            {
                "id": x.get("id"),
                "sha": x.get("sha"),
                "status": x.get("status") or x.get("path_ok"),
            }
            for x in slice_
            if isinstance(x, dict)
        ],
    }
    raw = json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hashlib.blake2b(raw, digest_size=8).hexdigest()
    return f"{tier}@{digest}"


def requires_from_inventory(op: str = "still") -> list[dict[str, Any]]:
    """Johnny-style BOM entries from lora inventory / stage roles (no blobs)."""
    inv_path = CONFIG_DIR / "lora_inventory_storyboard_2026-08-02.json"
    req: list[dict[str, Any]] = []
    if inv_path.is_file():
        inv = json.loads(inv_path.read_text(encoding="utf-8"))
        for item in inv.get("items") or inv.get("loras") or []:
            if not isinstance(item, dict):
                continue
            rid = item.get("id") or item.get("name")
            if not rid:
                continue
            kind = "lora"
            path = str(item.get("path") or "")
            if "diffusion" in path or "unet" in path:
                kind = "unet"
            elif "vae" in path.lower():
                kind = "vae"
            req.append({"kind": kind, "ref": str(rid), "role": item.get("role") or "storyboard"})
            if len(req) >= 8:
                break
    if not req:
        req = [
            {"kind": "unet", "ref": "qwen_edit_2509_fp8", "role": "storyboard_base_edit"},
            {"kind": "lora", "ref": "multi_angles", "role": "storyboard_camera"},
        ]
    if op in ("i2v", "video"):
        req.append({"kind": "workflow", "ref": "wan22_animate", "role": "i2v"})
    return req


def _estimate_wall(op: str, duration_s: float, qqq: str) -> tuple[float, float, float]:
    pricing = _load_pricing()
    providers = pricing.get("providers") or {}
    # prefer local_gpu for video, local_desk for still
    if op in ("i2v", "video"):
        key = "local_gpu"
        rate = float((providers.get(key) or {}).get("est_video_sec_per_s") or 4)
        wall = max(duration_s, 1.0) * rate
    else:
        key = "local_desk"
        wall = float((providers.get(key) or {}).get("est_still_sec") or 25)
    deadline = wall * 3.0
    max_usd = 0.0
    if qqq == "QQQ1":
        max_usd = float((providers.get("runpod_rtx4090") or {}).get("on_demand_per_hour") or 0.39) * (
            wall / 3600.0
        )
    return wall, deadline, round(max_usd, 4)


def _refuse_data_class(data_class: str, qqq_floor: str, *, allow_crowd: bool) -> str | None:
    if data_class in PHI_CLASSES:
        if allow_crowd or qqq_floor in CROWD_QQQ:
            return "phi_not_crowd_routable"
        # phi also refused for any packet that claims crowd pricing path
        return "phi_emit_forbidden"
    if data_class != "public" and allow_crowd:
        return "crowd_requires_data_class_public"
    return None


def emit_packet(
    *,
    op: str = "still",
    duration_s: float = 5.0,
    data_class: str = "internal",
    qqq_floor: str = "QQQ0",
    tier: str = "T1_vid_gen",
    actor: str = "mok-tua",
    run_id: str | None = None,
    shot_id: str | None = None,
    allow_crowd: bool = False,
    payload_text: str | None = None,
    ttl: str = "PT30M",
) -> dict[str, Any]:
    """Build ask_packet.v1. Raises ValueError on PHI / policy refuse."""
    from chains_render import append_event, content_hash, last_hash

    err = _refuse_data_class(data_class, qqq_floor, allow_crowd=allow_crowd)
    if err:
        raise ValueError(err)

    # crowd path forces public + QQQ3 floor
    if allow_crowd:
        if data_class != "public":
            raise ValueError("crowd_requires_data_class_public")
        if qqq_floor == "QQQ0":
            qqq_floor = "QQQ3"

    wall, deadline, max_usd = _estimate_wall(op, duration_s, qqq_floor)
    lock_ref = lock_ref_for_tier(tier if op in ("i2v", "video") else "T0_orchestrators" if op == "expand" else "T1_vid_gen")
    # stills often still T1 graph
    if op == "still":
        lock_ref = lock_ref_for_tier("T1_vid_gen")

    arch = ["cuda_sm89", "cuda_any"] if op in ("i2v", "video") else ["cuda_any", "mps_unified"]
    vram = 12.0 if op in ("i2v", "video") else 6.0

    # seal payload locally (lab): write under work/packets/
    packet_id = str(uuid.uuid4())
    sealed_dir = WORK / "packets" / packet_id
    sealed_dir.mkdir(parents=True, exist_ok=True)
    body = payload_text or json.dumps({"op": op, "shot_id": shot_id, "run_id": run_id}, indent=2)
    payload_path = sealed_dir / "payload.json"
    payload_path.write_text(body if isinstance(body, str) else json.dumps(body), encoding="utf-8")
    nbytes = payload_path.stat().st_size
    # content-address local cid
    cid = "local:" + hashlib.blake2b(payload_path.read_bytes(), digest_size=16).hexdigest()

    manifest = {
        "lock_ref": lock_ref,
        "requires": requires_from_inventory(op),
        "op": op,
        "resource": {
            "vram_min_gb": vram,
            "arch_any": arch,
            "disk_gb": 20.0,
        },
        "expect": {
            "wall_sec_p50": round(wall, 1),
            "wall_sec_deadline": round(deadline, 1),
            "on_deadline": "spill_local" if qqq_floor == "QQQ0" else "cancel",
        },
        "memory": {
            "peak_gb_est": vram * 0.75,
            "residency": "weights" if op == "still" else "latent",
        },
        "data_class": data_class,
        "price": {"max_usd": max_usd, "unit": "shot"},
        "qqq_floor": qqq_floor,
        "shot_id": shot_id,
        "run_id": run_id,
    }

    packet: dict[str, Any] = {
        "schema": "ask_packet.v1",
        "id": packet_id,
        "created": _utc(),
        "ttl": ttl,
        "manifest": manifest,
        "payload_ref": {
            "cid": cid,
            "enc": "local_path",
            "bytes": nbytes,
            "path": str(payload_path),
        },
        "custody": {
            "chain_id": "mok-tua-render",
            "actor": actor,
            "prev_hash": last_hash(),
            "content_hash": "",  # filled below
            "sig": None,
        },
    }
    # content_hash over packet without circular field
    ch_body = {k: v for k, v in packet.items() if k != "custody"}
    ch_body["custody"] = {k: v for k, v in packet["custody"].items() if k != "content_hash"}
    packet["custody"]["content_hash"] = content_hash(ch_body)

    # append emit event to render chain
    append_event(
        "ask_packet_emit",
        {
            "packet_id": packet_id,
            "lock_ref": lock_ref,
            "op": op,
            "data_class": data_class,
            "qqq_floor": qqq_floor,
            "allow_crowd": allow_crowd,
        },
        actor=actor,
    )

    out = sealed_dir / "packet.json"
    out.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    packet["_path"] = str(out)
    return packet


def validate_packet_shape(packet: dict[str, Any]) -> dict[str, Any]:
    """Lightweight validation without jsonschema dependency."""
    errors: list[str] = []
    for key in ("id", "created", "ttl", "manifest", "payload_ref", "custody"):
        if key not in packet:
            errors.append(f"missing:{key}")
    m = packet.get("manifest") or {}
    if m.get("data_class") in PHI_CLASSES:
        errors.append("phi_in_manifest")
    if m.get("data_class") in PHI_CLASSES and m.get("qqq_floor") in CROWD_QQQ:
        errors.append("phi_crowd_route")
    cust = packet.get("custody") or {}
    if cust.get("chain_id") != "mok-tua-render":
        errors.append("wrong_chain_id")
    return {"ok": len(errors) == 0, "errors": errors}


def emit_from_story_markdown(
    markdown: str,
    *,
    data_class: str = "internal",
    qqq_floor: str = "QQQ0",
    allow_crowd: bool = False,
    max_shots: int = 3,
) -> dict[str, Any]:
    """Parse story and emit one packet per shot (capped)."""
    from story_parse import parse_story

    story = parse_story(markdown)
    packets = []
    n = 0
    for scene in story.get("scenes") or []:
        for shot in scene.get("shots") or []:
            if n >= max_shots:
                break
            fields = shot.get("fields") or {}
            st = (fields.get("shot_type") or "video").lower()
            op = "still" if st == "still" else "video"
            dur = 5.0
            try:
                from stages import duration_seconds

                dur = duration_seconds(fields.get("duration") or 5)
            except Exception:
                pass
            prompt = fields.get("prompt") or fields.get("action") or ""
            packets.append(
                emit_packet(
                    op=op,
                    duration_s=dur,
                    data_class=data_class,
                    qqq_floor=qqq_floor,
                    allow_crowd=allow_crowd,
                    shot_id=shot.get("id"),
                    payload_text=json.dumps(
                        {"prompt": prompt, "shot": shot.get("id"), "fields": fields},
                        indent=2,
                        default=str,
                    ),
                )
            )
            n += 1
        if n >= max_shots:
            break
    return {
        "ok": True,
        "title": story.get("title") or (story.get("meta") or {}).get("title"),
        "count": len(packets),
        "packets": packets,
    }
