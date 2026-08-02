# mok-tua — Operator & developer guide

> **Looking for the plain-English overview?** Start at the root [README.md](../README.md).  
> This page keeps the **technical** detail (ports, CLI, tiers, federation, API tables).

**Version:** hybrid v0.5 · Control API **`:8799`**

---


Portable **shot-driven** storyboard + tiered staged rendering orchestrator for M.A.N.A.G.E.R.

**Hybrid v0.3.0** (2026-08-02) — director stack **process**: live T0–T4 pull/smoke/lock,
MRGPU resource monitor, discover→audit→stage nested CLI.

| Stage | Backend |
|-------|---------|
| S0 script expand | **Live Headroom** `:8787` |
| S1/S2 stills / storyboard | **Local SM ComfyUI** `:8188` (minimal SD or Qwen pin) **or** cloud: **Grok Imagine** / **Nano Banana** |
| S3 video | **MRGPU** Comfy Wan pin (primary) / AnimateDiff fallback / Seedance & Grok video earmarks |
| Cloud overflow | QQQ-gated; PHI never auto-cloud |

Control API: **`:8799`**. Director's Console peer: UI `:5173` · CPE `:9800` · orch `:9820`.

## Version history

| Ver | Date | Changes |
|-----|------|---------|
| **0.5.0** | 2026-08-02 | Conductor **TUI** (`tui/`): `--skin c64\|modern`, CLI `tui` + `run_tui.sh`, bridge to existing CLI verbs; vendor GUI mok-ups retained — see `docs/INTERFACES.md`, root `CHANGELOG.md` |
| **0.4.x** | 2026-08-02 | Human README, non-doxxing product art, vendor/mok-up showcase |
| **0.3.0** | 2026-08-02 | T0–T4 **tier lock** (`config/tier_lock_T0-T4.json`) + loading profiles; live `pull --tier` with dirty/conflict safety; **MRGPU monitor** (RAM/CPU/GPU/temp via exporters+SSH); `smoke` T0–T4 scorecard; nested `discover` / `audit` / `stage-app` / `lock`; progress bars on pull/load; **ask_packet.v1** federation (Johnny BOM + CHAINS render receipts + trusted node award; PHI unbroadcastable) — `docs/ASK_PACKET_FEDERATION.md` |
| **0.2.x** | 2026-08 | Providers/catalog, sides ingest, Qwen multi-angle lock, Grok Imagine / Nano Banana dry-run, `mok_tua_cli` launch/pull |
| **0.1.0** | 2026-07-27 | Initial scaffold — story parse, stages, Comfy/Headroom, MRGPU compose |

## Quick start (host, recommended)

```bash
cd ~/mok-tua
chmod +x scripts/*.sh scripts/mok_tua_cli.py
./scripts/run_host.sh
# other terminal:
./scripts/smoke_local.sh
./scripts/smoke_mrgpu.sh
./scripts/smoke_tiers.sh          # T0–T4 scorecard
```

## Director stack (Pinokio + SM + GitHub)

Full map of **Director's Console**, **Wan2GP**, **FaceFusion**, **FreeMoCap**,
**ACE-Step**, **TTS-Story**, FramePack, LivePortrait, etc. already on
`/Volumes/ai-data`:

- `config/director_stack_catalog.md` — human map + pipeline  
- `config/director_stack_catalog.json` — machine registry for launch recipes  
- `config/tier_lock_T0-T4.json` — **version pins + loading profiles** (scale/repro)

