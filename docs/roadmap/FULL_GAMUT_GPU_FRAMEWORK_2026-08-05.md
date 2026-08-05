# Full-gamut gpu-host creative stack — mok-tua framework

**Date:** 2026-08-05  
**Status:** approved earmark framework (Adobe Character Animator **back-burner**)  
**Control stamp:** `2026.08-mok-tua-full-gamut-gpu-host-framework`

---

## 0. Principle

```text
C64 deck / CLI  →  mok-tua (shots, QQQ, estimates, receipts)
                      │
     ┌────────────────┼────────────────┬──────────────┐
     ▼                ▼                ▼              ▼
  SM Comfy        Pinokio apps     FramePack SM    optional cloud
  :8188           pterm lifecycle  shared models   QQQ1 only
     │                │                │              │
     └────────────────┴────────────────┴──────────────┘
                      ▼
            social-staging → Postiz draft (human post)
```

- **Shared weights:** `/mnt/ai-data/models` (Mac: `/Volumes/ai-data/models`)  
- **No re-download** of models already on the pool  
- **QQQ0 local default**; cloud I2V / Suno never auto  

**Adobe Character Animator:** back-burner. No install/MCP work. Optional later export doc only. Local puppet path = FreeMoCap + OpenPose + LivePortrait / Wan talking-head.

---

## 1. Shared models law (FramePack + SM + Comfy)

| Surface | Mapping |
|---------|---------|
| Stability Matrix | `ModelDirectoryOverride` = `/mnt/ai-data/models/` (already set on Linux SM Data) |
| ComfyUI gpu-host | `extra_model_paths.yaml` → `base_path: /mnt/ai-data/models/` |
| FramePack Studio | `hf_download` **symlink** → `/mnt/ai-data/models/hf_hub` |
| FramePack LoRAs | `.framepack/settings.json` → `/mnt/ai-data/models/loras` |
| FramePack outputs | `/mnt/ai-data/work/framepack/outputs` |
| Launch | `scripts/run_framepack_shared_models.sh` (prefer `--offline` when hub present) |

**Policy:**

1. First launch must **not** create a second copy under the package tree.  
2. Set `FRAMEPACK_ALLOW_DOWNLOAD=1` only when intentionally seeding the **shared** hub.  
3. `MaxConcurrentDownloads: 0` in SM settings reduces surprise multi-fetch.  
4. Receipts: `/mnt/ai-data/work/framepack/receipts/framepack_launch_*.json`  

---

## 2. Capability matrix (approved)

### T0 — Orchestration

| Tool | Role |
|------|------|
| mok-tua CLI/API/TUI (C64) | Shots, QQQ, providers, estimates |
| Director’s Console | Human cinema prompts / multi-node |
| Headroom + LiteLLM | Expand sides, captions, lyrics drafts |

### T1 — Video

| Tool | Role | Priority |
|------|------|----------|
| SM Comfy + Wan 2.2 fp8 | Narrative I2V | P0 |
| AnimateDiff + mm_sd_v15 | Short smoke / 2–4s | P0 (proven) |
| **FramePack Studio (SM)** | Longer keyframe / newsies | P0 map done · smoke next |
| Wan2GP / Maestro | Gradio all-in-one | P1 clean launch |
| InfiniteTalk / talking-avatar workflows | Lipsync character | P1 |
| LTX / SVD / Mochi | Fallbacks | P2 |

### T2 — Audio / music

| Tool | Role |
|------|------|
| ACE-Step | **Default local BGM** |
| TTS-Story / Qwen3-TTS / Chatterbox | VO |
| SongGeneration / SoulX-Singer | Local song-ish |
| **Suno MCP** (earmark QQQ1) | Cloud custom lyrics/style — TOS/key gated |

### T3 — Identity + body

| Tool | Role | Gap |
|------|------|-----|
| IPAdapter FaceID | Face lock stills | **Weights to stage** |
| InstantID | SDXL face lock | **Weights to stage** |
| FaceFusion | Post swap | **CUDA fix** (cublas) |
| DreamTalk / LivePortrait | Talking head | Wire providers |
| FreeMoCap + OpenPose CN | Body / pose pins | Smoke → ControlNet |
| AI4Animation | Animation research | P2 |

