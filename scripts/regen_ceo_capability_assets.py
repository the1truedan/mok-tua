#!/usr/bin/env python3
"""Regenerate CEO capability art on GPU-host Comfy with IPAdapter FaceID PLUS V2.

Identity seed: docs/assets/pres-smoke/00-ceo-source-still.jpg

Outputs (committed assets):
  docs/assets/example-storyboard-sheet.jpg
  docs/assets/example-face-polish.jpg
  docs/assets/ceo-i2v-frame-strip.jpg
  docs/assets/hero-prompt-to-product.jpg  (compose from FaceID panels + strip)

Usage:
  COMFY_URL=http://gpu-host:8188 python3 scripts/regen_ceo_capability_assets.py
  SKIP_AD=1  … skip AnimateDiff
  SKIP_HERO=1 … skip hero compose
"""

from __future__ import annotations

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

from backends.comfy import ComfyClient  # noqa: E402
from artifact_receipt import build_receipt, write_receipt  # noqa: E402

try:
    from host_monitor import sample_host  # noqa: E402
except Exception:  # pragma: no cover
    sample_host = None  # type: ignore

COMFY_URL = os.environ.get("COMFY_URL", os.environ.get("COMFY_GPU_URL", "http://gpu-host:8188")).rstrip("/")
CKPT = os.environ.get("MOK_TUA_CKPT", "DreamShaper_8_pruned.safetensors")
# Explicit loaders (Unified FaceID needs ViT-H filename pattern our pool lacks)
FACEID_BIN = os.environ.get("MOK_TUA_FACEID_BIN", "ip-adapter-faceid-plusv2_sd15.bin")
FACEID_LORA = os.environ.get("MOK_TUA_FACEID_LORA_FILE", "ip-adapter-faceid-plusv2_sd15_lora.safetensors")
CLIP_VISION = os.environ.get("MOK_TUA_CLIP_VISION", "clip_vision_h.safetensors")
INSIGHTFACE = os.environ.get("MOK_TUA_INSIGHTFACE", "buffalo_l")  # full pack under Comfy models/insightface
FACEID_WEIGHT = float(os.environ.get("MOK_TUA_FACEID_WEIGHT", "0.95"))
FACEID_WEIGHT_V2 = float(os.environ.get("MOK_TUA_FACEID_WEIGHT_V2", "1.15"))
LORA_STRENGTH = float(os.environ.get("MOK_TUA_FACEID_LORA", "0.65"))
SOURCE = ROOT / "docs/assets/pres-smoke/00-ceo-source-still.jpg"
OUT_DIR = Path(os.environ.get("MOK_TUA_CEO_OUT", str(ROOT / "work" / "ceo_capability_regen")))
ASSETS = ROOT / "docs" / "assets"
RECEIPTS = ASSETS / "receipts"
PANELS_DIR = ASSETS / "capabilities" / "panels"

