# FramePack UI I2V smoke — gpu-host

**Date:** 2026-08-05  
**UI:** `http://gpu-host:7864/` · Gradio `/process`  
**Shared models:** `/mnt/ai-data/models` · `hf_download` → `models/hf_hub`  
**Source still:** `docs/assets/pres-smoke/00-ceo-source-still.jpg`  
**QQQ:** QQQ0 local  

## Stack

| Layer | Value |
|-------|--------|
| Package | `/mnt/ai-data/stability-matrix/Data/Packages/FramePack Studio` |
| Launcher | `scripts/run_framepack_shared_models.sh` · port **7864** |
| Runtime registry | `/mnt/ai-data/work/mok-tua/runtime/framepack_studio.json` |
| Hub FramePackI2V_HY | **24G** complete snapshots |
| Hub HunyuanVideo community | **~941M partial** (VAE-centric; may limit some paths) |

## API smoke (conductor path)

```bash
# Gradio 4
POST http://gpu-host:7864/gradio_api/call/process
# body: data = [image, prompt, n_prompt, seed, seconds, window, steps, cfg, gs, rs, vram_preserve, teacache, crf]
GET  http://gpu-host:7864/gradio_api/call/process/{event_id}  # SSE stream
```

Observed stages in SSE: **VAE encoding → CLIP Vision encoding → Start sampling** with GPU util **~100%** and VRAM **~11–13 GiB**.

## Receipt

`docs/assets/receipts/framepack_ceo_i2v.receipt.json`  
- `renderer: gpu-host_framepack_i2v`  
- `host_role: gpu-host`  
- `cloud_or_local: local`  
- Artifact: `work/ceo_capability_regen/framepack_ceo_i2v_smoke.mp4` when capture succeeds (not git blob)

## Operator UI path

1. Open `http://gpu-host:7864/`  
2. Drop CEO source still  
3. Prompt + short length (1–5 s)  
4. Start → wait sampling  
5. Save mp4 under work tree; `receipt stamp` if not auto  

## Gaps

- HunyuanVideo **full** transformer hub incomplete — if jobs fail after CLIP, seed with `FRAMEPACK_ALLOW_DOWNLOAD=1` into **shared** hub only.  
- Gradio SSE may drop mid-job; reconnect or use UI download.  
