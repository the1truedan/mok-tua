# Demo / export citations — **pre-FaceID** vs **post-FaceID**

**Sibling aesthetic lane (title cards):** [`../styles/blade-runner-title/`](../styles/blade-runner-title/) — Rands / Blade Runner mood; does not replace PETSCII Matrix.

Use these labels in README, Release notes, and receipts so agents and humans do not greenwash.

| Era | Meaning |
|-----|---------|
| **(pre-FaceID)** | Before IPAdapter FaceID PLUS V2 weights + padded InsightFace path were live and used for CEO identity. Includes comic zoompan, hybrid cloud I2V, prompt-lock/img2img only, stock-hero art. |
| **(post-FaceID)** | After FaceID PLUS V2 path: `ip-adapter-faceid-plusv2_sd15` + LoRA + CLIP vision H + InsightFace buffalo_l (padded source still). Receipts say `gpu_comfy_faceid_*` or equivalent. |

**Identity seed (both eras when CEO):** [`../pres-smoke/00-ceo-source-still.jpg`](../pres-smoke/00-ceo-source-still.jpg)  
**Law:** Grok Imagine I2V ≠ local GPU generative. ffmpeg Ken Burns ≠ generative GPU video.

---

## Playable exports (this page)

GitHub cannot inline-play a repo `.mp4` inside Markdown. **Click poster or ▶ link** → file page with native play button.

| Export | Poster (still) | ▶ Play (mp4) | Cite |
|--------|----------------|--------------|------|
| **PETSCII Matrix** brand short (~15s) | [poster.png](mok-tua-petscii-matrix-poster.png) | [▶ play export.mp4](mok-tua-petscii-matrix-export.mp4) | **(post-FaceID)** era · brand · **not** a face demo |
| **Procurement → M.A.N.A.G.E.R.** anime multi-angle / next-scene (**14.20 s**) | [poster.jpg](manager-pivot-procurement-to-manager-anime-poster.jpg) | [▶ play mp4](manager-pivot-procurement-to-manager-anime.mp4) | photoceopic ref · multi-angle + `Next Scene:` grammar · **Imagine stills** (local Qwen Edit staged, **OOM** on 16 GB) · ffmpeg hold · see [PROVENANCE](../capabilities/manager-pivot/PROVENANCE.json) |

<p align="center">
  <a href="mok-tua-petscii-matrix-export.mp4" title="Open playable PETSCII Matrix export">
    <img src="mok-tua-petscii-matrix-poster.png" alt="PETSCII Matrix brand short — click to play" width="720" />
  </a>
</p>

<p align="center">
  <a href="mok-tua-petscii-matrix-export.mp4"><strong>▶ Press to play — PETSCII Matrix export</strong></a>
</p>

Blob URL (same player):  
https://github.com/the1truedan/mok-tua/blob/main/docs/assets/exports/mok-tua-petscii-matrix-export.mp4

### Procurement → M.A.N.A.G.E.R. (anime multi-angle · next-scene)

<p align="center">
  <a href="manager-pivot-procurement-to-manager-anime.mp4" title="Open playable pivot short">
    <img src="manager-pivot-procurement-to-manager-anime-poster.jpg" alt="Anime pivot storyboard poster — click to play" width="720" />
  </a>
</p>

| Field | Value |
|-------|--------|
| **Duration** | **14.20 s** (30 fps · 426 frames · 6 panels × 71 frames) |
| **Narrative** | procurement vibecoding → M.A.N.A.G.E.R. framework |
| **Style** | anime · multi-angle camera phrases + `Next Scene:` continuity |
| **Identity ref** | [`../pres-smoke/00-ceo-source-still.jpg`](../pres-smoke/00-ceo-source-still.jpg) (photoceopic) |
| **Stills renderer** | xAI Imagine `image_edit` (QQQ1 opt-in demo · not medical) |
| **Local Qwen Image Edit** | weights **present** (`qwen_image_edit_2509_fp8` + multi-angle + next-scene LoRAs); **KSampler OOM** on RTX 4060 Ti 16 GB even with Comfy `--lowvram` |
| **Motion** | ffmpeg panel-hold (not generative video) |
| **Sheet** | [`../capabilities/manager-pivot/storyboard-sheet.jpg`](../capabilities/manager-pivot/storyboard-sheet.jpg) |
| **Full prompts / stats** | [`../capabilities/manager-pivot/PROVENANCE.json`](../capabilities/manager-pivot/PROVENANCE.json) |
| **Script** | `scripts/render_manager_pivot_qwen_storyboard.py` (local path when VRAM allows) |

**(pre-FaceID)** motion demos (Ken Burns / hybrid Grok) live under lab staging, not this folder — see table below and [`../../DEMO_VIDEO_PROOF_2026-08-05.md`](../../DEMO_VIDEO_PROOF_2026-08-05.md).

---

## (pre-FaceID) — cite as historical / honest fallbacks

