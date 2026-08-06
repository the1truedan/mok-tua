#!/usr/bin/env python3
"""Regenerate CEO storyboard + face polish + AnimateDiff strip on gpu-host Comfy.

Identity: docs/assets/pres-smoke/00-ceo-source-still.jpg via LoadImage + img2img
(IPAdapter nodes exist but weight files incomplete — honest prompt-locked + img2img).

Usage:
  COMFY_URL=http://REDACTED-LAN-IP:8188 python3 scripts/regen_ceo_capability_assets.py
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

from backends.comfy import ComfyClient, build_minimal_still_graph  # noqa: E402
from artifact_receipt import build_receipt, write_receipt  # noqa: E402

try:
    from host_monitor import sample_host  # noqa: E402
except Exception:  # pragma: no cover
    sample_host = None  # type: ignore

COMFY_URL = os.environ.get("COMFY_URL", os.environ.get("COMFY_gpu-host_URL", "http://REDACTED-LAN-IP:8188")).rstrip("/")
CKPT = os.environ.get("MOK_TUA_CKPT", "DreamShaper_8_pruned.safetensors")
SOURCE = ROOT / "docs/assets/pres-smoke/00-ceo-source-still.jpg"
OUT_DIR = Path(os.environ.get("MOK_TUA_CEO_OUT", str(ROOT / "work" / "ceo_capability_regen")))
ASSETS = ROOT / "docs" / "assets"
RECEIPTS = ASSETS / "receipts"

NEG = (
    "blurry, low quality, watermark, deformed face, extra limbs, wrong gender, "
    "woman, female, child, text gibberish, logo spam, cartoon, anime"
)

CEO_FACE = (
    "same man as reference selfie, fair skin, freckles, light red facial patches, "
    "green-hazel eyes, short sandy brown hair, goofy intense expression, "
    "handwritten black marker 'ceo' on forehead when forehead visible"
)

PANELS: list[tuple[str, str]] = [
    (
        "wide",
        f"cinematic storyboard panel, wide shot classroom-like tech meetup, {CEO_FACE}, "
        "hoodie, standing presenting mok-tua on projector, audience of laptops, natural light",
    ),
    (
        "medium",
        f"cinematic storyboard panel, medium shot at desk, {CEO_FACE}, sticky notes, "
        "dual monitors with terminal and IDE, teaching a colleague, warm lamp",
    ),
    (
        "closeup",
        f"cinematic storyboard panel, close-up face, {CEO_FACE}, speaking enthusiastically, "
        "shallow depth of field, soft key light",
    ),
    (
        "ots",
        f"cinematic storyboard panel, over-shoulder whiteboard sketch, {CEO_FACE} partial profile, "
        "writing 'shots · stills · I2V' on board, office",
    ),
    (
        "profile",
        f"cinematic storyboard panel, profile walking hallway, {CEO_FACE}, carrying notebook, "
        "candid photojournalism, fluorescent hallway",
    ),
    (
        "outdoor",
        f"cinematic storyboard panel, outdoor medium shot campus path, {CEO_FACE}, "
        "smiling after demo, trees and brick buildings soft bokeh",
    ),
]


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def upload_image(path: Path, name: str = "ceo_source_still.jpg") -> str:
    """POST multipart to Comfy /upload/image; return server filename."""
    boundary = "----MokTuaBoundary7MA4YWxkTrZu0gW"
    data = path.read_bytes()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{name}"\r\n'
        f"Content-Type: image/jpeg\r\n\r\n"
    ).encode() + data + f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        f"{COMFY_URL}/upload/image",
        data=body,
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        out = json.loads(resp.read().decode())
    # {"name": "...", "subfolder": "", "type": "input"}
    return str(out.get("name") or name)


def view_image(filename: str, *, subfolder: str = "", folder_type: str = "output") -> bytes:
    q = urllib.parse.urlencode(
        {"filename": filename, "subfolder": subfolder, "type": folder_type}
    )
    with urllib.request.urlopen(f"{COMFY_URL}/view?{q}", timeout=120) as resp:
        return resp.read()


def queue_and_wait(client: ComfyClient, graph: dict[str, Any], *, timeout_s: float = 300) -> dict[str, Any]:
    t0 = time.time()
    queued = client.queue_prompt(graph)
    if not queued.get("ok"):
        return {"ok": False, "error": "queue_failed", "queued": queued, "seconds": time.time() - t0}
    pid = (queued.get("result") or {}).get("prompt_id")
    if not pid:
        return {"ok": False, "error": "no_prompt_id", "queued": queued, "seconds": time.time() - t0}
    waited = client.wait_for_prompt(pid, timeout_s=timeout_s, poll_s=1.5)
    waited["seconds"] = time.time() - t0
    waited["prompt_id"] = pid
    return waited


def first_image_meta(outputs: dict[str, Any] | None) -> dict[str, Any] | None:
    if not outputs:
        return None
    for _nid, node_out in outputs.items():
        if not isinstance(node_out, dict):
            continue
        for key in ("images", "gifs"):
            items = node_out.get(key)
            if items:
                return {"key": key, **items[0]}
    return None


def build_img2img_graph(
    *,
    image_name: str,
    prompt: str,
    negative: str,
    seed: int,
    denoise: float,
    width: int,
    height: int,
    steps: int,
    filename_prefix: str,
    checkpoint: str = CKPT,
) -> dict[str, Any]:
    """LoadImage → ImageScale → VAEEncode → KSampler(denoise) → VAEDecode → SaveImage."""
    return {
        "1": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        "2": {
            "class_type": "ImageScale",
            "inputs": {
                "image": ["1", 0],
                "upscale_method": "lanczos",
                "width": width,
                "height": height,
                "crop": "center",
            },
        },
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": checkpoint}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["4", 1]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": negative, "clip": ["4", 1]}},
        "10": {"class_type": "VAEEncode", "inputs": {"pixels": ["2", 0], "vae": ["4", 2]}},
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": 7.0,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": denoise,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["10", 0],
            },
        },
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": filename_prefix, "images": ["8", 0]},
        },
    }


def build_animatediff_graph(
    *,
    prompt: str,
    negative: str,
    seed: int,
    frames: int = 16,
    width: int = 512,
    height: int = 512,
    steps: int = 16,
    filename_prefix: str = "ceo_ad",
) -> dict[str, Any]:
    """Minimal ADE Gen1 + VHS h264 — same family as prior gpu-host smoke."""
    return {
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": width, "height": height, "batch_size": frames},
        },
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["4", 1]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": negative, "clip": ["4", 1]}},
        "11": {
            "class_type": "ADE_AnimateDiffLoaderGen1",
            "inputs": {
                "model": ["4", 0],
                "model_name": "mm_sd_v15_v2.fp16.safetensors",
                "beta_schedule": "autoselect",
            },
        },
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": 7.0,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["11", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0],
            },
        },
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "12": {
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


def sample_gpu() -> dict[str, Any]:
    if sample_host is None:
        return {}
    try:
        # host_monitor uses role node; may SSH — ok
        s = sample_host("gpu-host")
        if s.get("ok"):
            return s
    except Exception:
        pass
    # direct nvidia via ssh one-liner
    try:
        proc = subprocess.run(
            [
                "ssh",
                "-o",
                "BatchMode=yes",
                "-o",
                "ConnectTimeout=4",
                "redacted@REDACTED-LAN-IP",
                "nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            cols = [c.strip() for c in proc.stdout.strip().splitlines()[0].split(",")]
            return {
                "ok": True,
                "gpu_util_pct": float(cols[0]),
                "gpu_mem_used_mib": float(cols[1]),
                "gpu_mem_total_mib": float(cols[2]),
                "gpu_temp_c": float(cols[3]),
                "source": "ssh_nvidia_smi",
            }
    except Exception:
        pass
    return {}


def collage_storyboard(panel_paths: list[Path], out_path: Path, labels: list[str]) -> None:
    from PIL import Image, ImageDraw, ImageFont

    # 3x2 grid like original 1280x720
    cell_w, cell_h = 400, 300
    pad = 24
    label_h = 36
    cols, rows = 3, 2
    W = pad + cols * (cell_w + pad)
    H = pad + rows * (cell_h + label_h + pad) + 40
    canvas = Image.new("RGB", (W, H), (245, 242, 236))
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 16)
        font_sm = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 12)
    except Exception:
        font = ImageFont.load_default()
        font_sm = font

    for i, p in enumerate(panel_paths[:6]):
        r, c = divmod(i, cols)
        x = pad + c * (cell_w + pad)
        y = pad + r * (cell_h + label_h + pad)
        im = Image.open(p).convert("RGB")
        im = im.resize((cell_w, cell_h), Image.Resampling.LANCZOS)
        # white panel frame
        draw.rectangle([x - 4, y - 4, x + cell_w + 4, y + cell_h + label_h + 4], fill=(255, 255, 255))
        canvas.paste(im, (x, y))
        label = labels[i] if i < len(labels) else p.stem
        draw.text((x + 8, y + cell_h + 8), label, fill=(30, 30, 30), font=font)
    cite = (
        "mok-tua · gpu-host Comfy · DreamShaper_8 · img2img from 00-ceo-source-still · QQQ0 · prompt-locked identity"
    )
    draw.text((pad, H - 28), cite, fill=(80, 80, 80), font=font_sm)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, quality=92)


def face_polish_sheet(before: Path, after: Path, out_path: Path) -> None:
    from PIL import Image, ImageDraw, ImageFont

    bw, bh = 640, 720
    canvas = Image.new("RGB", (bw * 2, bh), (20, 20, 24))
    for i, src in enumerate((before, after)):
        im = Image.open(src).convert("RGB")
        # cover crop
        im_ratio = im.width / im.height
        target_ratio = bw / bh
        if im_ratio > target_ratio:
            nh = im.height
            nw = int(nh * target_ratio)
            left = (im.width - nw) // 2
            im = im.crop((left, 0, left + nw, nh))
        else:
            nw = im.width
            nh = int(nw / target_ratio)
            top = (im.height - nh) // 2
            im = im.crop((0, top, nw, top + nh))
        im = im.resize((bw, bh), Image.Resampling.LANCZOS)
        canvas.paste(im, (i * bw, 0))
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 22)
        font_sm = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 13)
    except Exception:
        font = ImageFont.load_default()
        font_sm = font
    draw.rectangle([16, 16, 140, 48], fill=(0, 0, 0, 180))
    draw.rectangle([bw + 16, 16, bw + 120, 48], fill=(0, 0, 0, 180))
    draw.text((28, 22), "BEFORE", fill=(255, 255, 255), font=font)
    draw.text((bw + 28, 22), "AFTER", fill=(255, 255, 255), font=font)
    cite = "mok-tua · gpu-host Comfy img2img refine · DreamShaper_8 · source 00-ceo-source-still · QQQ0"
    draw.rectangle([0, bh - 36, bw * 2, bh], fill=(0, 0, 0))
    draw.text((16, bh - 28), cite, fill=(200, 200, 200), font=font_sm)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, quality=92)


def extract_frame_strip(mp4: Path, out_path: Path, n: int = 4) -> bool:
    if not shutil.which("ffmpeg"):
        return False
    tmp = OUT_DIR / "ad_frames"
    tmp.mkdir(parents=True, exist_ok=True)
    for f in tmp.glob("f*.jpg"):
        f.unlink()
    # extract evenly
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(mp4),
            "-vf",
            f"fps=2,scale=320:-1",
            str(tmp / "f%03d.jpg"),
        ],
        capture_output=True,
        timeout=60,
    )
    frames = sorted(tmp.glob("f*.jpg"))[:n]
    if len(frames) < 2:
        return False
    from PIL import Image, ImageDraw, ImageFont

    imgs = [Image.open(f).convert("RGB") for f in frames]
    h = max(i.height for i in imgs)
    w = sum(i.width for i in imgs) + 8 * (len(imgs) + 1)
    canvas = Image.new("RGB", (w, h + 48), (12, 18, 32))
    x = 8
    for im in imgs:
        canvas.paste(im, (x, 8))
        x += im.width + 8
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 12)
    except Exception:
        font = ImageFont.load_default()
    draw.text(
        (8, h + 16),
        "gpu-host AnimateDiff · DreamShaper_8 + mm_sd_v15_v2 · CEO prompt · QQQ0 · not Grok cloud",
        fill=(180, 200, 220),
        font=font,
    )
    canvas.save(out_path, quality=90)
    return True


def main() -> int:
    if not SOURCE.is_file():
        print("missing source still", SOURCE, file=sys.stderr)
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    client = ComfyClient(COMFY_URL, timeout=60.0)
    stats = client.system_stats()
    if not stats.get("ok"):
        print("comfy down", stats, file=sys.stderr)
        return 1

    print("upload source…")
    server_name = upload_image(SOURCE, "ceo_source_still.jpg")
    print("uploaded as", server_name)

    gpu_peaks: list[float] = []
    panel_paths: list[Path] = []
    panel_meta: list[dict[str, Any]] = []
    labels = [
        "1. Wide meetup",
        "2. Medium desk",
        "3. Close-up face",
        "4. Over-shoulder board",
        "5. Profile walking",
        "6. Outdoor medium",
    ]

    t_all = time.time()
    for i, (key, prompt) in enumerate(PANELS):
        seed = 42000 + i * 17
        denoise = 0.62 if key != "closeup" else 0.55
        graph = build_img2img_graph(
            image_name=server_name,
            prompt=prompt,
            negative=NEG,
            seed=seed,
            denoise=denoise,
            width=768,
            height=512,
            steps=22,
            filename_prefix=f"ceo_sb_{key}",
        )
        g0 = sample_gpu()
        print(f"panel {i+1}/6 {key} …")
        waited = queue_and_wait(client, graph, timeout_s=180)
        g1 = sample_gpu()
        for g in (g0, g1):
            if g.get("gpu_util_pct") is not None:
                gpu_peaks.append(float(g["gpu_util_pct"]))
        if not waited.get("ok"):
            print("FAIL panel", key, waited, file=sys.stderr)
            return 2
        meta = first_image_meta(waited.get("outputs"))
        if not meta:
            print("no image meta", waited, file=sys.stderr)
            return 2
        raw = view_image(meta["filename"], subfolder=meta.get("subfolder") or "", folder_type=meta.get("type") or "output")
        dest = OUT_DIR / f"panel_{i+1}_{key}.png"
        dest.write_bytes(raw)
        panel_paths.append(dest)
        panel_meta.append(
            {
                "id": key,
                "seed": seed,
                "denoise": denoise,
                "prompt": prompt,
                "seconds": waited.get("seconds"),
                "prompt_id": waited.get("prompt_id"),
                "filename": meta["filename"],
            }
        )
        print(f"  ok {dest.name} {waited.get('seconds'):.1f}s")

    sheet = ASSETS / "example-storyboard-sheet.jpg"
    collage_storyboard(panel_paths, sheet, labels)
    peak = max(gpu_peaks) if gpu_peaks else None
    wall_sb = time.time() - t_all
    rec_sb = build_receipt(
        sheet,
        renderer="gpu-host_comfy_img2img_storyboard",
        provider="comfy",
        cloud_or_local="local",
        model=CKPT,
        host_role="gpu-host",
        qqq="QQQ0",
        prompt=f"6-panel CEO storyboard from {SOURCE.name}; identity=img2img+prompt-lock (IPAdapter weights incomplete)",
        wall_clock_s=round(wall_sb, 2),
        tokens={"input": None, "output": None, "total": None, "note": "n/a local comfy"},
        gpu={"peak_util_pct": peak, "note": "sampled around panel jobs"},
        sampled_by="host_monitor_or_ssh",
        extra={"panels": panel_meta, "comfy_url_role": "gpu-host:8188", "identity": "prompt-locked+img2img"},
    )
    write_receipt(rec_sb, path=RECEIPTS / "example-storyboard-sheet.receipt.json", chain=True)
    # also sidecar next to asset
    write_receipt(rec_sb, path=sheet.with_suffix(sheet.suffix + ".receipt.json"), chain=False)
    print("wrote", sheet)

    # Face polish
    print("face polish after…")
    polish_prompt = (
        f"portrait photo polish of {CEO_FACE}, clean studio key light, subtle skin cleanup, "
        "natural pores retained, professional headshot, navy backdrop, same identity as reference"
    )
    g_fp = build_img2img_graph(
        image_name=server_name,
        prompt=polish_prompt,
        negative=NEG + ", heavy makeup, plastic skin, beauty filter extreme",
        seed=42424,
        denoise=0.45,
        width=768,
        height=1024,
        steps=24,
        filename_prefix="ceo_face_polish",
    )
    t_fp = time.time()
    g0 = sample_gpu()
    waited = queue_and_wait(client, g_fp, timeout_s=180)
    g1 = sample_gpu()
    if not waited.get("ok"):
        print("face polish fail", waited, file=sys.stderr)
        return 3
    meta = first_image_meta(waited.get("outputs"))
    assert meta
    after_path = OUT_DIR / "face_after.png"
    after_path.write_bytes(
        view_image(meta["filename"], subfolder=meta.get("subfolder") or "", folder_type=meta.get("type") or "output")
    )
    # before: scaled source for fair compare
    before_path = OUT_DIR / "face_before.jpg"
    shutil.copy(SOURCE, before_path)
    polish_out = ASSETS / "example-face-polish.jpg"
    face_polish_sheet(before_path, after_path, polish_out)
    peak_fp = max(
        [float(g["gpu_util_pct"]) for g in (g0, g1) if g.get("gpu_util_pct") is not None] or [None]
    )
    rec_fp = build_receipt(
        polish_out,
        renderer="gpu-host_comfy_img2img_face_polish",
        provider="comfy",
        cloud_or_local="local",
        model=CKPT,
        host_role="gpu-host",
        qqq="QQQ0",
        prompt=polish_prompt,
        wall_clock_s=round(time.time() - t_fp, 2),
        tokens={"input": None, "output": None, "total": None, "note": "n/a local comfy"},
        gpu={"peak_util_pct": peak_fp},
        sampled_by="host_monitor_or_ssh",
        extra={
            "before": "00-ceo-source-still.jpg",
            "after_denoise": 0.45,
            "prompt_id": waited.get("prompt_id"),
            "identity": "img2img from source still",
        },
    )
    write_receipt(rec_fp, path=RECEIPTS / "example-face-polish.receipt.json", chain=True)
    write_receipt(rec_fp, path=polish_out.with_suffix(polish_out.suffix + ".receipt.json"), chain=False)
    print("wrote", polish_out)

    # AnimateDiff short loop (txt2vid with CEO prompt — honest: not true I2V LoadImage unless we add img2vid graph)
    print("AnimateDiff loop…")
    ad_prompt = (
        f"short loop of {CEO_FACE}, subtle head motion and blink, dual monitor glow, "
        "coding at desk, gentle camera push-in, coherent face, cinematic"
    )
    ad_graph = build_animatediff_graph(prompt=ad_prompt, negative=NEG, seed=42042)
    t_ad = time.time()
    g0 = sample_gpu()
    waited = queue_and_wait(client, ad_graph, timeout_s=240)
    g1 = sample_gpu()
    ad_ok = bool(waited.get("ok"))
    ad_mp4 = OUT_DIR / "ceo_animatediff.mp4"
    strip = ASSETS / "ceo-i2v-frame-strip.jpg"
    ad_meta: dict[str, Any] = {"ok": ad_ok, "seconds": time.time() - t_ad}
    if ad_ok:
        meta = first_image_meta(waited.get("outputs"))
        ad_meta["outputs_meta"] = meta
        ad_meta["prompt_id"] = waited.get("prompt_id")
        if meta and meta.get("filename", "").endswith(".mp4"):
            try:
                ad_mp4.write_bytes(
                    view_image(
                        meta["filename"],
                        subfolder=meta.get("subfolder") or "",
                        folder_type=meta.get("type") or "output",
                    )
                )
                extract_frame_strip(ad_mp4, strip)
                peak_ad = max(
                    [float(g["gpu_util_pct"]) for g in (g0, g1) if g.get("gpu_util_pct") is not None]
                    or [None]
                )
                rec_ad = build_receipt(
                    ad_mp4 if ad_mp4.is_file() else strip,
                    renderer="gpu-host_comfy_animatediff",
                    provider="comfy",
                    cloud_or_local="local",
                    model=f"{CKPT}+mm_sd_v15_v2.fp16",
                    host_role="gpu-host",
                    qqq="QQQ0",
                    prompt=ad_prompt,
                    wall_clock_s=round(time.time() - t_ad, 2),
                    tokens={"input": None, "output": None, "total": None, "note": "n/a local comfy"},
                    gpu={"peak_util_pct": peak_ad},
                    extra={
                        "note": "txt2vid AnimateDiff short loop for collage; identity prompt-locked CEO (not cloud I2V)",
                        "frames": 16,
                        "fps": 8,
                    },
                )
                write_receipt(rec_ad, path=RECEIPTS / "ceo-animatediff.receipt.json", chain=True)
                if strip.is_file():
                    write_receipt(
                        build_receipt(
                            strip,
                            renderer="gpu-host_comfy_animatediff_frame_strip",
                            provider="comfy",
                            cloud_or_local="local",
                            model=f"{CKPT}+mm_sd_v15_v2.fp16",
                            host_role="gpu-host",
                            qqq="QQQ0",
                            prompt=ad_prompt,
                            wall_clock_s=round(time.time() - t_ad, 2),
                            gpu={"peak_util_pct": peak_ad},
                        ),
                        path=RECEIPTS / "ceo-i2v-frame-strip.receipt.json",
                        chain=False,
                    )
                print("wrote", ad_mp4, strip)
            except Exception as exc:
                ad_meta["download_error"] = str(exc)
                print("ad download err", exc, file=sys.stderr)
        else:
            print("ad no mp4 meta", meta, file=sys.stderr)
            ad_ok = False
    else:
        print("ad failed", waited, file=sys.stderr)

    summary = {
        "schema": "mok_tua_ceo_capability_regen.v1",
        "ts_utc": _utc(),
        "comfy": COMFY_URL.replace("REDACTED-LAN-IP", "gpu-host"),
        "checkpoint": CKPT,
        "identity": "prompt-locked+img2img from 00-ceo-source-still (IPAdapter weights incomplete on host)",
        "storyboard": str(sheet),
        "face_polish": str(polish_out),
        "animatediff": ad_meta,
        "gpu_peak_samples": gpu_peaks,
        "total_seconds": round(time.time() - t_all, 2),
    }
    (OUT_DIR / "regen_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0 if ad_ok or sheet.is_file() else 4


if __name__ == "__main__":
    raise SystemExit(main())
