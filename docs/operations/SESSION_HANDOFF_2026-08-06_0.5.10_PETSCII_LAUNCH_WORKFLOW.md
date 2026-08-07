# Session handoff — mok-tua **0.5.10** PETSCII Matrix v4 · TUI launch workflow

**Date:** 2026-08-06  
**Repo:** `~/mok-tua` · dual remote **github** (public) + **forgejo**  
**Branch:** `main` @ **`a054a60`** (PETSCII + workflow) · handoff docs follow-up  
**Version:** **0.5.10**  
**Visibility:** **PUBLIC** — https://github.com/the1truedan/mok-tua  
**Control mirror:** `~/grokcode/docs/operations/SESSION_HANDOFF_2026-08-06_MOK_TUA_0.5.10_PETSCII.md` (if present)

---

## 0. Paste into new chat

```text
Continue from ~/mok-tua/HANDOFF.md · 0.5.10 public main
→ docs/operations/SESSION_HANDOFF_2026-08-06_0.5.10_PETSCII_LAUNCH_WORKFLOW.md

Brand: docs/assets/exports/mok-tua-petscii-matrix-export.mp4 (~28s v4)
TUI: python3 scripts/mok_tua_cli.py tui
  → PETSCII intro → CLI help → status → deck
  → show/play/open jpg|png|mp4 · menu · media
Re-render: python3 scripts/render_petscii_matrix_export.py --procedural-boot

Qwen sampling PAUSED 16GB OOM. Prefer WAN/AnimateDiff sizzle over hammering Qwen.
Grok I2V ≠ local GPU. PHI never. gpu-prep before video segments.
```

---

## 1. What shipped (this session arc)

### Brand export v4

| Field | Value |
|-------|--------|
| Path | `docs/assets/exports/mok-tua-petscii-matrix-export.mp4` |
| Poster | `docs/assets/exports/mok-tua-petscii-matrix-poster.png` (disk menu still) |
| Duration | **28.0 s** · 672 frames · 24 fps · 1280×720 |
| Method | Procedural PIL + ffmpeg (CPU) · glyphs `tui/petscii.py` |
| Script | `scripts/render_petscii_matrix_export.py` |
| Cite | **(post-FaceID)** packaging era · **not** a face demo · QQQ0 |

**Beat sheet:**
1. C64 loader — character-cell LOADING bar 0→100%  
2. µ rain → resolves to PETSCII **MOK-TUA**  
3. Rain stops · logo brightens  
4. CRT TV turn-off (squash → center line → blip → black)  
5. tmux CLI (`0:mok-tua*`) help / doctor / software typewriter  
6. INSERT DISK splash (drive 8)  
7. C64 disk directory — args, prompt types (SEQ), capabilities (USR) + LOAD examples  

**Why not “prompt re-render”:** original short was static boot PNG hold + frozen mid-fill bar, then hard-cut to rain. v3/v4 rebuild procedural animation.

### TUI / CLI launch workflow

| Module | Role |
|--------|------|
| `tui/workflow.py` | Shared sequence: PETSCII print · CLI help · status/software · media-ready · deck lines |
| `tui/__main__.py` | `--no-intro` · `--no-status` · preflight before Textual |
| `tui/app.py` | Boot splash → deck intro with status; `menu`/`media`/`show`/`play`/`open` |
| `tui/repl.py` | Same verbs without Textual |
| `tui/bridge.py` | Shortcuts W/K/G · software/disk/gpu-prep · open→play |
| `tui/media.py` | `list_recent_media` · open alias |
| `tui/petscii.py` | `cli_args_menu` · `disk_directory_menu` |
| `scripts/mok_tua_cli.py` | `tui` passes intro flags |

**At READY. (examples):**
```text
menu
media
show docs/assets/exports/mok-tua-petscii-matrix-poster.png
play docs/assets/exports/mok-tua-petscii-matrix-export.mp4
open work/some_out.jpg
doctor
software
disk FRAMEPACK --splash
gpu-prep --profile video
```

### Prior wave still in tree (0.5.8–0.5.9)

- Manager pivot anime multi-angle **14.20 s** slideshow + PROVENANCE  
- AnimateDiff motion sizzle ~5 s (generative; not slideshow)  
- C64 software catalog JSON + `software` / `disk` / `gpu-prep`  
- Qwen Edit weights staged; **KSampler OOM** → sampling paused  

---

## 2. Git evidence

| Ref | Note |
|-----|------|
| `a054a60` | Lock PETSCII Matrix v4 brand short and TUI launch workflow (0.5.10) |
| Remote | `github` `main` pushed |

Do not re-commit unrelated dirty lab ops (`FRAMEPACK_*` smoke notes) unless intentional.

---

## 3. Tests

```bash
cd ~/mok-tua
python3 -m unittest tests.test_tui_petscii -v
# expected: 8 OK
```

---

## 4. Open residuals (honest)

| Item | Status |
|------|--------|
| Qwen Image Edit sampling on 16 GB | **PAUSED** — do not hammer |
| FramePack CEO mp4 `artifact_ok` finalize | open |
| Director backends registry | empty until UI register |
| Live tool log → demoscene RichLog stream | polish / not shipped |
| WAN 2.2 dual-noise low-MP API pin | optional polish (LoRAs on pool) |
| forgejo main sync | verify if lab mirror lagging |

---

## 5. Hippo (written this close)

| ID | Tags | Content summary |
|----|------|-----------------|
| `mem_83d4e6eb6f33` | agent-context · mok-tua · breakthrough · pin · verified | 0.5.10 PETSCII v4 path + TUI launch workflow + Qwen paused |
| `mem_3cb5f0a9cd8e` | agent-context · mok-tua · repeated-reminder · pin | show/play/open media at READY. · gpu-prep law |
| `mem_ca468b33ba22` | agent-context · mok-tua · breakthrough · pin · verified | control handoff pointer (grokcode) |

```bash
# re-pin if lost (from ~/mok-tua):
hippo remember "mok-tua 0.5.10 …" --tag agent-context --tag mok-tua --tag breakthrough --pin --verified
```

---

## 6. Next agent checklist

1. Read `HANDOFF.md` + this file.  
2. Do **not** resume Qwen sampling on 16 GB without new VRAM/quant plan.  
3. Prefer WAN / AnimateDiff for motion sizzle; segment + stitch for higher rez.  
4. Optional: wire live Comfy/FramePack/Directors logs through `demoscene_filter`.  
5. Any new public assets: scrub absolute `/Users/…` paths from receipts before push.
