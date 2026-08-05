# HANDOFF — mok-tua (latest)

**Date:** 2026-08-05  
**Version:** **0.5.4**  
**Branch:** `agent/mok-tua-staged-pulls-runbooks`  
**Visibility:** **PRIVATE** (human flip only)

## Start here

1. **Full packet:** [`docs/operations/SESSION_HANDOFF_2026-08-05_FULL_GAMUT_STAGED_SMOKE.md`](docs/operations/SESSION_HANDOFF_2026-08-05_FULL_GAMUT_STAGED_SMOKE.md)  
2. **TODO:** [`TODO.md`](TODO.md)  
3. **I2V provenance incident:** [`docs/operations/I2V_GROK_VS_MRGPU_CONTEXT_AMBIGUITY_INCIDENT_2026-08-05.md`](docs/operations/I2V_GROK_VS_MRGPU_CONTEXT_AMBIGUITY_INCIDENT_2026-08-05.md)  
4. **Framework:** [`docs/roadmap/FULL_GAMUT_MRGPU_FRAMEWORK_2026-08-05.md`](docs/roadmap/FULL_GAMUT_MRGPU_FRAMEWORK_2026-08-05.md)  
5. **Context pit (control):** `~/grokcode/docs/operations/AGENT_CONTEXT_PIT_AND_MULTI_CLI_CONTINUITY_2026-08-05.md`

## Smoke (last confirmed)

| Check | Result |
|-------|--------|
| Unit tests | 12 OK |
| C64 TUI REPL | READY. / help OK |
| MRGPU AnimateDiff | GPU peak 100% · report in `docs/reports/` |
| Pinokio gamut | HTTP matrix + honest Wan skip |
| FramePack | SM310 + recipe + registry · port **7864** · hub **seed downloading** · UI I2V after Gradio up |
| Public flip | pending human |

## FramePack dual lifecycle

| Start | Stop | LAN UI |
|-------|------|--------|
| `mok_tua_cli.py launch framepack_studio --live` | `stop framepack_studio` | `http://gpu-host:7864/` |
| `run_framepack_shared_models.sh --offline --server 0.0.0.0 --port 7864` | same stop / registry | same |
| SM Packages → Launch (after `--install-deps`) | SM stop only if SM owns PID | set server/port or open registry URL |

Registry: `/mnt/ai-data/work/mok-tua/runtime/framepack_studio.json`  
Ports: FramePack **7864** · ACE-Step **7865** · Maestro 7860 · FaceFusion 7870  
Docs: `FRAMEPACK_SHARED_MODELS` · `FRAMEPACK_SM_GUI_AND_ORCHESTRATION`

## Earmark — plain GitHub English

Before public flip / GH Release copy: **wait-what** from [mattpocock/skills](https://github.com/mattpocock/skills)  
→ re-pitch for **native English speakers, not AI aficionados**  
→ `docs/roadmap/WAIT_WHAT_GITHUB_PLAIN_ENGLISH_EARMARK_2026-08-05.md` (install optional; earmark only)

## Paste for new chat

```text
Continue from mok-tua HANDOFF.md → docs/operations/SESSION_HANDOFF_2026-08-05_FULL_GAMUT_STAGED_SMOKE.md
Grok I2V ≠ MRGPU local — see I2V_GROK_VS_MRGPU incident.
FramePack: SM venv fixed; launch/stop via mok-tua on :7864 LAN; UI I2V receipt next.
Next: short FramePack I2V + receipt; W0 identity; wait-what README pass; human public flip only.
```
