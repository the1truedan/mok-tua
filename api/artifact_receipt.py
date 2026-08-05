"""Artifact provenance receipts (sidecar JSON + optional caption burn-in).

Standing law (I2V incident): every still/clip needs renderer, qqq, gpu_evidence.
Tokens are filled when the API returns them; local Comfy often uses note=n/a.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WORK = Path(os.environ.get("WORK_FALLBACK", ROOT / "work"))
SCHEMA = "mok_tua_artifact_receipt.v1"

# Public-safe host roles only — never LAN IPs in burned captions.
SAFE_HOST_ROLES = frozenset({"gpu-host", "desk-host", "control-host", "cloud", "local", "n/a"})


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path, *, max_bytes: int | None = None) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        n = 0
        while True:
            chunk = fh.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
            n += len(chunk)
            if max_bytes is not None and n >= max_bytes:
                break
    return h.hexdigest()


def receipt_path_for(artifact: Path) -> Path:
    return artifact.with_suffix(artifact.suffix + ".receipt.json")


def infer_kind(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in {".mp4", ".webm", ".mov", ".mkv", ".gif"}:
        return "video"
    if ext in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
        return "image"
    if ext in {".md", ".txt", ".json"}:
        return "doc"
    return "file"


def format_caption_line(receipt: dict[str, Any], *, max_len: int = 120) -> str:
    """Single-line human citation (no LAN IPs / secrets)."""
    r = receipt.get("renderer") or "?"
    model = receipt.get("model") or "?"
    host = receipt.get("host_role") or "?"
    if host not in SAFE_HOST_ROLES and host not in ("?",):
        host = "host-redacted"
    wall = receipt.get("wall_clock_s")
    wall_s = f"{wall:.1f}s" if isinstance(wall, (int, float)) else "?"
    tok = receipt.get("tokens") or {}
    total = tok.get("total")
    if total is None:
        tok_s = tok.get("note") or "tok n/a"
    else:
        tok_s = f"tok {total}"
    gpu = receipt.get("gpu") or {}
    peak = gpu.get("peak_util_pct")
    gpu_s = f"GPU {peak:.0f}%" if isinstance(peak, (int, float)) else (
        gpu.get("note") or receipt.get("gpu_evidence") or "gpu ?"
    )
    qqq = receipt.get("qqq") or "?"
    line = f"{r} · {model} · {host} · {wall_s} · {tok_s} · {gpu_s} · {qqq}"
    if len(line) > max_len:
        return line[: max_len - 1] + "…"
    return line


def build_receipt(
    artifact: Path | str,
    *,
    renderer: str,
    provider: str | None = None,
    cloud_or_local: str = "local",
    model: str | None = None,
    host_role: str = "gpu-host",
    qqq: str = "QQQ0",
    prompt: str | None = None,
    negative_prompt: str | None = None,
    seed: int | str | None = None,
    wall_clock_s: float | None = None,
    tokens: dict[str, Any] | None = None,
    gpu: dict[str, Any] | None = None,
    cpu: dict[str, Any] | None = None,
    sampled_by: str | None = None,
    gpu_evidence: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    path = Path(artifact).expanduser().resolve()
    kind = infer_kind(path)
    digest = sha256_file(path) if path.is_file() else None
    tok = tokens or {"input": None, "output": None, "total": None, "note": "n/a"}
    if cloud_or_local == "cloud" and not gpu_evidence:
        gpu_evidence = "n/a cloud"
    if cloud_or_local == "local" and gpu and gpu.get("peak_util_pct") is not None:
        gpu_evidence = (
            f"peak_util={gpu['peak_util_pct']}% host_role={host_role}"
        )
    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "artifact": {
            "path": str(path),
            "name": path.name,
            "sha256": digest,
            "kind": kind,
            "exists": path.is_file(),
        },
        "renderer": renderer,
        "provider": provider or renderer.split("_")[0],
        "cloud_or_local": cloud_or_local,
        "model": model,
        "host_role": host_role if host_role in SAFE_HOST_ROLES else "host-redacted",
        "qqq": qqq,
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "seed": seed,
        "wall_clock_s": wall_clock_s,
        "tokens": tok,
        "gpu": gpu or {},
        "cpu": cpu or {},
        "gpu_evidence": gpu_evidence,
        "sampled_by": sampled_by or ("host_monitor" if gpu else "manual"),
        "ts_utc": _utc(),
        "caption_line": "",
    }
    if extra:
        receipt["extra"] = extra
    receipt["caption_line"] = format_caption_line(receipt)
    return receipt


def sample_to_gpu_cpu(sample: dict[str, Any] | None) -> tuple[dict[str, Any], dict[str, Any]]:
    """Map host_monitor.sample_host() into receipt gpu/cpu dicts."""
    if not sample or not sample.get("ok"):
        return {}, {}
    gpu = {
        k: sample[k]
        for k in (
            "gpu_util_pct",
            "gpu_temp_c",
            "gpu_mem_used_mib",
            "gpu_mem_total_mib",
        )
        if sample.get(k) is not None
    }
    if "gpu_util_pct" in gpu:
        gpu["peak_util_pct"] = gpu["gpu_util_pct"]
    cpu = {
        k: sample[k]
        for k in ("load1", "ram_used_gb", "ram_total_gb")
        if sample.get(k) is not None
    }
    return gpu, cpu


def write_receipt(
    receipt: dict[str, Any],
    *,
    path: Path | None = None,
    chain: bool = True,
) -> Path:
    art = receipt.get("artifact") or {}
    art_path = Path(art.get("path") or ".")
    out = path or receipt_path_for(art_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, default=str) + "\n", encoding="utf-8")
    if chain:
        try:
            from chains_render import append_event

            append_event(
                "artifact_receipt",
                {
                    "receipt_path": str(out),
                    "artifact_sha256": art.get("sha256"),
                    "renderer": receipt.get("renderer"),
                    "qqq": receipt.get("qqq"),
                    "gpu_evidence": receipt.get("gpu_evidence"),
                    "caption_line": receipt.get("caption_line"),
                },
            )
        except Exception:
            pass
    return out


def load_receipt(path: Path | str) -> dict[str, Any]:
    p = Path(path).expanduser()
    if p.suffix == ".json" and p.name.endswith(".receipt.json"):
        return json.loads(p.read_text(encoding="utf-8"))
    # allow pointing at the artifact itself
    side = receipt_path_for(p)
    if side.is_file():
        return json.loads(side.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"no receipt for {p}")


def burn_caption(
    artifact: Path | str,
    receipt: dict[str, Any] | None = None,
    *,
    out_path: Path | str | None = None,
    caption: str | None = None,
) -> dict[str, Any]:
    """Optional caption burn-in via ffmpeg drawtext (images/video).

    Returns {ok, path, method, error?}. Never writes over source unless out_path
    equals artifact and operator forces via same path intentionally.
    """
    src = Path(artifact).expanduser().resolve()
    if not src.is_file():
        return {"ok": False, "error": f"missing: {src}"}
    if receipt is None:
        try:
            receipt = load_receipt(src)
        except FileNotFoundError:
            return {"ok": False, "error": "no receipt; stamp first"}
    text = caption or format_caption_line(receipt, max_len=100)
    # escape for ffmpeg drawtext
    safe = (
        text.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace("%", "%%")
    )
    dest = Path(out_path) if out_path else src.with_name(src.stem + "_cited" + src.suffix)
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return {"ok": False, "error": "ffmpeg not on PATH", "caption": text}

    kind = infer_kind(src)
    # Bottom strip: black box + white-ish text
    vf = (
        f"drawtext=text='{safe}':fontsize=14:fontcolor=white:"
        f"box=1:boxcolor=black@0.65:boxborderw=6:"
        f"x=12:y=h-th-12"
    )
    cmd = [ffmpeg, "-y", "-i", str(src), "-vf", vf]
    if kind == "video":
        cmd += ["-codec:a", "copy", str(dest)]
    else:
        cmd += ["-frames:v", "1", str(dest)]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "error": str(exc), "caption": text}
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "")[-400:]
        return {"ok": False, "error": err or f"ffmpeg rc={proc.returncode}", "caption": text}
    return {"ok": True, "path": str(dest), "method": "ffmpeg_drawtext", "caption": text}


def stamp_from_monitor(
    artifact: Path | str,
    *,
    renderer: str,
    qqq: str = "QQQ0",
    prompt: str | None = None,
    model: str | None = None,
    cloud_or_local: str = "local",
    host_role: str = "gpu-host",
    wall_clock_s: float | None = None,
    tokens: dict[str, Any] | None = None,
    node: str = "mrgpu",
    burn: bool = False,
) -> dict[str, Any]:
    """Build + write receipt; optionally sample host_monitor and burn caption."""
    gpu: dict[str, Any] = {}
    cpu: dict[str, Any] = {}
    sampled_by = "manual"
    try:
        from host_monitor import sample_host

        sample = sample_host(node)
        gpu, cpu = sample_to_gpu_cpu(sample)
        if sample.get("ok"):
            sampled_by = "host_monitor"
    except Exception:
        pass

    if cloud_or_local == "cloud":
        tokens = tokens or {
            "input": None,
            "output": None,
            "total": None,
            "note": "fill from provider if available",
        }
    else:
        tokens = tokens or {
            "input": None,
            "output": None,
            "total": None,
            "note": "n/a local generative (no LLM token meter)",
        }

    receipt = build_receipt(
        artifact,
        renderer=renderer,
        cloud_or_local=cloud_or_local,
        model=model,
        host_role=host_role,
        qqq=qqq,
        prompt=prompt,
        wall_clock_s=wall_clock_s,
        tokens=tokens,
        gpu=gpu,
        cpu=cpu,
        sampled_by=sampled_by,
    )
    side = write_receipt(receipt)
    out: dict[str, Any] = {"ok": True, "receipt_path": str(side), "receipt": receipt}
    if burn:
        out["burn"] = burn_caption(artifact, receipt)
    return out
