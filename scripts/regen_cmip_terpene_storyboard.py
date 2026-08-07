#!/usr/bin/env python3
"""CMIP terpene-repo origin storyboard — FaceID PLUS V2 panels via mok-tua Comfy.

Identity seed (public mok-tua): docs/assets/pres-smoke/00-ceo-source-still.jpg
(handwritten 'ceo' on forehead selfie — same ref as capability/pres-smoke docs).

NOT Imagine/cloud: local GPU-host Comfy + IPAdapter FaceID.

Usage:
  COMFY_URL=http://REDACTED-LAN-IP:8188 python3 scripts/regen_cmip_terpene_storyboard.py
"""

from __future__ import annotations

import json
import os
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

# Reuse FaceID stack builders from CEO capability regen
from regen_ceo_capability_assets import (  # noqa: E402
    FACEID_WEIGHT,
    FACEID_WEIGHT_V2,
    LORA_STRENGTH,
    build_faceid_txt2img_graph,
    prepare_face_ref,
    upload_image,
    view_image,
    first_image_meta,
    queue_and_wait,
)

COMFY_URL = os.environ.get("COMFY_URL", "http://REDACTED-LAN-IP:8188").rstrip("/")
SOURCE = ROOT / "docs/assets/pres-smoke/00-ceo-source-still.jpg"
OUT = Path(os.environ.get("MOK_TUA_CMIP_OUT", str(ROOT / "work" / "cmip_terpene_storyboard")))
ASSETS = ROOT / "docs" / "assets" / "cmip-terpene-origin"
RECEIPTS = ROOT / "docs" / "assets" / "receipts"

# Comic / storyboard still style (readable panels, FaceID-locked)
STYLE = (
    "American comic book storyboard panel, bold black ink outlines, flat cel color, "
    "sequential art, graphic novel page frame, NOT photoreal, NOT 3d render, "
    "warm newsprint vibe, clear silhouette reading"
)

CEO = (
    "exact same man as the reference selfie, fair freckled skin, light red facial patches, "
    "green-hazel eyes, short sandy-brown hair, goofy intense CEO expression, "
    "clear handwritten black permanent-marker text reading ceo on the forehead "
    "(letters c-e-o readable, not a red mark, not hearts), founder vibecoding"
)

NEG = (
    "blurry, low quality, watermark, deformed face, extra limbs, wrong gender, "
    "woman, female, child, different person, face morph, uncanny valley, "
    "photoreal DSLR photo, stock model, celebrity lookalike, text gibberish, logo spam, "
    "hearts on forehead, red bindi, symbols instead of ceo letters, empty forehead, "
    "missing stoners when described, missing trash can when described"
)

# (key, title, prompt, seed, w, h)
PANELS: list[tuple[str, str, str, int, int, int]] = [
    (
        "01_vibecode",
        "1. Vibecoding",
        f"{STYLE}, medium shot night desk, {CEO} in green hoodie, triple monitors with chat and schema, "
        "sticky note says PTSD CARE, coffee, manic vibecoding the terpene database idea",
        43001,
        768,
        512,
    ),
    (
        "02_lookup",
        "2. Looking up terpenes",
        f"{STYLE}, {CEO} at dual monitors labeled PubChem and ChEBI, molecule sketches, "
        "books stacked, looking up terpene boiling points and CIDs, forehead ceo letters clear",
        43002,
        768,
        512,
    ),
    (
        "03_collect",
        "3. Collecting data",
        f"{STYLE}, wide chaos, {CEO} gathering huge piles of CSV printouts, USB sticks, "
        "spreadsheet tornado, data hoarding for the terpene DB",
        43003,
        768,
        512,
    ),
    (
        "04_stoners_arrive",
        "4. Stoners congregate",
        f"{STYLE}, crowded room, three chill stoners on beanbag chairs with snacks watching, "
        f"{CEO} still typing in center, community gathering around the project",
        43004,
        768,
        512,
    ),
    (
        "05_verify",
        "5. Verification check",
        f"{STYLE}, {CEO} with magnifying glass and red pen auditing rows, "
        "stamps LICENSE? and NO SOURCE, verification stress, forehead ceo letters clear",
        43005,
        768,
        512,
    ),
    (
        "06_toss",
        "6. Data tossed",
        f"{STYLE}, dramatic, {CEO} throwing boxes of unverified data into trash labeled NO PAPER TRAIL, "
        "green arrow to OPEN DATA path, decisive cleanup",
        43006,
        768,
        512,
    ),
    (
        "07_stoners_stay",
        "7. Stoners still hang",
        f"{STYLE}, after the purge, stoners still lounging on beanbags laughing, empty trash in corner, "
        f"{CEO} shrugging with half smile, community remains",
        43007,
        768,
        512,
    ),
    (
        "08_coder_codes",
        "8. Coder still codes",
        f"{STYLE}, final hero, {CEO} in lab coat at keyboard writing schema-only docs, "
        "screen shows cmip-terpene-db, small PTSD care pin on bag, forehead ceo letters clear, hope",
        43008,
        768,
        512,
    ),
]