### Social

| Tool | Role |
|------|------|
| Postiz (`postiz-app` clone) | Draft after render — **no auto-post** |

---

## 3. Model recommendations (16GB 4060 Ti)

### Image

| Use | Prefer |
|-----|--------|
| Fast / AD | DreamShaper 8 (have) |
| Public quality + identity | RealVisXL / Juggernaut XL + InstantID (stage) |
| Multi-angle | Qwen Image Edit fp8 (partial) |

### Video (director ladder)

1. `local_animatediff` — smoke  
2. `local_wan` (Wan 2.2 I2V fp8 short) — narrative  
3. `local_framepack` — longer newsies  
4. `grok_imagine_video` — QQQ1 only  

### Music

1. ACE-Step (local $0)  
2. Suno MCP (QQQ1 earmark)  

---

## 4. Install waves (no big-bang)

| Wave | Focus |
|------|--------|
| **W0** | IPAdapter FaceID + InstantID weights; FaceFusion CUDA; Wan I2V 1-clip; FramePack shared launch smoke |
| **W1** | Wan2GP/Maestro clean; InfiniteTalk pin; `local_framepack` provider |
| **W2** | FreeMoCap → OpenPose → re-render (puppet without Adobe) |
| **W3** | ACE-Step REST default; Postiz draft; C64 QQQ ticks; estimate/cost receipts; Suno MCP doc only |
| **W4** | Public polish + human flip |

---

## 5. Suno MCP (earmark only)

Third-party options exist (e.g. AceDataCloud SunoMCP, unofficial suno-mcp servers). Treat as:

- QQQ1 + explicit confirm  
- Lyrics/style from Headroom/Grok agent → MCP generate → mp3 into run  
- **Never** default path for public README  

Local ACE-Step remains the release story.

---

## 6. C64 deck UX (earmark)

- Status: `QQQ0 LOCAL` / provider name  
- Keys: cycle QQQ, video provider, face-ref on/off, estimate burn, run  
- `POST` → stage Postiz draft only  

---

## 7. Viral 30s MANAGER newsies template

| t | Visual | Audio |
|---|--------|-------|
| 0–5s | Title + face lock | ACE-Step sting |
| 5–12s | mok-tua / M.A.N.A.G.E.R. desk | TTS VO |
| 12–22s | Module montage (Wan/FramePack) | Underscore |
| 22–28s | Ship / smoke green | Sting |
| 28–30s | CTA | Postiz draft caption |

---

## 8. Operator commands (FramePack shared)

```bash
# On gpu-host — shared models, offline if hub already seeded
bash ~/mok-tua/scripts/run_framepack_shared_models.sh --offline --server 0.0.0.0 --port 7865

# Intentional first seed into SHARED hub only (not package tree)
FRAMEPACK_ALLOW_DOWNLOAD=1 bash ~/mok-tua/scripts/run_framepack_shared_models.sh --server 0.0.0.0 --port 7865
```

Verify:

```bash
ls -la /mnt/ai-data/stability-matrix/Data/Packages/FramePack\ Studio/hf_download
# → .../hf_download -> /mnt/ai-data/models/hf_hub
```

---

## 9. Related

- `docs/PUBLIC_RELEASE_PROTECT_BRANCH_2026-08-05.md`  
- `docs/reports/gpu-host_LOCAL_RENDER_SMOKE_2026-08-05.md`  
- `config/pinokio_gpu-host_staging.json` (`framepack_studio.shared_models`)  
- `scripts/run_framepack_shared_models.sh`  
- Control-repo: `docs/roadmap/MOK_TUA_PINOKIO_ORCHESTRATION_RELEASE_PLAN_2026-08-05.md`  

---

*Adobe Character Animator is explicitly deferred. FramePack uses shared `/mnt/ai-data/models` with re-download prohibition via symlink + offline policy.*
