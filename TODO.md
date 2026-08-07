# mok-tua TODO

**Last updated:** 2026-08-06  
**Version baseline:** **0.5.10** (PETSCII Matrix v4 · TUI launch workflow · show/play media; prior 0.5.7 transparency poster still cite)  
**Visibility:** private until human go · see `docs/PUBLIC_RELEASE_PROTECT_BRANCH_2026-08-05.md`  
**Handoff:** `HANDOFF.md` · smoke `docs/reports/SMOKE_TESTED_CAPABILITIES_2026-08-05.md`  
**Recheck:** `docs/operations/MODEL_PULL_RECHECK_VIDEO_ROBUST_2026-08-06.md`

---

## Done (2026-08-05 wave) ✅

| # | Item | Evidence |
|---|------|----------|
| D1 | Staged pulls + lab troubleshooting runbooks on branch | git tip + remote catch-up |
| D2 | LAN → role labels (`gpu-host` / …) in tracked configs | `config/*` scrub |
| D3 | Protect-after-public sequencing (free GH private cannot protect) | `docs/PUBLIC_RELEASE_PROTECT_BRANCH_…` |
| D4 | Pinokio gamut HTTP + pterm probes (honest skips) | `docs/reports/PINOKIO_GAMUT_SMOKE_…` |
| D5 | Full-gamut GPU framework (Adobe Character Animator **back-burner**) | `docs/roadmap/FULL_GAMUT_…` |
| D6 | FramePack shared models symlink + launcher + NFS write fallback | `scripts/run_framepack_shared_models.sh` |
| D7 | Host-local uv venv batch (`--install-deps`) for FramePack | host runtime; ops FRAMEPACK doc |
| D8 | I2V **Grok vs local GPU** provenance incident closed in process | `docs/operations/I2V_GROK_VS_GPU-host_…` |
| D9 | GPU-host Comfy stills + **AnimateDiff** generative smoke (GPU 100%) | `docs/reports/GPU-host_LOCAL_RENDER_…` |
| D10 | Hybrid Grok I2V demo labeled **not** local GPU | `docs/DEMO_VIDEO_PROOF_…` |
| D11 | C64 TUI REPL smoke (`--skin c64` → READY. / help) | unit 12 OK + REPL |
| D12 | Overnight E0–E16 storyboard→clip runbook + comic fixtures | overnight runbook · `fixtures/la_dark_one_…` |
| D13 | FramePack SM GUI `einops` miss — host SM 3.10 venv + package/venv symlink | `framepack-sm310-linux-amd64` · ops FRAMEPACK_SM_GUI… |
| D14 | FramePack launch recipe + port map pushed private | `api/providers.py` · orchestration `local_framepack` |
| D15 | Conductor TUI 0.5.5: PETSCII boot, two-pane, VIC-II stats, green/mono skins | `tui/` · INTERFACES |
| D16 | Artifact receipt sidecar + optional burn-caption | `api/artifact_receipt.py` · CLI `receipt` |
| D17 | CEO GPU-host storyboard + face polish + AD strip + accurate collage | 0.5.6 · smoke stamp |
| D18 | IPAdapter FaceID weights staged on shared pool (7 files) | `IPADAPTER_FACEID_INSTALL` · `stage_ipadapter_faceid.sh` |
| D19 | Wan 14B I2V weight inventory (no re-pull) | `WAN_WEIGHTS_STAGING` |
| D20 | Director HTTP path to models via Comfy documented | `DIRECTOR_MODELS_CONNECTIVITY` |
| D21 | Render scratch vs ai-data vs bees law | `RENDER_SCRATCH_VS_AI_DATA_BEES` |
| D22 | Hippo history + breakthrough milestones packet | `HIPPO_HISTORY_AND_BREAKTHROUGH_MILESTONES` |
| D23 | Session handoff 0.5.6 identity/FramePack private push | `SESSION_HANDOFF_…_0.5.6_IDENTITY_FRAMEPACK_PUSH` |
| D24 | 0.5.7 transparency poster + IPAdapter plus-face panels + IRL UIs | `products-capabilities.png` · `capabilities/` · stamp 0.5.7 |
| D25 | PETSCII boot glyph fix + inverse loader (CLI/Textual) | `tui/petscii.py` · themes · `ui-tui-boot.png` |

---

## Open — operator pick order

