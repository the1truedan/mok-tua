# FramePack Studio — SM GUI launch + mok-tua orchestration (GPU-host)

**Date:** 2026-08-05  
**Host:** gpu-host (GPU-host) · orchestrate from desk-host (desk-host) via SSH/role  
**Stamp:** `2026.08-framepack-sm-gui-venv-link`

---

## 1. Incident: `No module named 'einops'` from SM Packages UI

| Layer | What happened |
|-------|----------------|
| **SM Packages → Launch** | Activates `…/FramePack Studio/venv` then `python studio.py` |
| **That venv** | SM-created **empty** env (pip only, Python **3.10** from SM Assets) |
| **Prior fix** | Host uv env at `~/pinokio-host-runtimes/framepack-linux-amd64` (3.12) with torch/einops — used only by `run_framepack_shared_models.sh`, **not** SM GUI |
| **Result** | GUI path: `ModuleNotFoundError: einops` (would next fail on torch, etc.) |

### Fix (applied / re-runnable)

1. Host-local **SM-compatible** venv (cpython **3.10** from SM Assets):  
   `~/pinokio-host-runtimes/framepack-sm310-linux-amd64/env`
2. `uv pip install` torch(cu128) + `requirements.txt` (includes **einops**)
3. **Symlink** package `venv` → that host env (site-packages stay off NFS)
4. Re-Launch from Stability Matrix Packages UI

```bash
# From desk-host → gpu-host
scp ~/mok-tua/scripts/run_framepack_shared_models.sh gpu-host:/tmp/
ssh gpu-host 'bash /tmp/run_framepack_shared_models.sh --install-deps'
# Then SM GUI Launch, or:
ssh gpu-host 'bash /tmp/run_framepack_shared_models.sh --offline --server 0.0.0.0 --port 7864'
```

**Port:** FramePack **7864** (ACE-Step keeps **7865**).  

If SM “repairs” the package and recreates a real `venv/` directory, re-run `--install-deps` (re-links).

---

## 2. Paths (roles, not LAN)

| Role | Path |
|------|------|
| Package (source + GUI entry) | `/mnt/ai-data/stability-matrix/Data/Packages/FramePack Studio` |
| `hf_download` | symlink → `/mnt/ai-data/models/hf_hub` |
| SM package `venv` | symlink → host SM 3.10 env |
| Host SM 3.10 env | `~/pinokio-host-runtimes/framepack-sm310-linux-amd64/env` |
| Optional CLI 3.12 env | `~/pinokio-host-runtimes/framepack-linux-amd64/env` |
| UV cache | `/mnt/ai-data/uv-cache/gpu-host` · `UV_LINK_MODE=copy` |
| Shared models | `/mnt/ai-data/models` |

---

## 3. Launch matrix (mok-tua stack)

| Surface | How to start | Stop | Sees process? |
|---------|--------------|------|----------------|
| **mok-tua conductor** | `mok_tua_cli.py launch framepack_studio --live` | `stop framepack_studio` | launch state + NFS runtime registry |
| **CLI wrapper** | `run_framepack_shared_models.sh --offline --server 0.0.0.0 --port 7864` | mok-tua stop / kill pgid | writes `work/mok-tua/runtime/framepack_studio.json` |
| **Stability Matrix Packages** | Packages → Launch (after `--install-deps` venv link) | SM stop if SM owns PID | SM only for *its* spawn; use LAN URL if mok-tua owns |
| **Browser (LAN)** | `http://gpu-host:7864/` | n/a | Gradio queue / background jobs UI |

**Dual control truth:** SM GUI and mok-tua do **not** share process ownership automatically.  
**Robust model:** one owner (prefer mok-tua) + shared registry + same wrapper for any start path + LAN Gradio for everyone.

### From desk-host (desk-host) — orchestrate, don’t reinstall on Mac

```bash
# 1) one-time / after requirements change (also fixes SM GUI einops)
scp ~/mok-tua/scripts/run_framepack_shared_models.sh gpu-host:/tmp/
ssh gpu-host 'bash /tmp/run_framepack_shared_models.sh --install-deps'

# 2) smoke launch (Gradio on reserved port 7864)
ssh gpu-host 'bash /tmp/run_framepack_shared_models.sh --offline --server 0.0.0.0 --port 7864'
# or: python3 scripts/mok_tua_cli.py launch framepack_studio --live

# 3) open UI from desk browser
open http://gpu-host:7864/
```

Shared registry: `/mnt/ai-data/work/mok-tua/runtime/framepack_studio.json`  

Comfy stills/video remain `http://gpu-host:8188` via mok-tua `ComfyClient` — separate path.

---

## 4. Shared-models law (all launch surfaces)

1. **No** package-local multi-GB HF re-download  
2. `HF_HOME` via `hf_download` → shared `hf_hub`  
3. Prefer `--offline` when hub seeded; `FRAMEPACK_ALLOW_DOWNLOAD=1` only to seed **shared** hub  
4. Outputs/receipts: shared work tree or `$HOME/work/framepack` fallback  

---

## 5. Preflight checklist before “Launch” in SM

```bash
ssh gpu-host 'FP="/mnt/ai-data/stability-matrix/Data/Packages/FramePack Studio"
readlink -f "$FP/venv"
"$FP/venv/bin/python" -c "import einops,torch; print(einops.__version__, torch.__version__, torch.cuda.is_available())"
ls -la "$FP/hf_download"
test -d "$FP/diffusers_helper" && echo diffusers_helper_ok
'
```

| Check | Expect |
|-------|--------|
| `venv` | symlink under `~/pinokio-host-runtimes/framepack-sm310-…` |
| einops | imports (e.g. 0.8.x) |
| torch | CUDA True on 4060 Ti |
| hf_download | → `…/models/hf_hub` |
| diffusers_helper | directory present |

---

## 6. Related apps (same host-split pattern)

| App | Host runtime idea | Notes |
|-----|-------------------|-------|
| FramePack SM | `framepack-sm310-linux-amd64` | this doc |
| FaceFusion | pinokio host env | HTTP :7870 |
| Maestro | pinokio host env | HTTP :7860 |
| ComfyUI | SM / shared models | :8188 |
| Wan Gradio | pinokio | honest skip if ports down |

**Principle:** package **source** on NFS; **venv site-packages** host-local; **weights** on `/mnt/ai-data/models`.

---

## 7. Related docs

- `docs/operations/FRAMEPACK_SHARED_MODELS_2026-08-05.md`  
- `scripts/run_framepack_shared_models.sh`  
- `docs/roadmap/FULL_GAMUT_GPU_FRAMEWORK_2026-08-05.md`  
- UV NFS: control-repo `UV_CACHE_CROSS_HOST_NFS_INCIDENT_2026-08-04.md`  
