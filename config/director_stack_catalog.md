# Director stack catalog — Pinokio + SM + GitHub → mok-tua

**ROBUST map** of tools already on `/Volumes/ai-data` plus how to launch them for bleeding-edge **video / audio / face / body** work without pretending mok-tua is the only UI.

Machine twin: `director_stack_catalog.json`.

## One picture

```text
  sides PDF/FDX/MD
        │
        ▼
  ┌─────────────────┐     ┌──────────────────────┐
  │ mok-tua :8799   │◄───►│ Director's Console   │  Pinokio
  │ shots+stage+QQQ │     │ CPE :9800 / orch :9820│  storyboard UI
  └────────┬────────┘     └──────────┬───────────┘
           │                         │
     stills│                   prompts│
           ▼                         │
  ┌─────────────────┐                │
  │ SM Comfy :8188  │◄───────────────┘
  │ Qwen multi-angle│
  │ Wan / LTX / AD  │
  └────────┬────────┘
           │
     ┌─────┴──────────────────────────────┐
     ▼              ▼                     ▼
 Wan2GP         FaceFusion            FreeMoCap
 (Pinokio)      DreamTalk             AI4Animation
 FramePack      LivePortrait models   OpenPose CN
 (SM)           InsightFace
     │              │                     │
     └──────────────┴─────────────────────┘
                      │
                      ▼
              ACE-Step / TTS-Story / Qwen3-TTS
                      │
                      ▼
                 stitch + deliver
```

## What you already have (not vapor)

### T0 — Directors / orchestrators

| Tool | Where | Launch | Role |
|------|--------|--------|------|
| **mok-tua** | `~/mok-tua` | CLI + `:8799` + OWUI tools | Sides → shots → providers → audit |
| **Director's Console** | `pinokio/api/directorsconsole.pinokio.git` | Pinokio Start → UI `:5173`, CPE `:9800`, orch `:9820` | Cinema prompts + multi-node render management |
| **ai-gateway / Headroom** | compose | `:8787` / `:4000` | LLM expand, tool calls |

### T1 — Video gen (bleeding-edge local)

| Tool | Where | Notes |
|------|--------|------|
| **SM ComfyUI** | SM Packages | Primary API worker; Wan/LTX/Qwen graphs in Workflows |
| **Pinokio ComfyUI** | `comfyui.pinokio.git` | Alternate host / node experiments |
| **Wan2GP** | `wan2gp.git` → [deepbeepmeep/Wan2GP](https://github.com/deepbeepmeep/Wan2GP) | Wan 2.1/2.2 + LTX + Hunyuan + Qwen Image — **GPU-poor Gradio path** |
| **Wan (factory)** | `wan.git` | Pinokio script variant |
| **FramePack Studio** | SM Packages | Long-form / keyframe video package |

SM workflows already on disk (sample): Wan 2.2 animate, InfiniteTalk, Uni3C move, talking avatar Wan 2.2, Wan all-in-one, motion transfer, Qwen Edit 2509.

### T2 — Audio / music / VO

| Tool | Where | Role |
|------|--------|------|
| **ACE-Step** (+ UI) | `ace-step*.pinokio.git` | Music gen + **REST API** |
| **TTS-Story** | `TTS-Story.git` | Multi-voice story VO (Kokoro / Chatterbox) |
| **Qwen3-TTS** | `Qwen3-TTS-Pinokio.git` | TTS |
| **Chatterbox / AllTalk / Zonos / ZipVoice / VoxCPM / Voice-Pro / OpenAudio** | pinokio/api | Voice zoo |
| **Whisper WebUI / MLX transcription / Speaches** | pinokio/api | ASR → sides |

### T3 — Face + body track

| Tool | Where | Role |
|------|--------|------|
| **FaceFusion** | `facefusion-pinokio.git` | Face swap / enhance platform |
| **DreamTalk** | `dreamtalk.git` | Audio-driven talking head |
| **FreeMoCap** | `FreeMoCap.pinokio.git` | Markerless **body mocap** |
| **AI4Animation** | `ai4animationpy.pinokio.git` | Animation research stack |
| **LivePortrait + InsightFace + OpenPose CN** | `models/` | Weights for Comfy / apps |

## Launch modes (GUI + TUI + API)

| Mode | How |
|------|-----|
| **Pinokio GUI** | Install / Start / Update / Reset on each `*.pinokio.git` |
| **Stability Matrix GUI** | Launch Comfy / FramePack; point models at NFS pool |
| **mok-tua CLI** | `scripts/mok_tua_cli.py inventory\|stage\|sides\|run\|batch` |
| **mok-tua API / OWUI** | `GET /v1/tools/openai` · `POST /v1/tools/call` |
| **Director's Console API** | CPE `:9800` + Orchestrator `:9820` (see app README) |
| **Git bleeding edge** | `git -C /Volumes/ai-data/pinokio/api/<app> pull` then Pinokio **Update** |
| **GitHub mirrors** | `/Volumes/ai-data/github` (e.g. ComfyUI-VideoHelperSuite, proxypose) |

## Recommended “bleeding edge” demo chain (tonight-capable)

1. **Ingest** sides (PDF/FDX/MD) → mok-tua  
2. Optional: **Director's Console** CPE for camera language → paste into shot `camera:`  
3. **Stills**: SM Comfy + Qwen multi-angle / next-scene (locked)  
4. Optional: **FaceFusion** / LivePortrait for identity  
5. **VO**: TTS-Story or Qwen3-TTS from dialogue lines  
6. **Music**: ACE-Step API  
7. **Motion**: Wan2GP **or** Comfy Wan InfiniteTalk / animate pins on MRGPU  
8. **Body**: FreeMoCap capture → OpenPose maps → re-render pass  
9. **Stitch**: mok-tua run dir + ffmpeg  

## What to pull next (not installed / incomplete)

| Target | Why | Via |
|--------|-----|-----|
| StoryboardUI2 | Desktop angle grid + Comfy templates | git clone → SM or desktop |
| OminiControl Comfy node | FLUX object lock | custom_nodes + HF weights |
| Comfy.org Seedance / partner | Cloud board→video | partner keys / Comfy Cloud |
| More Wan InfiniteTalk models | Full lipsync on pool | `stage_manifest` + HF |
| Pinokio Update all T1–T3 | 0-day node/model scripts | Pinokio Update / `git pull` |

## Integration rule (keep robust)

- **mok-tua** owns shot ledger, QQQ, model stage, sides ingest, audit.  
- **Pinokio / SM** own install + GPU process lifecycle.  
- **Do not** re-implement Wan2GP/FaceFusion inside mok-tua — register them as **providers** with base_url + launch recipe (same pattern as Comfy/Grok).  
- Shared weights always under **`/Volumes/ai-data/models`** (stage CLI allowlist).  
- Johnny/CHIPPER catalog waves: index app versions + pins, never commit weights.

## CLI sketch for “pull + launch” registry (next build)

```bash
# planned shape (catalog-driven)
mok-tua launch directors_console   # pinokio start recipe
mok-tua launch wan2gp --host mrgpu
mok-tua launch sm_comfy --port 8188
mok-tua providers list             # from director_stack_catalog.json
```

Until that lands: Pinokio/SM GUI for process up, mok-tua CLI/API for story + stage + run.
