# MOCK-TUA

Portable **shot-driven** storyboard + tiered staged rendering orchestrator for M.A.N.A.G.E.R.

Hybrid v1 (desk-host):

| Stage | Backend |
|-------|---------|
| S0 script expand | **Live Headroom** `:8787` |
| S1/S2 stills / storyboard | **Live SM ComfyUI** `:8188` |
| S3 video | **gpu-host** Comfy `:8188` (container or host runtime) |
| Cloud overflow | Pricing estimate stub (HF ZeroGPU / RunPod tables) |

Control API: **`:8799`**.

## Quick start (host, recommended)

```bash
cd /Users/redacted/mock-tua
chmod +x scripts/*.sh
./scripts/run_host.sh
# other terminal:
./scripts/smoke_local.sh
./scripts/smoke_gpu-host.sh
```

## Docker (API only)

```bash
cp .env.example .env
# set LITELLM_MASTER_KEY from ~/ai-gateway/.env if you want live S0
docker compose up -d --build
./scripts/smoke_local.sh
```

Uses `host.docker.internal` for Headroom + desk-host Comfy.

## gpu-host video worker

```bash
# preferred until nvidia-ctk: host runtime from grokcode
ssh gpu-host 'bash ~/grokcode/scripts/comfy_gpu-host_host_runtime.sh smoke'

# docker path (needs nvidia-container-toolkit):
# docker compose -f docker-compose.gpu-host.yml up -d
```

## Story elements

See `schemas/music_video_story_elements.md` and `fixtures/sample_instructor_story.md`.

```bash
curl -s http://127.0.0.1:8799/v1/runs -H 'content-type: application/json' \
  -d @<(python3 -c "import json,pathlib; print(json.dumps({'markdown': pathlib.Path('fixtures/sample_instructor_story.md').read_text(), 'dry_run': True}))")
```

## Context / share ingest

Full recon export: `context/mock-tua.md`.  
**Agents:** fetch `grok.com/share` via `~/grokcode/scripts/batch_share_ingest.py` (never SPA scrape). See `CONTEXT.md`.

## Earmarks

- Comfy config portability → Mac Studio / PCI CUDA-ROCm Mac (`workflows/extra_model_paths.yaml` + grokcode `deploy/comfyui`)
- HF Pro ZeroGPU overflow (`config/pricing.yaml`, `MOCK_TUA_HF_LIVE=0` until wired)
- Tok-tua S-tier agent deck (agtop/ctop) — separate track
- Ansible portable node package — post-ACL unless needed sooner

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
