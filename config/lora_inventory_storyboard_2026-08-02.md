# Storyboard LoRA / model inventory — 2026-08-02

Pool: `/Volumes/ai-data/models` (Tower NFS). Machine-readable twin: `lora_inventory_storyboard_2026-08-02.json`.

## Present (verified on pool)

| Asset | Path | Role |
|-------|------|------|
| **Qwen-Edit multi-angles** | `loras/Qwen-Edit-2509-Multiple-angles.safetensors` (225 M) | Camera moves / FOV / close-up |
| **next-scene v2** | `loras/next-scene_lora-v2-3000.safetensors` (281 M) | Panel-to-panel continuity |
| Lightning 2509 | `loras/Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors` (810 M) | Fast steps with edit |
| Lightning 2511 | `loras/Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors` | Newer lightning |
| Qwen image base (fp8) | `diffusion_models/qwen_image_fp8_e4m3fn.safetensors` | Base diffusion |
| AnimateDiff mm | `animatediff/mm_sd_v15_v2.fp16.safetensors` | AD fallback |
| Wan 2.1 t2v 1.3B | `diffusion_models/wan2.1_t2v_1.3B_*.safetensors` | Primary video pin target |
| LTX 2B | `diffusion_models/ltx-video-2b-v0.9.5.safetensors` | Alt video |

## Gaps (graphs, not weights)

| Gap | Action |
|-----|--------|
| API export for Qwen multi-angle + next-scene | Export from Comfy → `workflows/qwen_next_scene_angles.api.json` |
| API export for AnimateDiff basic | Export → `workflows/animatediff_basic.api.json` |

Weights for multi-angle + next-scene + lightning are **on pool** as of 2026-08-02.

## mok-tua defaults

- Weights present for multi-angle + lightning → prefer provider `local_qwen_edit` **after** API graph export.
- Until pin is real: keep `local_sd_minimal` for live stills; still use camera/next-scene **prompt builder**.
- Video: `local_wan` primary, `local_animatediff` fallback.

## Johnny / CHIPPER catalog tip

When filing inventory for public handoff, copy only this index (not multi-GB weights) under:

`work/catalog/johnny-chipper/models-storyboard/<date>/`

Use the process templates in the public `johnny-appleseed-chipper` repo.