def free_comfy() -> None:
    try:
        req = urllib.request.Request(
            f"{COMFY_URL}/free",
            data=json.dumps({"unload_models": True, "free_memory": True}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=30).read()
    except Exception as e:
        print("free warn", e)


def compose_sheet(panel_paths: list[Path], out: Path, labels: list[str]) -> Path:
    from PIL import Image, ImageDraw, ImageFont

    cols, rows = 4, 2
    cell_w, cell_h = 768, 512
    pad, label_h = 16, 36
    sheet_w = cols * cell_w + (cols + 1) * pad
    sheet_h = rows * (cell_h + label_h) + (rows + 1) * pad + 48
    sheet = Image.new("RGB", (sheet_w, sheet_h), (24, 22, 28))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 22)
        title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 28)
    except Exception:
        font = ImageFont.load_default()
        title_font = font
    draw.text((pad, pad // 2), "CMIP origin · how the terpene schema repo came to be", fill=(240, 230, 200), font=title_font)
    for i, (p, lab) in enumerate(zip(panel_paths, labels)):
        r, c = divmod(i, cols)
        x = pad + c * (cell_w + pad)
        y = 48 + pad + r * (cell_h + label_h + pad)
        im = Image.open(p).convert("RGB").resize((cell_w, cell_h), Image.Resampling.LANCZOS)
        sheet.paste(im, (x, y))
        draw.text((x, y + cell_h + 6), lab, fill=(220, 210, 190), font=font)
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=92)
    return out


def main() -> int:
    if not SOURCE.is_file():
        print("missing face ref", SOURCE)
        return 2
    OUT.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    RECEIPTS.mkdir(parents=True, exist_ok=True)

    os.environ["COMFY_URL"] = COMFY_URL
    # monkeypatch upload/view host used inside imported helpers — they read COMFY_URL at call via module global
    import regen_ceo_capability_assets as cap

    cap.COMFY_URL = COMFY_URL

    free_comfy()
    time.sleep(2)
    client = ComfyClient(base_url=COMFY_URL)
    face_pad = prepare_face_ref(SOURCE, OUT / "ceo_face_padded.jpg")
    face_name = upload_image(face_pad, "cmip_ceo_face_padded.jpg")
    print("uploaded face", face_name, "comfy", COMFY_URL)

    panel_paths: list[Path] = []
    labels: list[str] = []
    results: list[dict[str, Any]] = []

    for key, title, prompt, seed, w, h in PANELS:
        print(f"== {key} {title} ==")
        free_comfy()
        time.sleep(1)
        graph = build_faceid_txt2img_graph(
            image_name=face_name,
            prompt=prompt,
            negative=NEG,
            seed=seed,
            width=w,
            height=h,
            steps=30,
            filename_prefix=f"cmip_origin_{key}",
            faceid_weight=1.0,
            faceid_weight_v2=1.25,
            lora_strength=0.7,
        )
        waited = queue_and_wait(client, graph, timeout_s=360)
        meta = first_image_meta(waited.get("outputs") or {})
        entry: dict[str, Any] = {
            "key": key,
            "title": title,
            "prompt_id": waited.get("prompt_id"),
            "ok": bool(meta),
            "seconds": waited.get("seconds"),
            "error": waited.get("error"),
        }
        if not meta:
            print("FAIL", key, waited.get("error") or waited.get("status") or list((waited.get("outputs") or {}).keys()))
            # dump status messages if any
            results.append(entry)
            continue
        raw = view_image(meta["filename"], subfolder=meta.get("subfolder") or "", folder_type=meta.get("type") or "output")
        dest = OUT / f"{key}.jpg"
        dest.write_bytes(raw)
        pub = ASSETS / f"{key}.jpg"
        pub.write_bytes(raw)
        panel_paths.append(dest)
        labels.append(title)
        entry["path"] = str(dest.relative_to(ROOT))
        entry["bytes"] = len(raw)
        results.append(entry)
        print("ok", dest, len(raw), f"{entry['seconds']:.1f}s")

    sheet = None
    if len(panel_paths) >= 4:
        sheet = compose_sheet(panel_paths, ASSETS / "cmip-origin-storyboard-sheet.jpg", labels)
        # also work/
        compose_sheet(panel_paths, OUT / "cmip-origin-storyboard-sheet.jpg", labels)
        print("sheet", sheet)

    free_comfy()
    stamp = {
        "schema": "mok_tua_cmip_terpene_origin_storyboard.v1",
        "ts_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "renderer": "gpu_comfy_faceid_plus_v2",
        "provider": "comfy",
        "cloud_or_local": "local",
        "not_imagine": True,
        "face_ref": str(SOURCE.relative_to(ROOT)),
        "face_ref_public": "https://github.com/the1truedan/mok-tua/blob/main/docs/assets/pres-smoke/00-ceo-source-still.jpg",
        "model": "DreamShaper_8_pruned + ip-adapter-faceid-plusv2_sd15 + clip_vision_h + buffalo_l",
        "comfy_url_host": COMFY_URL.split("//")[-1].split(":")[0],
        "panels": results,
        "sheet": str(sheet.relative_to(ROOT)) if sheet else None,
        "story": [
            "vibecode",
            "lookup terpene data",
            "collect data",
            "stoners congregate",
            "verification",
            "data tossed",
            "stoners stay",
            "coder still codes",
        ],
        "notes": "PTSD care nod allowed by founder; face plaster ok; identity from mok-tua CEO source still",
    }
    stamp_path = OUT / "summary.json"
    stamp_path.write_text(json.dumps(stamp, indent=2) + "\n")
    (ASSETS / "README.md").write_text(
        "# CMIP terpene origin storyboard (FaceID)\n\n"
        "Generated with **mok-tua** local Comfy FaceID PLUS V2 — not Imagine.\n\n"
        f"Face ref: [`00-ceo-source-still.jpg`](../pres-smoke/00-ceo-source-still.jpg) "
        "(public on [the1truedan/mok-tua](https://github.com/the1truedan/mok-tua)).\n\n"
        "Sheet: [cmip-origin-storyboard-sheet.jpg](cmip-origin-storyboard-sheet.jpg)\n"
    )
    art = sheet or (panel_paths[0] if panel_paths else stamp_path)
    rec = build_receipt(
        art,
        renderer="gpu_comfy_faceid_plus_v2",
        provider="comfy",
        model="DreamShaper_8 + faceid-plusv2_sd15",
        prompt="CMIP terpene origin 8-panel storyboard",
        extra={"summary": str(stamp_path.relative_to(ROOT)), "panel_count": len(panel_paths)},
    )
    write_receipt(rec, path=RECEIPTS / "cmip-terpene-origin-storyboard.receipt.json")
    print(json.dumps({"ok": len(panel_paths) == 8, "panels": len(panel_paths), "sheet": str(sheet)}, indent=2))
    return 0 if len(panel_paths) >= 6 else 1


if __name__ == "__main__":
    raise SystemExit(main())
