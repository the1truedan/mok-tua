# HANDOFF — mok-tua (latest)

**Date:** 2026-09-12 (H3 VocalLock lipsync smoke notations on public GitHub)  
**Version:** **0.7.0** product · **Unreleased** docs stamp 2026-09-12  
**Branch:** `main` · GitHub canonical  
**Visibility:** **PUBLIC** — https://github.com/the1truedan/mok-tua · `main` protected  
**Remotes:** `github` (canonical public) · `forgejo` (lab mirror, diverged history — do not rebase across)

## Start here

1. **This file** — current state  
2. **Latest release:** [`v0.7.0`](https://github.com/the1truedan/mok-tua/releases/tag/v0.7.0) · full notes in [`CHANGELOG.md`](CHANGELOG.md) · [`docs/MILESTONES.md`](docs/MILESTONES.md)  
3. **H3 VocalLock lipsync PASS:** [`docs/reports/SMOKE_TESTED_CAPABILITIES_2026-09-12.md`](docs/reports/SMOKE_TESTED_CAPABILITIES_2026-09-12.md) — verse batch 5/5, cited robustness links  
4. **Launch TUI:** `python3 scripts/mok_tua_cli.py tui` → PETSCII intro → CLI help → status → deck  
5. **Curate a cut:** `python3 scripts/mok_tua_cli.py curate scan|list|pick|order|assemble` — pick best takes across runs, ffmpeg-concat them in order  
6. **Interfaces:** [`docs/INTERFACES.md`](docs/INTERFACES.md) (launch workflow · media · software disks)  
7. **Prior smoke:** [`docs/reports/SMOKE_TESTED_CAPABILITIES_2026-08-15.md`](docs/reports/SMOKE_TESTED_CAPABILITIES_2026-08-15.md) · [`docs/operations/ORCHESTRATION_SMOKE_CITED_2026-08-07.md`](docs/operations/ORCHESTRATION_SMOKE_CITED_2026-08-07.md)  
8. **TODO:** [`TODO.md`](TODO.md)  
9. **Context pit (control):** `(private control plane — not required for public mok-tua use)`

## Paste for new chat

```text
Continue from ~/mok-tua/HANDOFF.md · version 0.7.0 · main public

DONE this arc (2026-09-12):
- MiniMax H3 VocalLock_V3 lipsync smoke notations landed on the public
  GitHub repo. Isolated ComfyUI :8189, verse batch 5/5 scenes, 32s window.
  Stamp: docs/reports/SMOKE_TESTED_CAPABILITIES_2026-09-12.md
- Cited public robustness links (MiniMax H3, Comfy-Org weights, LightX2V,
  T8mars Vocal Lock, Maestro, comfy-cli/comfy-mcp) on README + Pages +
  COMFY_ROBUST_NODES. Do not conflate with DreamTalk/LivePortrait/FaceFusion.

PRIOR still true:
- PocketTTS + DramaBox generation-verified (0.7.0). DramaBox is GPU-near-exclusive.
- LTX-2 audio-conditioned proof clips still on the live site (different mechanism).
- Qwen Edit 2509 fp8 PRESENT · sampling PAUSED on 16GB OOM — do not hammer
- Manager pivot 14.20s panel-hold slideshow (not generative motion)
- Grok I2V ≠ local GPU · FaceID InsightFace residual · PHI never
- Dedicated DreamTalk / LivePortrait / FaceFusion render still pending
- Maestro H3 Sol Engine picker still allowlist-blocked on a name-mismatched
  Ref2VA file (2026-09-02 audit) — that is not the VocalLock PASS path

NEXT (optional polish, not blocking):
- Dedicated lipsync-tool smoke (DreamTalk first) — the 08-17 earmark
- Verify the other 7 earmarked cloud Spaces the same way PocketTTS/DramaBox
  were verified (view_api(), one real call, only then write a backends/*.py)
- Retry hf_musicgen with a real reference clip instead of melodies=None
- hf_openvoice needs an older gradio_client pin or a direct HTTP call
- Live Comfy/FramePack/Directors log stream into TUI RichLog demoscene filter
- True WAN 2.2 dual-noise low-MP API pin (Lightning LoRAs on pool)
- FramePack mp4 artifact_ok finalize residual
```

## 2026-09-12 wave (docs / smoke notations)

| Item | Notes |
|------|--------|
| **H3 VocalLock_V3 PASS** | Isolated ComfyUI `:8189`, verse batch 5/5 scenes, 32s, 16 GB. Native AV lipsync — not LTX-2, not DreamTalk. |
| **Cited robustness links** | MiniMax H3 · Comfy-Org weights · LightX2V · T8mars Vocal Lock · Maestro · comfy-cli / comfy-mcp on README, Pages, and the 09-12 smoke report |
| **Not claimed** | Verse 2 / Director LTX-2.5 batch · dedicated lipsync tools · Maestro H3 picker |
| Public | https://github.com/the1truedan/mok-tua |

## 2026-09-02 wave (0.7.0)

| Item | Notes |
|------|--------|
| **PocketTTS backend** | `api/backends/pocket_tts.py` — generation-verified, real wav produced, no caveats |
| **DramaBox backend** | `api/backends/dramabox.py` — generation-verified, but GPU-near-exclusive confirmed by a real OOM; excluded from the concurrent "audio" launch chain |
| **HF Spaces category puller** | `scripts/sync_hf_spaces_by_category.py` — reads HF's real `?category=` pages, 300+ Spaces |
| **11 cloud-call earmarks** | `kind: "hf_space"` provider entries, none default-wired; 2/4 live-tested were down or incompatible |
| Public | https://github.com/the1truedan/mok-tua |

## 2026-08-15 wave (0.6.0)

| Item | Notes |
|------|--------|
| **MiniMax H3 confirmed** | Isolated ComfyUI install, image-to-video, real output checked |
| **LTX-2.3 confirmed** | Text-to-video with synced audio, same isolated install |
| **Director's Console verified** | Job submission end to end — real file on disk, not just a success response |
| **`curate` tool** | `scripts/mok_tua_cli.py curate scan\|list\|pick\|order\|assemble` — best-take picking across runs |
| **Lipsync integration points** | Face-swap/talking-head/portrait-animation wired into the model registry; **those tools** still unproven. Native H3 VocalLock and LTX-2 audio-conditioned are the two PASSes. |
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
