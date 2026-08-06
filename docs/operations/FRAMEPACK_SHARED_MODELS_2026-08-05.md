# FramePack Studio — shared models (no re-download)

**Date:** 2026-08-05  
**Package:** `/mnt/ai-data/stability-matrix/Data/Packages/FramePack Studio`  
**SM:** Linux `Data/` (not mac-Data)

## Assurance checklist

| Control | State |
|---------|--------|
| SM `ModelDirectoryOverride` | `/mnt/ai-data/models/` ✅ |
| Comfy `extra_model_paths` | `/mnt/ai-data/models/` ✅ |
| Package `hf_download` | **symlink** → `/mnt/ai-data/models/hf_hub` ✅ |
| LoRA dir | `/mnt/ai-data/models/loras` ✅ |
| Outputs | `/mnt/ai-data/work/framepack/outputs` ✅ |
| Launch wrapper | `scripts/run_framepack_shared_models.sh` ✅ |
| Offline-by-default when hub present | wrapper sets `HF_HUB_OFFLINE=1` + `--offline` ✅ |
| Allow shared seed only | `FRAMEPACK_ALLOW_DOWNLOAD=1` (writes into **shared** hub, not package) ✅ |

## Why symlink

`studio.py` hardcodes:

```python
os.environ['HF_HOME'] = .../FramePack Studio/hf_download
```

Redirecting that path to the shared hub is the only non-fork fix that stops package-local HF trees.

## Do / don’t

- **Do** launch via `run_framepack_shared_models.sh`  
- **Do** seed missing HF snapshots only with `FRAMEPACK_ALLOW_DOWNLOAD=1` into `models/hf_hub`  
- **Don’t** run bare `python studio.py` from a clean package without the symlink  
- **Don’t** point FramePack at Mac SM `mac-Data` packages from Linux  

## NFS permissions (Mac uid 501 vs Linux uid 1000)

Mac-created dirs under `/Volumes/ai-data/work/framepack` often show as **uid 501** on GPU-host with mode `2755` (group **no write**). Linux `dtm` is **uid 1000** / **gid 1000**, so you get:

```text
PermissionError: ... '/mnt/ai-data/work/framepack/receipts/...'
Connection closed  # ssh session ends when remote bash exits non-zero (set -e)
```

**Fix (from Mac, once):**

```bash
chmod -R g+rwX /Volumes/ai-data/work/framepack
# prefer 2775 on dirs so setgid keeps group=dtm
find /Volumes/ai-data/work/framepack -type d -exec chmod 2775 {} \;
```

Prefer creating lab work trees **on GPU-host** (`mkdir -m 2775`) so owner is uid 1000.

**Launcher:** `run_framepack_shared_models.sh` now tests write access and falls back to  
`$HOME/work/framepack/{outputs,metadata,receipts}` if NFS is not writable.

## Incomplete SM package (diffusers_helper missing)

If you see `ModuleNotFoundError: No module named 'diffusers_helper'`:

1. **Package source deleted** (SM tree had ~56 tracked deletions). Restore:

```bash
cd /mnt/ai-data/stability-matrix/Data/Packages/FramePack\ Studio
git restore diffusers_helper modules
```

2. **Empty SM package `venv` / `No module named 'einops'`** — Stability Matrix Packages → Launch uses `package/venv` (pip-only until linked). Install host-local SM **3.10** env + symlink:

```bash
scp ~/mok-tua/scripts/run_framepack_shared_models.sh gpu-host:/tmp/
ssh gpu-host 'bash /tmp/run_framepack_shared_models.sh --install-deps'
# Stability Matrix: Packages → FramePack Studio → Launch
# or CLI:
ssh gpu-host 'bash /tmp/run_framepack_shared_models.sh --offline --server 0.0.0.0 --port 7865'
```

| Item | Path |
|------|------|
| **SM GUI host venv (3.10)** | `~/pinokio-host-runtimes/framepack-sm310-linux-amd64/env` |
| Package `venv` | **symlink** → SM GUI host venv |
| Optional CLI 3.12 | `~/pinokio-host-runtimes/framepack-linux-amd64/env` |
| UV cache | `/mnt/ai-data/uv-cache/gpu-host` (`UV_LINK_MODE=copy`) |
| Package code | NFS SM package (source only) |
| Weights | `/mnt/ai-data/models` + `hf_hub` |

`--install-deps` = torch(cu128) + `requirements.txt` (**einops** included) + link `package/venv`.  
Full SM GUI + desk-host orchestration: `docs/operations/FRAMEPACK_SM_GUI_AND_ORCHESTRATION_2026-08-05.md`

## Lifecycle (mok-tua · SM · LAN)

| Surface | Start | Stop |
|---------|-------|------|
| mok-tua | `launch framepack_studio --live` | `stop framepack_studio` |
| Wrapper | `--offline --server 0.0.0.0 --port 7864` | stop via registry / mok-tua |
| SM GUI | Packages → Launch (after `--install-deps`) | SM stop only if SM owns process |
| Browser | `http://gpu-host:7864/` | use mok-tua stop |

**Port 7864** (ACE-Step **7865**). Registry: `/mnt/ai-data/work/mok-tua/runtime/framepack_studio.json`

## Smoke

```bash
scp ~/mok-tua/scripts/run_framepack_shared_models.sh gpu-host:/tmp/
ssh gpu-host 'bash /tmp/run_framepack_shared_models.sh --install-deps'
# SM Packages → Launch  OR  CLI:
ssh gpu-host 'bash /tmp/run_framepack_shared_models.sh --offline --server 0.0.0.0 --port 7864'
```

1. Launch (SM GUI or wrapper) on GPU-host  
2. Confirm no new multi-GB dirs under package tree  
3. HTTP OK on `http://gpu-host:7864/` from desk  
4. One short I2V job → receipt under `work/framepack/receipts/` (or `~/work/framepack/receipts` fallback)  

### Hub seed note (2026-08-05)

Shared `hf_hub` was empty (README only). First launch with `--offline` fails on  
`hunyuanvideo-community/HunyuanVideo` text_encoder.

| Blocker | Fix |
|---------|-----|
| Empty hub | `FRAMEPACK_ALLOW_DOWNLOAD=1` seed into **shared** hub only |
| NFS uid 501 vs 1000 write deny on `hf_hub` | From Mac: `chmod -R g+rwX /Volumes/ai-data/models/hf_hub` + mkdir hub/transformers/diffusers |
| SM empty venv / einops | `--install-deps` + package/venv → host SM 3.10 |

```bash
ssh gpu-host 'FRAMEPACK_ALLOW_DOWNLOAD=1 bash /tmp/run_framepack_shared_models.sh --server 0.0.0.0 --port 7864'
# log: /mnt/ai-data/work/framepack/logs/launch_7864_seed2.log
```

**In progress (operator):** seed download writing to `/mnt/ai-data/models/hf_hub` (multi‑GB Hunyuan shards; Gradio comes up after load).  
After snapshots land under `…/hf_hub/hub/models--*hunyuan*`, prefer offline / auto-offline.