Do **not** claim these as FaceID likeness or pure local-GPU generative film.

| Artifact | Class | Path / pointer | Cite as |
|----------|-------|----------------|---------|
| Local Ken Burns vibe demo (~12.5s) | ffmpeg `zoompan` of comic stills | lab staging `manager_vibe_demo_local_kenburns.mp4` (not in-repo) | **(pre-FaceID)** · CPU stitch · not GPU gen |
| GPU-host stills Ken Burns stitch | ffmpeg zoompan of DreamShaper stills | lab staging `manager_gpu_stills_kenburns_cpu_stitch.mp4` | **(pre-FaceID)** · CPU stitch of stills |
| Hybrid vibe demo (~14.6s) | Grok Imagine I2V ×2 + kenburns beat | lab staging `manager_vibe_demo_hybrid_12s.mp4` | **(pre-FaceID)** · **cloud I2V** · not local GPU |
| Comic storyboard smoke panels | DreamShaper comic · sticky-note “ceo energy” | overnight smoke dirs (lab) | **(pre-FaceID)** · creative comic · not FaceID selfie lock |
| Old README hero (stock woman instructor) | concept art | replaced; do not reintroduce | **(pre-FaceID)** · not CEO |
| Early hybrid storyboard / “weights incomplete” receipts | prompt-lock + img2img | superseded by FaceID sheets | **(pre-FaceID)** · identity drift expected |

Full write-up: [`../../DEMO_VIDEO_PROOF_2026-08-05.md`](../../DEMO_VIDEO_PROOF_2026-08-05.md) · provenance: [`../../operations/I2V_GROK_VS_LOCAL_GPU_CONTEXT_AMBIGUITY_INCIDENT_2026-08-05.md`](../../operations/I2V_GROK_VS_LOCAL_GPU_CONTEXT_AMBIGUITY_INCIDENT_2026-08-05.md).

---

## (post-FaceID) — cite as current CEO / brand exports

| Artifact | Class | Path | Cite as |
|----------|-------|------|---------|
| CEO storyboard sheet | FaceID PLUS V2 6-panel | [`../example-storyboard-sheet.jpg`](../example-storyboard-sheet.jpg) | **(post-FaceID)** |
| Individual panels | FaceID PLUS V2 | [`../capabilities/panels/`](../capabilities/panels/) | **(post-FaceID)** |
| Face polish B/A | gentle FaceID refine | [`../example-face-polish.jpg`](../example-face-polish.jpg) | **(post-FaceID)** |
| Short-loop strip | AnimateDiff + FaceID (glitch-filtered) | [`../ceo-i2v-frame-strip.jpg`](../ceo-i2v-frame-strip.jpg) | **(post-FaceID)** · not Grok |
| README hero | FaceID panels + clean player still | [`../hero-prompt-to-product.jpg`](../hero-prompt-to-product.jpg) | **(post-FaceID)** |
| Capability cards | split product cards | [`../product-capabilities/`](../product-capabilities/) | **(post-FaceID)** era packaging |
| PETSCII Matrix brand short | procedural identity film (no face) | [▶ `mok-tua-petscii-matrix-export.mp4`](mok-tua-petscii-matrix-export.mp4) | **(post-FaceID)** era · brand · **not** a face demo |
| Poster for brand short | still from hold | [`mok-tua-petscii-matrix-poster.png`](mok-tua-petscii-matrix-poster.png) | same |

FaceID install / path: [`../../operations/IPADAPTER_FACEID_INSTALL_2026-08-05.md`](../../operations/IPADAPTER_FACEID_INSTALL_2026-08-05.md).

---

## PETSCII Matrix export (detail)

**What it is:** Conductor **identity** short — not a tool walkthrough, not CEO face.

**Beat sheet:**
1. C64 PETSCII TUI boot (`mokup-c64-tui-live-boot.png`)
2. Matrix-style falling **µ** glyphs  
3. µs resolve into **clear PETSCII block lettering: MOK-TUA**  
4. Hold solid logo  
5. Dissolve back into dropping µ rain  

**How made:** Procedural PIL + ffmpeg (local CPU). Glyphs from `tui/petscii.py`.  
**QQQ:** QQQ0 · no cloud · no PHI.  
**Cite:** **(post-FaceID)** packaging era · **not** a FaceID face proof (no selfie in this clip).

---

## Suggested README wording

```markdown
### Motion demos

- **(pre-FaceID)** Ken Burns / hybrid vibe clips — comic zoompan or cloud I2V; see DEMO_VIDEO_PROOF (do not claim FaceID likeness).
- **(post-FaceID)** CEO stills + AD strip from FaceID PLUS V2; brand short: [PETSCII Matrix export](docs/assets/exports/mok-tua-petscii-matrix-export.mp4).
```

## Host role labels (public tree)

Tracked configs and receipts use **role labels only**: `gpu-host`, `desk-host`, `control-host`.  
No private lab machine nicknames in this repository.
