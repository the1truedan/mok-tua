# Session handoff — mok-tua **0.5.6** identity · FramePack · private GitHub push

**Date:** 2026-08-05 (lab close → 2026-08-06 UTC)  
**Repo:** `~/mok-tua` · dual remote **github** + **forgejo** (no userinfo in URLs)  
**Branch:** `agent/mok-tua-staged-pulls-runbooks` · private `main` @ **`da0696d`** (GitHub pushed)  
**Version:** **0.5.6** (CEO gpu-host examples + accurate collage; TUI **0.5.5**; full-gamut **0.5.4**)  
**Visibility:** **PRIVATE** — public flip **human-gated only**  
**Control mirror:** `~/grokcode/docs/operations/SESSION_HANDOFF_2026-08-05_MOK_TUA_0.5.6_PRIVATE_PUSH.md`

---

## 0. Paste into new chat

```text
Continue from ~/mok-tua/HANDOFF.md
→ docs/operations/SESSION_HANDOFF_2026-08-05_0.5.6_IDENTITY_FRAMEPACK_PUSH.md
→ docs/reports/SMOKE_TESTED_CAPABILITIES_2026-08-05.md
Hippo: HIPPO_CONTEXT_CITATIONS_ONLY=1 · tags agent-context, repeated-reminder, mok-tua
  mem_a90a6784d352 (0.5.4 gamut) · mem_3a6f16cb1fe7 (I2V law)
  mem_4d41b64adf49 (0.5.6 wave) · mem_3ba0c3707a4b (storage SSD/bees)
  control mem_efce82990a85

DONE this arc (private GH):
- 0.5.6 CEO gpu-host storyboard/face-polish/AD strip + accurate products-capabilities collage
- C64 TUI 0.5.5 PETSCII + two-pane + receipts API
- IPAdapter FaceID 7 weights on /mnt/ai-data/models/ipadapter · Comfy lists
- Wan 14B I2V tensors inventory on diffusion_models · no re-pull
- FramePack :7864 shared models · GPU sampling ~100% · status receipt (mp4 finalize open)
- Director HTTP OK · backends registry still empty (UI register)
- Storage law: hot scratch local SSD → promote finals to /ai-data; bees = settled only

PHI: never. Public flip: human only. Grok I2V ≠ gpu-host local.
```

---

## 1. Canonical start (product repo)

| Doc | Role |
|-----|------|
| [`HANDOFF.md`](../../HANDOFF.md) | Front door |
| [`TODO.md`](../../TODO.md) | Open/closed board |
| [`docs/reports/SMOKE_TESTED_CAPABILITIES_2026-08-05.md`](../reports/SMOKE_TESTED_CAPABILITIES_2026-08-05.md) | 0.5.6 smoke matrix |
| [`docs/operations/I2V_GROK_VS_gpu-host_CONTEXT_AMBIGUITY_INCIDENT_2026-08-05.md`](I2V_GROK_VS_gpu-host_CONTEXT_AMBIGUITY_INCIDENT_2026-08-05.md) | Provenance law |
| [`docs/operations/IPADAPTER_FACEID_INSTALL_2026-08-05.md`](IPADAPTER_FACEID_INSTALL_2026-08-05.md) | FaceID pool |
| [`docs/operations/FRAMEPACK_I2V_SMOKE_2026-08-05.md`](FRAMEPACK_I2V_SMOKE_2026-08-05.md) | FramePack I2V |
| [`docs/operations/WAN_WEIGHTS_STAGING_2026-08-05.md`](WAN_WEIGHTS_STAGING_2026-08-05.md) | Wan inventory |
| [`docs/operations/DIRECTOR_MODELS_CONNECTIVITY_2026-08-05.md`](DIRECTOR_MODELS_CONNECTIVITY_2026-08-05.md) | Director ↔ models |
| [`docs/operations/RENDER_SCRATCH_VS_AI_DATA_BEES_2026-08-05.md`](RENDER_SCRATCH_VS_AI_DATA_BEES_2026-08-05.md) | SSD vs NFS vs bees |
| [`docs/operations/HIPPO_HISTORY_AND_BREAKTHROUGH_MILESTONES_2026-08-05.md`](HIPPO_HISTORY_AND_BREAKTHROUGH_MILESTONES_2026-08-05.md) | Hippo chain + milestones |
| Control context pit | `~/grokcode/docs/operations/AGENT_CONTEXT_PIT_AND_MULTI_CLI_CONTINUITY_2026-08-05.md` |

---

## 2. What landed (breakthrough summary)

### Product / UX

| Item | Evidence |
|------|----------|
| Conductor TUI **0.5.5** | PETSCII boot · two-pane · VIC-II stats · skins c64/green/mono · live stills `mokup-c64-tui-live*.png` |
| Artifact receipts | `api/artifact_receipt.py` · CLI `receipt stamp` · `renderer` + `qqq` + `gpu_evidence` |
| CEO example assets **0.5.6** | storyboard + face polish + AD frame strip + accurate `products-capabilities.png` (not Drive montage) |
| Unit tests | `python3 -m unittest discover -s tests -q` → **20 OK** (smoke stamp) |

### Identity / models (gpu-host shared pool)

