# Smoke-tested capabilities — mok-tua **0.5.10** (+ 2026-08-07 orchestration)

**Date:** 2026-08-07  
**Public:** https://github.com/the1truedan/mok-tua  
**Comfy lab pin:** **0.30.2** · torch 2.6.0+cu124 · `gpu-host:8188` · `--lowvram` recommended on 16 GB  
**Policy:** accuracy over montage · path + receipt under each PASS · never label cloud I2V as local GPU

**Orchestration SSOT:** [`docs/operations/ORCHESTRATION_SMOKE_CITED_2026-08-07.md`](../operations/ORCHESTRATION_SMOKE_CITED_2026-08-07.md)  
**Prior matrix (0.5.7 poster era):** [`SMOKE_TESTED_CAPABILITIES_2026-08-05.md`](SMOKE_TESTED_CAPABILITIES_2026-08-05.md)

---

## Tested matrix (cited)

| Capability | Status | Evidence |
|------------|--------|----------|
| Unit tests | **PASS** | `python3 -m unittest discover -s tests -q` |
| PETSCII / TUI launch workflow (0.5.10) | **PASS** | `docs/operations/SESSION_HANDOFF_2026-08-06_0.5.10_PETSCII_LAUNCH_WORKFLOW.md` · brand short export |
| Artifact receipts | **PASS** | `api/artifact_receipt.py` · `docs/assets/receipts/*` |
| CEO identity seed (forehead “ceo”) | **PASS** | `docs/assets/pres-smoke/00-ceo-source-still.jpg` |
| FaceID PLUS V2 storyboard panels | **PASS** | `scripts/regen_ceo_capability_assets.py` · prior panels/receipts |
| **CMIP origin 8-panel FaceID storyboard** | **PASS** | `docs/assets/cmip-terpene-origin/` · `scripts/regen_cmip_terpene_storyboard.py` · receipt `cmip-terpene-origin-storyboard.receipt.json` |
| AnimateDiff generative sizzle | **PASS** (week of 08-07) | `docs/assets/exports/manager-pivot-motion-sizzle-animatediff.mp4` |
| Exclusive GPU free + gate loop | **PASS** (ops) | documented in orchestration smoke · restart if residual VRAM after big models |
| MiniMax H3 native nodes + weights | **PARTIAL** | loaders/nodes OK; day-0 generic KSampler path not green |
| Qwen Image Edit full KSampler | **PAUSED_OOM_16GB** | do not hammer |
| FramePack long I2V | **UI/prior** | see FramePack ops docs; exclusive window |

---

## Regenerated / new assets (2026-08-07)

| Asset | Renderer |
|-------|----------|
| `docs/assets/cmip-terpene-origin/0N_*.jpg` | `gpu_comfy_faceid_plus_v2` (local Comfy · **not Imagine**) |
| `docs/assets/cmip-terpene-origin/cmip-origin-storyboard-sheet.jpg` | collage of 8 panels |
| `docs/assets/receipts/cmip-terpene-origin-storyboard.receipt.json` | custody stamp |

Face ref: `docs/assets/pres-smoke/00-ceo-source-still.jpg`  
External story repo: https://github.com/the1truedan/cmip-terpene-db

---

## Operator re-run

```bash
export COMFY_URL=http://gpu-host:8188
python3 -m unittest discover -s tests -q
curl -s -X POST "$COMFY_URL/free" -H 'Content-Type: application/json' \
  -d '{"unload_models":true,"free_memory":true}'
PYTHONPATH=scripts:api:. python3 scripts/regen_cmip_terpene_storyboard.py
```
