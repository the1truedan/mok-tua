# Smoke-tested capabilities — mok-tua **0.5.6**

**Date:** 2026-08-05 (lab)  
**Branch:** `agent/mok-tua-staged-pulls-runbooks` → merge to `main` (private)  
**Comfy:** gpu-host `:8188` · ComfyUI **0.29.0** · RTX 4060 Ti  
**Policy:** accuracy over montage · never label cloud I2V as gpu-host local

---

## Tested matrix

| Capability | Status | Evidence |
|------------|--------|----------|
| Unit tests | **PASS** | `python3 -m unittest discover -s tests -q` → 20 OK |
| Conductor TUI PETSCII boot | **PASS** | `tui/petscii.py` + `docs/assets/mokup-c64-tui-live-boot.png` |
| Conductor TUI two-pane + VIC-II stats | **PASS** | `tui/app.py` + `mokup-c64-tui-live.png` |
| Skins c64 / green / mono / modern | **PASS** | `tui/themes/*.tcss` · aliases 1980crt |
| Artifact receipt stamp + host sample | **PASS** | `api/artifact_receipt.py` · CLI `receipt stamp` |
| gpu-host Comfy still (DreamShaper_8) | **PASS** | CEO storyboard hybrid · GPU util samples peak **100%** |
| CEO storyboard sheet regen | **PASS** | `docs/assets/example-storyboard-sheet.jpg` + receipt |
| CEO face polish img2img | **PASS** | `docs/assets/example-face-polish.jpg` + receipt |
| AnimateDiff short loop (QQQ0) | **PASS** | `work/ceo_capability_regen/ceo_animatediff.mp4` · frame strip in assets |
| Capability collage (accurate workflow) | **PASS** | `docs/assets/products-capabilities.png` from rewritten HTML |
| FramePack UI I2V (API + GPU) | **IN PROGRESS / partial** | Gradio `:7864` · VAE→CLIP→sampling · util ~100% · see `FRAMEPACK_I2V_SMOKE` + receipt |
| Wan **weights** on pool | **PASS** (inventory) | `wan2.2_i2v_*_14B_fp8` present · `WAN_WEIGHTS_STAGING` |
| Wan live Gradio ports | **SKIP** (honest) | pinokio gamut until ports up |
| IPAdapter FaceID weights | **PASS** | 7 files in `models/ipadapter/` · Comfy loader lists |
| Director stack HTTP | **PASS** | UI 5173 · CPE 9800 · orch 9820 healthy |
| Director Comfy backend registry | **FAIL** | `/api/backends` empty — register in UI |
| Cloud Grok Imagine I2V | **NOT DEFAULT** | I2V incident law — QQQ1 only, never “local” |

---

## Regenerated assets (this stamp)

| Asset | Renderer | Model | Host | Notes |
|-------|----------|-------|------|-------|
| `example-storyboard-sheet.jpg` | `gpu-host_comfy_storyboard_hybrid` | DreamShaper_8_pruned | gpu-host | Replaces woman instructor sheet; CEO context |
| `example-face-polish.jpg` | `gpu-host_comfy_img2img_face_polish` | DreamShaper_8_pruned | gpu-host | BEFORE=source still · AFTER=denoise≈0.28 |
| `ceo-i2v-frame-strip.jpg` | `gpu-host_comfy_animatediff` | DS8 + mm_sd_v15_v2.fp16 | gpu-host | From AD mp4; not git blob video |
| `products-capabilities.png` | HTML→Chrome screenshot | n/a | desk | Accurate workflow collage |
| `mokup-c64-tui-live*.png` | TUI composite | n/a | desk | Boot + two-pane |

Receipts: `docs/assets/receipts/*.receipt.json` (+ optional sidecars next to JPGs).

## Unchanged (intentionally)

- `pres-smoke/00-ceo-source-still.jpg` (seed only)  
- `pres-smoke/01`–`04` mockups (still route-unknown — see PROVENANCE.md)  
- Vendor Comfy/Director mokups and graphs (labeled example vs executed)

---

## Operator re-run

```bash
export COMFY_URL=http://REDACTED-LAN-IP:8188   # or gpu-host if resolved
python3 scripts/regen_ceo_capability_assets.py
# collage:
# Chrome headless → docs/assets/products-capabilities.png
python3 -m unittest discover -s tests -q
```
