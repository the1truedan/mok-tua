# Demo / export citations — **pre-FaceID** vs **post-FaceID**

Use these labels in README, Release notes, and receipts so agents and humans do not greenwash.

| Era | Meaning |
|-----|---------|
| **(pre-FaceID)** | Before IPAdapter FaceID PLUS V2 weights + padded InsightFace path were live and used for CEO identity. Includes comic zoompan, hybrid cloud I2V, prompt-lock/img2img only, stock-hero art. |
| **(post-FaceID)** | After FaceID PLUS V2 path: `ip-adapter-faceid-plusv2_sd15` + LoRA + CLIP vision H + InsightFace buffalo_l (padded source still). Receipts say `mrgpu_comfy_faceid_*` or equivalent. |

**Identity seed (both eras when CEO):** `docs/assets/pres-smoke/00-ceo-source-still.jpg`  
**Law:** Grok Imagine I2V ≠ MRGPU local. ffmpeg Ken Burns ≠ generative GPU video.

---

## (pre-FaceID) — cite as historical / honest fallbacks

Do **not** claim these as FaceID likeness or pure MRGPU generative film.

| Artifact | Class | Path / pointer | Cite as |
|----------|-------|----------------|---------|
| Local Ken Burns vibe demo (~12.5s) | ffmpeg `zoompan` of comic stills | `/Volumes/ai-data/work/social-staging/2026-08/manager_vibe_demo_20260805T1620/manager_vibe_demo_local_kenburns.mp4` | **(pre-FaceID)** · CPU stitch · not GPU gen |
| MRGPU stills Ken Burns stitch | ffmpeg zoompan of DreamShaper stills | `…/manager_mrgpu_local_render_20260805/clips/manager_mrgpu_stills_kenburns_cpu_stitch.mp4` | **(pre-FaceID)** · CPU stitch of stills |
| Hybrid vibe demo (~14.6s) | Grok Imagine I2V ×2 + kenburns beat | same vibe_demo dir `manager_vibe_demo_hybrid_12s.mp4` | **(pre-FaceID)** · **cloud I2V** · not MRGPU |
| Comic storyboard smoke panels | DreamShaper comic · sticky-note “ceo energy” | comic smoke `manager_updates_*` · overnight panels under `work/smoke/mok-tua-overnight-2026-08-05/` | **(pre-FaceID)** · creative comic · not FaceID selfie lock |
| Old README hero (stock woman instructor) | concept art | replaced; do not reintroduce | **(pre-FaceID)** · not CEO |
| Early hybrid storyboard / “weights incomplete” receipts | prompt-lock + img2img | superseded by FaceID sheets | **(pre-FaceID)** · identity drift expected |

Full write-up: [`docs/DEMO_VIDEO_PROOF_2026-08-05.md`](../../DEMO_VIDEO_PROOF_2026-08-05.md) · provenance incident: [`docs/operations/I2V_GROK_VS_MRGPU_CONTEXT_AMBIGUITY_INCIDENT_2026-08-05.md`](../../operations/I2V_GROK_VS_MRGPU_CONTEXT_AMBIGUITY_INCIDENT_2026-08-05.md).

---

## (post-FaceID) — cite as current CEO / brand exports

| Artifact | Class | Path | Cite as |
|----------|-------|------|---------|
| CEO storyboard sheet | FaceID PLUS V2 6-panel | `docs/assets/example-storyboard-sheet.jpg` | **(post-FaceID)** |
| Individual panels | FaceID PLUS V2 | `docs/assets/capabilities/panels/01–06-*.jpg` | **(post-FaceID)** |
| Face polish B/A | gentle FaceID refine | `docs/assets/example-face-polish.jpg` | **(post-FaceID)** |
| Short-loop strip | AnimateDiff + FaceID (glitch-filtered) | `docs/assets/ceo-i2v-frame-strip.jpg` | **(post-FaceID)** · not Grok |
| README hero | FaceID panels + clean player still | `docs/assets/hero-prompt-to-product.jpg` | **(post-FaceID)** |
| Capability cards | split product cards | `docs/assets/product-capabilities/product-capabilities-NN-*.jpg` | **(post-FaceID)** era packaging |
| PETSCII Matrix brand short | procedural identity film (no face) | `docs/assets/exports/mok-tua-petscii-matrix-export.mp4` | **(post-FaceID)** era · brand export · **not** a face demo |
| Poster for brand short | still from hold | `docs/assets/exports/mok-tua-petscii-matrix-poster.png` | same |

FaceID install / path: [`docs/operations/IPADAPTER_FACEID_INSTALL_2026-08-05.md`](../../operations/IPADAPTER_FACEID_INSTALL_2026-08-05.md).

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

## GitHub play

Prefer poster click → mp4 (Release or path). Inline player only with GitHub attachment URLs when available.