### P0 — unblock creative local video

| # | Item | Gate |
|---|------|------|
| **0a** | **Qwen Image Edit 2509 fp8** into pool (unlock multi-angle + next-scene LoRAs already present) | stage_manifest `qwen_edit_2509_fp8` · in flight 2026-08-06 |
| **0b** | Smoke `qwen_next_scene_angles` after Edit base lands | receipt + 2–3 angle stills |
| **0c** | Comfy ≥0.30 + **MiniMax H3** pruned pack (~42.5 G) | manifest `local_minimax_h3` · native nodes required |
| **0d** | Blade Runner title-card blink short (template scaffold done) | `docs/assets/styles/blade-runner-title/` |
| **1** | FramePack **finalize mp4** + receipt `artifact_ok: true` (`renderer: gpu_framepack_i2v`) | GPU sampling already observed · capture/promote from local SSD |
| **2** | If hub incomplete: one intentional `FRAMEPACK_ALLOW_DOWNLOAD=1` seed into **shared** hub only | never package-local HF tree |
| **3** | Wan 2.2 / Wan2GP **one-clip I2V** when ports/adapters live | honest skip until Wan ports up (not FramePack 7864) |
| **4** | W0 residual: complete InsightFace buffalo_l/antelope for true FaceID; InstantID; FaceFusion CUDA | plus-face path live · FaceID InsightFace residual |
| **4b** | Director: register Comfy backend in UI | `/api/backends` currently `[]` |

### P1 — conductor + social

| # | Item | Gate |
|---|------|------|
| **5** | ~~`local_framepack` provider~~ **wired** — close after live I2V | `orchestration.json` + `LAUNCH_RECIPES` + runtime registry |
| **6** | C64 deck earmark keys: QQQ cycle, video provider, face-ref, estimate burn | W3 framework · TUI shell ready |
| **7** | ACE-Step default local BGM path | QQQ0 |
| **8** | Postiz draft-only after render (no auto-post) | human OAuth later |
| **9** | Suno MCP **doc + QQQ1 only** (not default) | earmark |

### P2 — public

| # | Item | Gate |
|---|------|------|
| **9b** | **wait-what earmark** — plain-English pass on README / Release / PR bodies for **native English speakers, not AI aficionados** | [mattpocock/skills `wait-what`](https://github.com/mattpocock/skills/blob/main/skills/productivity/wait-what/SKILL.md) · doc `docs/roadmap/WAIT_WHAT_GITHUB_PLAIN_ENGLISH_EARMARK_2026-08-05.md` · install optional |
| **10** | Human: review packet → `gh repo edit … --visibility public` | **never agent-unattended** |
| **11** | Immediately enable `main` branch protection post-flip | free public allows it |
| **12** | Optional GH Release + attach **local-GPU** mp4 (prefer local proof over hybrid) | asset not git blob; body gets wait-what pass first |

### Explicit non-goals (this quarter unless reopened)

- Adobe Character Animator install / MCP  
- Auto-post to social  
- PHI / medical bodies in this repo  
- Recursive chmod of all ai-data  
- Claiming cloud I2V as “local GPU”

---

## Smoke re-run cheatsheet

```bash
cd ~/mok-tua
python3 -m unittest discover -s tests -q
python3 scripts/mok_tua_cli.py tui --repl --skin c64
# FramePack (gpu-host):
#   scp scripts/run_framepack_shared_models.sh gpu-host:/tmp/
#   ssh gpu-host 'bash /tmp/run_framepack_shared_models.sh --offline --server 0.0.0.0 --port 7864'
```

---

## Control-repo mirrors

| Artifact | Path |
|----------|------|
| Release plan (elevated) | `~/grokcode/docs/roadmap/MOK_TUA_PINOKIO_ORCHESTRATION_RELEASE_PLAN_2026-08-05.md` |
| Milestones ledger | `~/grokcode/data/progress/milestones.jsonl` |
| Full-gamut stamp JSON | `~/grokcode/data/catalog/mok_tua_full_gamut_framework_2026-08-05.json` |
| Public packet JSON | `~/grokcode/data/catalog/mok_tua_public_release_packet_2026-08-05.json` |
| Context pit | `~/grokcode/docs/operations/AGENT_CONTEXT_PIT_AND_MULTI_CLI_CONTINUITY_2026-08-05.md` |
