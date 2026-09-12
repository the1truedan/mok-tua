# ROBUST Comfy custom_nodes for mok-tua (2026-08-02)

**Scope:** GPU worker capability for storyboard → identity → I2V → lipsync.  
**Orchestrator stays mok-tua;** Pinokio apps cover music/VO/FaceFusion/mocap (see G).

Machine roster: `config/comfy_nodes_mok_tua_roster.json`.

**2026-09-12:** native MiniMax H3 VocalLock lipsync is PASS on the isolated H3 env
(not this shared `:8188` roster). Cited public links and the three-mechanism split live in
[docs/reports/SMOKE_TESTED_CAPABILITIES_2026-09-12.md](reports/SMOKE_TESTED_CAPABILITIES_2026-09-12.md).
DreamTalk / LivePortrait / wav2lip in pack D below remain **installed, not smoke-rendered**.

## F install order (done via script)

1. Audit import failures / object_info  
2. Install P0/P1: **KJNodes, GGUF, Inspire-Pack, efficiency-nodes, Florence2**  
3. Shared deps + **numpy==1.26.4** pin  
4. Disable avoid-list (AniPortrait, Moore-AnimateAnyone, BlenderAI*, Assistant, RVC, broken Inference-Core)  
5. Dedupe `comfyui-custom-scripts` vs `ComfyUI-Custom-Scripts`  
6. `chmod a+rwx` on `.git` tops (Manager `.cnr-id` on NFS)  
7. Smoke: `scripts/smoke_comfy_robust.sh` + `mok-tua smoke --tiers T0-T4`

```bash
# on gpu-host
bash ~/mok-tua/scripts/comfy_robust_install_gpu.sh
# restart Comfy host runtime, then:
COMFY_URL=http://127.0.0.1:8188 bash ~/mok-tua/scripts/smoke_comfy_robust.sh
```

From Mac:

```bash
ssh gpu-host 'bash -s' < scripts/comfy_robust_install_gpu.sh
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

## Cited public sources (H3 / lipsync robustness)

Not a second node roster. These are the upstreams behind the 2026-09-12 VocalLock PASS and the 2026-08-15 LTX-2 clips. Full table: [docs/reports/SMOKE_TESTED_CAPABILITIES_2026-09-12.md](reports/SMOKE_TESTED_CAPABILITIES_2026-09-12.md).

| Source | URL |
|--------|-----|
| MiniMax H3 | https://huggingface.co/MiniMaxAI/MiniMax-H3 |
| Comfy-Org H3 weights | https://huggingface.co/Comfy-Org/MiniMax-H3 |
| Native H3 nodes | https://github.com/Comfy-Org/ComfyUI/pull/15224 |
| LightX2V | https://github.com/ModelTC/LightX2V |
| T8mars Vocal Lock | https://github.com/T8mars/comfyui-minimax-h3-audio-T8 |
| Maestro | https://github.com/Blizaine/Maestro |
| comfy-cli | https://github.com/Comfy-Org/comfy-cli |
| comfy-mcp | https://github.com/Comfy-Org/comfy-mcp |
| Awesome MiniMax-H3 | https://github.com/wildminder/awesome-minimax-H3 |
