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

Mac-created dirs under `/Volumes/ai-data/work/framepack` often show as **uid 501** on MRGPU with mode `2755` (group **no write**). Linux `dtm` is **uid 1000** / **gid 1000**, so you get:

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

Prefer creating lab work trees **on MRGPU** (`mkdir -m 2775`) so owner is uid 1000.

**Launcher:** `run_framepack_shared_models.sh` now tests write access and falls back to  
`$HOME/work/framepack/{outputs,metadata,receipts}` if NFS is not writable.

## Incomplete SM package (diffusers_helper missing)

If you see `ModuleNotFoundError: No module named 'diffusers_helper'`:

1. **Package source deleted** (SM tree had ~56 tracked deletions). Restore:

```bash
cd /mnt/ai-data/stability-matrix/Data/Packages/FramePack\ Studio
git restore diffusers_helper modules
```

2. **No host venv** — system `python3` is wrong. Install deps with **uv** into a **host-local** venv (not on NFS):

```bash
scp ~/mok-tua/scripts/run_framepack_shared_models.sh gpu-host:/tmp/
ssh gpu-host 'bash /tmp/run_framepack_shared_models.sh --install-deps'
# then launch
ssh gpu-host 'bash /tmp/run_framepack_shared_models.sh --offline --server 0.0.0.0 --port 7865'
```

| Item | Path |
|------|------|
| Host venv | `~/pinokio-host-runtimes/framepack-linux-amd64/env` |
| UV cache | `/mnt/ai-data/uv-cache/mrgpu` (`UV_LINK_MODE=copy`) |
| Package code | NFS SM package (source only) |
| Weights | `/mnt/ai-data/models` + `hf_hub` |

`--install-deps` = batch `uv pip install` torch(cu128) + `requirements.txt`. Re-run after requirements change.

## Smoke (next)

```bash
scp ~/mok-tua/scripts/run_framepack_shared_models.sh gpu-host:/tmp/
ssh gpu-host 'bash /tmp/run_framepack_shared_models.sh --install-deps'
ssh gpu-host 'bash /tmp/run_framepack_shared_models.sh --offline --server 0.0.0.0 --port 7865'
```

1. Launch with wrapper on MRGPU  
2. Confirm no new multi-GB dirs under package tree  
3. One short I2V job → receipt under `work/framepack/receipts/` (or `~/work/framepack/receipts` fallback)  
