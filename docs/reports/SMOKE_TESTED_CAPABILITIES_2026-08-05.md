# Smoke-tested capabilities — mok-tua **0.5.7**

**Date:** 2026-08-05 (lab) · stamp refresh for transparency poster  
**Branch:** `agent/mok-tua-staged-pulls-runbooks` → `main` (private)  
**Comfy:** gpu-host `:8188` · ComfyUI **0.29.0** · RTX 4060 Ti  
**Policy:** accuracy over montage · IRL UI screenshots · path+prompt under each capability card · never label cloud I2V as gpu-host local

Catalog: [`capability_stamp_0.5.7.json`](capability_stamp_0.5.7.json)

---

## Tested matrix

| Capability | Status | Evidence |
|------------|--------|----------|
| Unit tests | **PASS** | `python3 -m unittest discover -s tests -q` → 22 OK |
| PETSCII boot fixed + inverse | **PASS** | 5×5 glyphs · `ui-tui-boot.png` · `tui/petscii.py` |
| Conductor two-pane + VIC-II | **PASS** | `ui-tui-deck.png` / `mokup-c64-tui-live.png` |
| CLI REPL launch | **PASS** | `ui-cli-repl.png` · `tui --repl --skin c64` |
| Artifact receipt stamp | **PASS** | `api/artifact_receipt.py` |
| IPAdapter plus-face storyboard panels | **PASS** | `capabilities/panels/01–06-*.jpg` + receipts |
| CEO face polish (BEFORE/AFTER) | **PASS** | `example-face-polish.jpg` · forehead “ceo” kept |
| AnimateDiff frame strip | **PASS** (prior 0.5.6) | `ceo-i2v-frame-strip.jpg` · GPU 100% |
| ComfyUI IRL screenshot | **PASS** | `ui-comfy-ceo.png` |
| FramePack Gradio IRL | **PASS** (UI) | `ui-framepack.png` · mp4 finalize **pending** |
| Director IRL | **PASS** (UI) | `ui-director.png` · backends empty residual |
| Transparency poster | **PASS** | `products-capabilities.png` vertical cards |

## Pending / earmarked (not PASS)

| Item | Note |
|------|------|
| FaceID InsightFace | buffalo_l incomplete · antelope loader error — residual |
| FramePack mp4 `artifact_ok` | status receipt only |
| Wan live Gradio ports | honest skip |
| Director Comfy backend register | `/api/backends` empty |
| InstantID / FaceFusion CUDA polish | residual |

---

## Regenerated assets (0.5.7)

| Asset | Renderer / source |
|-------|-------------------|
| `capabilities/panels/0N-*.jpg` | `gpu-host_comfy_ipadapter_plusface_img2img` |
| `example-storyboard-sheet.jpg` | collage of panels |
| `example-face-polish.jpg` | plus-face polish denoise 0.32 |
| `capabilities/ui/*` | IRL screenshots + PETSCII render |
| `products-capabilities.png` | HTML→Chrome vertical poster |

Source still **unchanged:** `pres-smoke/00-ceo-source-still.jpg`  
Pres-smoke 01–04 remain mock / route-unknown.

---

## Operator re-run

```bash
export COMFY_URL=http://gpu-host:8188
python3 scripts/regen_ceo_ipadapter_panels_0_5_7.py
# poster:
# Chrome headless → docs/assets/mokups/capability-collage.html → products-capabilities.png
python3 -m unittest discover -s tests -q
```
