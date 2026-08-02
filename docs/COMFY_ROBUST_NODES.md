# ROBUST Comfy custom_nodes for mok-tua (2026-08-02)

**Scope:** GPU worker capability for storyboard → identity → I2V → lipsync.  
**Orchestrator stays mok-tua;** Pinokio apps cover music/VO/FaceFusion/mocap (see G).

Machine roster: `config/comfy_nodes_mok_tua_roster.json`.

## F install order (done via script)

1. Audit import failures / object_info  
2. Install P0/P1: **KJNodes, GGUF, Inspire-Pack, efficiency-nodes, Florence2**  
3. Shared deps + **numpy==1.26.4** pin  
4. Disable avoid-list (AniPortrait, Moore-AnimateAnyone, BlenderAI*, Assistant, RVC, broken Inference-Core)  
5. Dedupe `comfyui-custom-scripts` vs `ComfyUI-Custom-Scripts`  
6. `chmod a+rwx` on `.git` tops (Manager `.cnr-id` on NFS)  
7. Smoke: `scripts/smoke_comfy_robust.sh` + `mok-tua smoke --tiers T0-T4`

```bash
# on mrgpu
bash ~/mok-tua/scripts/comfy_robust_install_mrgpu.sh
# restart Comfy host runtime, then:
COMFY_URL=http://127.0.0.1:8188 bash ~/mok-tua/scripts/smoke_comfy_robust.sh
```

From Mac:

```bash
ssh mrgpu 'bash -s' < scripts/comfy_robust_install_mrgpu.sh
./scripts/smoke_comfy_robust.sh
```

## A–E packs (summary)

| Pack | Purpose |
|------|---------|
| A Core | Manager, VHS, FreeMemory, essentials, rgthree, was, Impact |
| B Stills | controlnet_aux, Adv ControlNet, IPAdapter, Qwen bridge, panels, layerdiffuse, SAM, UltimateSDUpscale |
| C Video | Wan, AnimateDiff, Frame-Interpolation, DepthAnythingV2, MimicMotion, LTX extras |
| D Face | ReActor, InstantID, LivePortrait, wav2lip, AudioScheduler, tts_audio_suite |
| E Deps | numpy 1.26.4, onnxruntime-gpu, insightface, imageio-ffmpeg, transformers |

## G — not in Comfy

ACE-Step, TTS-Story, FaceFusion, FreeMoCap, mok-tua ledger/QQQ, OminiControl (FLUX earmark).

## Avoid (disabled)

Moore-AnimateAnyone, AniPortrait, BlenderAI (server), Assistant, RVC, Inference-Core-Nodes (broken import).
