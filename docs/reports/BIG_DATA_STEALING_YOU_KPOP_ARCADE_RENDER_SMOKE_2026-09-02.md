# Big Data Stealing You — K-pop arcade MV render smoke (2026-09-02)

Smoke-test render pass through `fixtures/big_data_stealing_you_kpop_arcade.md` (never
previously rendered — the fixture's own notes said "earmark only, operator drops WAV +
optional dance mp4 + dog still before queue"). Scope: 4 of 8 scripted shots, not the full
storyboard — one non-audio establishing shot through mok-tua's own pipeline, and three
beat-synced shots (the two keytar-dog inserts and the three-idol dance break) through the
one infrastructure this GPU has ever actually proven audio-conditioned LTX-2.3 video on.

**Not used this run:** the pose-swap/MimicMotion leg (operator's call — no dance-motion
reference clip or dog reference still exist yet on disk); the official ComfyUI-shipped
LTX-2.3 templates (need 31.21GB of models not installed here — a different, heavier model
set than what's actually staged).

---

## Clarification — two rendering legs, honestly separated

| Leg | Shots | Engine | Audio-conditioned? |
|---|---|---|---|
| **mok-tua-native** | `shot_01_01` (wide arcade establishing) | mok-tua's own `api.backends.comfy.ComfyClient` → gpu-host ComfyUI `:8188` | No — text-only, no audio-sync needed for a static establishing shot |
| **Maestro (external)** | `shot_03_01`, `shot_04_01`, `shot_05_01` (dog, dance break, dog) | Maestro's own REST API (`/api/v1/generate`), isolated gpu-host ComfyUI env `:8189`, `ltx2_22B_distilled_1_1` profile | **Yes** — real per-shot WAV `audio_guide`, `audio_prompt_type: "A"` |

mok-tua's own pipeline has no in-repo audio-conditioned LTX-2.3 workflow graph and no CLI
wiring for MimicMotion pose-swap (both confirmed by reading the actual code, not just docs).
The one real prior audio-conditioned proof (`director_pipeline_id 8d4238dd`, job `dba1d6f6`,
2026-08-15) went through this same external Maestro app — this run reproduces that path on
purpose, on a smaller slice, rather than inventing an unproven in-repo graph.

---

## Program stack

| Layer | Value |
|---|---|
| GPU host | mrgpu (RTX 4060 Ti 16GB, 64GB RAM) |
| mok-tua-native Comfy | `gpu-host:8188`, ComfyUI 0.29.0, `DreamShaper_8_pruned.safetensors` |
| Maestro engine | Maestro v1.9.1, isolated ComfyUI-adjacent env `:8189` (ComfyUI 0.31.0, torch cu130, `comfy-aimdo`/`comfy-kitchen` int8 kernels) |
| Maestro model | `ltx2_22B_distilled_1_1` — `ltx-2.3-22b-distilled-1.1_diffusion_model_quanto_bf16_int8.safetensors` (already staged in Maestro's own `app/ckpts/`, no download needed) |
| Access path | SSH tunnels from desk to gpu-host: `:8189` (isolated Comfy, started fresh — was not running), `:42005`→local `:17862` (Maestro's real live port; `:7860` is actually DreamTalk, not Maestro — the project's own `gpu_exclusive.py` allowlist entry for `maestro:7860` is stale), `:8188`→local `:8188` (so mok-tua's hardcoded `desk-host` endpoint resolves to the real gpu-host Comfy instead of a nonexistent local Mac install) |
| Job submission | Direct `curl -X POST http://127.0.0.1:17862/api/v1/generate` — field names (`audio_prompt_type`, `audio_guide`) taken from Maestro's own `services/director_pipeline.py` clip-rerun logic, the same code path behind the original 08-15 proof render |

---

## OOM clear (E1, before staging)

Before touching either GPU env, `nvidia-smi` on gpu-host showed only **2.9GB free of 16GB** —
two idle background apps unrelated to this task were holding the rest: **DramaBox-TTS**
(9.9GB, `launch_low_vram.py`) and **ace-step-ui** (2.7GB). Neither is in `gpu_exclusive.py`'s
stop-competitor allowlist (`framepack:7864`, `maestro:7860`, `facefusion:7870`) — that's a
real gap in the tool, not something it caught automatically. Confirmed with the user before
stopping either (SIGTERM, not kill -9); both are Pinokio-managed and restart from the Pinokio
UI. After: **1.5GB used / 14.9GB free**.

`mok-tua gpu-prep --live` was then run twice — once per Comfy env, since
`gpu_exclusive.COMFY_URLS` hardcodes `:8188` (needed `COMFY_URL=http://gpu-host:8188`
override) and again for `:8189`. `ready: true`, `14854 MiB` free before the first render.
The isolated `:8189` H3/LTX env itself wasn't running and had to be started fresh per the
documented operator recipe (`docs/reports/SMOKE_TESTED_CAPABILITIES_2026-08-15.md`).

**Anomaly, unresolved:** mid-OOM-clear, two background-task notifications arrived claiming
actions ("restore ace-step-ui", "launch DramaBox low-VRAM mode") that were never issued this
session. Ground truth was independently re-verified via direct SSH (both apps confirmed
stopped, VRAM healthy) and the claims were not acted on. Flagged to the user; source unknown.

---

## Wall-clock (per shot, real receipts)

| Shot | Engine | job_id | seed | active gen time | total job elapsed | requested video_length | actual video_length |
|---|---|---|---|---|---|---|---|
| `shot_01_01` (still only) | mok-tua-native | Comfy `prompt_id 7736daa6` | 1222170729 | 26.1s | — | — | 768×768 PNG |
| `shot_03_01` (dog hops keytar) | Maestro | `b9962bd3` | 166279455 | 151s | 152s | 150 frames | **129 frames (5.16s)** |
| `shot_04_01` (dance break) | Maestro | `ac670598` | 750365704 | 175s | 280s | 250 frames | **129 frames (5.16s)** |
| `shot_05_01` (dog insert) | Maestro | `c0dce62c` | 481200513 | 135s | 136s | 125 frames | **~121 frames (4.84s)** |

**Discrepancy, honestly reported:** requested `video_length` was not consistently honored —
delivered clips ran shorter than asked (5.16s / 5.16s / 4.84s vs 6s / 10s / 5s requested), all
converging near Maestro's own ~5s default. Root cause not diagnosed this pass (possibly an
internal clamp tied to `sliding_window_size` or the audio_guide's own length) — noted here
rather than silently treated as a match to the fixture's shot windows.

`shot_01_01`'s in-repo video leg (`local_animatediff`) stayed `pin_pending` — no API-format
workflow graph is exported for it yet in this repo (`workflows/animatediff_basic.api.json`
is a placeholder), confirmed by an actual run attempt, not just prior documentation.

---

## Prompts — verbatim, as actually sent (E3, `api/prompt_build.build_panel_prompt`)

**style_lock** (frontmatter, appended to every shot): *"anime cel restyle of the Suno cover:
vintage upright arcade cabinet, cyan waveform CRT + marquee, dusty workshop, wooden floor,
single coin; cool cyan on warm wood; film grain; not photoreal"*

**shot_01_01** (mok-tua-native still):
> Move the camera slightly forward from a medium-wide shot toward the subject. Wide shot of a
> dusty analog arcade workshop, vintage upright cabinet center, cyan waveform glowing on CRT
> and marquee, wooden floor, single coin in the foreground, anime cel, film grain, cool cyan
> on warm wood *[+ style_lock]*

**shot_03_01** (Maestro, audio-conditioned, 16–22s song window):
> Low-angle eye-level shot looking up at the subject. Slightly too-serious dog hops up with a
> keytar, paws on the keys, cyan CRT light on fur, anime cel, in time with the waveform
> *[+ style_lock]*
> negative_prompt (passed through to Maestro, unlike mok-tua's own pipeline which never wires
> this field): *"human hands, extra dogs, photoreal, horror"*

**shot_04_01** (Maestro, audio-conditioned, 22–32s song window — the core "dancing anime
girls in time with the beat" ask):
> locked wide, beat cut Three-wide K-pop dance break in front of the arcade cabinet, in time
> with the song, anime cel, cyan backlight, wooden floor, coin still visible *[+ style_lock]*

**shot_05_01** (Maestro, audio-conditioned, 32–37s song window):
> close insert Close-up of dog paws on keytar keys, cyan waveform on CRT behind, anime cel,
> motion in time with the audio *[+ style_lock]*

`character_refs`, `pose_source`, and the fixture's `audio.*`/`queue.*` frontmatter fields
remain pure operator documentation in mok-tua's own `story_parse.py`/`stages.py` — confirmed
unread by that code. Maestro's engine has no notion of them either; its only audio input is
the raw per-shot WAV passed as `audio_guide`.

---

## Outputs

| File | Role |
|---|---|
| `work/runs/20260902T214854Z-c29a45a2/shot_01_01_still.png` | Real Comfy still, DreamShaper_8, 768×768 |
| `work/runs/bds_kpop_arcade_smoke/shot_03_01.mp4` | Maestro, audio-conditioned, h264+AAC |
| `work/runs/bds_kpop_arcade_smoke/shot_04_01.mp4` | Maestro, audio-conditioned, h264+AAC |
| `work/runs/bds_kpop_arcade_smoke/shot_05_01.mp4` | Maestro, audio-conditioned, h264+AAC |
| `work/runs/bds_kpop_arcade_smoke/combined_preview.mp4` | `mok-tua curate assemble`, shot order 03→04→05, 15.2s, h264+AAC |
| `work/audio/big_data_stealing_you.wav` + 3 per-shot trimmed WAVs | Staged canonical audio + `audio_guide` sources |
| `work/chains/mok-tua-render.jsonl` | 5 new hash-linked events appended this run (verified intact, 32 total, tip `blake2b:c7d387a9…`) |

All four generative outputs confirmed via `ffprobe` — real video/audio streams, non-zero
duration, not placeholder files or success-only API responses.

---

## Honesty section — what's real mok-tua capability vs. what this run worked around

| Claim | Status |
|---|---|
| mok-tua's own fixture parser (`story_parse.py`) reads this exact schema | ✅ Real, unmodified |
| mok-tua's own Comfy stills path produces real GPU output | ✅ Real (`shot_01_01`), once `desk-host`'s hardcoded `127.0.0.1:8188` was tunneled to the real gpu-host Comfy — this repo assumes a local Mac ComfyUI (Metal) that doesn't exist on this machine |
| mok-tua's own `local_animatediff`/video leg | ❌ `pin_pending` — no API graph exported, confirmed by a real run attempt |
| mok-tua's own audio-conditioned LTX-2.3 path | ❌ Does not exist in this repo — the `ltx_fflf` pin is UI-format, non-audio, and orphaned from `video_providers` |
| Audio-conditioned generation happened | ✅ Real — `ffprobe`-confirmed AAC track on all 3 Maestro clips, `audio_guide` pointed at real per-shot WAV segments trimmed from the actual song |
| `negative_prompt`/`character_refs`/`pose_source` shape the render | Mixed — Maestro *does* accept `negative_prompt` (used for `shot_03_01`); mok-tua's own pipeline never reads any of these three fields |
| GPU exclusivity / OOM clear enforced automatically | Partial — `gpu-prep`'s Comfy-`/free` + VRAM-sample loop works, but its competitor-stop allowlist missed two real 12.6GB-holding apps; those were identified and stopped manually with the user's confirmation |
| `mok-tua chains`/`curate` ledger and assembly | ✅ Real — both exercised against real files this run, not synthetic fixtures |
| Pose-swap (`plan_pose_swap`/MimicMotion) | Skipped — implemented and workflow-ready in-repo, but no CLI wiring and no reference assets exist yet; operator's explicit call this pass |

---

## Smoke verdict

| Check | Result |
|---|---|
| GPU-host reachable, OOM-cleared before staging | ✅ |
| Real still via mok-tua's own Comfy client | ✅ |
| Real audio-conditioned video via the one proven engine (Maestro) | ✅ 3/3 shots |
| Output files confirmed on disk (not just success responses) | ✅ ffprobe-verified, video+audio streams |
| Requested duration honored | ⚠️ No — shorter than requested on all 3 Maestro shots, uninvestigated |
| Full 8-scene storyboard rendered | ❌ Out of scope this pass — 4 of 8 shots, smoke test only |
| Pose-swap / dance-motion fidelity | ❌ Not attempted — missing reference assets |

*Use this as the current honest capability baseline for "Big Data Stealing You" — a real,
receipted 4-shot slice, not a claim that the fixture's full 8-scene storyboard is production-ready.*
