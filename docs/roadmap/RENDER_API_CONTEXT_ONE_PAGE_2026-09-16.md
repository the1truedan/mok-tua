# Render API context — one page (2026-09-16)

Concise, copy-pasteable reference for driving Maestro + ComfyUI across the fleet. Companion to
`MOK_TUA_RESOURCE_INDEX_DESIGN_2026-09-16.md` (the full design doc) — this is the fast-lookup
version. Every command below was actually run this session, not guessed from docs.

## Mechanism disambiguation (read this before claiming lip-sync works)

Three different, non-interchangeable mechanisms exist in this fleet. Never say "lip-sync works"
without naming which one:

| Mechanism | Where | Status |
|---|---|---|
| **LTX-2 audio-conditioned** | Maestro REST only (`director/pipeline/start`, `video_model: ltx2_25_nvfp4`) | **Proven** — Fill a Bust, 53 deliverables as of 2026-09-16 |
| **MiniMax H3 VocalLock_V3** | Isolated ComfyUI `:8189` (H3-only env) | **Proven** — verse batch 5/5, 2026-09-12 |
| **DreamTalk / LivePortrait / FaceFusion** | Various ComfyUI custom nodes | **Unproven** in this fleet |

mok-tua's own **shared** ComfyUI (`:8188`, the one smoke-tested below) has **no working
audio-conditioned video path today** — the in-repo `ltx_fflf` pin is UI-format/non-audio and
orphaned from `video_providers`. If a shot needs real audio-driven lip-sync, route it to Maestro
or the isolated H3 `:8189` env, not the shared `:8188` ComfyUI.

## Maestro (mrgpu only — smoke-tested live 2026-09-16)

```bash
# Start (bypass pterm, which can silently no-op)
ssh mrgpu 'cd /mnt/ai-data/pinokio/api/Maestro/app && \
  SERVER_PORT=42005 setsid nohup env-sol/bin/python launch.py \
  > /tmp/maestro-launch.log 2>&1 < /dev/null & disown'
# ready in ~15-20s; poll:
ssh mrgpu "curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:42005/"

# What's available right now (real response, 2026-09-16)
curl -s http://127.0.0.1:42005/api/v1/loras/directories
#   {"directories": ["ace_step_v1_5_xl","flux2_klein_9b","kugelaudio","ltx2",
#                     "minimax_h3","wan","wan_1.3B","wan_5B"]}

# Render orchestration core (the only 2 endpoints Fill a Bust's shot_common.py needs)
curl -s -X POST http://127.0.0.1:42005/api/v1/director/pipeline/start -d @request.json
curl -s http://127.0.0.1:42005/api/v1/director/pipeline/{pid}    # status/progress

# List/inspect what's already been rendered this session
curl -s http://127.0.0.1:42005/api/v1/director/pipelines
```

Full 190-route catalog: `../grokcode/docs/catalog/MAESTRO_API_ENDPOINTS_2026-09-16.md` (that
repo, cross-referenced — not duplicated here).

**Stop when done** (frees ~1.6GB RAM + GPU headroom for other work on the box):
`ssh mrgpu 'pkill -f "env-sol/bin/python launch.py"'`

## ComfyUI, per host (2026-09-16 status)

| Host | Port(s) | Status this pass | Notes |
|---|---|---|---|
| **mrgpu** | `:8188` (shared) · `:8189` (isolated H3) | **Smoke-tested live** — see below | 2,793 node types loaded (~70 custom-node packages) |
| **m4rv** (this Mac) | `:8188` (shared) · `:8288` (independent local) | Not started this pass | Mac was under real memory pressure (11GB local llama-server + Docker + RipX); don't start ComfyUI here without checking `free`/`vm_stat` first |
| **tower** | `:8190` (manage-only, CPU) | Not deployed | No container exists yet (`docker ps -a` empty) — `deploy/comfyui-tower-manage/docker-compose.yml` has never been `up`'d. CPU-only by design (GPU reserved for `tower-ollama`); not worth deploying for real renders, only for node/model management if ever needed |

