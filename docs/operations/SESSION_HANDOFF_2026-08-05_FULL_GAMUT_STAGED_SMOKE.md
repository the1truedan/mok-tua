# Session handoff — mok-tua full gamut · staged pulls · smoke (2026-08-05)

**Branch:** `agent/mok-tua-staged-pulls-runbooks`  
**Visibility:** **PRIVATE** until human flip  
**Stamp:** `2026.08-mok-tua-full-gamut-staged-smoke`  
**Rule:** Cite paths + IDs. Do not NFS-deep-walk or re-run overnight without a new claim.

**Paste-first (new chat):**

```text
Continue from mok-tua docs/operations/SESSION_HANDOFF_2026-08-05_FULL_GAMUT_STAGED_SMOKE.md
Also: docs/operations/I2V_GROK_VS_gpu-host_CONTEXT_AMBIGUITY_INCIDENT_2026-08-05.md
      docs/roadmap/FULL_GAMUT_gpu-host_FRAMEWORK_2026-08-05.md
Control: ~/grokcode/docs/operations/AGENT_CONTEXT_PIT_AND_MULTI_CLI_CONTINUITY_2026-08-05.md
Hippo: HIPPO_CONTEXT_CITATIONS_ONLY=1 · tags agent-context, repeated-reminder, mok-tua
```

---

## 1. Done this arc

| Item | Status | Where |
|------|--------|--------|
| Staged pulls + lab runbooks (prior tip) | ✅ | branch history + remote catch-up commits |
| LAN / role scrub in configs | ✅ | `gpu-host` / `desk-host` / `control-host` |
| Protect-after-public runbook | ✅ | `docs/PUBLIC_RELEASE_PROTECT_BRANCH_2026-08-05.md` |
| Privacy rescan (remotes, secrets, PHI) | ✅ | gamut report §1 |
| Pinokio gamut HTTP + pterm | ✅ / honest skips | `docs/reports/PINOKIO_GAMUT_SMOKE_2026-08-05.md` |
| Full-gamut framework (Adobe back-burner) | ✅ | `docs/roadmap/FULL_GAMUT_gpu-host_FRAMEWORK_2026-08-05.md` |
| FramePack shared models map + launcher | ✅ | `scripts/run_framepack_shared_models.sh` · ops FRAMEPACK doc |
| Host uv venv + `--install-deps` batch | ✅ installed on gpu-host (torch cu128 path) | host: `~/pinokio-host-runtimes/framepack-linux-amd64` |
| I2V Grok vs gpu-host incident | ✅ documented | ops incident 2026-08-05 |
| **gpu-host local render** (stills + AnimateDiff) | ✅ GPU 100% ~48s | `docs/reports/gpu-host_LOCAL_RENDER_SMOKE_2026-08-05.md` |
| Hybrid Grok I2V demo | ✅ labeled QQQ1 / not GPU | `docs/DEMO_VIDEO_PROOF_2026-08-05.md` |
| Overnight E0–E16 comic path | ✅ complete w/ skips | overnight runbook + social handoff (control) |
| C64 conductor TUI smoke | ✅ | `mok_tua_cli.py tui --repl --skin c64` → READY. + help |
| Unit tests | ✅ 12 OK | `python3 -m unittest discover -s tests` |
| Public flip | ⏳ human only | earmark was 16:20 CDT; still private until go |

---

## 2. Smoke confirmation matrix

### 2.1 Conductor / C64 deck

| Check | Result |
|-------|--------|
| `python3 -m unittest discover -s tests` | **12 OK** |
| C64 REPL: help / READY. banner | **OK** (2026-08-05) |
| CLI verbs via TUI bridge | **OK** (doctor/providers/smoke/… documented) |

```bash
cd ~/mok-tua
python3 -m unittest discover -s tests -q
python3 scripts/mok_tua_cli.py tui --repl --skin c64   # H help · Q quit
# or: ./scripts/run_tui.sh --skin c64
```

### 2.2 Models / tools (tested or honest skip)

