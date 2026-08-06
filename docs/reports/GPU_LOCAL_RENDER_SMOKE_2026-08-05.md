# local GPU render smoke — M.A.N.A.G.E.R. (2026-08-05)

## Clarification (prior vs this run)

| Artifact | Renderer | GPU? | Notes |
|----------|----------|------|-------|
| **Prior** `manager_vibe_demo_hybrid_12s.mp4` | **Grok Imagine I2V** + ffmpeg | **No** (cloud + CPU) | Why you saw no GPU-host usage |
| **Prior** `manager_vibe_demo_local_kenburns.mp4` | **ffmpeg zoompan only** | **No** generative GPU | Pans static PNGs |
| **Prior comic** `manager_updates_20260805T152028Z` | **ComfyUI DreamShaper_8** (local) | **Yes** (stills) | IPAdapter failed; face = prompt + optional FaceFusion strip |
| **This run** `manager_gpu_local_render_20260805` | **ComfyUI on GPU-host** stills + **AnimateDiff** video | **Yes** | Receipt below |

**Not used this run:** Grok Imagine, xAI cloud, session `image_to_video`.

---

## Program stack (local only)

| Layer | Value |
|-------|--------|
| Conductor client | `mok-tua` `api.backends.comfy.ComfyClient` |
| Program | **ComfyUI 0.29.0** on **GPU-host** |
| Device | `cuda:0 NVIDIA GeForce RTX 4060 Ti` |
| PyTorch | `2.6.0+cu124` |
| Still checkpoint | `DreamShaper_8_pruned.safetensors` |
| Video motion | **AnimateDiff-Evolved** `mm_sd_v15_v2.fp16.safetensors` |
| Video mux | **VHS_VideoCombine** → `video/h264-mp4` |
| Endpoint | Comfy `http://gpu-host:8188` (live lab) |

---

## Story / plot (coherent M.A.N.A.G.E.R. arc)

**Logline:** Developer runs the M.A.N.A.G.E.R. stack — mok-tua plans shots, Comfy paints stills on GPU-host, AnimateDiff makes short motion, smoke/receipts for public flip.

| Shot | ID | Beat |
|------|-----|------|
| 1 | `s1_conductor` | Dual-monitor desk; C64 + IDE; labels mok-tua / M.A.N.A.G.E.R. conductor |
| 2 | `s2_comfy_queue` | Comfy node graph on screen; GPU tower; storyboard generation |
| 3 | `s3_ship_thumbs` | Thumbs-up after smoke; GitHub PR “mok-tua public release” |

---

## Wall-clock (prompt → files on staging)

| Phase | Seconds | GPU evidence |
|-------|---------|----------------|
| Still `s1_conductor` | **3.31** | Comfy queue complete |
| Still `s2_comfy_queue` | **3.32** | VRAM **2518 → 3542 MiB** |
| Still `s3_ship_thumbs` | **3.29** | **util 100%** at sample |
| AnimateDiff 16 frames @ 8 fps | **36.50** | samples peak **100%** util; mem ~3.3–3.5 GiB |
| ffmpeg kenburns of stills (CPU stitch only) | ~1 | **Not** generative GPU video |
| **End-to-end total** | **~47.8** | receipt `wall_clock.total_seconds` |

Timestamps (UTC) in `receipts/gpu_local_render.json`.

---

## Models + prompts (verbatim in receipt)

### Stills (each: 768×512, 22 steps, euler, cfg 7, DreamShaper_8)

See JSON fields `stills[].prompt` / `negative` / `seed` / `prompt_id`.

### AnimateDiff video

- **Frames:** 16 · **fps:** 8 · **size:** 512×512 · **steps:** 16 · **seed:** 42042  
- **Motion module:** `mm_sd_v15_v2.fp16.safetensors`  
- **Prompt:** realistic man mid-30s … coding at dual monitors running M.A.N.A.G.E.R. conductor and mok-tua …

---

## Outputs

| File | Role |
|------|------|
| `…/panels/s1_conductor.png` | GPU-host Comfy still |
| `…/panels/s2_comfy_queue.png` | GPU-host Comfy still |
| `…/panels/s3_ship_thumbs.png` | GPU-host Comfy still |
| `…/clips/animatediff_manager_gpu_ad_00001.mp4` | **GPU-host AnimateDiff** generative video |
| `…/clips/manager_gpu_stills_kenburns_cpu_stitch.mp4` | CPU preview of stills (labeled non-GPU) |
| `…/receipts/gpu_local_render.json` | Full machine receipt |

Staging root:  
`/Volumes/ai-data/work/social-staging/2026-08/manager_gpu_local_render_20260805/`

---

## Face likeness honesty

| Capability | Status on this Comfy |
|------------|----------------------|
| IPAdapter model files | **Empty** (`/models/ipadapter` count 0) |
| InstantID models | **Empty** |
| FaceFusion UI | **Live** `:7870` (not auto-wired in this smoke) |
| This run identity | **Prompt-only** (generic “mid-30s man”) — **not** guaranteed to look like you |

**Prior comic** used `face_ref` from `~/Downloads/my-circle-face.png` in **prompt text only** (IPAdapter timed out). FaceFusion strip pass improved faces on that comic, not on the Grok video.

**Next for true likeness (local):** FaceFusion post-swap on these stills/clip using `face_ref.png`, or install IPAdapter FaceID weights on GPU-host and re-queue.

---

## Smoke verdict

| Check | Result |
|-------|--------|
| Local Comfy reachable | ✅ |
| Stills via mok-tua Comfy client | ✅ 3/3 |
| Generative video via Comfy AnimateDiff | ✅ |
| GPU util observed | ✅ peak **100%** |
| Grok used | ❌ |
| Wan Gradio ports | still offline (AnimateDiff used instead) |

*Use this packet as the GPU-host evidence path for the 16:20 public story — not the Grok hybrid.*
