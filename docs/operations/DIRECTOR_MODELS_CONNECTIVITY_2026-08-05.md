# Director’s Console — connectivity to `/ai-data/models` + Comfy

**Date:** 2026-08-05  
**Host:** gpu-host  
**Pool:** `/mnt/ai-data/models` (NFS share; Mac sees `/Volumes/ai-data/models`)

## Service matrix (live probe)

| Surface | Port | Probe | Result |
|---------|------|-------|--------|
| Director UI | 5173 | HTTP `/` | **200** |
| Cinema Prompt Eng (CPE) | 9800 | `/api/health` | **healthy** `cinema-prompt-engineering` |
| Orchestrator API | 9820 | `/health` | **healthy** `job_manager_connected` + `backend_manager_connected` |
| Orchestrator backends | 9820 | `/api/backends` | **`backends: []`** — no Comfy registered yet |
| ComfyUI | 8188 | `/system_stats` | **200** · pool via `extra_model_paths.yaml` |
| FramePack Gradio | 7864 | `/` | **200** |

## How Director reaches models

Director does **not** mmap the model tree directly for diffusion weights. Path:

```text
Director UI / CPE
    → Orchestrator (:9820) jobs
        → ComfyUI backend (:8188)
            → extra_model_paths base_path = /mnt/ai-data/models/
```

Defaults in code (`templates_system/config.py`, orchestrator backend model):

- `COMFYUI_HOST=127.0.0.1`  
- `COMFYUI_PORT=8188`  

So **on-host** Director → local Comfy is the intended wiring.  
Shared pool connectivity is **Comfy’s** `extra_model_paths` + filesystem mounts.

### Pool visibility (gpu-host)

| Path | Readable | Notes |
|------|----------|-------|
| `/mnt/ai-data/models` | OK | top-level dirs present |
| `…/checkpoints` | OK | DreamShaper_8 etc. |
| `…/diffusion_models` | OK | Wan 2.2 I2V 14B fp8 present |
| `…/ipadapter` | OK | FaceID weights installed this session |
| `…/hf_hub` | OK | FramePackI2V_HY 24G; Hunyuan community hub **partial** (VAE-only ~941M) |

## Gap: empty backend registry

`GET /api/backends` → `total: 0`. Orchestrator is healthy but has **no Comfy backend entry**, so job dispatch to models will not run until a backend is registered in the Director UI / config store.

### Operator fix

1. Open Director UI `http://gpu-host:5173/`  
2. Add / enable Comfy backend: host `127.0.0.1` port `8188` (or LAN role name only in docs)  
3. Re-check: `curl -sS http://gpu-host:9820/api/backends` should show online=1  
4. Smoke: queue a still via Director → Comfy using DreamShaper from pool  

Automated POST schema for backend create was **not** exposed on OpenAPI (only list/status/restart) — registration is UI-driven in this build.

## Folder / project APIs (gallery)

Available: `/api/browse-folders`, `/api/scan-folder-images`, `/api/list-projects`, …  
These scan **project/output trees**, not the weight pool. Model discovery for rendering remains Comfy object_info + checkpoints on disk.

## Smoke commands

```bash
# services
curl -sS http://gpu-host:9800/api/health
curl -sS http://gpu-host:9820/health
curl -sS http://gpu-host:9820/api/backends
curl -sS http://gpu-host:8188/system_stats | head -c 200

# pool (on gpu-host)
test -d /mnt/ai-data/models/checkpoints && test -d /mnt/ai-data/models/ipadapter
ls /mnt/ai-data/models/ipadapter/*.bin | wc -l   # expect 2 FaceID bins
ls /mnt/ai-data/models/diffusion_models/wan2.2_i2v_*.safetensors
```

## Verdict

| Check | Result |
|-------|--------|
| Filesystem path `/mnt/ai-data/models` reachable on Director host | **PASS** |
| Comfy bound to shared pool | **PASS** |
| Director stack HTTP healthy | **PASS** |
| Director → Comfy backend registered | **FAIL / empty** — human UI register needed |
| End-to-end Director render via pool | **BLOCKED** on backend registration |