| Layer | Tool | Smoke | Notes |
|-------|------|-------|-------|
| Orchestration | mok-tua API/CLI/TUI | ✅ unit + C64 | |
| Stills | ComfyUI DreamShaper_8 | ✅ gpu-host | comic + local render |
| Video gen local | AnimateDiff `mm_sd_v15_v2` | ✅ gpu-host | peak util 100% |
| Video gen local | Wan Gradio :7861–7865 | ⏭ skip | ports down at probe |
| Video gen local | FramePack Studio | 🔧 deps + map | launch next; shared `hf_hub` |
| Face | FaceFusion :7870 | ✅ HTTP | CUDA/cublas residual |
| Face lock weights | IPAdapter / InstantID | ❌ empty | W0 |
| Director | UI :5173 · CPE :9800 | ✅ | orch :9820 404 |
| Maestro | :7860 | ✅ HTTP | |
| Pinokio control | desk :42000 | ✅ | pterm search gamut |
| Cloud I2V | Grok Imagine | ✅ hybrid only | **QQQ1** · not local proof |
| Music | ACE-Step / Suno MCP | earmark | W3 |
| Social | Postiz | earmark draft-only | no auto-post |

### 2.3 Staged pulls policy (remind)

- Clean pulls only; no Maestro force on dirty wrappers  
- Host-split UV cache: `/mnt/ai-data/uv-cache/gpu-host` · `UV_LINK_MODE=copy`  
- Affinity catalog (control): `data/catalog/pinokio_api_host_affinity_2026-08-05.json`  
- Hygiene script: `scripts/pinokio_pull_hygiene.sh`

### 2.4 FramePack next commands (gpu-host)

```bash
# from desk-host — role alias Host gpu-host / gpu-host
scp ~/mok-tua/scripts/run_framepack_shared_models.sh gpu-host:/tmp/
ssh gpu-host 'bash /tmp/run_framepack_shared_models.sh --install-deps'   # once / after reqs change
ssh gpu-host 'bash /tmp/run_framepack_shared_models.sh --offline --server 0.0.0.0 --port 7865'
# if hub missing snapshots once: FRAMEPACK_ALLOW_DOWNLOAD=1 (writes shared hf_hub only)
```

---

## 3. Open / next (TODO pointer)

See `TODO.md` in this repo. Priority operator picks:

1. FramePack UI launch smoke + short I2V receipt (shared models)  
2. W0 identity (IPAdapter/InstantID stage + FaceFusion CUDA)  
3. Wan I2V one-clip when ports/adapters live  
4. Human public flip + immediate `main` protection  
5. C64 QQQ/provider keys (earmark W3)  
6. Postiz draft + ACE-Step default music  

**Do not:** auto-flip public · auto-post social · PHI into this repo · Adobe Character Animator work.

---

## 4. Version / remotes

| Item | Value |
|------|--------|
| Product version this packet | **0.5.4** |
| GitHub | `github` → `the1truedan/mok-tua` (private) |
| Forgejo | optional private mirror (no userinfo) |
| Control ledger | `~/grokcode/data/progress/milestones.jsonl` |

---

## 5. Related docs (index only)

| Doc | Role |
|-----|------|
| `docs/roadmap/FULL_GAMUT_gpu-host_FRAMEWORK_2026-08-05.md` | Capability matrix + waves |
| `docs/operations/FRAMEPACK_SHARED_MODELS_2026-08-05.md` | Shared weights law |
| `docs/operations/I2V_GROK_VS_gpu-host_CONTEXT_AMBIGUITY_INCIDENT_2026-08-05.md` | Provenance incident |
| `docs/reports/gpu-host_LOCAL_RENDER_SMOKE_2026-08-05.md` | Local GPU proof |
| `docs/reports/PINOKIO_GAMUT_SMOKE_2026-08-05.md` | Mesh probes |
| `docs/DEMO_VIDEO_PROOF_2026-08-05.md` | Hybrid honesty |
| `docs/PUBLIC_RELEASE_PROTECT_BRANCH_2026-08-05.md` | Flip sequence |
| `docs/OVERNIGHT_STORYBOARD_TO_CLIP_RUNBOOK_2026-08-05.md` | E0–E16 |
| `docs/REPEATED_CONTEXT_BUNDLE.md` | Compact ops facts |
