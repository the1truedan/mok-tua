# Overnight runbook — storyboard → movie clips (2026-08-05)

**Goal:** Pinokio-staged providers + mok-tua orchestration produce stills, short I2V clips, and a combined preview for Arc 1 (April Fools), ready for social-staging drafts — **not** live posts.

**Affinity catalog:** `~/grokcode/data/catalog/pinokio_api_host_affinity_2026-08-05.json`  
**Sides:** `fixtures/la_dark_one_april_fools_sides.md`  
**Bible:** `/Volumes/ai-data/work/story-anim/bibles/LA_DARK_ONE_STORY_BIBLE_PUBLIC_SAFE.md`  
**Staging policy:** `config/pinokio_gpu-host_staging.json`

---

## Numbered steps (E0–E16)

| # | Action | Command / check | Receipt |
|---|--------|-----------------|--------|
| **E0** | Preflight | `ls` bible + sides + `work/story-anim`; NFS up | paths |
| **E1** | UV on gpu-host | Process env `UV_CACHE_DIR=/mnt/ai-data/uv-cache/gpu-host` | env log |
| **E2** | Remotes scrub | `cd ~/mok-tua && git remote -v` (no userinfo) | clean |
| **E3** | Affinity gate | Only P0/P1 `gpu-host_cuda` / either; SKIP `mac_metal` | catalog |
| **E4** | Dirty audit | Read staging JSON dirty flags; **no** force pull on dirty | note |
| **E5** | Pull clean only | FF-only clean trees; leave dirty Wan/TTS/etc. as-is | pull log |
| **E6** | Director's Console | HTTP 200 on :5173 :9800 :9820 (Linux runtime) | probe |
| **E7** | Comfy stills | Probe :8188; 1 smoke still | still path |
| **E8** | Wan I2V | 1× 2–4s from still | clip path |
| **E9** | Optional | Maestro/FramePack/FaceFusion only if gate green | skip ok |
| **E10** | Ingest sides | mok-tua stage Arc 1 fixture | run id |
| **E11** | 6 panels | Generate all storyboard stills | `panels/` |
| **E12** | Key clips | I2V on shots 2.1 + 2.3 (+ optional 1.1) | `clips/` |
| **E13** | Combine | ffmpeg concat per shot order | `combined_preview.mp4` |
| **E14** | Scorecard | Write overnight JSON under work/smoke + grokcode catalog | json |
| **E15** | Social inbox | Copy to `/Volumes/ai-data/work/social-staging/2026-08/` | list |
| **E16** | Handoff | Update SESSION_HANDOFF; **no auto-post** | md |

---

## Pull allowlist (tonight)

| Pri | App | Do |
|-----|-----|-----|
| P0 | UV + Pinokio daemon | verify |
| P0 | Sovereign Comfy | up + still |
| P0 | Wan2GP / wangpu-host / wan | up + 1 I2V (**no** dirty force-pull) |
| P0 | Directors Console | up if Linux runtime healthy |
| P1 | mok-tua | sides → stage → collect |
| P2 | TTS / ACE | only if clean + Linux sox |
| P3 | Maestro / FramePack / FaceFusion | defer unless clean |
| SKIP | macOS-use, phosphene, mlx-*, agentsviewMAC | Mac Pinokio only |

---

## Combine sketch

```bash
RUN=work/runs/<run_id>
# clips.txt lists clip paths in storyboard order
ffmpeg -y -f concat -safe 0 -i "$RUN/clips.txt" \
  -c:v libx264 -pix_fmt yuv420p "$RUN/combined_preview.mp4"
```

---

## Privacy

- Coach public-safe essence only (see bible)
- QQQ cloud upload **off**
- Human approve before Postiz / Linktree / Substack

---

## Live overnight path (2026-08-05 executed)

**SSH runbook:** `~/grokcode/docs/operations/SSH_gpu-host_OVERNIGHT_MOK_TUA_2026-08-05.md`

| Item | Path on gpu-host |
|------|----------------|
| Work root (Linux-owned NFS) | `/mnt/ai-data/work/smoke/mok-tua-overnight-2026-08-05` |
| Runner | `.../overnight_e0_e16_runner.sh` |
| Scorecard / AM report | `scorecard.json` · `AM_REPORT.md` |
| Mac mirror (read; Mac-created subtree may be 501-sticky) | `/Volumes/ai-data/work/smoke/mok-tua/overnight/2026-08-05` |

```bash
# status from desk-host
ssh -o BatchMode=yes gpu-host '
  R=/mnt/ai-data/work/smoke/mok-tua-overnight-2026-08-05
  ps -p $(cat $R/receipts/overnight.pid) -o pid,etime,cmd
  tail -40 $(ls -t $R/logs/overnight_*.log | head -1)
'
```

**UV:** always `UV_CACHE_DIR=/mnt/ai-data/uv-cache/gpu-host` on gpu-host.

---

## LiteLLM / gateway metrics (staging earmark)

Overnight probe writes `receipts/gateway_metrics.json` (Headroom `:8787`, LiteLLM `:4000`, Pinokio `:42000`).

**Implement next in mok-tua conductor (not overnight-blocking):**

1. JSONL per routed call: `ts`, `route`, `model`, `latency_ms`, `prompt_tokens`, `completion_tokens`, `status`, `request_id` (bodies redacted).
2. Wire Headroom → LiteLLM only; never PHI.
3. Scorecard field `providers.litellm_metrics` → path under `work/smoke`.
