# Orchestration smoke (cited) — 2026-08-07

**Audience:** public operators · **Host role:** `gpu-host` (Comfy `:8188`)  
**Policy:** accuracy over montage · receipts under each PASS · never label cloud I2V as local GPU  
**Comfy pin this lab day:** **0.30.2** · torch 2.6.0+cu124 · prefer `--lowvram` on 16 GB class

This page is the **working orchestration loop** that was smoke-checked with receipts. Paths are **repo-relative** or role-based (`gpu-host`), not personal home directories.

---

## Conductor loop (exclusive GPU)

```text
1. probe-running   → nvidia-smi · forbidden PIDs (Frame-Pack / facefusion) · Comfy /queue
2. clean gate      → prefer used_mib ≤ 800 · hard abort ≥ 2048 (lab default)
3. free            → POST /free {unload_models, free_memory}
4. if residual     → process restart of Comfy (API free can stick after big loads)
5. run pin         → storyboard / AD / FaceID / video exclusive only
6. free again      → stamp receipt (api/artifact_receipt.py)
```

**Vocabulary:** use **`--probe-running`** for non-destructive progress (not typo variants).

Related public CMIP policy/schema (external):  
[the1truedan/cmip-terpene-db](https://github.com/the1truedan/cmip-terpene-db)

---

## Smoke matrix (2026-08-07 lab)

| Pin | Status | Evidence (in-repo) |
|-----|--------|--------------------|
| Unit tests | **PASS** | `python3 -m unittest discover -s tests -q` |
| Comfy reachability | **PASS** | `scripts/smoke_gpu.sh` / `COMFY_URL=http://gpu-host:8188` |
| CEO FaceID source still | **PASS** (identity seed) | [`docs/assets/pres-smoke/00-ceo-source-still.jpg`](../assets/pres-smoke/00-ceo-source-still.jpg) |
| CMIP origin 8-panel FaceID storyboard | **PASS** (generative local Comfy) | [`docs/assets/cmip-terpene-origin/`](../assets/cmip-terpene-origin/) · receipt [`cmip-terpene-origin-storyboard.receipt.json`](../assets/receipts/cmip-terpene-origin-storyboard.receipt.json) |
| FaceID stack (DreamShaper + faceid-plusv2 + clip_vision_h + buffalo_l) | **PASS** on regen | `scripts/regen_cmip_terpene_storyboard.py` · `scripts/regen_ceo_capability_assets.py` |
| AnimateDiff sizzle (prior same week) | **PASS** generative | [`docs/assets/exports/manager-pivot-motion-sizzle-animatediff.mp4`](../assets/exports/manager-pivot-motion-sizzle-animatediff.mp4) · prior motion summary stamps |
| CEO AnimateDiff FaceID loop | **PASS** (prior) | receipt [`ceo-animatediff.receipt.json`](../assets/receipts/ceo-animatediff.receipt.json) |
| MiniMax H3 loaders / nodes (Comfy ≥0.30) | **PARTIAL** | Weights + native nodes present; generic KSampler on NestedTensor still **graph-open** — not green generative day-0 |
| Qwen Image Edit full sample | **PAUSED** | 16 GB OOM class — weights ok, do not hammer KSampler |
| FireRed / Qwen Edit DC weights pool | **PRESENT** (pool) | promote receipts private lab; do not claim in-tree multi-GB weights |

Older capability poster matrix (0.5.7):  
[`docs/reports/SMOKE_TESTED_CAPABILITIES_2026-08-05.md`](../reports/SMOKE_TESTED_CAPABILITIES_2026-08-05.md)

---

## Operator re-run (public-safe)

```bash
# from mok-tua checkout
export COMFY_URL=http://gpu-host:8188   # or your LAN host:port

# unit smoke
python3 -m unittest discover -s tests -q

# free Comfy before exclusive FaceID / video
curl -s -X POST "$COMFY_URL/free" \
  -H 'Content-Type: application/json' \
  -d '{"unload_models":true,"free_memory":true}'

# CMIP origin storyboard (FaceID PLUS V2 · not Imagine)
PYTHONPATH=scripts:api:. python3 scripts/regen_cmip_terpene_storyboard.py

# classic CEO capability FaceID panels (optional)
python3 scripts/regen_ceo_capability_assets.py
```

**Do not:**

- Point Mac multi-GB HF writes at shared NFS as the download plane  
- Run Frame-Pack / facefusion concurrent with exclusive video / FaceID smokes  
- Claim Imagine/cloud stills as local GPU Comfy  
- Commit absolute home paths or LAN IPs into receipts (relative paths only)

---

## Orchestration map (conductor)

```text
script / story
  → mok-tua API/CLI (shots · QQQ · receipts)
  → Headroom (optional local LLM expand)
  → ComfyUI gpu-host (stills · FaceID · AnimateDiff · WAN when pinned)
  → Director’s Console (human control surface)
  → exports + docs/assets/receipts/*
```

Config staging (models intent, not multi-GB bodies): `config/stage_manifest.yaml`  
Smoke helpers: `scripts/smoke_gpu.sh` · `scripts/smoke_tiers.sh` · `scripts/smoke_comfy_robust.sh`

---

## Cross-links

| Doc | Role |
|-----|------|
| [HANDOFF.md](../../HANDOFF.md) | Session front door |
| [INTERFACES.md](../INTERFACES.md) | TUI / media / disks |
| [SESSION_HANDOFF_2026-08-06_0.5.10…](SESSION_HANDOFF_2026-08-06_0.5.10_PETSCII_LAUNCH_WORKFLOW.md) | 0.5.10 PETSCII launch |
| [cmip-terpene-db](https://github.com/the1truedan/cmip-terpene-db) | Schema-only chemistry public sister repo |
