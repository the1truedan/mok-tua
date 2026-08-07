# HANDOFF — mok-tua (latest)

**Date:** 2026-08-06  
**Version:** **0.5.9** (C64 software catalog · gpu-prep · Qwen sampling paused · motion sizzle path)  
**Branch:** `agent/mok-tua-staged-pulls-runbooks` → **main** (public)  
**Visibility:** **PUBLIC** — https://github.com/the1truedan/mok-tua · `main` protected

## Start here

1. **Smoke stamp 0.5.7:** [`docs/reports/SMOKE_TESTED_CAPABILITIES_2026-08-05.md`](docs/reports/SMOKE_TESTED_CAPABILITIES_2026-08-05.md) · [`capability_stamp_0.5.7.json`](docs/reports/capability_stamp_0.5.7.json)  
2. **Model pull recheck (video robust):** [`docs/operations/MODEL_PULL_RECHECK_VIDEO_ROBUST_2026-08-06.md`](docs/operations/MODEL_PULL_RECHECK_VIDEO_ROBUST_2026-08-06.md)  
3. **Public flip disclosure recheck:** [`docs/operations/PUBLIC_FLIP_DISCLOSURE_RECHECK_2026-08-06.md`](docs/operations/PUBLIC_FLIP_DISCLOSURE_RECHECK_2026-08-06.md)  
4. **Blade Runner title cards (Rands lane):** [`docs/assets/styles/blade-runner-title/`](docs/assets/styles/blade-runner-title/)  
5. **Capability poster:** [`docs/assets/products-capabilities.png`](docs/assets/products-capabilities.png) (vertical transparency cards)  
6. **TODO:** [`TODO.md`](TODO.md)  
7. **I2V provenance:** [`docs/operations/I2V_GROK_VS_LOCAL_GPU_CONTEXT_AMBIGUITY_INCIDENT_2026-08-05.md`](docs/operations/I2V_GROK_VS_LOCAL_GPU_CONTEXT_AMBIGUITY_INCIDENT_2026-08-05.md)  
8. **Context pit (control):** `~/grokcode/docs/operations/AGENT_CONTEXT_PIT_AND_MULTI_CLI_CONTINUITY_2026-08-05.md`

## 2026-08-06 wave

| Item | Notes |
|------|--------|
| Qwen Image Edit 2509 fp8 | **PRESENT** · sampling **PAUSED** on 16 GB (OOM) — do not hammer |
| Manager pivot slideshow | **14.20 s** panel-hold · public · not generative motion |
| Motion sizzle | AnimateDiff I2V script `render_motion_sizzle_from_still.py` + `gpu-prep` |
| C64 software catalog | `software` · `disk` · demoscene load screens · `gpu-prep` |
| MiniMax H3 | Manifest only — after Comfy ≥0.30 |
| Public | https://github.com/the1truedan/mok-tua |

## What 0.5.7 shipped

| Item | Notes |
|------|--------|
| Transparency poster | Individual cards + path/prompt under each photo |
| Fixed PETSCII boot | 5×5 glyphs · inverse loader colors |
| IPAdapter panels | plus-face img2img · `capabilities/panels/01–06` |
| Face polish | BEFORE/AFTER · forehead “ceo” kept |
| IRL UIs | Comfy · FramePack · Director screenshots |
| FaceID InsightFace | **residual** (models incomplete) — not claimed |

## Smoke (last confirmed)

| Check | Result |
|-------|--------|
| Unit tests | 22 OK |
| PETSCII + inverse boot | PASS |
| CLI REPL | PASS |
| IPAdapter panels + polish | PASS |
| AnimateDiff strip | PASS (prior) |
| FramePack UI | PASS screenshot · mp4 finalize open |
| Director UI | PASS screenshot · backends empty residual |
| Public flip | pending human |

## Paste for new chat

```text
Continue from mok-tua HANDOFF.md · version 0.5.7
products-capabilities.png = vertical transparency poster (IRL UIs + IPAdapter panels)
FaceID InsightFace residual; plus-face path used. Grok I2V ≠ local GPU. Human public flip only.
```
