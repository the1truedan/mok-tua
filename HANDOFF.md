# HANDOFF — mok-tua (latest)

**Date:** 2026-08-06  
**Version:** **0.5.10** (PETSCII Matrix v4 brand short · TUI launch workflow · show/play media)  
**Branch:** `main` @ **`a054a60`** (+ follow-up handoff commit if present)  
**Visibility:** **PUBLIC** — https://github.com/the1truedan/mok-tua · `main` protected  
**Remotes:** `github` (canonical public) · `forgejo` (lab mirror)

## Start here

1. **This file** + ops handoff: [`docs/operations/SESSION_HANDOFF_2026-08-06_0.5.10_PETSCII_LAUNCH_WORKFLOW.md`](docs/operations/SESSION_HANDOFF_2026-08-06_0.5.10_PETSCII_LAUNCH_WORKFLOW.md)  
2. **Brand short:** [`docs/assets/exports/mok-tua-petscii-matrix-export.mp4`](docs/assets/exports/mok-tua-petscii-matrix-export.mp4) · cite [`docs/assets/exports/README.md`](docs/assets/exports/README.md)  
3. **Launch TUI:** `python3 scripts/mok_tua_cli.py tui` → PETSCII intro → CLI help → status → deck  
4. **Interfaces:** [`docs/INTERFACES.md`](docs/INTERFACES.md) (launch workflow · media · software disks)  
5. **Smoke stamp 0.5.7:** [`docs/reports/SMOKE_TESTED_CAPABILITIES_2026-08-05.md`](docs/reports/SMOKE_TESTED_CAPABILITIES_2026-08-05.md)  
6. **TODO:** [`TODO.md`](TODO.md)  
7. **Context pit (control):** `~/grokcode/docs/operations/AGENT_CONTEXT_PIT_AND_MULTI_CLI_CONTINUITY_2026-08-05.md`

## Paste for new chat

```text
Continue from ~/mok-tua/HANDOFF.md · version 0.5.10 · main public
→ docs/operations/SESSION_HANDOFF_2026-08-06_0.5.10_PETSCII_LAUNCH_WORKFLOW.md
→ docs/assets/exports/README.md (PETSCII Matrix v4 cite)

DONE this arc (public GH main a054a60+):
- PETSCII Matrix brand short v4 (~28s): loader → µ rain → bright MOK-TUA → CRT off →
  tmux CLI → INSERT DISK → C64 disk directory (args · prompts · caps)
  re-render: scripts/render_petscii_matrix_export.py
- TUI launch workflow (tui/workflow.py): PETSCII intro → CLI help/args → status+software
  probes → deck; READY. accepts show/play/open for jpg|png|mp4
- verbs: menu · media · open · W software · K disk · G gpu-prep
- escapes: tui --no-intro · --no-status
- unit tests test_tui_petscii 8 OK

PRIOR still true:
- Qwen Edit 2509 fp8 PRESENT · sampling PAUSED on 16GB OOM — do not hammer
- Manager pivot 14.20s panel-hold slideshow (not generative motion)
- Motion sizzle AnimateDiff path + gpu-prep; prefer WAN/AD over Qwen OOM path
- C64 software catalog software/disk/gpu-prep
- Grok I2V ≠ local GPU · FaceID InsightFace residual · PHI never

NEXT (optional polish, not blocking):
- Live Comfy/FramePack/Directors log stream into TUI RichLog demoscene filter
- True WAN 2.2 dual-noise low-MP API pin (Lightning LoRAs on pool)
- FramePack mp4 artifact_ok finalize residual
```

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
