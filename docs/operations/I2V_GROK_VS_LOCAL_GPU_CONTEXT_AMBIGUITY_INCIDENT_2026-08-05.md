# Incident — I2V provenance ambiguity (Grok Imagine vs local GPU)

**Date:** 2026-08-05  
**Severity:** operational / trust (not security)  
**Status:** closed with documented dual-path + labeling rules  
**Repos:** `mok-tua` · related control stamps in `~/grokcode`  
**Stamp:** `2026.08-i2v-grok-vs-gpu-host-context-ambiguity`

---

## 1. Summary

An operator asked for **local GPU-host** image/video proof (GPU util, timed model/prompt evidence, identity path).  
The first “demo video” packet was labeled as if it exercised the **local stack**, but the **generative** I2V segments were produced by **Grok Imagine** (`image_to_video` in the agent session) and **ffmpeg** only. **GPU-host GPU util stayed near zero** during that path — correctly, because nothing was queued on ComfyUI / Wan / AnimateDiff.

That ambiguity (cloud I2V dressed as lab local) broke trust in smoke evidence and must not recur in handoffs or public packets.

---

## 2. Timeline (lab day)

| Phase | What happened | Actual renderer |
|-------|----------------|-----------------|
| A | Comic stills `manager_updates_…` | **ComfyUI DreamShaper_8** on GPU-host (local stills) |
| B | “MANAGER vibe demo” hybrid mp4 (~14.58 s) | **Grok Imagine I2V ×2** + ffmpeg + local kenburns fallback |
| C | Operator: “why no GPU usage?” | Expected — hybrid path never touched CUDA on gpu-host |
| D | Corrective smoke `manager_gpu_local_render_20260805` | **Comfy stills + AnimateDiff** on **RTX 4060 Ti**, ~48 s e2e, GPU peak **100%** |

---

## 3. Root cause — context ambiguity (not a code bug)

1. **Two I2V paths share product language** (“demo video”, “I2V”, “MANAGER vibe”) without a mandatory **provenance tag**.  
2. **Agent tools** (`image_to_video` / Grok Imagine) are fast and session-local; they feel “in the lab workflow” even when compute is cloud.  
3. **ffmpeg kenburns** of local PNGs looks “local” but is **not generative GPU video**.  
4. Handoffs listed deliverables by filename/duration **before** renderer/GPU evidence, so readers assumed GPU-host.

---

## 4. Impact

| Area | Impact |
|------|--------|
| Operator trust | High — “local” claim contradicted by zero GPU util |
| Public flip narrative | Medium — hybrid clip is valid **QQQ1 cloud** evidence, not local GPU proof |
| Identity / face match | Confused further: Grok I2V ≠ FaceFusion/IPAdapter local path |
| Cost / QQQ | Cloud I2V burns cloud quota without QQQ1 explicit gate in the narrative |

---

## 5. Evidence paths (canonical)

| Label | Path | Provenance |
|-------|------|------------|
| **Hybrid (cloud I2V)** | `work/social-staging/2026-08/manager_vibe_demo_20260805T1620/manager_vibe_demo_hybrid_12s.mp4` | Grok Imagine + ffmpeg — **no** GPU-host generative |
| Local kenburns only | same dir `manager_vibe_demo_local_kenburns.mp4` | CPU stitch of stills |
| **GPU-host generative** | `work/social-staging/2026-08/manager_gpu_local_render_20260805/` | Comfy + AnimateDiff · receipt `receipts/gpu_local_render.json` |
| Report (local) | `docs/reports/GPU_LOCAL_RENDER_SMOKE_2026-08-05.md` | Corrective |
| Report (hybrid honesty) | `docs/DEMO_VIDEO_PROOF_2026-08-05.md` | Correction banner |
| Gamut probes | `docs/reports/PINOKIO_GAMUT_SMOKE_2026-08-05.md` | HTTP/pterm; Wan ports honest skip |

---

## 6. Corrective actions (done)

1. Dual-path docs: hybrid vs local GPU labeled; hybrid banner says **not local GPU**.  
2. GPU-host smoke report with wall-clock, VRAM, util, models, prompts, seeds.  
3. Full-gamut framework: default ladder `local_animatediff` → `local_wan` → `local_framepack` → `grok_imagine_video` **QQQ1 only**.  
4. Bundle item (this incident) so multi-brand agents cite provenance first.

---

## 7. Standing rules (do not regress)

### Every video artifact must carry three fields

```text
renderer:   gpu_comfy_animatediff | gpu_comfy_wan | gpu_framepack | grok_imagine_i2v | ffmpeg_kenburns | other
qqq:        QQQ0 | QQQ1
gpu_evidence: peak_util% + host_role  OR  "n/a cloud"  OR  "n/a cpu-only"
```

### Language

| Say | Don’t say |
|-----|-----------|
| “GPU-host AnimateDiff smoke (GPU 100%)” | “local demo video” without renderer |
| “Grok Imagine I2V (QQQ1 cloud)” | “lab I2V” for cloud path |
| “ffmpeg kenburns of stills (CPU)” | “local video gen” for zoompan |

### Agent protocol

1. If the user says **GPU-host / local / GPU** → queue **Comfy / FramePack / Wan** only; do **not** call session `image_to_video` unless they also say cloud/Grok.  
2. If cloud is used, **lead with QQQ1** in the first sentence of the result.  
3. Receipts before vibes: path + renderer + util or explicit `n/a cloud`.

---

## 8. Related incidents / laws

- UV cache host-split · NFS uid 501 vs 1000 · FramePack shared models  
- Context pit: no bulk transcript; cite paths + IDs  
- Public packet: hybrid may ship as optional cloud demo; **GPU-host path is the local proof**

---

## 9. Residual risk

| Risk | Mitigation |
|------|------------|
| Wan Gradio ports offline at probe | Use Comfy AnimateDiff / FramePack; honest skip in gamut report |
| Identity still prompt-only | W0: IPAdapter / InstantID weights + FaceFusion CUDA |
| Agent reuses hybrid filename in “local” pitch | Handoff + Hippo tag `error` / `repeated-reminder` |

---

*Closed for process: evidence dual-path is documented. Reopen only if a new packet claims local GPU without CUDA evidence.*
