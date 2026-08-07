#!/usr/bin/env python3
"""Multi-angle + next-scene Qwen Image Edit storyboard → ~14.20s clip.

Narrative: procurement vibecoding → M.A.N.A.G.E.R. framework (anime style).
Identity inspiration: docs/assets/pres-smoke/00-ceo-source-still.jpg (photoceopic).

Usage:
  COMFY_URL=http://gpu-host:8188 python3 scripts/render_manager_pivot_qwen_storyboard.py
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

from artifact_receipt import build_receipt, write_receipt  # noqa: E402
from backends.comfy import ComfyClient  # noqa: E402
from qwen_graph import build_qwen_edit_storyboard_graph  # noqa: E402

COMFY_URL = os.environ.get("COMFY_URL", "http://gpu-host:8188").rstrip("/")
SOURCE = Path(
    os.environ.get(
        "MOK_TUA_REF",
        str(ROOT / "docs/assets/pres-smoke/00-ceo-source-still.jpg"),
    )
)
OUT = Path(os.environ.get("MOK_TUA_PIVOT_OUT", str(ROOT / "work" / "manager_pivot_qwen")))
PUBLIC_PANELS = ROOT / "docs/assets/capabilities" / "manager-pivot"
PUBLIC_EXPORTS = ROOT / "docs/assets/exports"
RECEIPTS = ROOT / "docs/assets/receipts"
TARGET_DURATION_S = 14.20
# 4060 Ti 16GB: Qwen Edit TE+UNET is heavy — default 384², lightning off, 2 LoRAs max
W, H = int(os.environ.get("MOK_TUA_QWEN_W", "384")), int(os.environ.get("MOK_TUA_QWEN_H", "384"))
STEPS = int(os.environ.get("MOK_TUA_QWEN_STEPS", "6"))
CFG = float(os.environ.get("MOK_TUA_QWEN_CFG", "1.0"))
USE_LIGHTNING = os.environ.get("MOK_TUA_QWEN_LIGHTNING", "0") == "1"
USE_REF_IMAGE = os.environ.get("MOK_TUA_QWEN_REF", "1") == "1"

# Identity + anime style locked; narrative progresses procurement → MANAGER
ID = (
    "same person as the reference photoceopic selfie: fair skin, freckles, light red facial patches, "
    "green-hazel eyes, short sandy brown hair, expressive face, handwritten black marker letters "
    "spelling ceo on forehead when forehead visible"
)

STYLE = (
    "high quality anime style illustration, clean cel shading, vivid but soft palette, "
    "studio anime production still, detailed face matching reference, coherent proportions"
)

NEG = (
    "blurry, low quality, watermark, photoreal photograph, 3d render, deformed face, "
    "extra limbs, wrong gender, woman, child, text gibberish, logo spam, horror, gore"
)

# (key, camera/next-scene instruction, scene beat)
BEATS: list[tuple[str, str, str]] = [
    (
        "01_wide_procurement",
        "Turn the camera to a wide-angle lens, front eye-level establishing shot.",
        "chaotic government procurement office, stacks of RFPs and purchase orders flying, "
        "multiple laptops open with messy vibecoding tabs, sticky notes everywhere, "
        f"{ID} in blue hoodie looking overwhelmed at the center, {STYLE}",
    ),
    (
        "02_medium_vibecode",
        "Medium shot, eye-level, subject facing camera three-quarter view.",
        "Next Scene: same office but tighter, "
        f"{ID} frantically vibecoding procurement automations, coffee cups, "
        "screens full of half-finished scripts and red error banners, anime stress lines, {STYLE}",
    ),
    (
        "03_close_pivot",
        "Turn the camera to a close-up, eye-level.",
        "Next Scene: close-up of "
        f"{ID}, eyes widening with realization, soft rim light, "
        "faint holographic letters MANAGER forming in the air, hopeful expression, {STYLE}",
    ),
    (
        "04_board_manager",
        "Front-right quarter view, eye-level medium shot.",
        "Next Scene: "
        f"{ID} stands before a glowing anime architecture board labeled M.A.N.A.G.E.R., "
        "modules as clean icons: memory, agents, care, tools, receipts, custody, "
        "old procurement chaos fading into background bokeh, {STYLE}",
    ),
    (
        "05_orbit_framework",
        "Rotate the camera 30 degrees to the right while keeping the subject centered.",
        "Next Scene: "
        f"{ID} orchestrating floating anime UI panels of the framework, "
        "local-first privacy lock icons, chain-of-custody tickets, calm blue-teal light, {STYLE}",
    ),
    (
        "06_wide_new_world",
        "Turn the camera to a wide-angle lens, front eye-level establishing shot.",
        "Next Scene: bright modern lab, "
        f"{ID} presenting the M.A.N.A.G.E.R. framework on a large display, "
        "tidy desks, colleagues with laptops, hope and order after chaos, "
        "title energy without readable tiny text, {STYLE}",
    ),
]


def upload_image(path: Path, name: str = "photoceopic_ref.jpg") -> str:
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
    with urllib.request.urlopen(req, timeout=120) as resp:
        out = json.loads(resp.read().decode())
    return out.get("name") or name


def view_image(filename: str, *, subfolder: str = "", folder_type: str = "output") -> bytes:
    q = urllib.parse.urlencode(
        {"filename": filename, "subfolder": subfolder, "type": folder_type}
    )
    with urllib.request.urlopen(f"{COMFY_URL}/view?{q}", timeout=180) as resp:
        return resp.read()


def first_image_meta(outputs: Any) -> dict[str, str] | None:
    if not isinstance(outputs, dict):
        return None
    for _nid, node_out in outputs.items():
        if not isinstance(node_out, dict):
            continue
        imgs = node_out.get("images") or []
        if imgs:
            im = imgs[0]
            return {
                "filename": im.get("filename") or "",
                "subfolder": im.get("subfolder") or "",
                "type": im.get("type") or "output",
            }
    return None


def inject_ref(graph: dict[str, Any], image_name: str) -> dict[str, Any]:
    g = json.loads(json.dumps(graph))
    g["25"] = {"class_type": "LoadImage", "inputs": {"image": image_name}}
    g["30"]["inputs"]["image1"] = ["25", 0]
    g["31"]["inputs"]["image1"] = ["25", 0]
    # mild identity lock via denoise on empty latent still works; keep denoise 1.0 for edit-plus text path
    return g


def queue_and_wait(client: ComfyClient, graph: dict[str, Any], *, timeout_s: float) -> dict[str, Any]:
    q = client.queue_prompt(graph)
    if not q.get("ok"):
        return {"ok": False, "phase": "queue", "detail": q}
    pid = (q.get("result") or {}).get("prompt_id")
    if not pid:
        return {"ok": False, "phase": "queue", "detail": q}
    return client.wait_for_prompt(pid, timeout_s=timeout_s, poll_s=2.0)


def collage(panel_paths: list[Path], labels: list[str], out: Path) -> None:
    from PIL import Image, ImageDraw, ImageFont

    cell_w, cell_h = 360, 360
    pad, label_h = 16, 40
    cols, rows = 3, 2
    W = pad + cols * (cell_w + pad)
    H = pad + rows * (cell_h + label_h + pad) + 56
    canvas = Image.new("RGB", (W, H), (18, 20, 28))
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 13)
        font_sm = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 10)
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
        draw.text((x, y + cell_h + 4), labels[i][:48], fill=(220, 220, 230), font=font)
    foot = (
        "mok-tua · Qwen Image Edit 2509 + multi-angle + next-scene · anime · "
        "procurement vibecoding → M.A.N.A.G.E.R. · photoceopic ref · gpu-host"
    )
    draw.text((pad, H - 28), foot, fill=(140, 145, 160), font=font_sm)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, quality=92)


def build_video(panel_paths: list[Path], out_mp4: Path, duration_s: float) -> dict[str, Any]:
    """Hold each panel equally so total length ≈ duration_s."""
    n = len(panel_paths)
    per = duration_s / n
    fps = 30
    frames_each = max(1, int(round(per * fps)))
    # rebuild exact duration: adjust last panel
    total_frames = int(round(duration_s * fps))
    base = total_frames // n
    rem = total_frames - base * n
    frame_counts = [base + (1 if i < rem else 0) for i in range(n)]

    list_file = OUT / "ffmpeg_concat.txt"
    tmp_dir = OUT / "hold_frames"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True)
    # sequence as numbered frames for constant fps
    idx = 0
    for p, fc in zip(panel_paths, frame_counts):
        for _ in range(fc):
            dest = tmp_dir / f"f{idx:05d}.png"
            # symlink or copy
            try:
                dest.symlink_to(p.resolve())
            except OSError:
                shutil.copy2(p, dest)
            idx += 1
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-framerate",
        str(fps),
        "-i",
        str(tmp_dir / "f%05d.png"),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-crf",
        "18",
        "-movflags",
        "+faststart",
        str(out_mp4),
    ]
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    wall = time.time() - t0
    # probe duration
    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(out_mp4),
        ],
        capture_output=True,
        text=True,
    )
    dur = float(probe.stdout.strip() or 0)
    return {
        "ok": proc.returncode == 0,
        "ffmpeg_wall_s": wall,
        "duration_s": dur,
        "fps": fps,
        "frames_total": idx,
        "frames_per_panel": frame_counts,
        "stderr_tail": (proc.stderr or "")[-500:],
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    PUBLIC_PANELS.mkdir(parents=True, exist_ok=True)
    PUBLIC_EXPORTS.mkdir(parents=True, exist_ok=True)
    RECEIPTS.mkdir(parents=True, exist_ok=True)

    if not SOURCE.is_file():
        print("missing SOURCE", SOURCE, file=sys.stderr)
        return 1

    client = ComfyClient(COMFY_URL, timeout=60.0)
    stats = client.system_stats()
    if not stats.get("ok"):
        print("comfy down", stats, file=sys.stderr)
        return 1
    print("comfy", (stats.get("stats") or {}).get("system", {}).get("comfyui_version"))

    server_name = ""
    if USE_REF_IMAGE:
        print("upload ref", SOURCE)
        server_name = upload_image(SOURCE, "photoceopic_ref.jpg")
        print("server_name", server_name)
    else:
        print("ref image disabled (text+identity prompt only)")

    panel_paths: list[Path] = []
    labels: list[str] = []
    panel_meta: list[dict[str, Any]] = []
    t_all = time.time()

    def free_vram() -> None:
        try:
            data = json.dumps({"unload_models": True, "free_memory": True}).encode()
            req = urllib.request.Request(
                f"{COMFY_URL}/free",
                data=data,
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=30).read()
        except Exception as exc:
            print("free_vram warn", exc)

    free_vram()

    for i, (key, camera, scene) in enumerate(BEATS):
        prompt = f"{camera}\n{scene}"
        seed = 62000 + i * 37
        # Stack only multi-angle + next-scene (no Lightning) to fit 16GB
        graph = build_qwen_edit_storyboard_graph(
            prompt,
            negative=NEG,
            seed=seed,
            steps=STEPS,
            cfg=CFG,
            width=W,
            height=H,
            filename_prefix=f"mgr_pivot_{key}",
            use_lightning=USE_LIGHTNING,
            next_scene_strength=0.78 if i > 0 else 0.50,
            multi_angles_strength=0.95,
            denoise=1.0,
        )
        if USE_REF_IMAGE and server_name:
            graph = inject_ref(graph, server_name)
        print(f"panel {i+1}/{len(BEATS)} {key} {W}x{H} lightning={USE_LIGHTNING} ref={bool(server_name)} …")
        free_vram()
        t0 = time.time()
        waited = queue_and_wait(client, graph, timeout_s=900)
        wall = time.time() - t0
        if not waited.get("ok"):
            print("FAIL", key, json.dumps(waited, default=str)[:800], file=sys.stderr)
            return 2
        meta = first_image_meta(waited.get("outputs"))
        if not meta or not meta.get("filename"):
            print("no image meta", waited, file=sys.stderr)
            return 2
        raw = view_image(
            meta["filename"],
            subfolder=meta.get("subfolder") or "",
            folder_type=meta.get("type") or "output",
        )
        dest = OUT / f"{key}.png"
        dest.write_bytes(raw)
        pub = PUBLIC_PANELS / f"{key}.jpg"
        # convert to jpg for docs weight
        try:
            from PIL import Image

            Image.open(dest).convert("RGB").save(pub, quality=90)
        except Exception:
            shutil.copy2(dest, pub.with_suffix(".png"))
            pub = pub.with_suffix(".png")
        panel_paths.append(dest)
        labels.append(key.replace("_", " ")[:40])
        rec = build_receipt(
            dest,
            renderer="gpu_comfy_qwen_image_edit_2509",
            model=(
                "qwen_image_edit_2509_fp8_e4m3fn + "
                "Qwen-Edit-2509-Multiple-angles + next-scene_lora-v2-3000 + "
                "Lightning-4steps"
            ),
            host_role="gpu-host",
            qqq="QQQ0",
            prompt=prompt,
            seed=seed,
            wall_clock_s=wall,
            gpu_evidence="comfy_queue_ok",
            extra={
                "camera": camera,
                "beat": key,
                "steps": STEPS,
                "cfg": CFG,
                "width": W,
                "height": H,
                "ref": "docs/assets/pres-smoke/00-ceo-source-still.jpg",
                "narrative": "procurement_vibecoding_to_MANAGER",
                "style": "anime",
                "public_panel": str(pub.relative_to(ROOT)),
            },
        )
        write_receipt(rec)
        write_receipt(rec, path=pub.with_suffix(pub.suffix + ".receipt.json"))
        panel_meta.append(
            {
                "key": key,
                "path": str(dest.relative_to(ROOT)),
                "public": str(pub.relative_to(ROOT)),
                "seed": seed,
                "wall_clock_s": round(wall, 2),
                "prompt": prompt,
            }
        )
        print(f"  ok {wall:.1f}s → {dest.name}")

    sheet = PUBLIC_PANELS / "storyboard-sheet.jpg"
    collage(panel_paths, labels, sheet)

    mp4_work = OUT / "manager_pivot_anime_14s2.mp4"
    vinfo = build_video(panel_paths, mp4_work, TARGET_DURATION_S)
    if not vinfo.get("ok"):
        print("ffmpeg fail", vinfo, file=sys.stderr)
        return 3
    mp4_pub = PUBLIC_EXPORTS / "manager-pivot-procurement-to-manager-anime.mp4"
    shutil.copy2(mp4_work, mp4_pub)
    poster = PUBLIC_EXPORTS / "manager-pivot-procurement-to-manager-anime-poster.jpg"
    shutil.copy2(panel_paths[0].with_suffix(".png") if False else panel_paths[-1], OUT / "poster_src.png")
    try:
        from PIL import Image

        Image.open(panel_paths[-1]).convert("RGB").save(poster, quality=90)
    except Exception:
        shutil.copy2(sheet, poster)

    total_wall = time.time() - t_all
    summary = {
        "schema": "mok_tua_manager_pivot_qwen.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "narrative": "procurement vibecoding → M.A.N.A.G.E.R. framework",
        "style": "anime",
        "ref_image": "docs/assets/pres-smoke/00-ceo-source-still.jpg",
        "ref_note": "photoceopic identity inspiration",
        "models": {
            "diffusion": "qwen_image_edit_2509_fp8_e4m3fn.safetensors",
            "text_encoder": "qwen_2.5_vl_7b_fp8_scaled.safetensors",
            "vae": "qwen_image_vae.safetensors",
            "loras": [
                "Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors",
                "Qwen-Edit-2509-Multiple-angles.safetensors",
                "next-scene_lora-v2-3000.safetensors",
            ],
        },
        "comfy": {"url_role": "gpu-host:8188", "version": "0.29.0"},
        "panels": panel_meta,
        "video": {
            "path": str(mp4_pub.relative_to(ROOT)),
            "work_path": str(mp4_work.relative_to(ROOT)),
            "target_duration_s": TARGET_DURATION_S,
            "measured_duration_s": vinfo.get("duration_s"),
            "fps": vinfo.get("fps"),
            "frames_total": vinfo.get("frames_total"),
            "frames_per_panel": vinfo.get("frames_per_panel"),
            "renderer": "ffmpeg_panel_hold + qwen_image_edit_stills",
        },
        "wall_clock_total_s": round(total_wall, 2),
        "qqq": "QQQ0",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (PUBLIC_PANELS / "PROVENANCE.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    vrec = build_receipt(
        mp4_pub,
        renderer="ffmpeg_hold_from_qwen_edit_panels",
        model="qwen_image_edit_2509_fp8 + multi-angle + next-scene LoRAs",
        host_role="gpu-host",
        qqq="QQQ0",
        prompt=" | ".join(m["prompt"][:120] for m in panel_meta),
        wall_clock_s=total_wall,
        gpu_evidence="stills_on_gpu_host_then_ffmpeg",
        extra={
            "duration_s": vinfo.get("duration_s"),
            "target_duration_s": TARGET_DURATION_S,
            "panel_count": len(panel_paths),
            "summary": str((OUT / "summary.json").relative_to(ROOT)),
        },
    )
    write_receipt(vrec)
    write_receipt(vrec, path=mp4_work.with_suffix(mp4_work.suffix + ".receipt.json"))

    print(json.dumps({"ok": True, "summary": summary["video"], "total_s": total_wall}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
