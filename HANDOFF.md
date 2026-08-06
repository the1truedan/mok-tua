# HANDOFF — mok-tua (latest)

**Date:** 2026-08-05  
**Version:** **0.5.6** (CEO MRGPU examples + accurate collage; TUI 0.5.5; full-gamut 0.5.4)  
**Branch:** `agent/mok-tua-staged-pulls-runbooks` → **main** (private)  
**Visibility:** **PRIVATE** (human flip only)

## Start here

1. **This wave packet:** [`docs/operations/SESSION_HANDOFF_2026-08-05_0.5.6_IDENTITY_FRAMEPACK_PUSH.md`](docs/operations/SESSION_HANDOFF_2026-08-05_0.5.6_IDENTITY_FRAMEPACK_PUSH.md)  
2. **Hippo + breakthroughs:** [`docs/operations/HIPPO_HISTORY_AND_BREAKTHROUGH_MILESTONES_2026-08-05.md`](docs/operations/HIPPO_HISTORY_AND_BREAKTHROUGH_MILESTONES_2026-08-05.md)  
3. **Storage law (SSD · NFS · bees):** [`docs/operations/RENDER_SCRATCH_VS_AI_DATA_BEES_2026-08-05.md`](docs/operations/RENDER_SCRATCH_VS_AI_DATA_BEES_2026-08-05.md)  
4. **TODO:** [`TODO.md`](TODO.md)  
5. **I2V provenance:** [`docs/operations/I2V_GROK_VS_MRGPU_CONTEXT_AMBIGUITY_INCIDENT_2026-08-05.md`](docs/operations/I2V_GROK_VS_MRGPU_CONTEXT_AMBIGUITY_INCIDENT_2026-08-05.md)  
6. **Smoke stamp 0.5.6:** [`docs/reports/SMOKE_TESTED_CAPABILITIES_2026-08-05.md`](docs/reports/SMOKE_TESTED_CAPABILITIES_2026-08-05.md)  
7. **Context pit (control):** `~/grokcode/docs/operations/AGENT_CONTEXT_PIT_AND_MULTI_CLI_CONTINUITY_2026-08-05.md`

## Smoke (last confirmed)

| Check | Result |
|-------|--------|
| Unit tests | 20 OK |
| C64 TUI | PETSCII boot · two-pane · VIC-II stats · skins c64/green/mono |
| CEO storyboard + face polish | MRGPU Comfy · receipts · GPU peak 100% on stills/AD |
| products-capabilities.png | Accurate still→conductor→loop collage (not Drive montage) |
| Smoke stamp 0.5.6 | `docs/reports/SMOKE_TESTED_CAPABILITIES_2026-08-05.md` |
| IPAdapter FaceID weights | `/mnt/ai-data/models/ipadapter/` · 7 files · Comfy lists them |
| Wan I2V weights | present on pool (`wan2.2_i2v_*_14B_fp8`) · staging doc |
| Director → models | pool OK via Comfy; **backends registry empty** (UI register) |
| FramePack I2V | UI live :7864 · GPU sampling observed · status receipt · **mp4 finalize open** |
| MRGPU AnimateDiff | GPU peak 100% · report in `docs/reports/` |
| Pinokio gamut | HTTP matrix + honest Wan skip |
| Storage hybrid | hot scratch **local SSD** → promote finals to `/ai-data`; bees = settled only |
| Public flip | pending human |

## FramePack dual lifecycle

| Start | Stop | LAN UI |
|-------|------|--------|
| `mok_tua_cli.py launch framepack_studio --live` | `stop framepack_studio` | `http://gpu-host:7864/` |
| `run_framepack_shared_models.sh --offline --server 0.0.0.0 --port 7864` | same stop / registry | same |
| SM Packages → Launch (after `--install-deps`) | SM stop only if SM owns PID | set server/port or open registry URL |

Registry: `/mnt/ai-data/work/mok-tua/runtime/framepack_studio.json`  
Ports: FramePack **7864** · ACE-Step **7865** · Maestro 7860 · FaceFusion 7870  
Docs: `FRAMEPACK_SHARED_MODELS` · `FRAMEPACK_SM_GUI_AND_ORCHESTRATION` · `FRAMEPACK_I2V_SMOKE`

## Earmark — plain GitHub English

Before public flip / GH Release copy: **wait-what** from [mattpocock/skills](https://github.com/mattpocock/skills)  
→ re-pitch for **native English speakers, not AI aficionados**  
→ `docs/roadmap/WAIT_WHAT_GITHUB_PLAIN_ENGLISH_EARMARK_2026-08-05.md` (install optional; earmark only)

## Paste for new chat

```text
Continue from mok-tua HANDOFF.md
→ docs/operations/SESSION_HANDOFF_2026-08-05_0.5.6_IDENTITY_FRAMEPACK_PUSH.md
→ docs/operations/HIPPO_HISTORY_AND_BREAKTHROUGH_MILESTONES_2026-08-05.md
0.5.6: CEO MRGPU assets + FaceID pool + Wan inventory + FramePack partial I2V on private GH.
Storage: local SSD scratch → promote to /ai-data; bees settled only; NFS uid 501 vs 1000.
Grok I2V ≠ MRGPU local. FramePack mp4 finalize next; Director register Comfy; human public flip only.
```