NEG = (
    "blurry, low quality, watermark, deformed face, extra limbs, wrong gender, "
    "woman, female, child, text gibberish, logo spam, cartoon, anime, "
    "different person, face morph, uncanny"
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
    boundary = "----MokTuaBoundary7MA4YWxkTrZu0gW"
    data = path.read_bytes()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{name}"\r\n'
        f"Content-Type: image/jpeg\r\n\r\n"
    ).encode() + data + (
        f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{boundary}--\r\n"
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
        for key in ("images", "gifs"):
            items = node_out.get(key)
            if items:
                return {"key": key, **items[0]}
    return None


def prepare_face_ref(source: Path, out: Path, canvas: int = 1024, face_h: int = 520) -> Path:
    """Pad extreme close-up so InsightFace det_size=640 can see a full face."""
    from PIL import Image

    im = Image.open(source).convert("RGB")
    bg = Image.new("RGB", (canvas, canvas), (40, 44, 52))
    ratio = face_h / im.height
    nw = int(im.width * ratio)
    face = im.resize((nw, face_h), Image.Resampling.LANCZOS)
    x = (canvas - nw) // 2
    y = max(0, (canvas - face_h) // 2 - 40)
    bg.paste(face, (x, y))
    out.parent.mkdir(parents=True, exist_ok=True)
    bg.save(out, quality=95)
    return out


def _faceid_core_nodes(image_name: str, *, faceid_weight: float, faceid_weight_v2: float, lora_strength: float) -> dict[str, Any]:
    """Shared explicit FaceID stack: ckpt+lora+clip_vision+ipadapter+insightface+apply."""
    return {
        "1": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "14": {
            "class_type": "LoraLoader",
            "inputs": {
                "model": ["4", 0],
                "clip": ["4", 1],
                "lora_name": FACEID_LORA,
                "strength_model": lora_strength,
                "strength_clip": max(0.4, lora_strength - 0.1),
            },
        },
        "15": {"class_type": "CLIPVisionLoader", "inputs": {"clip_name": CLIP_VISION}},
        "16": {"class_type": "IPAdapterModelLoader", "inputs": {"ipadapter_file": FACEID_BIN}},
        "17": {
            "class_type": "IPAdapterInsightFaceLoader",
            "inputs": {"provider": "CUDA", "model_name": INSIGHTFACE},
        },
        "21": {
            "class_type": "IPAdapterFaceID",
            "inputs": {
                "model": ["14", 0],
                "ipadapter": ["16", 0],
                "image": ["1", 0],
                "weight": faceid_weight,
                "weight_faceidv2": faceid_weight_v2,
                "weight_type": "linear",
                "combine_embeds": "concat",
                "start_at": 0.0,
                "end_at": 1.0,
                "embeds_scaling": "V only",
                "clip_vision": ["15", 0],
                "insightface": ["17", 0],
            },
        },
    }


def build_faceid_txt2img_graph(
    *,
    image_name: str,
    prompt: str,
    negative: str,
    seed: int,
    width: int,
    height: int,
    steps: int,
    filename_prefix: str,
    faceid_weight: float = FACEID_WEIGHT,
    faceid_weight_v2: float = FACEID_WEIGHT_V2,
    lora_strength: float = LORA_STRENGTH,
) -> dict[str, Any]:
    """LoadImage face ref + explicit FaceID + EmptyLatent txt2img."""
    g = _faceid_core_nodes(
        image_name,
        faceid_weight=faceid_weight,
        faceid_weight_v2=faceid_weight_v2,
        lora_strength=lora_strength,
    )
    g.update(
        {
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": width, "height": height, "batch_size": 1},
            },
            "6": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["14", 1]}},
            "7": {"class_type": "CLIPTextEncode", "inputs": {"text": negative, "clip": ["14", 1]}},
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": 7.0,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["21", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0],
                },
            },
            "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
            "9": {
                "class_type": "SaveImage",
                "inputs": {"filename_prefix": filename_prefix, "images": ["8", 0]},
            },
        }
    )
    return g


def build_faceid_img2img_graph(
    *,
    image_name: str,
    init_image_name: str,
    prompt: str,
    negative: str,
    seed: int,
    denoise: float,
    width: int,
    height: int,
    steps: int,
    filename_prefix: str,
) -> dict[str, Any]:
    """FaceID-conditioned img2img. image_name=face ref; init_image_name=pixels to encode."""
    g = _faceid_core_nodes(
        image_name,
        faceid_weight=FACEID_WEIGHT,
        faceid_weight_v2=FACEID_WEIGHT_V2,
        lora_strength=LORA_STRENGTH,
    )
    # override load for init if different file — use second LoadImage
    g["2"] = {"class_type": "LoadImage", "inputs": {"image": init_image_name}}
    g["2s"] = {
        "class_type": "ImageScale",
        "inputs": {
            "image": ["2", 0],
            "upscale_method": "lanczos",
            "width": width,
            "height": height,
            "crop": "center",
        },
    }
    g.update(
        {
            "10": {"class_type": "VAEEncode", "inputs": {"pixels": ["2s", 0], "vae": ["4", 2]}},
            "6": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["14", 1]}},
            "7": {"class_type": "CLIPTextEncode", "inputs": {"text": negative, "clip": ["14", 1]}},
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": 7.0,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": denoise,
                    "model": ["21", 0],
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
    )
    return g


