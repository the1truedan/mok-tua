#!/usr/bin/env python3
"""0.5.7: CEO panels + polish via IPAdapter plus-face (img2img) on gpu-host Comfy.

InsightFace FaceID residual: buffalo_l incomplete / antelope loader error on host —
this path uses ip-adapter-plus-face_sd15 + clip_vision_h (no InsightFace).

Usage:
  COMFY_URL=http://gpu-host:8188 python3 scripts/regen_ceo_ipadapter_panels_0_5_7.py
"""

from __future__ import annotations

import json
import os
import shutil
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

COMFY_URL = os.environ.get("COMFY_URL", "http://gpu-host:8188").rstrip("/")
CKPT = os.environ.get("MOK_TUA_CKPT", "DreamShaper_8_pruned.safetensors")
IP_FILE = "ip-adapter-plus-face_sd15.safetensors"
CLIP_VISION = "clip_vision_h.safetensors"
SOURCE = ROOT / "docs/assets/pres-smoke/00-ceo-source-still.jpg"
OUT_DIR = Path(os.environ.get("MOK_TUA_CEO_OUT", str(ROOT / "work" / "ceo_capability_regen")))
PANELS_DIR = ROOT / "docs/assets/capabilities/panels"
ASSETS = ROOT / "docs/assets"
RECEIPTS = ASSETS / "receipts"

NEG = (
    "blurry, low quality, watermark, deformed face, extra limbs, wrong gender, "
    "woman, female, child, text gibberish, logo spam, cartoon, anime, plastic skin, "
    "hearts on forehead, symbols on forehead"
)

CEO = (
    "same man as the reference selfie photo, fair skin, freckles, light red facial patches, "
    "green-hazel eyes, short sandy brown hair, goofy intense expression, "
    "handwritten black marker letters spelling ceo on forehead (not hearts, not doodles)"
)

PANELS: list[tuple[str, str, float, int, int]] = [
    # key, scene prompt, denoise, w, h
    (
        "wide",
        f"cinematic storyboard panel, wide shot tech meetup classroom, {CEO}, "
        "blue hoodie, standing by projector showing mok-tua, audience laptops, natural light, 35mm photo",
        0.52,
        768,
        512,
    ),
    (
        "medium",
        f"cinematic storyboard panel, medium shot at desk, {CEO}, sticky notes, "
        "dual monitors with terminal, teaching a colleague, warm lamp, photoreal",
        0.50,
        768,
        512,
    ),
    (
        "closeup",
        f"cinematic storyboard panel, close-up face, {CEO}, speaking, shallow DOF, soft key light, photoreal",
        0.38,
        640,
        768,
    ),
    (
        "ots",
        f"cinematic storyboard panel, over-shoulder whiteboard, {CEO} partial profile, "
        "writing shots stills I2V on board, office, photoreal",
        0.52,
        768,
        512,
    ),
    (
        "profile",
        f"cinematic storyboard panel, profile walking hallway, {CEO}, notebook, candid, fluorescent hallway",
        0.50,
        768,
        512,
    ),
    (
        "outdoor",
        f"cinematic storyboard panel, outdoor medium campus path, {CEO}, after demo, brick buildings bokeh",
        0.50,
        768,
        512,
    ),
]

LABELS = [
    "1. Wide meetup",
    "2. Medium desk",
    "3. Close-up face",
    "4. Over-shoulder board",
    "5. Profile walking",
    "6. Outdoor medium",
]


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def upload_image(path: Path, name: str = "ceo_source_still.jpg") -> str:
    boundary = "----MokTuaBoundary7MA4YWxkTrZu0gW"
    data = path.read_bytes()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{name}"\r\n'
        f"Content-Type: image/jpeg\r\n\r\n"
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
    with urllib.request.urlopen(req, timeout=60) as resp:
        out = json.loads(resp.read().decode())
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
        items = node_out.get("images")
        if items:
            return items[0]
    return None


