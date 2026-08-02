"""Thin award broker: score nodes for an ask_packet (dry-run by default).

Score = lock_match*100 + uptime*10 + role_match*5 - price_hint - latency_penalty
Never awards non-public packets to crowd (untrusted) nodes.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from chains_render import append_event
from crowd_index import list_nodes, load_nodes, seed_lab_nodes


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def score_node(node: dict[str, Any], packet: dict[str, Any]) -> dict[str, Any]:
    m = packet.get("manifest") or {}
    lock_ref = str(m.get("lock_ref") or "")
    op = str(m.get("op") or "still")
    data_class = str(m.get("data_class") or "internal")
    resource = m.get("resource") or {}
    arch_any = set(resource.get("arch_any") or [])
    vram_min = float(resource.get("vram_min_gb") or 0)

    reasons: list[str] = []
    score = 0.0

    # data class gate
    accepted = set(node.get("data_classes_accepted") or [])
    if data_class == "public":
        if "public" not in accepted and "internal" not in accepted:
            return {"id": node.get("id"), "score": -1e9, "eligible": False, "reasons": ["data_class_reject"]}
    elif data_class == "internal":
        if not node.get("trusted"):
            return {"id": node.get("id"), "score": -1e9, "eligible": False, "reasons": ["internal_requires_trusted"]}
        if "internal" not in accepted and "public" not in accepted:
            return {"id": node.get("id"), "score": -1e9, "eligible": False, "reasons": ["data_class_reject"]}
    else:
        # phi should never reach here
        return {"id": node.get("id"), "score": -1e9, "eligible": False, "reasons": ["phi_blocked"]}

    locks = set(node.get("lock_hashes_resident") or [])
    # match full lock_ref or same tier prefix
    tier_prefix = lock_ref.split("@")[0] if "@" in lock_ref else lock_ref
    lock_hit = lock_ref in locks or any(str(x).startswith(tier_prefix + "@") for x in locks)
    if lock_hit:
        score += 100.0
        reasons.append("lock_match")
    else:
        score -= 20.0
        reasons.append("lock_miss")

    roles = set(node.get("roles") or [])
    role_map = {
        "still": "still",
        "i2v": "i2v",
        "video": "video",
        "expand": "expand",
        "tts": "tts",
        "face": "face",
        "stitch": "stitch",
    }
    need = role_map.get(op, op)
    if need in roles or (op == "video" and "i2v" in roles):
        score += 5.0
        reasons.append("role_match")
    else:
        score -= 50.0
        reasons.append("role_miss")

    arch = node.get("arch")
    if arch in arch_any or (arch == "cuda_sm89" and "cuda_any" in arch_any):
        score += 3.0
        reasons.append("arch_ok")
    elif "cpu" in arch_any and arch == "cpu":
        score += 1.0
    else:
        score -= 10.0
        reasons.append("arch_weak")

    vram = float(node.get("vram_gb") or 0)
    if vram + 0.01 >= vram_min:
        score += 2.0
    else:
        score -= 30.0
        reasons.append("vram_low")

    score += 10.0 * float(node.get("uptime_score") or 0)
    score -= float(node.get("price_hint_usd") or 0) * 10.0

    if node.get("trusted"):
        score += 5.0
        reasons.append("trusted")

    eligible = score > 0 and "role_miss" not in reasons and "vram_low" not in reasons
    return {
        "id": node.get("id"),
        "score": round(score, 3),
        "eligible": eligible,
        "reasons": reasons,
        "endpoint": node.get("endpoint"),
        "trusted": bool(node.get("trusted")),
    }


def award_packet(
    packet: dict[str, Any],
    *,
    dry_run: bool = True,
    prefer_trusted: bool = True,
) -> dict[str, Any]:
    m = packet.get("manifest") or {}
    data_class = str(m.get("data_class") or "internal")
    if data_class in ("phi", "phi-adjacent"):
        return {
            "ok": False,
            "error": "phi_not_awardable",
            "packet_id": packet.get("id"),
        }

    # ensure seed exists
    if not (load_nodes().get("nodes")):
        seed_lab_nodes()

    nodes = list_nodes(trusted_only=(data_class != "public" or prefer_trusted)).get("nodes") or []
    if data_class == "public" and not prefer_trusted:
        nodes = list_nodes(trusted_only=False).get("nodes") or []

    scored = [score_node(n, packet) for n in nodes]
    scored.sort(key=lambda r: r["score"], reverse=True)
    eligible = [r for r in scored if r.get("eligible")]
    winner = eligible[0] if eligible else None

    result = {
        "ok": bool(winner),
        "dry_run": dry_run,
        "packet_id": packet.get("id"),
        "lock_ref": m.get("lock_ref"),
        "data_class": data_class,
        "winner": winner,
        "ranked": scored[:10],
        "ts": _utc(),
    }
    if winner and not dry_run:
        append_event(
            "ask_packet_award",
            {
                "packet_id": packet.get("id"),
                "node_id": winner.get("id"),
                "score": winner.get("score"),
                "lock_ref": m.get("lock_ref"),
            },
            actor="award-broker",
        )
        result["receipt_stub"] = {
            "schema": "ask_receipt.v1",
            "packet_id": packet.get("id"),
            "created": _utc(),
            "node_id": winner.get("id"),
            "status": "awarded",
            "lock_ref_claimed": m.get("lock_ref"),
            "actual": {},
            "expect": m.get("expect"),
            "artifact_hash": None,
            "attestation": {"kind": "self_report", "detail": "award only; work not executed"},
        }
    return result