def build_faceid_animatediff_graph(
    *,
    image_name: str,
    prompt: str,
    negative: str,
    seed: int,
    frames: int = 16,
    width: int = 512,
    height: int = 512,
    steps: int = 16,
    filename_prefix: str = "ceo_ad_faceid",
) -> dict[str, Any]:
    """FaceID-conditioned AnimateDiff short loop."""
    g = _faceid_core_nodes(
        image_name,
        faceid_weight=FACEID_WEIGHT,
        faceid_weight_v2=FACEID_WEIGHT_V2,
        lora_strength=LORA_STRENGTH,
    )
    g.update(
        {
            "11": {
                "class_type": "ADE_AnimateDiffLoaderGen1",
                "inputs": {
                    "model": ["21", 0],
                    "model_name": "mm_sd_v15_v2.fp16.safetensors",
                    "beta_schedule": "autoselect",
                },
            },
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": width, "height": height, "batch_size": frames},
            },
            "6": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["14", 1]}},
            "7": {"class_type": "CLIPTextEncode", "inputs": {"text": negative, "clip": ["14", 1]}},
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
    )
    return g


def sample_gpu() -> dict[str, Any]:
    if sample_host is not None:
        try:
            s = sample_host("gpu-host")
            if s.get("ok"):
                return s
        except Exception:
            pass
    try:
        proc = subprocess.run(
            [
                "ssh",
                "-o",
                "BatchMode=yes",
                "-o",
                "ConnectTimeout=4",
                os.environ.get("MOCK_TUA_SSH_TARGET", "operator@gpu-host"),
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
        draw.rectangle([x - 4, y - 4, x + cell_w + 4, y + cell_h + label_h + 4], fill=(255, 255, 255))
        canvas.paste(im, (x, y))
        label = labels[i] if i < len(labels) else p.stem
        draw.text((x + 8, y + cell_h + 8), label, fill=(30, 30, 30), font=font)
    cite = (
        "mok-tua · GPU-host Comfy · DreamShaper_8 · IPAdapter FaceID PLUS V2 · "
        "source 00-ceo-source-still · QQQ0"
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
    draw.rectangle([16, 16, 140, 48], fill=(0, 0, 0))
    draw.rectangle([bw + 16, 16, bw + 120, 48], fill=(0, 0, 0))
    draw.text((28, 22), "BEFORE", fill=(255, 255, 255), font=font)
    draw.text((bw + 28, 22), "AFTER", fill=(255, 255, 255), font=font)
    cite = (
        "mok-tua · GPU-host Comfy FaceID PLUS V2 · DreamShaper_8 · "
        "source 00-ceo-source-still · QQQ0"
    )
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
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(mp4),
            "-vf",
            "fps=2,scale=320:-1",
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
        "GPU-host AnimateDiff + FaceID PLUS V2 · DreamShaper_8 + mm_sd_v15_v2 · "
        "CEO source · QQQ0 · not Grok cloud",
        fill=(180, 200, 220),
        font=font,
    )
    canvas.save(out_path, quality=90)
    return True


def compose_hero(panel_paths: list[Path], strip_or_panel: Path, out_path: Path) -> None:
    """1280x720 hero: storyboard board of CEO panels + video chrome with CEO still/frame."""
    from PIL import Image, ImageDraw, ImageFont

    W, H = 1280, 720
    canvas = Image.new("RGB", (W, H), (12, 22, 40))
    draw = ImageDraw.Draw(canvas)
    # gradient-ish side glow
    for x in range(W):
        t = x / W
        r = int(12 + 30 * t)
        g = int(22 + 10 * (1 - t))
        b = int(40 + 20 * t)
        draw.line([(x, 0), (x, H)], fill=(r, g, b))

    try:
        font_lg = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 22)
        font_sm = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 14)
        font_xs = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 11)
    except Exception:
        font_lg = font_sm = font_xs = ImageFont.load_default()

    draw.text((36, 28), "mok-tua", fill=(180, 200, 230), font=font_lg)
    draw.text((36, 56), "storyboard  ·  animate  ·  teach", fill=(140, 160, 190), font=font_xs)

    # Board
    board_x, board_y = 48, 96
    board_w, board_h = 760, 560
    draw.rounded_rectangle(
        [board_x - 8, board_y - 8, board_x + board_w + 8, board_y + board_h + 8],
        radius=10,
        fill=(28, 32, 40),
        outline=(70, 80, 100),
        width=3,
    )
    draw.rectangle(
        [board_x, board_y, board_x + board_w, board_y + board_h],
        fill=(248, 246, 240),
    )

    cols, rows = 3, 2
    pad = 16
    cell_w = (board_w - pad * (cols + 1)) // cols
    cell_h = (board_h - pad * (rows + 1)) // rows
    for i, p in enumerate(panel_paths[:6]):
        r, c = divmod(i, cols)
        x = board_x + pad + c * (cell_w + pad)
        y = board_y + pad + r * (cell_h + pad)
        im = Image.open(p).convert("RGB")
        im = im.resize((cell_w, cell_h - 18), Image.Resampling.LANCZOS)
        draw.rectangle([x - 2, y - 2, x + cell_w + 2, y + cell_h + 2], outline=(200, 190, 170), width=1)
        canvas.paste(im, (x, y))
        draw.text((x + 4, y + cell_h - 16), f"{i+1:02d}", fill=(80, 80, 80), font=font_xs)

    # Player chrome — ONE clean still only.
    # Never paste a multi-frame AD strip (wide crop of glitched frames → black "blade" on forehead).
    px, py = 860, 200
    pw, ph = 360, 280
    draw.rounded_rectangle(
        [px - 6, py - 6, px + pw + 6, py + ph + 40],
        radius=14,
        fill=(18, 24, 36),
        outline=(240, 160, 60),
        width=2,
    )
    if strip_or_panel.is_file():
        im = Image.open(strip_or_panel).convert("RGB")
        # Multi-frame strip → first frame cell only
        if im.width > im.height * 1.8:
            content_h = im.height - 48 if im.height > 100 else im.height
            frame_w = max(1, (im.width - 8 * 5) // 4)
            im = im.crop((8, 8, 8 + frame_w, 8 + max(1, content_h)))
        # cover-crop to player aspect
        target_ratio = pw / ph
        ir = im.width / max(1, im.height)
        if ir > target_ratio:
            nh = im.height
            nw = int(nh * target_ratio)
            left = (im.width - nw) // 2
            im = im.crop((left, 0, left + nw, nh))
        else:
            nw = im.width
            nh = int(nw / target_ratio)
            top = max(0, (im.height - nh) // 2 - nh // 10)
            top = min(top, max(0, im.height - nh))
            im = im.crop((0, top, nw, top + nh))
        im = im.resize((pw, ph), Image.Resampling.LANCZOS)
        canvas.paste(im, (px, py))
    cx, cy = px + pw // 2, py + ph // 2
    draw.ellipse([cx - 32, cy - 32, cx + 32, cy + 32], fill=(240, 160, 60))
    draw.polygon([(cx - 10, cy - 16), (cx - 10, cy + 16), (cx + 18, cy)], fill=(20, 20, 24))
    draw.rectangle([px, py + ph, px + pw, py + ph + 28], fill=(12, 16, 24))
    draw.text((px + 12, py + ph + 8), "FaceID still · clean player", fill=(180, 190, 210), font=font_xs)

    draw.text((860, 500), "CEO identity from", fill=(160, 175, 200), font=font_sm)
    draw.text((860, 522), "00-ceo-source-still", fill=(200, 210, 230), font=font_sm)
    draw.text((860, 548), "GPU-host · FaceID PLUS V2 · QQQ0", fill=(120, 140, 170), font=font_xs)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, quality=92)


def main() -> int:
    if not SOURCE.is_file():
        print("missing source still", SOURCE, file=sys.stderr)
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    PANELS_DIR.mkdir(parents=True, exist_ok=True)

    client = ComfyClient(COMFY_URL, timeout=60.0)
    stats = client.system_stats()
    if not stats.get("ok"):
        print("comfy down", stats, file=sys.stderr)
        return 1

    print("prep + upload face ref (padded for InsightFace)…")
    face_prep = prepare_face_ref(SOURCE, OUT_DIR / "ceo_face_padded.jpg")
    server_name = upload_image(face_prep, "ceo_face_padded.jpg")
    source_name = upload_image(SOURCE, "ceo_source_still.jpg")
    print("uploaded face_ref=", server_name, "source=", source_name)
    print(f"FaceID bin={FACEID_BIN} weight={FACEID_WEIGHT} v2={FACEID_WEIGHT_V2} insight={INSIGHTFACE}")

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
        seed = 52000 + i * 19
        # closeup: slightly lower weight so face stays natural
        fw = FACEID_WEIGHT if key != "closeup" else min(FACEID_WEIGHT, 0.9)
        graph = build_faceid_txt2img_graph(
            image_name=server_name,
            prompt=prompt,
            negative=NEG,
            seed=seed,
            width=768,
            height=512,
            steps=24,
            filename_prefix=f"ceo_faceid_{key}",
            faceid_weight=fw,
        )
        g0 = sample_gpu()
        print(f"panel {i+1}/6 {key} FaceID…")
        waited = queue_and_wait(client, graph, timeout_s=240)
        g1 = sample_gpu()
        for g in (g0, g1):
            if g.get("gpu_util_pct") is not None:
                gpu_peaks.append(float(g["gpu_util_pct"]))
        if not waited.get("ok"):
            print("FAIL panel", key, waited, file=sys.stderr)
            # try dump node errors
            print(json.dumps(waited, indent=2, default=str)[:2000], file=sys.stderr)
            return 2
        meta = first_image_meta(waited.get("outputs"))
        if not meta:
            print("no image meta", waited, file=sys.stderr)
            return 2
        raw = view_image(meta["filename"], subfolder=meta.get("subfolder") or "", folder_type=meta.get("type") or "output")
        dest = OUT_DIR / f"panel_{i+1}_{key}.png"
        dest.write_bytes(raw)
        # also commit-friendly copy under capabilities/panels
        dest_jpg = PANELS_DIR / f"{i+1:02d}-{key}.jpg"
        try:
            from PIL import Image

            Image.open(dest).convert("RGB").save(dest_jpg, quality=90)
        except Exception:
            shutil.copy(dest, dest_jpg.with_suffix(".png"))
        panel_paths.append(dest)
        panel_meta.append(
            {
                "id": key,
                "seed": seed,
                "prompt": prompt,
                "faceid_bin": FACEID_BIN,
                "faceid_weight": fw,
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
        renderer="gpu_comfy_faceid_storyboard",
        provider="comfy",
        cloud_or_local="local",
        model=f"{CKPT}+{FACEID_BIN}",
        host_role="gpu-host",
        qqq="QQQ0",
        prompt=f"6-panel CEO storyboard FaceID from {SOURCE.name}",
        wall_clock_s=round(wall_sb, 2),
        tokens={"input": None, "output": None, "total": None, "note": "n/a local comfy"},
        gpu={"peak_util_pct": peak, "note": "sampled around panel jobs"},
        sampled_by="host_monitor_or_ssh",
        extra={
            "panels": panel_meta,
            "comfy_url_role": "gpu-host:8188",
            "identity": "IPAdapter FaceID PLUS V2 + padded 00-ceo-source-still",
            "face_ref": "ceo_face_padded.jpg",
        },
    )
    write_receipt(rec_sb, path=RECEIPTS / "example-storyboard-sheet.receipt.json", chain=True)
    write_receipt(rec_sb, path=sheet.with_suffix(sheet.suffix + ".receipt.json"), chain=False)
    print("wrote", sheet)

    # Face polish
    print("face polish FaceID…")
    polish_prompt = (
        f"portrait photo polish of {CEO_FACE}, clean studio key light, subtle skin cleanup, "
        "natural pores retained, professional headshot, navy backdrop, same identity as reference, "
        "handwritten black marker ceo on forehead visible"
    )
    g_fp = build_faceid_img2img_graph(
        image_name=server_name,
        init_image_name=source_name,
        prompt=polish_prompt,
        negative=NEG + ", heavy makeup, plastic skin, beauty filter extreme",
        seed=52424,
        denoise=0.42,
        width=768,
        height=1024,
        steps=24,
        filename_prefix="ceo_faceid_polish",
    )
    t_fp = time.time()
    g0 = sample_gpu()
    waited = queue_and_wait(client, g_fp, timeout_s=240)
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
    before_path = OUT_DIR / "face_before.jpg"
    shutil.copy(SOURCE, before_path)
    polish_out = ASSETS / "example-face-polish.jpg"
    face_polish_sheet(before_path, after_path, polish_out)
    peak_fp = max(
        [float(g["gpu_util_pct"]) for g in (g0, g1) if g.get("gpu_util_pct") is not None] or [0.0]
    )
    rec_fp = build_receipt(
        polish_out,
        renderer="gpu_comfy_faceid_face_polish",
        provider="comfy",
        cloud_or_local="local",
        model=f"{CKPT}+{FACEID_BIN}",
        host_role="gpu-host",
        qqq="QQQ0",
        prompt=polish_prompt,
        wall_clock_s=round(time.time() - t_fp, 2),
        tokens={"input": None, "output": None, "total": None, "note": "n/a local comfy"},
        gpu={"peak_util_pct": peak_fp},
        sampled_by="host_monitor_or_ssh",
        extra={
            "before": "00-ceo-source-still.jpg",
            "after_denoise": 0.42,
            "prompt_id": waited.get("prompt_id"),
            "identity": "FaceID PLUS V2 img2img from source still",
        },
    )
    write_receipt(rec_fp, path=RECEIPTS / "example-face-polish.receipt.json", chain=True)
    write_receipt(rec_fp, path=polish_out.with_suffix(polish_out.suffix + ".receipt.json"), chain=False)
    print("wrote", polish_out)

    strip = ASSETS / "ceo-i2v-frame-strip.jpg"
    ad_ok = False
    ad_meta: dict[str, Any] = {}
    ad_mp4 = OUT_DIR / "ceo_animatediff_faceid.mp4"
    if os.environ.get("SKIP_AD", "").strip() in ("1", "true", "yes"):
        print("SKIP_AD set — keep existing strip if present")
        ad_meta = {"ok": False, "skipped": True}
    else:
        print("AnimateDiff + FaceID loop…")
        ad_prompt = (
            f"short loop of {CEO_FACE}, subtle head motion and blink, dual monitor glow, "
            "coding at desk, gentle camera push-in, coherent face, cinematic"
        )
        ad_graph = build_faceid_animatediff_graph(
            image_name=server_name,
            prompt=ad_prompt,
            negative=NEG,
            seed=52042,
        )
        t_ad = time.time()
        g0 = sample_gpu()
        waited = queue_and_wait(client, ad_graph, timeout_s=360)
        g1 = sample_gpu()
        ad_ok = bool(waited.get("ok"))
        ad_meta = {"ok": ad_ok, "seconds": time.time() - t_ad}
        if ad_ok:
            meta = first_image_meta(waited.get("outputs"))
            ad_meta["outputs_meta"] = meta
            ad_meta["prompt_id"] = waited.get("prompt_id")
            if meta and str(meta.get("filename", "")).endswith(".mp4"):
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
                        or [0.0]
                    )
                    rec_ad = build_receipt(
                        ad_mp4 if ad_mp4.is_file() else strip,
                        renderer="gpu_comfy_faceid_animatediff",
                        provider="comfy",
                        cloud_or_local="local",
                        model=f"{CKPT}+mm_sd_v15_v2.fp16+{FACEID_BIN}",
                        host_role="gpu-host",
                        qqq="QQQ0",
                        prompt=ad_prompt,
                        wall_clock_s=round(time.time() - t_ad, 2),
                        tokens={"input": None, "output": None, "total": None, "note": "n/a local comfy"},
                        gpu={"peak_util_pct": peak_ad},
                        extra={
                            "note": "FaceID-conditioned AnimateDiff short loop; not cloud I2V",
                            "frames": 16,
                            "fps": 8,
                        },
                    )
                    write_receipt(rec_ad, path=RECEIPTS / "ceo-animatediff.receipt.json", chain=True)
                    if strip.is_file():
                        write_receipt(
                            build_receipt(
                                strip,
                                renderer="gpu_comfy_faceid_animatediff_frame_strip",
                                provider="comfy",
                                cloud_or_local="local",
                                model=f"{CKPT}+mm_sd_v15_v2.fp16+{FACEID_BIN}",
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
                    ad_ok = False
            else:
                print("ad no mp4 meta", meta, file=sys.stderr)
                ad_ok = False
        else:
            print("ad failed", waited, file=sys.stderr)

    # Hero compose
    hero = ASSETS / "hero-prompt-to-product.jpg"
    if os.environ.get("SKIP_HERO", "").strip() in ("1", "true", "yes"):
        print("SKIP_HERO set")
    else:
        print("compose hero…")
        # Prefer FaceID closeup panel for player (never multi-frame AD strip → black-blade glitch)
        hero_src = panel_paths[2] if len(panel_paths) > 2 else (panel_paths[0] if panel_paths else SOURCE)
        compose_hero(panel_paths, hero_src, hero)
        write_receipt(
            build_receipt(
                hero,
                renderer="gpu_ceo_hero_compose",
                provider="compose+comfy_faceid",
                cloud_or_local="local",
                model=f"{CKPT}+{FACEID_BIN}",
                host_role="gpu-host",
                qqq="QQQ0",
                prompt="hero compose: 6 FaceID CEO panels + player chrome from AD/closeup",
                wall_clock_s=round(time.time() - t_all, 2),
                gpu={"peak_util_pct": peak},
                extra={
                    "panels": [str(p.name) for p in panel_paths],
                    "player_source": str(hero_src.name),
                    "identity": "CEO only — no stock woman hero",
                },
            ),
            path=RECEIPTS / "hero-prompt-to-product.receipt.json",
            chain=False,
        )
        print("wrote", hero)

    summary = {
        "schema": "mok_tua_ceo_capability_regen.v2_faceid",
        "ts_utc": _utc(),
        "comfy": "gpu-host:8188",  # role label only; never log raw COMFY_URL
        "checkpoint": CKPT,
        "faceid_bin": FACEID_BIN,
        "identity": "IPAdapter FaceID PLUS V2 from padded 00-ceo-source-still",
        "storyboard": str(sheet),
        "face_polish": str(polish_out),
        "hero": str(hero) if hero.is_file() else None,
        "animatediff": ad_meta,
        "gpu_peak_samples": gpu_peaks,
        "total_seconds": round(time.time() - t_all, 2),
    }
    (OUT_DIR / "regen_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0 if sheet.is_file() else 4


if __name__ == "__main__":
    raise SystemExit(main())
