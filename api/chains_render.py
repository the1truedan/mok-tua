"""CHAINS-shaped append-only log for mok-tua *render* receipts only.

chain_id is always ``mok-tua-render`` — never interleave with caregiving/PHI
custody (see grokcode ADR 0003 + johnny-appleseed-chipper CHAINS notes).

v1: tamper-evident hash links (prev_hash + content_hash). Signatures optional.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WORK = Path(os.environ.get("WORK_FALLBACK", ROOT / "work"))
CHAIN_ID = "mok-tua-render"
GENESIS = "blake3:genesis-mok-tua-render-v1"


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def chain_path() -> Path:
    p = WORK / "chains" / f"{CHAIN_ID}.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def content_hash(obj: dict[str, Any]) -> str:
    """Stable hash over event body excluding prev_hash and sig."""
    body = {k: v for k, v in obj.items() if k not in ("prev_hash", "sig", "content_hash")}
    raw = json.dumps(body, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    # stdlib: blake2b 32-byte hex (blake3 not guaranteed installed)
    return "blake2b:" + hashlib.blake2b(raw, digest_size=16).hexdigest()


def last_hash() -> str:
    path = chain_path()
    if not path.is_file():
        return GENESIS
    last = ""
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                last = line
    if not last:
        return GENESIS
    try:
        ev = json.loads(last)
        return str(ev.get("content_hash") or GENESIS)
    except json.JSONDecodeError:
        return GENESIS


def append_event(
    kind: str,
    payload: dict[str, Any],
    *,
    actor: str = "mok-tua",
    sig: str | None = None,
) -> dict[str, Any]:
    prev = last_hash()
    event: dict[str, Any] = {
        "schema": "chains_event.v1",
        "chain_id": CHAIN_ID,
        "kind": kind,
        "ts": _utc(),
        "actor": actor,
        "payload": payload,
        "prev_hash": prev,
        "sig": sig,
    }
    event["content_hash"] = content_hash(event)
    with chain_path().open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, default=str) + "\n")
    return event


def verify_chain(max_events: int = 10_000) -> dict[str, Any]:
    path = chain_path()
    if not path.is_file():
        return {"ok": True, "events": 0, "path": str(path), "note": "empty"}
    prev = GENESIS
    n = 0
    errors: list[str] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            n += 1
            if n > max_events:
                break
            try:
                ev = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"line {n}: {exc}")
                break
            if ev.get("prev_hash") != prev:
                errors.append(f"line {n}: prev_hash mismatch")
            ch = ev.get("content_hash")
            expected = content_hash(ev)
            if ch != expected:
                errors.append(f"line {n}: content_hash mismatch")
            prev = ch or prev
    return {
        "ok": len(errors) == 0,
        "events": n,
        "path": str(path),
        "errors": errors[:20],
        "tip_hash": prev,
    }
