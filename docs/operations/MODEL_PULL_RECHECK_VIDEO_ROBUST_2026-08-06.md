# Model pull recheck — video robust + dual-track (2026-08-06)

**Status:** Qwen Edit weights **present** · **sampling PAUSED on 16 GB** (OOM) · motion path → **WAN / AnimateDiff**  
**Host:** gpu-host Comfy **0.29.0** · pool `/Volumes/ai-data/models` (~2.2 TB free)  
**Upstream plan:** control-repo plan session · `VIDEO_GEN_ROBUST_EXPANSION.md`  
**Grok share (recon):** `3ea6f4e3-65d6-47b3-bcb9-677c1347f24c`  
**Staging law:** Track A = Comfy pool · Track B = LiteLLM/Ollama (do not mix H3 video with coding LLM pulls)

### Qwen Edit decision (2026-08-06)

| Item | Verdict |
|------|---------|
| Pool stage | **PASS** — `local_qwen_edit` 6/6 |
| KSampler on RTX 4060 Ti 16 GB | **OOM** (256–768², ±ref, ±Lightning, `--lowvram`) |
| Day-0 storyboard sampling | **PAUSED** — do not hammer |
| Resume when | Larger VRAM, better quant, or proven low-VRAM Comfy pack |
| Motion sizzle instead | **AnimateDiff** / **WAN 2.2** (owned weights) + `gpu-prep` |

---

## 1. Present / missing (bounded probe)

| Asset | Status |
|-------|--------|
| WAN 2.2 I2V/T2V 14B fp8 dual-noise | **present** — default ship path |
| WAN 2.2 ti2v 5B | **present** |
| Qwen Image gen fp8 | **present** (~19 G) |
| Qwen Image **Edit** 2509 fp8 | **PRESENT** (~**20 GB**) — host-local mrgpu download+promote 2026-08-06 · `local_qwen_edit` inventory **6/6** |
| Multi-angles + next-scene + Lightning LoRAs | **present** |
| MiniMax H3 pruned pack | **missing** — needs Comfy ≥0.30 + ~42.5 G |
| ID-V2V | **earmark only** (multi-GPU research) |

## 2. Stage queue

| Pri | Action | Disk | Gate |
|-----|--------|-----:|------|
| P0 | Qwen Edit 2509 via `stage_manifest` `qwen_edit_2509_fp8` | ~20 G | unlock angles/next-scene |
| P0 | CrisperWhisper (Track B, separate) | small | voice → agent |
| P1 | Comfy ≥0.30 + MiniMax H3 pruned | ~42.5 G | native nodes in object_info |
| P2 | Inkling / DeepSeek-V4-Flash | 100–180 G+ | **high-RAM host only** — not mrgpu 16 G day-0 |
| P3 | ID-V2V | app-local | research |

### CLI

```bash
cd ~/mok-tua
export PYTHONPATH=api
# inventory
python3 -c "from stage_models import stage_models; import json; print(json.dumps(stage_models(dry_run=True, required_for='local_qwen_edit'), indent=2))"
# live Edit base only
python3 -c "from stage_models import stage_models; import json; print(json.dumps(stage_models(dry_run=False, only_ids=['qwen_edit_2509_fp8']), indent=2))"
# after Comfy >=0.30 — H3 pack (do not run on 0.29 expecting native nodes)
python3 -c "from stage_models import stage_models; import json; print(json.dumps(stage_models(dry_run=False, required_for='local_minimax_h3'), indent=2))"
```

## 3. Naming clarity

| Name | Role |
|------|------|
| **MiniMax H3** | Video + native stereo **omni** (Comfy) — **not** a coding LLM |
| **Inkling-Small / DeepSeek-V4-Flash** | Agentic LLMs — Track B; oversized for single 4060 Ti without huge system RAM |
| **Practical mrgpu coding today** | Ollama tags already present (`qwen3-coder:30b`, `qwen2.5-coder:14b`, …) via LiteLLM |

## 4. Aesthetic lanes

| Lane | Location |
|------|----------|
| C64 / PETSCII | `tui/themes/c64.tcss` · `docs/assets/exports/` |
| Blade Runner title cards (Rands) | `docs/assets/styles/blade-runner-title/` |

## 5. Public flip (disclosure)

mok-tua tracked-tree recheck 2026-08-06: remotes clean of userinfo · **0** RFC1918 · **0** `/Users/` in tracked files.  
**Human go still required.** See `docs/PUBLIC_RELEASE_PROTECT_BRANCH_2026-08-05.md`.  
Do not block flip on H3 weights.

## 6. Non-goals

- Auto public flip  
- NFS unbounded find  
- ID-V2V production claims on 16 GB  
- PHI through cloud video APIs  