def build_ipadapter_img2img(
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
    ip_weight: float = 0.72,
) -> dict[str, Any]:
    """LoadImage → scale → IPAdapter plus-face → VAEEncode → KSampler → SaveImage."""
    return {
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "21": {"class_type": "IPAdapterModelLoader", "inputs": {"ipadapter_file": IP_FILE}},
        "23": {"class_type": "CLIPVisionLoader", "inputs": {"clip_name": CLIP_VISION}},
        "16": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        "2": {
            "class_type": "ImageScale",
            "inputs": {
                "image": ["16", 0],
                "upscale_method": "lanczos",
                "width": width,
                "height": height,
                "crop": "center",
            },
        },
        "17": {
            "class_type": "IPAdapterAdvanced",
            "inputs": {
                "model": ["4", 0],
                "ipadapter": ["21", 0],
                "image": ["2", 0],
                "weight": ip_weight,
                "weight_type": "linear",
                "combine_embeds": "concat",
                "start_at": 0.0,
                "end_at": 1.0,
                "embeds_scaling": "V only",
                "clip_vision": ["23", 0],
            },
        },
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["4", 1]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": negative, "clip": ["4", 1]}},
        "10": {"class_type": "VAEEncode", "inputs": {"pixels": ["2", 0], "vae": ["4", 2]}},
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": 6.5,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": denoise,
                "model": ["17", 0],
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


def collage_storyboard(panel_paths: list[Path], out_path: Path, labels: list[str]) -> None:
    from PIL import Image, ImageDraw, ImageFont

    cell_w, cell_h = 400, 300
    pad = 24
    label_h = 36
    cols, rows = 3, 2
    W = pad + cols * (cell_w + pad)
    H = pad + rows * (cell_h + label_h + pad) + 48
    canvas = Image.new("RGB", (W, H), (245, 242, 236))
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 16)
        font_sm = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 11)
    except Exception:
        font = ImageFont.load_default()
        font_sm = font
    for i, p in enumerate(panel_paths[:6]):
        r, c = divmod(i, cols)
        x = pad + c * (cell_w + pad)
        y = pad + r * (cell_h + label_h + pad)
        im = Image.open(p).convert("RGB")
        im.thumbnail((cell_w, cell_h))
        ox = x + (cell_w - im.width) // 2
        oy = y + (cell_h - im.height) // 2
        canvas.paste(im, (ox, oy))
        draw.text((x, y + cell_h + 6), labels[i], fill=(30, 30, 30), font=font)
    foot = (
        "mok-tua 0.5.7 · IPAdapter plus-face img2img from 00-ceo-source-still · "
        "QQQ0 · gpu-host · FaceID InsightFace residual (models incomplete)"
    )
    draw.text((pad, H - 28), foot, fill=(80, 80, 80), font=font_sm)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, quality=92)