```bash
# conductor TUI (C64 default; same verbs as below)
python3 scripts/mok_tua_cli.py tui                 # or ./scripts/run_tui.sh
python3 scripts/mok_tua_cli.py tui --skin modern
python3 scripts/mok_tua_cli.py tui --repl          # no Textual
# optional full-screen: pip install -r tui/requirements.txt

# status board
python3 scripts/mok_tua_cli.py providers
python3 scripts/mok_tua_cli.py doctor
python3 scripts/mok_tua_cli.py monitor          # MRGPU RAM/CPU/GPU/temp

# dry-run launch recipes (safe)
python3 scripts/mok_tua_cli.py launch demo
python3 scripts/mok_tua_cli.py launch wan2gp
python3 scripts/mok_tua_cli.py launch full

# actually spawn (only processes mok-tua can stop later)
python3 scripts/mok_tua_cli.py launch directors_console --live
python3 scripts/mok_tua_cli.py stop directors_console

# live tier pulls (O'Reilly mode) + mrgpu progress strip
python3 scripts/mok_tua_cli.py pull --tier T0_orchestrators --live --monitor mrgpu
python3 scripts/mok_tua_cli.py pull --tier T1_vid_gen --live --monitor mrgpu
python3 scripts/mok_tua_cli.py pull --tier T2_audio_music --live --monitor mrgpu
python3 scripts/mok_tua_cli.py pull --tier T3_face_body --live --monitor mrgpu
python3 scripts/mok_tua_cli.py pull --all-bleed --live --monitor mrgpu

# T0–T4 smoke + lock
python3 scripts/mok_tua_cli.py smoke --tiers T0-T4
python3 scripts/mok_tua_cli.py lock write --smoke-ref work/smoke/tier_smoke_YYYY-MM-DD.json
python3 scripts/mok_tua_cli.py lock load demo          # dry-run load order
python3 scripts/mok_tua_cli.py lock load demo --live --monitor mrgpu
```

HTTP: `GET /v1/providers` · `GET /v1/doctor` · `POST /v1/providers/{id}/launch`

**Rule:** Pinokio/SM own install + GPU process life; mok-tua owns shots, stage,
QQQ, launch recipes, audit, and **tier lock**. Pull bleeding edge with `pull` / Pinokio **Update**.

### Pull safety policy (live)

- Prefer **nested `app/.git`** over dirty Pinokio wrappers (`install.js` / `reset.js`).
- **Skip** dirty trees, merge conflicts (`UU`), and very-dirty (>40 files) — never `git reset --hard`.
- `behind=0` + dirty → treat as current; re-pull only after clean/repair.
- Known blocker: **wan2gp** may have `UU install.js` / `UU update.js` — repair pinokio scripts only, leave model cache alone.
- TTS-Story / FreeMoCap / DreamTalk often Pinokio-dirty — path smoke only until cleaned.

### Process CLI (discover → audit → stage → pull → smoke → lock)

When new GitHub / Pinokio options appear, use the nested process (vetted before promote):

```bash
python3 scripts/mok_tua_cli.py discover --source all
python3 scripts/mok_tua_cli.py audit facefusion
python3 scripts/mok_tua_cli.py audit /Volumes/ai-data/github/SomeRepo --trivy --docker --osv
python3 scripts/mok_tua_cli.py stage-app storyboard_ui2          # earmark into catalog gaps
python3 scripts/mok_tua_cli.py pull <id> --live --monitor mrgpu
python3 scripts/mok_tua_cli.py smoke --tiers T0-T4
python3 scripts/mok_tua_cli.py lock write
```

Audit hooks earmark grokcode tooling: `scripts/github_staging_repos.py`,
`scan-all-dockerfiles.sh`, optional `trivy` / `osv-scanner` if installed.

### T0–T4 lock + loading (scale)

| Tier | Role |
|------|------|
| **T0** | Orchestrators — mok-tua + Director's Console |
| **T1** | Video gen — SM Comfy, Wan2GP, FramePack |
| **T2** | Audio/music — ACE-Step, TTS-Story, voice zoo |
| **T3** | Face/body — FaceFusion, DreamTalk, FreeMoCap, pose models |
| **T4** | Comfy workflow pins + node object_info smoke |

Loading profiles in the lock file: `demo`, `full_local`, `video_mrgpu`, `face`, `audio`, `body`.
`lock load <profile>` walks the list with progress bars (and optional MRGPU monitor).

## Ask-packet federation (trusted lab, not a public market)

Encapsulated compute asks: **Johnny BOM** (`requires[]`) + **tier_lock join key** +
**pricing expectations** + sealed payload + **CHAINS** receipts on chain
`mok-tua-render` (never caregiving PHI chain).

