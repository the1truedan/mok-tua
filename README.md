# MOCK-TUA

Portable **shot-driven** storyboard + tiered staged rendering orchestrator for M.A.N.A.G.E.R.

Hybrid v1 (MAC):

| Stage | Backend |
|-------|---------|
| S0 script expand | **Live Headroom** `:8787` |
| S1/S2 stills / storyboard | **Live SM ComfyUI** `:8188` |
| S3 video | **GPU** Comfy `:8188` (container or host runtime) |
| Cloud overflow | Pricing estimate stub (HF ZeroGPU / RunPod tables) |

Control API: **`:8799`**.

## Quick start (host, recommended)

```bash
cd ~/mock-tua
chmod +x scripts/*.sh
./scripts/run_host.sh
# other terminal:
./scripts/smoke_local.sh
./scripts/smoke_gpu.sh
```

## Docker (API only)

```bash
cp .env.example .env
# set LITELLM_MASTER_KEY to your own LLM gateway/proxy key if you want live S0
docker compose up -d --build
./scripts/smoke_local.sh
```

Uses `host.docker.internal` for Headroom + MAC Comfy.

## GPU video worker

```bash
# preferred until nvidia-ctk: a host-runtime launcher script for ComfyUI on
# your GPU box (not included in this repo -- write your own equivalent to
# start/stop ComfyUI outside Docker)
ssh gpu 'bash path/to/your/comfy_gpu_host_runtime.sh smoke'

# docker path (needs nvidia-container-toolkit):
# docker compose -f docker-compose.gpu.yml up -d
```

## Story elements

See `schemas/music_video_story_elements.md` and `fixtures/sample_instructor_story.md`.

```bash
curl -s http://127.0.0.1:8799/v1/runs -H 'content-type: application/json' \
  -d @<(python3 -c "import json,pathlib; print(json.dumps({'markdown': pathlib.Path('fixtures/sample_instructor_story.md').read_text(), 'dry_run': True}))")
```

## Earmarks

- Comfy config portability across CUDA/MPS/ROCm hosts
  (`workflows/extra_model_paths.yaml`)
- HF Pro ZeroGPU overflow (`config/pricing.yaml`, `MOCK_TUA_HF_LIVE=0` until
  wired)
- Ansible-based portable node packaging, not yet built

## API map

| Method | Path |
|--------|------|
| GET | `/healthz` |
| POST | `/v1/parse` |
| POST | `/v1/estimate` |
| POST | `/v1/runs` |
| GET | `/v1/runs` |
| GET | `/v1/runs/{id}` |
| POST | `/v1/runs/{id}/shots/{shot}/resume` |
| GET | `/v1/probe/comfy` |