def face_polish_sheet(before: Path, after: Path, out: Path) -> None:
    from PIL import Image, ImageDraw, ImageFont

    b = Image.open(before).convert("RGB")
    a = Image.open(after).convert("RGB")
    h = 480
    b.thumbnail((360, h))
    a.thumbnail((360, h))
    pad = 20
    W = pad * 3 + b.width + a.width
    H = pad * 3 + max(b.height, a.height) + 40
    canvas = Image.new("RGB", (W, H), (20, 24, 36))
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 14)
    except Exception:
        font = ImageFont.load_default()
    canvas.paste(b, (pad, pad + 24))
    canvas.paste(a, (pad * 2 + b.width, pad + 24))
    draw.text((pad, 6), "BEFORE · 00-ceo-source-still", fill=(200, 200, 220), font=font)
    draw.text((pad * 2 + b.width, 6), "AFTER · IPAdapter plus-face polish", fill=(200, 220, 200), font=font)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, quality=92)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PANELS_DIR.mkdir(parents=True, exist_ok=True)
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    if not SOURCE.is_file():
        print("missing source", SOURCE, file=sys.stderr)
        return 1

    client = ComfyClient(COMFY_URL)
    print("upload", SOURCE)
    server_name = upload_image(SOURCE)
    print("server image", server_name)

    panel_paths: list[Path] = []
    panel_meta: list[dict[str, Any]] = []
    t_all = time.time()

    for i, (key, prompt, denoise, w, h) in enumerate(PANELS):
        seed = 43000 + i * 19
        graph = build_ipadapter_img2img(
            image_name=server_name,
            prompt=prompt,
            negative=NEG,
            seed=seed,
            denoise=denoise,
            width=w,
            height=h,
            steps=22,
            filename_prefix=f"ceo57_sb_{key}",
            ip_weight=0.70 if key != "closeup" else 0.78,
        )
        print(f"panel {i+1}/6 {key} denoise={denoise} …")
        waited = queue_and_wait(client, graph, timeout_s=200)
        if not waited.get("ok"):
            print("FAIL", key, waited, file=sys.stderr)
            return 2
        meta = first_image_meta(waited.get("outputs"))
        if not meta:
            print("no meta", waited, file=sys.stderr)
            return 2
        raw = view_image(
            meta["filename"],
            subfolder=meta.get("subfolder") or "",
            folder_type=meta.get("type") or "output",
        )
        dest_work = OUT_DIR / f"panel_{i+1}_{key}.png"
        dest_work.write_bytes(raw)
        dest_assets = PANELS_DIR / f"{i+1:02d}-{key}.jpg"
        from PIL import Image
        Image.open(dest_work).convert("RGB").save(dest_assets, quality=92)
        panel_paths.append(dest_work)
        panel_meta.append(
            {
                "id": key,
                "path": str(dest_assets.relative_to(ROOT)),
                "seed": seed,
                "denoise": denoise,
                "prompt": prompt,
                "seconds": waited.get("seconds"),
                "prompt_id": waited.get("prompt_id"),
                "ipadapter": IP_FILE,
                "ip_weight": 0.70 if key != "closeup" else 0.78,
            }
        )
        # per-panel mini receipt
        write_receipt(
            build_receipt(
                dest_assets,
                renderer="gpu-host_comfy_ipadapter_plusface_img2img",
                provider="comfy",
                cloud_or_local="local",
                model=f"{CKPT}+{IP_FILE}",
                host_role="gpu-host",
                qqq="QQQ0",
                prompt=prompt,
                wall_clock_s=round(float(waited.get("seconds") or 0), 2),
                extra={"seed": seed, "denoise": denoise, "faceid_insightface": "residual_incomplete"},
            ),
            path=dest_assets.with_suffix(".jpg.receipt.json"),
            chain=False,
        )
        print(f"  ok {dest_assets.name} {waited.get('seconds'):.1f}s")

    sheet = ASSETS / "example-storyboard-sheet.jpg"
    collage_storyboard(panel_paths, sheet, LABELS)
    wall_sb = time.time() - t_all
    rec_sb = build_receipt(
        sheet,
        renderer="gpu-host_comfy_ipadapter_plusface_storyboard",
        provider="comfy",
        cloud_or_local="local",
        model=f"{CKPT}+{IP_FILE}",
        host_role="gpu-host",
        qqq="QQQ0",
        prompt=f"6-panel CEO storyboard IPAdapter plus-face img2img from {SOURCE.name}",
        wall_clock_s=round(wall_sb, 2),
        tokens={"input": None, "output": None, "total": None, "note": "n/a local comfy"},
        extra={
            "panels": panel_meta,
            "identity": "ip-adapter-plus-face_sd15 + img2img from CEO still",
            "faceid_insightface": "residual — buffalo_l incomplete / antelope loader error",
            "version": "0.5.7",
        },
    )
    write_receipt(rec_sb, path=RECEIPTS / "example-storyboard-sheet.receipt.json", chain=True)
    write_receipt(rec_sb, path=sheet.with_suffix(sheet.suffix + ".receipt.json"), chain=False)
    print("wrote", sheet)

    # Face polish — lower denoise preserve forehead text
    polish_prompt = (
        f"portrait photo polish of {CEO}, clean studio key light, subtle skin cleanup, "
        "natural pores retained, professional headshot, navy backdrop, same identity"
    )
    g_fp = build_ipadapter_img2img(
        image_name=server_name,
        prompt=polish_prompt,
        negative=NEG + ", heavy makeup, plastic skin",
        seed=42424,
        denoise=0.32,
        width=640,
        height=800,
        steps=24,
        filename_prefix="ceo57_face_polish",
        ip_weight=0.80,
    )
    t_fp = time.time()
    waited = queue_and_wait(client, g_fp, timeout_s=200)
    if not waited.get("ok"):
        print("polish fail", waited, file=sys.stderr)
        return 3
    meta = first_image_meta(waited.get("outputs"))
    assert meta
    after_path = OUT_DIR / "face_after.png"
    after_path.write_bytes(
        view_image(meta["filename"], subfolder=meta.get("subfolder") or "", folder_type=meta.get("type") or "output")
    )
    before_path = OUT_DIR / "face_before.jpg"
    shutil.copy(SOURCE, before_path)
    polish_out = ASSETS / "example-face-polish.jpg"
    face_polish_sheet(before_path, after_path, polish_out)
    rec_fp = build_receipt(
        polish_out,
        renderer="gpu-host_comfy_ipadapter_plusface_polish",
        provider="comfy",
        cloud_or_local="local",
        model=f"{CKPT}+{IP_FILE}",
        host_role="gpu-host",
        qqq="QQQ0",
        prompt=polish_prompt,
        wall_clock_s=round(time.time() - t_fp, 2),
        extra={"before": "00-ceo-source-still.jpg", "denoise": 0.32, "version": "0.5.7"},
    )
    write_receipt(rec_fp, path=RECEIPTS / "example-face-polish.receipt.json", chain=True)
    write_receipt(rec_fp, path=polish_out.with_suffix(polish_out.suffix + ".receipt.json"), chain=False)
    print("wrote", polish_out)

    summary = {
        "schema": "mok_tua_ceo_ipadapter_panels.v1",
        "version": "0.5.7",
        "ts_utc": _utc(),
        "comfy_role": "gpu-host:8188",
        "ipadapter": IP_FILE,
        "faceid_insightface": "residual",
        "storyboard": str(sheet),
        "face_polish": str(polish_out),
        "panels": panel_meta,
        "total_seconds": round(time.time() - t_all, 2),
    }
    (OUT_DIR / "regen_0_5_7_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
