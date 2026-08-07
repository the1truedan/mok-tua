#!/usr/bin/env python3
"""Generative motion sizzle from a still — AnimateDiff (owned, 16GB-safe).

Prefers AnimateDiff over Qwen Edit (OOM) and full WAN dual-noise until a
dedicated low-MP WAN API pin is stable. Optional multi-segment concat.

Usage:
  COMFY_URL=http://gpu-host:8188 \\
  python3 scripts/render_motion_sizzle_from_still.py \\
    --still docs/assets/capabilities/manager-pivot/04_board_manager.jpg

  # segments (shorter, free VRAM between):
  … --segments 2 --frames 12
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

from artifact_receipt import build_receipt, write_receipt  # noqa: E402
from backends.comfy import ComfyClient  # noqa: E402
from gpu_exclusive import gpu_prep  # noqa: E402
from progress import ProgressBus  # noqa: E402

COMFY_URL = os.environ.get("COMFY_URL", "http://gpu-host:8188").rstrip("/")
CKPT = os.environ.get("MOK_TUA_CKPT", "DreamShaper_8_pruned.safetensors")
AD_MODEL = os.environ.get("MOK_TUA_AD_MODEL", "mm_sd_v15_v2.fp16.safetensors")


def upload_image(path: Path, name: str) -> str:
    boundary = "----MokTuaBoundarySizzle"
    data = path.read_bytes()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{name}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode() + data + (
        f"\r\n--{boundary}\r\n"
        f'Content-Disposition: form-data; name="overwrite"\r\n\r\ntrue\r\n'
        f"--{boundary}--\r\n"
    ).encode()
    req = urllib.request.Request(
        f"{COMFY_URL}/upload/image",
        data=body,
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        out = json.loads(resp.read().decode())
    return str(out.get("name") or name)


def view_file(filename: str, *, subfolder: str = "", folder_type: str = "output") -> bytes:
    q = urllib.parse.urlencode(
        {"filename": filename, "subfolder": subfolder, "type": folder_type}
    )
    with urllib.request.urlopen(f"{COMFY_URL}/view?{q}", timeout=300) as resp:
        return resp.read()


def first_output_file(outputs: Any, *, prefer_video: bool = True) -> dict[str, str] | None:
    if not isinstance(outputs, dict):
        return None
    images: list[dict[str, str]] = []
    for _nid, node_out in outputs.items():
        if not isinstance(node_out, dict):
            continue
        for key in ("gifs", "videos", "images"):
            for im in node_out.get(key) or []:
                if not isinstance(im, dict):
                    continue
                entry = {
                    "filename": im.get("filename") or "",
                    "subfolder": im.get("subfolder") or "",
                    "type": im.get("type") or "output",
                }
                if prefer_video and (
                    entry["filename"].endswith(".mp4")
                    or key in ("gifs", "videos")
                ):
                    return entry
                images.append(entry)
    return images[0] if images else None


def build_ad_i2v_graph(
    *,
    image_name: str,
    prompt: str,
    negative: str,
    seed: int,
    frames: int,
    width: int,
    height: int,
    steps: int,
    denoise: float,
    filename_prefix: str,
) -> dict[str, Any]:
    """AnimateDiff motion from start image (img2img denoise)."""
    return {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": CKPT},
        },
        "2": {
            "class_type": "LoadImage",
            "inputs": {"image": image_name},
        },
        "10": {
            "class_type": "ADE_AnimateDiffLoaderGen1",
            "inputs": {
                "model": ["1", 0],
                "model_name": AD_MODEL,
                "beta_schedule": "autoselect",
            },
        },
        "11": {
            "class_type": "VAEEncode",
            "inputs": {"pixels": ["2", 0], "vae": ["1", 2]},
        },
        "12": {
            "class_type": "RepeatLatentBatch",
            "inputs": {"samples": ["11", 0], "amount": frames},
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": prompt, "clip": ["1", 1]},
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": negative, "clip": ["1", 1]},
        },
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": 6.5,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": denoise,
                "model": ["10", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["12", 0],
            },
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["1", 2]},
        },
        "20": {
            "class_type": "VHS_VideoCombine",
            "inputs": {
                "images": ["8", 0],
                "frame_rate": 8.0,
                "loop_count": 0,
                "filename_prefix": filename_prefix,
                "format": "video/h264-mp4",
                "pingpong": False,
                "save_output": True,
            },
        },
    }


def concat_mp4s(paths: list[Path], dest: Path) -> dict[str, Any]:
    lst = dest.parent / "concat_list.txt"
    lines = []
    for p in paths:
        lines.append(f"file '{p.resolve()}'")
    lst.write_text("\n".join(lines) + "\n", encoding="utf-8")
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(lst),
        "-c",
        "copy",
        str(dest),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return {"ok": proc.returncode == 0, "stderr": (proc.stderr or "")[-400:]}


def main() -> int:
    ap = argparse.ArgumentParser(description="Motion sizzle from still (AnimateDiff)")
    ap.add_argument(
        "--still",
        default=str(
            ROOT / "docs/assets/capabilities/manager-pivot/04_board_manager.jpg"
        ),
    )
    ap.add_argument("--prompt", default=None)
    ap.add_argument("--segments", type=int, default=1)
    ap.add_argument("--frames", type=int, default=16)
    ap.add_argument("--width", type=int, default=512)
    ap.add_argument("--height", type=int, default=512)
    ap.add_argument("--steps", type=int, default=14)
    ap.add_argument("--denoise", type=float, default=0.52)
    ap.add_argument("--seed", type=int, default=77001)
    ap.add_argument("--no-gpu-prep", action="store_true")
    args = ap.parse_args()

    still = Path(args.still)
    if not still.is_file():
        print("missing still", still, file=sys.stderr)
        return 1

    prompt = args.prompt or (
        "anime style cinematic motion, subtle camera push-in, "
        "M.A.N.A.G.E.R. framework board glow, same character as reference, "
        "gentle head motion and blink, coherent face, soft light, high quality"
    )
    negative = (
        "blurry, low quality, watermark, morphing face, extra limbs, "
        "flicker, text gibberish, static photo, slideshow"
    )

    out_dir = ROOT / "work" / "motion_sizzle"
    pub = ROOT / "docs/assets/exports"
    out_dir.mkdir(parents=True, exist_ok=True)
    pub.mkdir(parents=True, exist_ok=True)

    bus = ProgressBus(enabled=True)
    bus.task("prep", "gpu-prep video", detail="free comfy")
    if not args.no_gpu_prep:
        prep = gpu_prep("video", live=True, stop_competitors=True)
        bus.done("prep", detail=f"free≈{(prep.get('after') or {}).get('gpu_mem_free_mib')}")
    else:
        prep = {"skipped": True}
        bus.done("prep", detail="skipped")

    client = ComfyClient(COMFY_URL, timeout=60.0)
    stats = client.system_stats()
    if not stats.get("ok"):
        bus.fail("prep", detail="comfy down")
        bus.close()
        print("comfy unreachable", stats, file=sys.stderr)
        return 1

    bus.task("upload", "upload still")
    server_name = upload_image(still, still.name)
    bus.done("upload", detail=server_name)

    segments: list[Path] = []
    segment_meta: list[dict[str, Any]] = []
    t_all = time.time()

    for i in range(max(1, args.segments)):
        sid = f"seg{i+1}"
        bus.task(sid, f"AnimateDiff segment {i+1}/{args.segments}")
        client.free_memory()
        time.sleep(0.5)
        seed = args.seed + i * 17
        graph = build_ad_i2v_graph(
            image_name=server_name,
            prompt=prompt + (f", beat {i+1}" if args.segments > 1 else ""),
            negative=negative,
            seed=seed,
            frames=args.frames,
            width=args.width,
            height=args.height,
            steps=args.steps,
            denoise=args.denoise,
            filename_prefix=f"mok_sizzle_{sid}",
        )
        t0 = time.time()

        def _tick(elapsed: float, status: str, _sid=sid) -> None:
            soft = min(0.95, elapsed / 180.0)
            bus.update(_sid, frac=soft, detail=status)

        q = client.queue_prompt(graph)
        if not q.get("ok"):
            bus.fail(sid, detail="queue")
            bus.close()
            print("queue fail", q, file=sys.stderr)
            return 2
        pid = (q.get("result") or {}).get("prompt_id")
        waited = client.wait_for_prompt(pid, timeout_s=900, poll_s=2.0, on_tick=_tick)
        wall = time.time() - t0
        if not waited.get("ok"):
            bus.fail(sid, detail=str(waited.get("status")))
            bus.close()
            print("wait fail", json.dumps(waited, default=str)[:600], file=sys.stderr)
            return 3
        meta = first_output_file(waited.get("outputs"), prefer_video=True)
        if not meta or not meta.get("filename"):
            bus.fail(sid, detail="no output")
            bus.close()
            print("no output", waited.get("outputs"), file=sys.stderr)
            return 4
        raw = view_file(
            meta["filename"],
            subfolder=meta.get("subfolder") or "",
            folder_type=meta.get("type") or "output",
        )
        dest = out_dir / f"sizzle_{sid}.mp4"
        dest.write_bytes(raw)
        segments.append(dest)
        segment_meta.append(
            {
                "path": str(dest.relative_to(ROOT)),
                "seed": seed,
                "wall_clock_s": round(wall, 2),
                "frames": args.frames,
                "width": args.width,
                "height": args.height,
                "denoise": args.denoise,
            }
        )
        bus.done(sid, detail=f"{wall:.0f}s")

    final = out_dir / "manager_pivot_motion_sizzle.mp4"
    if len(segments) == 1:
        shutil.copy2(segments[0], final)
    else:
        bus.task("concat", "ffmpeg concat")
        c = concat_mp4s(segments, final)
        if not c.get("ok"):
            bus.fail("concat", detail="ffmpeg")
            bus.close()
            print(c, file=sys.stderr)
            return 5
        bus.done("concat")

    pub = ROOT / "docs/assets/exports" / "manager-pivot-motion-sizzle-animatediff.mp4"
    shutil.copy2(final, pub)
    # poster = first frame via ffmpeg
    poster = ROOT / "docs/assets/exports" / "manager-pivot-motion-sizzle-animatediff-poster.jpg"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(final),
            "-vframes",
            "1",
            str(poster),
        ],
        capture_output=True,
    )
    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(pub),
        ],
        capture_output=True,
        text=True,
    )
    dur = float(probe.stdout.strip() or 0)
    total_wall = time.time() - t_all

    summary = {
        "schema": "mok_tua_motion_sizzle.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "renderer": "gpu_comfy_animatediff_i2v",
        "model": f"{CKPT} + {AD_MODEL}",
        "still": str(still) if not str(still).startswith(str(ROOT)) else str(still.relative_to(ROOT)),
        "prompt": prompt,
        "negative": negative,
        "segments": segment_meta,
        "video": {
            "path": str(pub.relative_to(ROOT)),
            "poster": str(poster.relative_to(ROOT)),
            "measured_duration_s": dur,
            "generative": True,
            "not_slideshow": True,
        },
        "gpu_prep": {
            "live": True,
            "before_free_mib": (prep.get("before") or {}).get("gpu_mem_free_mib"),
            "after_free_mib": (prep.get("after") or {}).get("gpu_mem_free_mib"),
        },
        "qwen_edit": "paused_on_16gb_oom — use AnimateDiff/WAN for motion",
        "wall_clock_total_s": round(total_wall, 2),
        "qqq": "QQQ0",
        "host_role": "gpu-host",
    }
    # relativize still path
    try:
        summary["still"] = str(still.resolve().relative_to(ROOT.resolve()))
    except Exception:
        summary["still"] = still.name

    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    rec = build_receipt(
        pub,
        renderer="gpu_comfy_animatediff_i2v",
        model=summary["model"],
        host_role="gpu-host",
        qqq="QQQ0",
        prompt=prompt,
        wall_clock_s=total_wall,
        gpu_evidence="animatediff_queue_ok",
        extra={
            "duration_s": dur,
            "segments": len(segments),
            "summary": str((out_dir / "summary.json").relative_to(ROOT)),
        },
    )
    if str(rec.get("artifact", {}).get("path", "")).startswith("/"):
        rec["artifact"]["path"] = str(pub.relative_to(ROOT))
    write_receipt(rec)
    bus.done("all", detail=f"{dur:.1f}s")
    bus.close()
    print(json.dumps({"ok": True, "video": summary["video"], "wall_s": total_wall}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
