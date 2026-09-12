# Smoke-tested capabilities — H3 VocalLock lipsync (2026-09-12)

**Date:** 2026-09-12  
**Hosts:** gpu-host (RTX 4060 Ti 16GB) — isolated ComfyUI `:8189`  
**Format:** text-only. No new in-repo clips this pass. The [live site](https://the1truedan.github.io/mok-tua/) still plays the 2026-08-15 LTX-2 proof shots.  
**Prior stamp:** [SMOKE_TESTED_CAPABILITIES_2026-08-15.md](SMOKE_TESTED_CAPABILITIES_2026-08-15.md)

This is a **notation of a real render that already succeeded**, not a new GPU job. It closes the “song → video → lipsync still pending” gap from 0.6.0 / 0.7.0 for **one** lipsync mechanism (MiniMax H3 VocalLock), and it cites the public robustness stack so the next operator does not rediscover it.

---

## Three lipsync mechanisms — do not conflate

| Mechanism | What it actually does | Status 2026-09-12 |
|-----------|------------------------|-------------------|
| **LTX-2 audio-conditioned generation** | The video model is given a real WAV (`audio_prompt_type: "A"`) and generates picture + motion against that track. Mouth motion is a side-effect of audio-conditioned sampling, not a discrete lipsync pass. | **PASS** since 2026-08-15. Proof clips on the [live site](https://the1truedan.github.io/mok-tua/). |
| **MiniMax H3 VocalLock (native AV)** | Isolated ComfyUI H3 graph. A vocal stem is locked to a named subject (`Vocal Lock` / VocalLock_V3). The Omni transformer jointly denoises video + audio latents; lips follow the stem because audio is in the latent, not pasted on afterwards. | **PASS** — verse batch, **5/5 scenes**, 32s window, identity still + manual vocal stem, isolated `:8189`. Best identity/lip-sync of this project so far. |
| **Dedicated lipsync tools** (DreamTalk / LivePortrait / FaceFusion) | A still (or silent clip) plus audio, run through a *separate* talking-head tool. | **Still unproven** as a mok-tua job. Wired in the registry. Do not mark PASS. |

The 2026-08-17 earmark ([LIPSYNC_SMOKETEST_EARMARK_2026-08-17.md](../operations/LIPSYNC_SMOKETEST_EARMARK_2026-08-17.md)) asked for a dedicated-tool render. That request is **still open**. This stamp answers a different question: *does native H3 VocalLock actually lip-sync on this 16 GB box?* Yes.

---

## H3 VocalLock_V3 — what passed

| Field | Value |
|-------|--------|
| Engine | Isolated ComfyUI H3 env (`:8189`), not the shared `:8188` pin |
| Model | MiniMax H3 Ref2VA pruned INT8 + video VAE + audio VAE + Qwen3-VL-32B nvfp4 text encoder |
| Speed | LightX2V turbo LoRAs (FL2V 8-step 768p + Ref2V 4-step) already on the graph |
| Identity | One reference still, strict one-person / mouth-visible contract |
| Audio | Manual vocal stem (not a live Demucs job; not text-prompted blind) |
| Window | 32 seconds per scene |
| Result | **Verse 1: 5/5 scenes complete** (operator QC: identity + lip-sync) |

Verse 2 and a later Director / LTX-2.5 shot batch were **in flight at notation time**. They are not claimed here. Do not treat this stamp as “the whole music-video pipeline is done.”

### What this is *not*

- Not a DreamTalk / LivePortrait / FaceFusion / InfiniteTalk proof.
- Not Maestro’s H3 Sol Engine picker. A 2026-09-02 Maestro `compatible_model_paths` check **blocked** a differently-named H3 Ref2VA file ([VIDEO_GEN_MODEL_INVENTORY_AUDIT_2026-09-02.md](VIDEO_GEN_MODEL_INVENTORY_AUDIT_2026-09-02.md)). The PASS above is the **isolated ComfyUI** graph, which does not use that allowlist.
- Not H3 Full, not LTX Dev 22B, not a second turbo LoRA stacked on the same sampler.
- Not a claim that SDXL / PhotoMaker / PuLID / IP-Adapter FaceID plug into this graph. They do not.

---

## Cited robustness links (public)

Use these when staging the next H3 / lipsync workflow. Check Hugging Face sibling files (`?blobs=true`) before picking a precision — blog posts often list only one variant.

### Official H3

| What | Link |
|------|------|
| MiniMax H3 model card | https://huggingface.co/MiniMaxAI/MiniMax-H3 |
| MiniMax H3 source repo | https://github.com/MiniMax-AI/MiniMax-H3 |
| ComfyUI-repackaged weights (INT8 / pruned / nvfp4 TE) | https://huggingface.co/Comfy-Org/MiniMax-H3 |
| Native ComfyUI H3 nodes (merged 2026-08-03) | https://github.com/Comfy-Org/ComfyUI/pull/15224 |
| Official H3 Turbo LoRA Space | https://huggingface.co/spaces/MiniMaxAI/MiniMax-H3-Turbo-Lora |

### Speed / turbo (do not stack two on one sampler until an A/B)

| What | Link |
|------|------|
| LightX2V (H3 T2AV / I2AV / Ref2AV, turbo 4-step and 8-step 768p) | https://github.com/ModelTC/LightX2V |
| LightX2V H3 configs | https://github.com/ModelTC/LightX2V/tree/main/configs/minimax_h3 |
| LightX2V MiniMax-H3 Turbo-SLA | https://huggingface.co/lightx2v/Minimax-h3-Turbo-SLA |
| larryvrh independent turbo LoRA (v4 EMA line) | https://huggingface.co/larryvrh/MiniMax-H3-Turbo-Lora |

### VocalLock / audio-drive (the PASS mechanism)

| What | Link |
|------|------|
| T8mars H3 audio pack — Vocal Lock, lock_source vs remix, documented 32s Vocal Lock V3 sample | https://github.com/T8mars/comfyui-minimax-h3-audio-T8 |
| Local Ref2VA + Vocal Lock MV app (reference, not this lab’s runner) | https://github.com/animede/Minimax-H3-lipsync-mv |
| All-in-one H3 node (Audio Drive mode) | https://github.com/LeonQ8/ComfyUI-ALLinONE-MinimaxH3 |
| LongMedia LipSync latent setup (replace native audio stream inside an H3 AV latent) | https://github.com/vizart-vj/ComfyUI-MiniMax-H3-LongMedia |

### Indexes (community, not a second SoR)

| What | Link |
|------|------|
| Awesome MiniMax-H3 (checkpoints, turbo table, workflows) | https://github.com/wildminder/awesome-minimax-H3 |
| MiniMax H3 integrations index | https://github.com/MiniMax-AI/awesome-minimax-h3-integration |
| ComfyUI Wiki — open weights + day-0 native nodes | https://comfyui-wiki.com/en/news/2026-08-03-minimax-h3-open-weights-comfyui |

### Conductor / orchestration robustness (cited, not all smoked this pass)

| What | Link | mok-tua note |
|------|------|--------------|
| ComfyUI | https://github.com/comfyanonymous/ComfyUI | Isolated `:8189` for H3; shared `:8188` stays pinned |
| Maestro | https://github.com/Blizaine/Maestro | Proven for LTX-2 audio-conditioned jobs via REST `/api/v1/generate`. Gradio port **drifts**; `:7860` is DreamTalk, not Maestro. |
| comfy-cli | https://github.com/Comfy-Org/comfy-cli | Substrate for scripted/JSON runs |
| comfy-mcp | https://github.com/Comfy-Org/comfy-mcp | Structured run/monitor/introspect against a remote `COMFYUI_URL` — adopt later; do not install mid-render |
| comfy-kitchen | https://github.com/Comfy-Org/comfy-kitchen | Quant kernels; confirm overlap with the H3 env’s existing `int8_tensorwise` / `convrot` ops before claiming a speedup |
| Director's Console | https://github.com/cocktailpeanut/directorsconsole.pinokio.git | Job-submission plumbing PASS since 2026-08-15 |
| Pinokio | https://pinokio.computer | App installer, not the pipeline |
| Stability Matrix | https://github.com/LykosAI/StabilityMatrix | Shared weights |

---

## Operator re-run (after GPU idle)

Isolated H3 env only. Exclusive GPU. Do not start this while another diffusion job holds the card.

```bash
# on gpu-host — isolated H3 env, not the shared Comfy pin
source /mnt/ai-data/comfyui-h3/envs/mrgpu/bin/activate
cd /mnt/ai-data/comfyui-h3/src/ComfyUI
python main.py --listen 0.0.0.0 --port 8189 --disable-auto-launch
```

Graph contract that QC’d:

1. Ref2VA pruned INT8 + both VAEs + Qwen3-VL nvfp4 TE (files from [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3)).
2. VocalLock_V3 (or equivalent T8mars Vocal Lock) with a **manual vocal stem**, not the full mix, bound to one subject.
3. One identity still. Mouth visible. No second turbo LoRA on the same sampler until a bounded A/B.
4. Hard timeout: if “Loading model” shows zero VRAM/CPU/disk for ~2 minutes, cancel. That hang class is documented on the Maestro path, not this Comfy path, but the same patience rule applies.

Dedicated DreamTalk / LivePortrait / FaceFusion smoke remains the next lipsync row, not a re-run of this one.

---

## Companion docs

- [SMOKE_TESTED_CAPABILITIES_2026-08-15.md](SMOKE_TESTED_CAPABILITIES_2026-08-15.md) — H3 I2V + LTX-2.3 + LTX-2 audio-conditioned PASS; dedicated tools still pending
- [LIPSYNC_SMOKETEST_EARMARK_2026-08-17.md](../operations/LIPSYNC_SMOKETEST_EARMARK_2026-08-17.md) — dedicated-tool earmark (still open)
- [H3_OPTIMIZED_SMOKE_CAMPAIGN_EARMARK_2026-09-02.md](../operations/H3_OPTIMIZED_SMOKE_CAMPAIGN_EARMARK_2026-09-02.md) — Maestro allowlist / remaining candidates
- [VIDEO_GEN_MODEL_INVENTORY_AUDIT_2026-09-02.md](VIDEO_GEN_MODEL_INVENTORY_AUDIT_2026-09-02.md) — why Maestro H3 ref2va was blocked
- [COMFY_ROBUST_NODES.md](../COMFY_ROBUST_NODES.md) — GPU worker roster
- [HF_CLOUD_SPACES_EARMARK_2026-09-02.md](../HF_CLOUD_SPACES_EARMARK_2026-09-02.md) — optional cloud comparison Space, not this PASS