```bash
# Start shared ComfyUI on a given host (script lives in grokcode, self-contained bash)
scp grokcode/scripts/comfy_launch_shared.sh <host>:/tmp/
ssh <host> "bash /tmp/comfy_launch_shared.sh <host>"   # ~60-90s to fully load custom nodes

# Real smoke-test calls (mrgpu, 2026-09-16)
curl -s http://127.0.0.1:8188/system_stats   # {"system": {"comfyui_version": "0.30.2", ...}}
curl -s http://127.0.0.1:8188/queue          # {"queue_running": 0, "queue_pending": 0}
curl -s http://127.0.0.1:8188/object_info | python3 -c \
  "import json,sys; print(len(json.load(sys.stdin)))"   # -> 2793 node types
```

**Stop when done:** `ssh mrgpu 'pkill -f "ComfyUI.*main.py.*8188"'`

## Cloud (2026-09-16 — partial, needs an account to go further)

Not a proven route yet — this is where the trail currently ends, honestly reported rather than
guessed:

- **HuggingFace Spaces**: `huggingface.co` itself is reachable from this dev box (200), but the
  bookmarked Space (`hugging-apps/bernini-diffusers-v2-demo`, a Bernini Diffusers image demo —
  not video) did not respond on its guessed `*.hf.space` subdomain from here. Could be asleep
  (free-tier Spaces sleep on inactivity), a wrong subdomain guess, or a network restriction on
  `*.hf.space` specifically from this environment. **Also note the user's own HF MCP settings
  page is bookmarked** (`huggingface.co/settings/mcp`) — worth checking directly whether HF's
  official MCP server is already enabled on the account before building anything custom.
- **RunComfy** (`runcomfy.com/comfyui-workflows`): reachable (200), markets "runnable guaranteed"
  pre-set ComfyUI workflows in the cloud. Needs an account/API key to test for real — not free
  by default, may have a trial tier. Worth evaluating with credentials before Fill-a-Bust-scale
  cloud rendering is attempted anywhere.
- **Conclusion for now**: local (Maestro + mrgpu ComfyUI) stays the only proven route for complex
  shots. Cloud is a real option to keep exploring but isn't validated yet — don't route
  production renders there without a follow-up session that actually authenticates and calls one
  of these with real credentials.

## What the Brave bookmark trail (AI folder, bulk-added 2026-09-16) is actually pointing at

Not exhaustive — the AI folder has 1,250+ entries, mostly a GitHub reading list. The load-bearing
signal:

- **`guaardvark/guaardvark`** — "self-hosted AI studio: local video, image, music, voice, LoRA
  training... on one GPU, driven from the Studio or by your coding agent (Claude Code, Cursor,
  Codex, OpenClaw) through MCP and skills." **This is directly relevant prior art for the
  resource-index goal in `MOK_TUA_RESOURCE_INDEX_DESIGN_2026-09-16.md`** — worth evaluating
  before writing more mok-tua-native orchestration code; it may already solve part of this.
- **`juwalbose/JBAiVideoSuite`** — "connects to local LLM & ComfyUI... generate MinimaxH3
  videos" — same shape of problem as Fill a Bust, worth a read for prompt/pipeline ideas.
- **`szprivate/agentY`**, **`yxpzyr/comfyui-remote-panel`** — smaller agent-drives-ComfyUI tools,
  same space as the resource-index goal.
- **H3 ComfyUI addon ecosystem is actively expanding** past what's on the pool today: camera
  control (`Minimax h3 Camera Control`), long-form continuum/multishot stitching, R2V+audio,
  low-VRAM multi-ref workflows — all recent Civitai bookmarks. Worth a pass to see which of these
  nodes/workflows aren't yet pulled to `/mnt/ai-data/models/` before assuming the current H3
  setup is complete.
- **Lip-sync/animation alternatives bookmarked**: `Viggle-AI-video`, `HumanAIGC/AnimateAnyone`,
  `DanielSWolf/rhubarb-lip-sync`, `xianfei/SysMocap`. None of these are proven in this fleet yet
  (see mechanism table above) — they're candidates for a future DreamTalk/LivePortrait-class
  evaluation, not a current option.
