# Render scratch vs `/ai-data` vs bees — mok-tua storage law

**Date:** 2026-08-05  
**Applies to:** Comfy, FramePack, Wan, Director intermediates, overnight E0–E16  
**Hosts:** gpu-host (gpu-host) · desk Mac NFS client · Unraid/bees volume behind `/mnt/ai-data`

---

## Short answer

| Question | Answer |
|----------|--------|
| Write local SSD first then `/ai-data`? | **Yes for hot scratch and multi-GB rewrite streams.** Promote **finals** (mp4, stamped receipts, publishable stills) to shared volume. |
| Issues seeing data on NFS with permissions? | **Yes — real.** Mac **uid 501** vs Linux **uid 1000**; group/world bits differ; trees created from the wrong side become “visible but not writable” to the GPU process. |
| Safe to render straight to shared volume with bees? | **Safe for settled models + finished artifacts.** **Not preferred** for Gradio `/tmp`-class churn, partial frames, or jobs that rewrite the same path thousands of times — bees thrash + NFS latency. |

---

## Layers

```text
┌─────────────────────────────────────────────────────────────┐
│  LOCAL SSD (gpu-host preferred)                             │
│  /tmp · package work · ~/scratch · SM Gradio temp           │
│  → hot I2V sampling, intermediates, failed attempts         │
└───────────────────────────┬─────────────────────────────────┘
                            │ promote on success
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  SHARED /mnt/ai-data  (Mac: /Volumes/ai-data)               │
│  models/  ·  models/hf_hub/  ·  work/mok-tua/artifacts/     │
│  → weights, HF hub seed, final mp4/jpg, runtime registries  │
│  bees: OK on settled trees only                             │
└─────────────────────────────────────────────────────────────┘
```

### Put on shared `/ai-data` (read-heavy / long-lived)

- Comfy / SM model weights (`models/checkpoints`, `ipadapter`, `diffusion_models`, …)  
- Shared HF hub (`models/hf_hub`) — single seed, never package-local duplicate trees  
- Finished CEO/smoke artifacts under `work/…` when stamped  
- Runtime registries JSON (small, multi-process read)  
- Scorecards / overnight receipts (append-mostly)

### Keep on local SSD until promote

- FramePack / Gradio sampling temps (`/tmp/gradio`, package cache mid-job)  
- AnimateDiff frame dumps before encode  
- Failed / half-written mp4  
- Anything rewritten every few seconds  

### bees (block-level dedupe)

- **Good:** identical multi-GB weight files, archived finished clips, HF snapshot stability.  
- **Bad:** active scratch that mutates — bees does not “fix” NFS permission bugs and adds background I/O on hot rewrite paths.  
- Treat bees as **post-settlement** hygiene, not a live render backend.

---

## Permissions pattern that works

1. **Create work dirs on the host that runs the GPU process** (gpu-host), or use a known shared group + `g+rwX` + setgid if multi-user.  
2. Avoid Mac-side `mkdir` into `/Volumes/ai-data/work/framepack/...` for GPU-owned jobs when uid mapping is broken.  
3. Launcher pattern (already in FramePack scripts): try shared path; on permission/write failure → **local fallback** + log promote path.  
4. Do **not** recursive-chmod the whole pool “to make it work.”

---

## FramePack-specific note (2026-08-05)

- Live path used Gradio temps under **`/tmp`** on gpu-host during sampling (correct for hot path).  
- Shared hub + models stayed on `/mnt/ai-data/models`.  
- NFS `work/framepack` trees owned by uid **501** were a real footgun for Linux-side rewrite.  
- Receipt status path may point at desk `work/` until promote — document `artifact` path after copy.

---

## Policy one-liner for agents

> **Models and finals on ai-data; hot render on local SSD; bees only on settled data; never claim cloud I2V as local.**
