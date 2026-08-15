# Smoke-tested capabilities — mok-tua **0.6.0**

**Date:** 2026-08-15  
**Hosts:** gpu-host (RTX 4060 Ti 16GB) — main ComfyUI `:8188`, isolated env `:8189`  
**Format:** text-only — no screenshots or video embeds in this report. See [CHANGELOG.md](../../CHANGELOG.md) for what shipped, [MILESTONES.md](../MILESTONES.md) for the dated ledger.

---

## Tested matrix

| Capability | Status | Evidence |
|------------|--------|----------|
| MiniMax H3 image-to-video | **PASS** | Isolated ComfyUI v0.31.0 env (`:8189`, torch 2.9+/cu130 — the shared `:8188` install can't take this ComfyUI version without breaking other pinned tools). Real render: 704×384, 124 frames (~5.2s), synced h264 video + aac audio, peak VRAM ~15GB/16.4GB. |
| LTX-2.3 text-to-video + audio | **PASS** | Same isolated `:8189` env, int8-quantized distilled transformer. |
| Director's Console job submission | **PASS** | `POST /api/job` on the Orchestrator (`:9820`) with a real ComfyUI workflow, `backend_affinity: mrgpu-8188`. Response: `status: completed`. Confirmed a real output file landed on disk at both the backend's own output directory and the orchestrator's per-job output path — not just a success response. |
| `mok-tua curate` (scan/list/pick/order/assemble) | **PASS** | Synthetic two-run fixture: two takes of the same shot across separate directories, grouped correctly by shot id; picked the non-default take; assembled output verified frame-by-frame (correct color at t=0 matching the picked take, correct color at t=1.5s matching the second shot, correct total duration). |
| Lipsync tool integration points | **PARTIAL** | Face-swap/talking-head/portrait-animation tools identified and wired into the model registry. No end-to-end lipsync render has been proven yet — do not claim more than "wired in." |

## Pending / earmarked (not PASS)

| Item | Note |
|------|------|
| LTX-2.5 | Weights staged, download in progress at time of writing — not yet smoke-tested |
| HunyuanVideo 1.5 | Weights staged, download in progress — not yet smoke-tested |
| CogVideoX 1.5 | Weights staged, download in progress — ComfyUI support itself is on an unmerged wrapper branch upstream, expect friction |
| WAN2.1 Vace 14B | Weights staged, download in progress — targeted at the reference-conditioning approach for cross-shot consistency, not yet tested |
| Krea 2 (RAW/Turbo/Identity Edit) | Weights staged — the model browser previously showed this as fully installed when it was not; re-verify actual weight presence before trusting that UI count again |
| Director's Console cinematography (camera moves, shot grammar) | Job-submission *plumbing* is proven (see above), but only with a trivial still image. No render has actually exercised the camera-move/shot-grammar catalog (the 144-angle grid, named moves like push-in or crane, the 67 film-style presets) — the feature surface is real and live via the API, it just hasn't been used in an actual test render yet |
| Full song → video → lipsync proof run | The piece still missing before claiming the whole pipeline end to end |

---

## Operator re-run

```bash
# H3 / LTX-2.3 — isolated env
ssh mrgpu
source /mnt/ai-data/comfyui-h3/envs/mrgpu/bin/activate
cd /mnt/ai-data/comfyui-h3/src/ComfyUI
python main.py --listen 0.0.0.0 --port 8189 --disable-auto-launch

# Director's Console job submission
curl -X POST http://gpu-host:9820/api/job -H "Content-Type: application/json" -d @job.json

# curate
python3 scripts/mok_tua_cli.py curate scan my_project ./runs/*
python3 scripts/mok_tua_cli.py curate assemble my_project out.mp4
```