```bash
python3 scripts/mok_tua_cli.py nodes seed
python3 scripts/mok_tua_cli.py packet emit fixtures/sample_instructor_story.md \
  --data-class public --qqq QQQ3 --allow-crowd
python3 scripts/mok_tua_cli.py packet award work/packets/<id>/packet.json
python3 scripts/mok_tua_cli.py chains verify
```

Schemas: `schemas/ask_packet.v1.json`, `ask_receipt.v1.json`, `node_advertisement.v1.json`.  
Design: `docs/ASK_PACKET_FEDERATION.md`. Pricing earmark: `crowd_federated` (QQQ3, public only).

## ROBUST Comfy worker (MRGPU)

Living roster + avoid-list: `config/comfy_nodes_mok_tua_roster.json`  
Docs: `docs/COMFY_ROBUST_NODES.md`

```bash
# on mrgpu — install P0/P1 nodes, deps, disable broken, fix .git perms
bash scripts/comfy_robust_install_mrgpu.sh
# restart Comfy, then capability smoke:
COMFY_URL=http://127.0.0.1:8188 bash scripts/smoke_comfy_robust.sh
./scripts/smoke_tiers.sh   # T0–T4 mok-tua stack
```

**Outside Comfy (G):** ACE-Step, TTS-Story, FaceFusion, FreeMoCap, mok-tua ledger — not custom_nodes.
## Tonight: sides → batch demo

```bash
# 1) Check / stage models into /Volumes/ai-data/models/{loras,diffusion_models,...}
python3 scripts/mok_tua_cli.py inventory
python3 scripts/mok_tua_cli.py stage --required-for local_qwen_edit   # dry-run
python3 scripts/mok_tua_cli.py stage --required-for local_qwen_edit --live

# 2) PDF / Final Draft (.fdx) / MD / TXT sides → story + dry run
python3 scripts/mok_tua_cli.py sides /path/to/sides.pdf -o /tmp/sides.md --run
python3 scripts/mok_tua_cli.py sides /path/to/script.fdx --run
python3 scripts/mok_tua_cli.py batch fixtures/sample_sides_plain.txt fixtures/sample_instructor_story.md

# 3) Live stills (Comfy up) — locked default still_provider=local_qwen_edit
python3 scripts/mok_tua_cli.py run /tmp/sides.md --live-still --no-dry-run

# 4) HTTP / Open WebUI tools
curl -s http://127.0.0.1:8799/v1/tools/openai | head
curl -s http://127.0.0.1:8799/v1/stage/inventory
# OWUI: config/openwebui_mok_tua_tools.json → POST /v1/tools/call
```

## Docker (API only)

```bash
cp .env.example .env
# set LITELLM_MASTER_KEY from ~/ai-gateway/.env if you want live S0
docker compose up -d --build
./scripts/smoke_local.sh
```

Uses `host.docker.internal` for Headroom + M4RV Comfy.

## MRGPU video worker

```bash
# preferred until nvidia-ctk: host runtime from grokcode
ssh mrgpu 'bash ~/grokcode/scripts/comfy_mrgpu_host_runtime.sh smoke'

# docker path (needs nvidia-container-toolkit):
# docker compose -f docker-compose.mrgpu.yml up -d
```

## Story elements

See `schemas/music_video_story_elements.md` and `fixtures/sample_instructor_story.md`.

```bash
curl -s http://127.0.0.1:8799/v1/runs -H 'content-type: application/json' \
  -d @<(python3 -c "import json,pathlib; print(json.dumps({'markdown': pathlib.Path('fixtures/sample_instructor_story.md').read_text(), 'dry_run': True}))")
```

### Provider selection (v0.2)

```bash
# Local stills with Next Scene / camera grammar (prompt builder always on)
curl -s http://127.0.0.1:8799/v1/runs -H 'content-type: application/json' -d '{
  "markdown": "...",
  "dry_run": true,
  "still_provider": "local_sd_minimal",
  "video_provider": "local_wan",
  "qqq": "QQQ0"
}'

# Cloud stills plan (no spend while dry_run=true)
curl -s http://127.0.0.1:8799/v1/runs -H 'content-type: application/json' -d '{
  "markdown": "...",
  "dry_run": true,
  "still_provider": "grok_imagine",
  "qqq": "QQQ1",
  "quality_stills": false
}'

# Nano Banana still plan
curl -s http://127.0.0.1:8799/v1/runs -H 'content-type: application/json' -d '{
  "markdown": "...",
  "dry_run": true,
  "still_provider": "nano_banana",
  "qqq": "QQQ1"
}'
```

