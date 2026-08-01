# mok-tua (a.k.a. MOCK-TUA)

Turn a short script into storyboard stills and optional video clips by
walking a fixed stage ladder — text expand → stills → video — against the
tools you already run at home (local LLM gateway + ComfyUI).

Built for small creative pipelines, not a hosted “movie studio” product.

### Stages (hybrid Mac v1)

| Stage | What happens | Where |
|-------|----------------|------|
| S0 | Expand / shape the script | Local Headroom gateway `:8787` |
| S1/S2 | Still frames / storyboard | ComfyUI `:8188` |
| S3 | Video (when you want motion) | GPU ComfyUI `:8188` |
| Cloud | Overflow cost estimate only | Stub tables (HF ZeroGPU / RunPod) |

Control API listens on **`:8799`**.

## Quick start (on the host)

```bash
cd ~/mok-tua   # or your clone path
chmod +x scripts/*.sh
./scripts/run_host.sh
# other terminal:
./scripts/smoke_local.sh
./scripts/smoke_gpu.sh
```

## Docker (API only)

```bash
cp .env.example .env
# optional: set LITELLM_MASTER_KEY if S0 should hit your live gateway
docker compose up -d --build
./scripts/smoke_local.sh
```

From Docker on a Mac, Headroom and Comfy are reached via `host.docker.internal`.

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