| Item | State | Path / note |
|------|-------|-------------|
| IPAdapter FaceID + plus-face SD1.5 | **INSTALLED** | `/mnt/ai-data/models/ipadapter/` · 7 files · Comfy lists · `scripts/stage_ipadapter_faceid.sh` |
| Wan 2.2 14B I2V fp8 pair | **INVENTORY OK** | `diffusion_models/wan2.2_i2v_*_14B_fp8*` · no bulk re-download |
| Wan Gradio ports | **HONEST SKIP** | not FramePack 7864 |
| Director stack HTTP | **PASS** | UI 5173 · CPE 9800 · orch 9820 |
| Director backends registry | **EMPTY** | register Comfy in UI — pool is fine via Comfy |
| InstantID / FaceFusion CUDA | residual | FaceFusion UI up; full CUDA polish still open |

### FramePack I2V

| Item | State |
|------|--------|
| Shared models launcher | `scripts/run_framepack_shared_models.sh` · registry `work/mok-tua/runtime/framepack_studio.json` |
| Port | **7864** (ACE-Step stays **7865**) |
| Hub FramePackI2V_HY | ~24G complete under `models/hf_hub` |
| HunyuanVideo hub | partial (VAE-centric) — may limit some paths |
| GPU proof | SSE: VAE → CLIP Vision → sampling · util **~100%** · VRAM **~11–13 GiB** |
| Receipt | `docs/assets/receipts/framepack_ceo_i2v.receipt.json` · `renderer: gpu-host_framepack_i2v` · **mp4 artifact finalize still open** (`artifact_ok: false` on status json path) |

### Provenance law (do not re-break)

- **Grok Imagine I2V ≠ gpu-host local.** Hybrid demos are QQQ1 cloud.  
- Every clip: `renderer` + `qqq` + `gpu_evidence`.  
- Canonical local video proof remains AnimateDiff report + FramePack local path when mp4 lands.

---

## 3. Storage policy (SSD · NFS · bees) — operator law

See full note: [`RENDER_SCRATCH_VS_AI_DATA_BEES_2026-08-05.md`](RENDER_SCRATCH_VS_AI_DATA_BEES_2026-08-05.md).

| Layer | Where | Why |
|-------|--------|-----|
| **Models / HF hub / finished publishable artifacts** | `/mnt/ai-data/...` (Mac: `/Volumes/ai-data/...`) | Shared pool · Comfy/FramePack read · bees-friendly **settled** data |
| **Hot render scratch / Gradio intermediates** | **Local SSD first** (e.g. `/tmp`, host `~/work/scratch`, SM package temp) then **promote** finals | Avoid NFS latency, uid mismatch, and bees thrash on rewrite-heavy temps |
| **bees** | Dedup **settled** trees only | Not for live scratch churn |

**Permissions reality:** Mac NFS clients often **uid 501**; Linux gpu-host **uid 1000**. Writing FramePack work trees from Mac→NFS can create trees the GPU process cannot rewrite. Prefer create/own on gpu-host or local SSD + promote.

---

## 4. Smoke matrix (do not re-greenwash)

| Check | Result |
|-------|--------|
| Unit tests | 20 OK |
| C64 TUI | PASS (live stills) |
| CEO storyboard / face polish / AD | PASS · GPU peak 100% |
| products-capabilities collage | PASS · accurate workflow |
| IPAdapter FaceID pool | PASS |
| Wan weights inventory | PASS · ports SKIP |
| Director → models via Comfy | PASS path · registry FAIL empty |
| FramePack UI I2V | **PARTIAL** — GPU sampling observed · final mp4 capture open |
| Public flip | pending human |

---

## 5. Next (operator pick)

1. **FramePack finalize** — capture mp4 under work tree · stamp receipt `artifact_ok: true` · optional auto-promote from local SSD.  
2. **Director** — register Comfy backend in UI (`/api/backends` non-empty).  
3. **W0 residual** — InstantID residual; FaceFusion CUDA polish.  
4. **Wan one-clip** when ports/adapters live (honest skip until then).  
5. **wait-what** plain-English pass on README/Release before flip.  
6. **Human** public flip + immediate `main` protection (free plan post-public only).

---

## 6. Remotes / push discipline

```text
github   https://github.com/the1truedan/mok-tua.git     PRIVATE
forgejo  <lab-forgejo>/the1truedan/mok-tua.git  # LAN URL local-only; not for public tree
```

- Push **private** branch/main only with operator intent.  
- **Never** `gh repo edit --visibility public` without explicit human go.  
- Do not commit secrets, PHI, LAN credentials, or bulk model binaries.

---

## 7. Hippo / control ledger IDs

| ID | Role |
|----|------|
| `mem_a90a6784d352` | 0.5.4 full-gamut packet |
| `mem_3a6f16cb1fe7` | I2V provenance law |
| `mem_4d41b64adf49` | 0.5.6 identity + FramePack + FaceID + Wan + Director |
| `mem_3ba0c3707a4b` | render scratch vs ai-data vs bees |
| Control `mem_efce82990a85` | grokcode 0.5.6 push index |
| Control `mem_1b3e1b9dc884` | earlier 0.5.4 control pointer |
| Milestone `2026.08-mok-tua-0.5.6-ceo-capability-smoke` | complete |
| Milestone `2026.08-mok-tua-ipadapter-faceid-pool` | complete |
| Milestone `2026.08-mok-tua-framepack-i2v-partial` | partial / in progress |
| Milestone `2026.08-mok-tua-render-scratch-vs-bees` | complete (policy) |

---

*End handoff. Prefer citations over re-walk of NFS or AgentsView year view.*