List providers: `GET /v1/info`

## Capability matrix (annuda-whole-thang)

| Capability | Status | How |
|------------|--------|-----|
| Shot markdown parse + estimate | **live** | `/v1/parse`, `/v1/estimate` |
| Minimal SD storyboard stills | **live** | `still_provider=local_sd_minimal` |
| Camera + Next Scene prompt grammar | **live** | `config/camera_angles.json` + `api/prompt_build.py` |
| Qwen multi-angle + next-scene LoRAs | **weights on pool** | Inventory `config/lora_inventory_storyboard_2026-08-02.*`; API graph export still pending → pin placeholder |
| StoryboardUI2 angle library | **ported (partial)** | presets/phrases in `camera_angles.json` (no PyQt6) |
| Wan I2V on MRGPU | **pin_pending** | path in `workflow_pins.wan22_animate`; needs live submit + API-ready graph |
| AnimateDiff (Money99-era) | **fallback earmark** | `video_provider=local_animatediff` + export `animatediff_basic.api.json` |
| Grok Imagine stills | **wired (dry_run safe)** | `still_provider=grok_imagine` + `XAI_API_KEY` for live |
| Nano Banana stills | **wired (dry_run safe)** | `still_provider=nano_banana` + Google key or `comfy` CLI |
| Seedance board→video | **earmark** | Comfy.org partner workflows; Phase 4 |
| OminiControl subject lock | **earmark tier_b** | objects/props; not humans |
| aby.one | **competitive only** | no stable open API |

## CLI remote earmarks (ops smoke)

### Grok Imagine

```bash
export XAI_API_KEY=...
curl -X POST https://api.x.ai/v1/images/generations \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"grok-imagine-image","prompt":"storyboard panel, instructor medium close-up"}'
```

Optional community CLI: `npm i -g grok-image-cli` (stores key in OS keychain).

### Nano Banana

```bash
# Comfy-Org CLI (when comfy + partner API configured)
comfy generate nano-banana --prompt "storyboard panel, instructor medium close-up" --download panel.png
```

These CLIs are **ops earmarks**; production runs should go through `POST /v1/runs` with `still_provider`.

## Context / share ingest

Full recon export: `context/mock-tua.md`.  
**Agents:** fetch `grok.com/share` via `~/grokcode/scripts/batch_share_ingest.py` (never SPA scrape). See `CONTEXT.md`.

## Earmarks

- Comfy config portability → Mac Studio / PCI CUDA-ROCm Mac (`workflows/extra_model_paths.yaml` + grokcode `deploy/comfyui`)
- Export real API graphs for `qwen_next_scene_angles` and `animatediff_basic`
- HF Pro ZeroGPU overflow (`config/pricing.yaml`, live only under QQQ3/1 + public data class)
- Seedance / Comfy Cloud partner client (Phase 4)
- Tok-tua S-tier agent deck (agtop/ctop) — separate track
- Ansible portable node package — post-ACL unless needed sooner
- OminiControl Comfy node for non-human subject lock

## API map

| Method | Path |
|--------|------|
| GET | `/healthz` |
| GET | `/v1/info` |
| POST | `/v1/parse` |
| POST | `/v1/estimate` |
| POST | `/v1/runs` |
| GET | `/v1/runs` |
| GET | `/v1/runs/{id}` |
| POST | `/v1/runs/{id}/shots/{shot}/resume` |
| GET | `/v1/probe/comfy` |

## QQQ modes

| Mode | Meaning |
|------|---------|
| **QQQ0** | Local only (Comfy M4RV/MRGPU) |
| **QQQ3** | Free/public overflow (HF ZeroGPU; limited Grok if public data) |
| **QQQ1** | Paid cloud (Grok Imagine, Nano Banana, Seedance, RunPod) — requires non-PHI + explicit confirm |

Set via request `qqq` or env `MOCK_TUA_QQQ`.

## License

MIT — see LICENSE.
