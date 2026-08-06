# Wan weights — staging / inventory (shared pool)

**Date:** 2026-08-05  
**Pool:** `/mnt/ai-data/models`  
**Comfy path key:** `diffusion_models` (+ `wan` alias in extra_model_paths)

## Status: **weights present — no bulk re-download required**

Primary I2V / T2V tensors already live under `diffusion_models/` (not the empty `wan/models/` code tree).

### Core (executed inventory)

| File | ~Size | Role |
|------|-------|------|
| `wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors` | 14G | I2V high-noise |
| `wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors` | 14G | I2V low-noise |
| `wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors` | 14G | T2V high |
| `wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors` | 14G | T2V low |
| `wan2.2_ti2v_5B_fp16.safetensors` | 9.4G | TI2V 5B |
| `wan2.1_t2v_1.3B_fp16.safetensors` / `_bf16` | 2.7G | 1.3B T2V |
| `wan2.1_fun_camera_v1.1_1.3B_bf16.safetensors` | 3.1G | Fun camera |
| `wan2.1_fun_inp_1.3B_bf16.safetensors` | 3.0G | Fun inpaint |
| `wan2.1_vace_1.3B_fp16.safetensors` | 4.1G | VACE |
| Lightning LoRAs `Wan2.2-Lightning_I2V-A14B-*` | 586M ea | Fast I2V |

### Code / config tree (not weights)

`/mnt/ai-data/models/wan/` — Wan2GP-style Python/config tree; `models/` and `vae/` subdirs **empty**.  
Comfy should load **diffusion_models** tensors via workflow Loaders, not this tree.

### Staging actions taken

1. Inventory documented (this file).  
2. Confirmed Comfy `extra_model_paths` includes `diffusion_models` + `wan` alias.  
3. **No** multi-GB re-pull (disk already holds 14B fp8 I2V pair).  
4. Optional hygiene: symlink key I2V files into `wan/models/` only if a Pinokio app hardcodes that path:

```bash
# optional — only if Wan2GP UI cannot see diffusion_models
mkdir -p /mnt/ai-data/models/wan/models
ln -sfn /mnt/ai-data/models/diffusion_models/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors \
  /mnt/ai-data/models/wan/models/
# … low_noise similarly
```

### Still pending for “Wan live ports”

- Gradio / Pinokio Wan2GP HTTP ports (gamut honest skip until adapters up).  
- Full Comfy Wan **workflow pin** export in-repo (`workflows/` still placeholder for some paths).  
- Text encoder / VAE companions if a specific workflow errors (load-test next).

### Connectivity check

```bash
ls /mnt/ai-data/models/diffusion_models/wan2.2_i2v_*.safetensors
curl -sS http://gpu-host:8188/object_info | python3 -c "import sys,json; print('comfy ok')"
```
