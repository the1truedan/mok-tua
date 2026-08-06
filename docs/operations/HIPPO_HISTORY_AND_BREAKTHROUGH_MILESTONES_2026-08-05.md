# Hippo history + breakthrough milestones — mok-tua private push (0.5.4 → 0.5.6)

**Date:** 2026-08-05  
**Repo:** `the1truedan/mok-tua` (PRIVATE)  
**Branch arc:** `agent/mok-tua-staged-pulls-runbooks` · private `main`  
**Control ledger:** `~/grokcode/data/progress/milestones.jsonl`

Use `HIPPO_CONTEXT_CITATIONS_ONLY=1` and cite IDs — do not dump full transcripts.

---

## 1. Hippo citation chain (product store `~/mok-tua/.hippo`)

| ID | Tags | Topic | Version |
|----|------|--------|---------|
| `mem_a90a6784d352` | agent-context, repeated-reminder, mok-tua | 0.5.4 full-gamut staged smoke · FramePack launcher · Pinokio gamut · AnimateDiff GPU100% · public flip human | 0.5.4 |
| `mem_3a6f16cb1fe7` | agent-context, repeated-reminder, mok-tua | I2V law: Grok Imagine ≠ MRGPU local · every clip needs renderer+qqq+gpu_evidence | 0.5.4+ |
| `mem_4d41b64adf49` | agent-context, repeated-reminder, mok-tua | 0.5.6 CEO MRGPU assets · FaceID pool · Wan inventory · FramePack partial I2V · Director path · handoff packet | 0.5.6 |
| `mem_3ba0c3707a4b` | agent-context, repeated-reminder, mok-tua | Render law: hot scratch local SSD; models/finals ai-data; bees settled only; uid 501 vs 1000 | policy |

### Control store (`~/grokcode/.hippo`) — index only

| ID | Topic |
|----|--------|
| `mem_efce82990a85` | Control index for 0.5.6 private push + breakthrough stamps B1–B9 |
| `mem_1b3e1b9dc884` | Earlier 0.5.4 control pointer (still valid; prefer `mem_efce82990a85` for 0.5.6) |
| `mem_b5e604c3478c` | Multi-CLI continuity / context pit |
| Compact packet | `docs/operations/SESSION_HANDOFF_2026-08-05_COMPACT_NEW_CHAT.md` |

### Promote rule (Headroom path)

Only memories tagged **`agent-context`** or **`repeated-reminder`** enter bounded prompt context. Pin + verified. No PHI, secrets, or raw chat dumps.

```sh
cd ~/mok-tua
hippo remember "…" --tag agent-context --tag repeated-reminder --tag mok-tua --pin --verified
```

---

## 2. Breakthrough milestones (narrative)

### B1 — Full-gamut staged smoke (**0.5.4**) — complete

- Framework + staged-pulls runbooks  
- FramePack **shared models** launcher + host uv deps  
- Pinokio gamut HTTP matrix with **honest Wan skip**  
- MRGPU Comfy still + **AnimateDiff** GPU peak **100%**  
- C64 TUI REPL smoke  
- **Stamp:** `2026.08-mok-tua-full-gamut-staged-smoke`  
- **Tip then:** `7949eac`

### B2 — I2V provenance incident closed — complete

- Hybrid “MANAGER vibe” path was **Grok Imagine I2V** (no CUDA)  
- Canonical local proof documented separately  
- **Stamp:** `2026.08-i2v-grok-vs-mrgpu-context-ambiguity`

### B3 — Conductor TUI demoscene + receipts (**0.5.5**) — complete

- PETSCII boot → two-pane deck · VIC-II stat bars · green/mono skins  
- `api/artifact_receipt.py` + CLI `receipt`  
- Live documentation stills for collage  
- **Commits:** `b579cf9` … `7c28521` lineage

### B4 — CEO MRGPU capability examples (**0.5.6**) — complete

