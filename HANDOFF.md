# HANDOFF — mok-tua (latest)

**Date:** 2026-08-15 (video model coverage + Director's Console + curate)  
**Version:** **0.6.0** (MiniMax H3 + LTX-2.3 confirmed · DC job submission verified · `curate` tool · lipsync integration points)  
**Branch:** `main` · GitHub `6fa99de`..`56e6743`  
**Visibility:** **PUBLIC** — https://github.com/the1truedan/mok-tua · `main` protected  
**Remotes:** `github` (canonical public) · `forgejo` (lab mirror, diverged history — do not rebase across)

## Start here

1. **This file** — current state  
2. **Latest release:** [`v0.6.0`](https://github.com/the1truedan/mok-tua/releases/tag/v0.6.0) · full notes in [`CHANGELOG.md`](CHANGELOG.md) · [`docs/MILESTONES.md`](docs/MILESTONES.md)  
3. **Launch TUI:** `python3 scripts/mok_tua_cli.py tui` → PETSCII intro → CLI help → status → deck  
4. **Curate a cut:** `python3 scripts/mok_tua_cli.py curate scan|list|pick|order|assemble` — pick best takes across runs, ffmpeg-concat them in order  
5. **Interfaces:** [`docs/INTERFACES.md`](docs/INTERFACES.md) (launch workflow · media · software disks)  
6. **Smoke stamp:** [`docs/reports/SMOKE_TESTED_CAPABILITIES_2026-08-07.md`](docs/reports/SMOKE_TESTED_CAPABILITIES_2026-08-07.md) · [`docs/operations/ORCHESTRATION_SMOKE_CITED_2026-08-07.md`](docs/operations/ORCHESTRATION_SMOKE_CITED_2026-08-07.md)  
7. **TODO:** [`TODO.md`](TODO.md)  
8. **Context pit (control):** `(private control plane — not required for public mok-tua use)`

## Paste for new chat

```text
Continue from ~/mok-tua/HANDOFF.md · version 0.6.0 · main public

DONE this arc:
- MiniMax H3 image-to-video confirmed working end to end (isolated ComfyUI env,
  needed for a newer core version without breaking the main install)
- LTX-2.3 text-to-video with synced audio confirmed working end to end
- Director's Console job submission verified end to end — real rendered file on
  disk checked, not just a 200 response (closes the prior "backends registry
  residual empty" gap below)
- New `curate` CLI subcommand (api/curate.py): scan/list/pick/order/assemble —
  pick the best take of a shot across separate runs, ffmpeg-concat the picks
- Lipsync tool integration points (face-swap/talking-head/portrait-animation)
  identified and wired into the model registry — full proof run still pending
- No demo video shipped with this release yet — pipeline pieces proven
  individually, a finished example is still in progress

PRIOR still true:
- Qwen Edit 2509 fp8 PRESENT · sampling PAUSED on 16GB OOM — do not hammer
- Manager pivot 14.20s panel-hold slideshow (not generative motion)
- Motion sizzle AnimateDiff path + gpu-prep; prefer WAN/AD over Qwen OOM path
- C64 software catalog software/disk/gpu-prep
- PETSCII Matrix v4 brand short + TUI launch workflow (see CHANGELOG 0.5.10)
- Grok I2V ≠ local GPU · FaceID InsightFace residual · PHI never

NEXT (optional polish, not blocking):
- Full song → video → lipsync proof run (the piece still missing above)
- Live Comfy/FramePack/Directors log stream into TUI RichLog demoscene filter
- True WAN 2.2 dual-noise low-MP API pin (Lightning LoRAs on pool)
- FramePack mp4 artifact_ok finalize residual
```

## 2026-08-15 wave (0.6.0)

| Item | Notes |
|------|--------|
| **MiniMax H3 confirmed** | Isolated ComfyUI install, image-to-video, real output checked |
| **LTX-2.3 confirmed** | Text-to-video with synced audio, same isolated install |
| **Director's Console verified** | Job submission end to end — real file on disk, not just a success response |
| **`curate` tool** | `scripts/mok_tua_cli.py curate scan\|list\|pick\|order\|assemble` — best-take picking across runs |
| **Lipsync integration points** | Face-swap/talking-head/portrait-animation wired into the model registry; proof run pending |
| Public | https://github.com/the1truedan/mok-tua |

## 2026-08-06 wave (0.5.8 → 0.5.10)

| Item | Notes |
|------|--------|
| **0.5.10 PETSCII Matrix v4** | ~28s · loader→µ→bright logo→CRT→tmux→disk menu · **locked on main** |
| **0.5.10 TUI launch workflow** | `tui/workflow.py` · help + status on deck · `show`/`play`/`open` jpg/png/mp4 |
| **0.5.9 C64 catalog** | `software` · `disk` · demoscene load screens · `gpu-prep` |
| **0.5.9 Motion sizzle** | AnimateDiff I2V ~5s · 2 segments · not slideshow |
| **0.5.8 Manager pivot** | **14.20 s** panel-hold anime multi-angle · public |
| Qwen Image Edit 2509 fp8 | **PRESENT** · sampling **PAUSED** on 16 GB (OOM) |
| Public | https://github.com/the1truedan/mok-tua |

## Launch workflow (operator)

```bash
cd ~/mok-tua
python3 scripts/mok_tua_cli.py tui
# faster offline:
python3 scripts/mok_tua_cli.py tui --no-status
# skip CLI preflight print:
python3 scripts/mok_tua_cli.py tui --no-intro

# at READY.
menu
media
show docs/assets/exports/mok-tua-petscii-matrix-poster.png
play docs/assets/exports/mok-tua-petscii-matrix-export.mp4
doctor
software
disk COMFYUI --splash
```

| Step | What |
|------|------|
| 1 | CLI PETSCII loader (char-cell LOADING bar) |
| 2 | CLI args menu + C64 disk directory text |
| 3 | `status` + `software` probes |
| 4 | Textual PETSCII splash → two-pane deck |
| 5 | READY. — commands + show/play/open media |

Re-render brand short:

```bash
python3 scripts/render_petscii_matrix_export.py --procedural-boot
```

## Smoke (last confirmed)

| Check | Result |
|-------|--------|
| Unit tests `test_tui_petscii` | **8 OK** (0.5.10) |
| PETSCII Matrix export v4 | **PASS** · 28s · 1280×720 · 24fps · on main |
| TUI resolve_command media/menu | **PASS** |
| Prior 0.5.7 smoke stamp | PASS (see reports) |
| Qwen KSampler | **PAUSED** OOM 16GB |
| FramePack mp4 finalize | residual open |
| Director backends registry | residual empty |

## What 0.5.7 shipped (still cite)

| Item | Notes |
|------|--------|
| Transparency poster | Individual cards + path/prompt under each photo |
| Fixed PETSCII boot | 5×5 glyphs · inverse loader colors |
| IPAdapter panels | plus-face img2img · `capabilities/panels/01–06` |
| Face polish | BEFORE/AFTER · forehead “ceo” kept |
| IRL UIs | Comfy · FramePack · Director screenshots |
| FaceID InsightFace | **residual** (models incomplete) — not claimed |

## Hippo tags (recall)

Prefer: `agent-context` · `repeated-reminder` · `mok-tua` · `breakthrough`  
`HIPPO_CONTEXT_CITATIONS_ONLY=1` for bounded repo-relative citations only.  
Do not put PHI, secrets, or LAN credentials in Hippo.

| ID | Note |
|----|------|
| `mem_83d4e6eb6f33` | 0.5.10 PETSCII v4 + TUI launch workflow (pinned · verified) |
| `mem_3cb5f0a9cd8e` | media show/play/open at READY. (pinned · repeated-reminder) |
| `mem_ca468b33ba22` | control mirror handoff pointer (grokcode · pinned) |

## Laws that stay true

- Grok Imagine I2V ≠ local GPU generative — label both.  
- ffmpeg Ken Burns / panel-hold ≠ generative motion.  
- One active GPU renderer; `gpu-prep` before heavy video; free Comfy between segments.  
- Hot render scratch local SSD → promote finals to ai-data; bees settled only.  
- Public tree: role hostnames only (`gpu-host`), no home absolute paths in receipts.  
- PHI never on cloud LLM or public git.
