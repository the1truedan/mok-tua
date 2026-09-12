# Lipsync/talking-avatar smoketest — earmark (2026-08-17)

**2026-09-12 update:** native **MiniMax H3 VocalLock_V3** on isolated ComfyUI is **PASS**
(verse batch, 5/5 scenes). That is a different mechanism from this earmark. See
[docs/reports/SMOKE_TESTED_CAPABILITIES_2026-09-12.md](../reports/SMOKE_TESTED_CAPABILITIES_2026-09-12.md).
This file still tracks the **dedicated-tool** row (DreamTalk / LivePortrait / FaceFusion /
`wan_infinitetalk`), which remains unproven.

**Trigger:** `/Volumes/ai-data/work/story-anim/bibles/LA_DARK_ONE_STORY_BIBLE_PUBLIC_SAFE.md`.
Earmark only — not a flip blocker, not scheduled yet. Run when an overnight staging window
opens (pattern: `docs/OVERNIGHT_STORYBOARD_TO_CLIP_RUNBOOK_2026-08-05.md`).

## Why this bible triggers it

LA Dark One is currently scoped as six-panel comic-strip beats (silhouette characters, no
real-person likenesses — see the bible's `ANTI_HALLUCINATION` block on Coach), so today's
Arc 1/2 panels don't strictly need talking-head lipsync. But the generation path the bible
itself declares —

```
this bible → sides MD → mok-tua shots → Comfy panels → Wan I2V key panels → collect/ffmpeg → social-staging
```

— already has a lipsync/talking-avatar step in the pipeline's own step catalog
(`config/director_stack_catalog.json` → `"S3b", "tool": "dreamtalk|wan_infinitetalk", "action":
"lipsync / talking avatar"`), sitting right after I2V/animate (S3) and before body-track
retarget (S3c). If any future arc adds narrator VO synced to an on-model mouth (as opposed to a
silent silhouette panel), that step needs to already be proven, not discovered mid-render.

## Current state — registered, never actually rendered

Per `docs/reports/SMOKE_TESTED_CAPABILITIES_2026-08-15.md` (Tested matrix + Pending/earmarked
sections), the lipsync-capable tools are **wired into the model registry but no render has
exercised them**:

| Tool | Where it's registered | Status |
|---|---|---|
| DreamTalk | `config/director_stack_catalog.json` id `dreamtalk`, Pinokio `pinokio/api/dreamtalk.git` | Installed/staged, not rendered |
| LivePortrait | `config/director_stack_catalog.json` id `liveportrait_models`, `models/liveportrait` | Installed/staged, not rendered |
| FaceFusion | `config/director_stack_catalog.json` + `config/tier_lock_T0-T4.json` id `facefusion` | Installed/staged, not rendered |
| wan_infinitetalk | Comfy workflow templates only (`workflow-wananimate22infinitetalkv1-*.json` etc, under `pull_targets_not_on_pool`) | Workflow templates present, model/pull state not confirmed |

The 08-15 report is explicit that the one real render proof to date (LTX-2.3's audio-conditioned
generation) is a **different mechanism** — native audio-conditioned video generation, not a
discrete lipsync pass applied on top of a silent render — and should not be conflated with these
four tools actually working.

## What the smoketest should prove

1. At least one dedicated lipsync tool (DreamTalk is the simplest single-image+audio-in
   candidate — start there) takes a still panel image + a short VO clip and produces a
   lip-synced clip, end to end, via the existing job-submission plumbing already proven for
   Director's Console (per the same 08-15 report, submission plumbing is real, just untested
   with this specific tool).
2. `wan_infinitetalk` — confirm whether its models are actually pulled (`pull_targets_not_on_pool`
   suggests they may not be) before attempting a render; this may be a pull step, not just a
   smoke step.
3. Feed into the existing `mok-tua smoke --tiers T0-T4` scorecard (`scripts/smoke_tiers.sh`) as
   a new row rather than a one-off — so future model/version bumps re-verify it automatically
   instead of silently rotting back to "registered, never rendered."

## Not in scope for this earmark

- FaceFusion/ReActor as pure face-swap/identity-reenact (S1b) — different step, already noted
  separately in `docs/COMFY_ROBUST_NODES.md` pack D, not a lipsync claim.
- Any actual LA Dark One render — the bible has no dialogue-audio arc drafted yet. This is
  capability staging, not content production.

## Companion docs

- `docs/reports/SMOKE_TESTED_CAPABILITIES_2026-08-15.md` — source of the "never rendered" finding.
- `docs/OVERNIGHT_STORYBOARD_TO_CLIP_RUNBOOK_2026-08-05.md` — overnight staging pattern to slot
  this into.
- `config/director_stack_catalog.json` — S3b step definition, tool IDs/paths.
- `config/tier_lock_T0-T4.json` — where a new lipsync smoke row would register.
