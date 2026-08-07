# HANDOFF — mok-tua (latest)

**Date:** 2026-08-06  
**Version:** **0.5.10** (PETSCII Matrix v4 brand short · TUI launch workflow · show/play media)  
**Branch:** `main` (public)  
**Visibility:** **PUBLIC** — https://github.com/the1truedan/mok-tua · `main` protected

## Start here

1. **Brand short:** [`docs/assets/exports/mok-tua-petscii-matrix-export.mp4`](docs/assets/exports/mok-tua-petscii-matrix-export.mp4) · cite [`docs/assets/exports/README.md`](docs/assets/exports/README.md)  
2. **Launch TUI:** `python3 scripts/mok_tua_cli.py tui` → PETSCII intro → CLI help → status → deck  
3. **Smoke stamp 0.5.7:** [`docs/reports/SMOKE_TESTED_CAPABILITIES_2026-08-05.md`](docs/reports/SMOKE_TESTED_CAPABILITIES_2026-08-05.md)  
4. **Model pull recheck (video robust):** [`docs/operations/MODEL_PULL_RECHECK_VIDEO_ROBUST_2026-08-06.md`](docs/operations/MODEL_PULL_RECHECK_VIDEO_ROBUST_2026-08-06.md)  
5. **TODO:** [`TODO.md`](TODO.md)  
6. **Context pit (control):** `~/grokcode/docs/operations/AGENT_CONTEXT_PIT_AND_MULTI_CLI_CONTINUITY_2026-08-05.md`

## 2026-08-06 wave

| Item | Notes |
|------|--------|
| PETSCII Matrix export v4 | ~28s · loader→µ→bright logo→CRT off→tmux→disk menu · locked |
| TUI launch workflow | `tui/workflow.py` · help + status on deck · `show`/`play`/`open` jpg/png/mp4 |
| Qwen Image Edit 2509 fp8 | **PRESENT** · sampling **PAUSED** on 16 GB (OOM) — do not hammer |
| Manager pivot slideshow | **14.20 s** panel-hold · public · not generative motion |
| Motion sizzle | AnimateDiff I2V + `gpu-prep` |
| C64 software catalog | `software` · `disk` · demoscene load screens · `gpu-prep` |
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
