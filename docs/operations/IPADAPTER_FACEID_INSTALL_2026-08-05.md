# IPAdapter FaceID weights — shared pool install

**Date:** 2026-08-05  
**Host:** gpu-host (GPU-host)  
**Pool:** `/mnt/ai-data/models/ipadapter/`  
**Comfy:** extra_model_paths `ipadapter: ipadapter | IpAdapter | …` · live `:8188`

## Status

| Item | State |
|------|--------|
| FaceID + plus-face SD1.5 weights | **INSTALLED** (7 files, ~569 MiB) |
| LoRA symlinks under `models/loras/` | **OK** (FaceID loras) |
| `clip_vision_h.safetensors` | **OK** (pre-existing) |
| InsightFace `buffalo_l` / `antelopev2` | **OK** under `models/insightface/` |
| Comfy `IPAdapterModelLoader` lists files | **OK** (no restart required) |

## Files

```text
/mnt/ai-data/models/ipadapter/
  ip-adapter-faceid-plusv2_sd15.bin
  ip-adapter-faceid-plusv2_sd15_lora.safetensors
  ip-adapter-faceid_sd15.bin
  ip-adapter-faceid_sd15_lora.safetensors
  ip-adapter-plus-face_sd15.safetensors
  ip-adapter-plus_sd15.safetensors
  ip-adapter_sd15.safetensors
```

Sources: Hugging Face `h94/IP-Adapter-FaceID` + `h94/IP-Adapter` (models/).

## Re-install

```bash
# from desk → gpu-host
ssh gpu-host 'bash -s' < scripts/stage_ipadapter_faceid.sh
# or re-run wget block in that script
```

## Use in Comfy (SD1.5 / DreamShaper)

1. `CheckpointLoaderSimple` → DreamShaper_8  
2. `IPAdapterUnifiedLoaderFaceID` preset **FACEID PLUS V2** (or load bin via `IPAdapterModelLoader`)  
3. Reference image = `LoadImage` (e.g. CEO source still)  
4. Provider **CUDA** for InsightFace  

## Note

Empty nested dirs `IpAdapter` / `IpAdapters15` (old SM stubs) remain as clutter; real weights are **flat files** in `ipadapter/`.