- Regen from `00-ceo-source-still` (not woman/stock man)  
- Storyboard hybrid + face polish img2img + AD frame strip  
- Accurate `products-capabilities.png` workflow collage  
- Smoke stamp: `docs/reports/SMOKE_TESTED_CAPABILITIES_2026-08-05.md`  
- **Stamp:** `2026.08-mok-tua-0.5.6-ceo-capability-smoke`  
- **Tip then:** `7c28521` / `cbd20c8`

### B5 — Identity pool: IPAdapter FaceID — complete

- 7 weights ~569 MiB under `/mnt/ai-data/models/ipadapter/`  
- LoRA links · Comfy `IPAdapterModelLoader` lists without restart  
- Installer: `scripts/stage_ipadapter_faceid.sh`  
- **Stamp:** `2026.08-mok-tua-ipadapter-faceid-pool`

### B6 — Wan weights honesty — complete (inventory) / ports open

- 14B I2V fp8 pair + related tensors already on `diffusion_models/`  
- No multi-GB re-pull  
- Live Wan Gradio still **honest skip**  
- **Stamp:** `2026.08-mok-tua-wan-weights-inventory`

### B7 — FramePack UI I2V on MRGPU — **partial**

- Gradio **:7864** · shared hub FramePackI2V_HY **24G**  
- SSE stages + GPU ~100% during sampling  
- Status receipt stamped; **final mp4 `artifact_ok` still open**  
- **Stamp:** `2026.08-mok-tua-framepack-i2v-partial`

### B8 — Director ↔ `/ai-data/models` — path OK / registry open

- UI/CPE/orch healthy; models via Comfy `extra_model_paths`  
- `/api/backends` empty until UI register  
- **Stamp:** `2026.08-mok-tua-director-models-path-check`

### B9 — Render storage hybrid law — complete (policy)

- Local SSD scratch → promote finals to ai-data  
- bees for settled data only  
- NFS uid 501 vs 1000 documented  
- **Stamp:** `2026.08-mok-tua-render-scratch-vs-bees`

---

## 3. Machine ledger rows (control `milestones.jsonl`)

Append-only in `~/grokcode/data/progress/milestones.jsonl` (see control push). IDs:

| milestone_id | status | package |
|--------------|--------|---------|
| `2026.08-mok-tua-full-gamut-staged-smoke` | complete | 0.5.4 |
| `2026.08-i2v-grok-vs-mrgpu-context-ambiguity` | complete | 0.5.4 |
| `2026.08-mok-tua-0.5.6-ceo-capability-smoke` | complete | 0.5.6 |
| `2026.08-mok-tua-ipadapter-faceid-pool` | complete | 0.5.6 |
| `2026.08-mok-tua-wan-weights-inventory` | complete | 0.5.6 |
| `2026.08-mok-tua-framepack-i2v-partial` | in_progress | 0.5.6 |
| `2026.08-mok-tua-director-models-path-check` | complete | 0.5.6 |
| `2026.08-mok-tua-render-scratch-vs-bees` | complete | 0.5.6 |

Prior plan stamps remain: `2026.08-mok-tua-pinokio-orchestration-release-plan`, comic overnight planned rows.

---

## 4. Version timeline (private GitHub)

| Version | Date | One-line |
|---------|------|----------|
| 0.5.0–0.5.3 | 2026-08-02 | Conductor foundation / presentation smoke |
| **0.5.4** | 2026-08-05 | Full-gamut staged smoke · FramePack shared models · I2V law |
| **0.5.5** | 2026-08-05 | PETSCII TUI · receipts |
| **0.5.6** | 2026-08-05 | CEO MRGPU examples · accurate collage · FaceID/Wan/FramePack/Director ops stamps |

---

## 5. Explicit non-breakthroughs (keep honest)

- Public GitHub flip — **not done**  
- FramePack final CEO mp4 in git/work with `artifact_ok: true` — **open**  
- Wan live one-clip Gradio — **skip**  
- Director Comfy backend registered — **open**  
- InstantID residual / FaceFusion full CUDA polish — **open**  
- Adobe Character Animator — **back-burner**

---

*Cite this file + HANDOFF.md; do not re-walk `/Volumes/ai-data` for “context.”*
