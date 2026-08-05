# mok-tua TODO

**Last updated:** 2026-08-05  
**Version baseline:** **0.5.4** (full-gamut staged smoke packet)  
**Visibility:** private until human go · see `docs/PUBLIC_RELEASE_PROTECT_BRANCH_2026-08-05.md`  
**Handoff:** `docs/operations/SESSION_HANDOFF_2026-08-05_FULL_GAMUT_STAGED_SMOKE.md`

---

## Done (2026-08-05 wave) ✅

| # | Item | Evidence |
|---|------|----------|
| D1 | Staged pulls + lab troubleshooting runbooks on branch | git tip + remote catch-up |
| D2 | LAN → role labels (`gpu-host` / …) in tracked configs | `config/*` scrub |
| D3 | Protect-after-public sequencing (free GH private cannot protect) | `docs/PUBLIC_RELEASE_PROTECT_BRANCH_…` |
| D4 | Pinokio gamut HTTP + pterm probes (honest skips) | `docs/reports/PINOKIO_GAMUT_SMOKE_…` |
| D5 | Full-gamut gpu-host framework (Adobe Character Animator **back-burner**) | `docs/roadmap/FULL_GAMUT_…` |
| D6 | FramePack shared models symlink + launcher + NFS write fallback | `scripts/run_framepack_shared_models.sh` |
| D7 | Host-local uv venv batch (`--install-deps`) for FramePack | host runtime; ops FRAMEPACK doc |
| D8 | I2V **Grok vs gpu-host** provenance incident closed in process | `docs/operations/I2V_GROK_VS_gpu-host_…` |
| D9 | gpu-host Comfy stills + **AnimateDiff** generative smoke (GPU 100%) | `docs/reports/gpu-host_LOCAL_RENDER_…` |
| D10 | Hybrid Grok I2V demo labeled **not** local GPU | `docs/DEMO_VIDEO_PROOF_…` |
| D11 | C64 TUI REPL smoke (`--skin c64` → READY. / help) | unit 12 OK + REPL |
| D12 | Overnight E0–E16 storyboard→clip runbook + comic fixtures | overnight runbook · `fixtures/la_dark_one_…` |
| D13 | FramePack SM GUI `einops` miss — host SM 3.10 venv + package/venv symlink | `framepack-sm310-linux-amd64` · ops FRAMEPACK_SM_GUI… |

---

## Open — operator pick order

### P0 — unblock creative local video

| # | Item | Gate |
|---|------|------|
| **1** | FramePack Studio **launch smoke** on gpu-host — SM GUI + CLI (`--offline`) + one short I2V → receipt | **einops/SM venv fixed** (sm310 host + package/venv symlink) · re-Launch Packages UI · shared `hf_hub` |
| **2** | If hub empty: one intentional `FRAMEPACK_ALLOW_DOWNLOAD=1` seed into **shared** hub only | never package-local HF tree |
| **3** | Wan 2.2 / Wan2GP **one-clip I2V** when ports/adapters live | honest skip until :786x up |
| **4** | W0 identity: stage **IPAdapter FaceID + InstantID** weights; FaceFusion CUDA residual | likeness ≠ prompt alone |

### P1 — conductor + social

| # | Item | Gate |
|---|------|------|
| **5** | `local_framepack` provider entry in mok-tua providers catalog | after launch smoke |
| **6** | C64 deck earmark keys: QQQ cycle, video provider, face-ref, estimate burn | W3 framework |
| **7** | ACE-Step default local BGM path | QQQ0 |
| **8** | Postiz draft-only after render (no auto-post) | human OAuth later |
| **9** | Suno MCP **doc + QQQ1 only** (not default) | earmark |

### P2 — public

| # | Item | Gate |
|---|------|------|
| **9b** | **wait-what earmark** — plain-English pass on README / Release / PR bodies for **native English speakers, not AI aficionados** | [mattpocock/skills `wait-what`](https://github.com/mattpocock/skills/blob/main/skills/productivity/wait-what/SKILL.md) · doc `docs/roadmap/WAIT_WHAT_GITHUB_PLAIN_ENGLISH_EARMARK_2026-08-05.md` · install optional |
| **10** | Human: review packet → `gh repo edit … --visibility public` | **never agent-unattended** |
| **11** | Immediately enable `main` branch protection post-flip | free public allows it |
| **12** | Optional GH Release + attach **gpu-host** mp4 (prefer local proof over hybrid) | asset not git blob; body gets wait-what pass first |

### Explicit non-goals (this quarter unless reopened)

- Adobe Character Animator install / MCP  
- Auto-post to social  
- PHI / medical bodies in this repo  
- Recursive chmod of all ai-data  
- Claiming cloud I2V as “gpu-host local”

---

## Smoke re-run cheatsheet

```bash
cd ~/mok-tua
python3 -m unittest discover -s tests -q
python3 scripts/mok_tua_cli.py tui --repl --skin c64
# FramePack (gpu-host):
#   scp scripts/run_framepack_shared_models.sh gpu-host:/tmp/
#   ssh gpu-host 'bash /tmp/run_framepack_shared_models.sh --offline --server 0.0.0.0 --port 7865'
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
