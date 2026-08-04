# mok-tua operations catch-up and two-day test plan

**Window:** 2026-08-04 preparation → 2026-08-05 release-candidate smoke

This plan reconciles the current Hippo handoffs, Pinokio staging records, UV
cache incident notes, Comfy roster, and the A.I.D.A. scan intake path.

## Current truth

The local provider catalog is path-complete but not live in this shell: the
doctor probe reported grade A, 22/44 checks, and `live 0/22`. That is a
readiness snapshot, not a failed install. The important runtime gates remain:

- mok-tua API and Comfy health;
- desk-host still worker;
- gpu-host Wan/I2V worker;
- one audio/TTS service with a stable output contract;
- receipt-backed submit, poll, collect, and resume.

The current default lock is `local_qwen_edit` for stills and `local_wan` for
video. Treat Wan as incomplete until a real low-VRAM job produces a receipt.
AnimateDiff remains fallback/placeholder territory. ACE-Step, TTS-Story,
Qwen3-TTS, Chatterbox, Whisper, FaceFusion, and FramePack are installed or
staged candidates, not automatically live adapters.

## Pinokio and UV path policy

The canonical gpu-host paths are:

```text
/mnt/ai-data/pinokio
/mnt/ai-data/pinokio/api
/mnt/ai-data/uv-cache/gpu-host
/mnt/ai-data/uv-cache/gpu-host/pip
/mnt/ai-data/hf-cache
/mnt/ai-data/models
```

The gpu-host SSH audit on 2026-08-04 found `redacted` UID/GID 1000 and effective
read/write/traverse access on Pinokio and both host-split UV cache roots. The
export is Tower NFSv4.2 with `sec=sys`; directory modes are setgid/shared-write
(2777). This does **not** prove every file is writable: UID-501 metadata and
dirty nested Git files can still block individual pulls.

The previous UV failure was not a directory permission problem. A malformed
cache object and a dangling host-specific symlink contaminated the shared
cache. Keep gpu-host and desk-host cache roots separate, use `UV_LINK_MODE=copy` on
NFS, quarantine only malformed entries, and never delete the entire cache.

If a Pinokio pull cannot write its shared cache, use a host-local temporary
download/build directory only for that operation, then promote verified wheels
or models into the canonical host-split cache. Do not put a virtualenv or
compiled `node_modules` on the shared NFS tree.

## Staged pull and model assurance matrix

| Lane | Preferred resource | Current posture | Assurance gate |
|---|---|---|---|
| Still/image | Stability Matrix Comfy on desk-host; Qwen edit graph | primary, path present | `/system_stats`, `/object_info`, one 512px local render + output hash |
| Video/I2V | gpu-host Comfy Wan pin or Wan2GP | staged; submit contract incomplete | low-VRAM 8–16 frame clip, poll/collect receipt, no cloud |
| Video fallback | AnimateDiff / FramePack | fallback/optional | only after explicit workflow export and smoke artifact |
| Music/audio | ACE-Step | installed/staged, adapter pending | short WAV/MP3, duration/sample-rate metadata, receipt |
| Voice | TTS-Story or Qwen3-TTS | installed/staged, contract audit pending | short synthetic line, normalized audio output, receipt |
| Speech ingest | Whisper WebUI | installed/staged | synthetic audio transcription with confidence and no raw sensitive logs |
| Face/body | FaceFusion / DreamTalk / FreeMoCap | optional post-video | synthetic identity or consented subject, explicit privacy class |

Do not pull every bleeding-edge candidate. The safe order is T0 orchestrators,
T1 video, T2 audio, then optional T3 face/body and T4 workflow pins. Before a
pull: fetch refs, inspect dirty state, confirm zero or reviewable upstream
delta, verify cache/model roots, and preserve local launcher changes.

## 2026-08-04 preparation

1. Confirm the gpu-host Pinokio and host-split UV paths with the bounded SSH
   probes; record UID/GID, modes, mount options, and free space.
2. Run `providers`, `doctor`, and path-only `smoke`; record unavailable services
   as `unknown` or `not live`, never as absent.
3. Verify Comfy node roster and model inventory against the Qwen still and Wan
   video workflow pins. Do not download multi-GB weights merely to make a
   catalog row green.
4. Repair or quarantine only the exact malformed UV entries if a pull reproduces
   the prior `Not a directory` error. Use a temporary host-local pull folder
   when cache writes are blocked, and retain the package hash.
5. Prepare three synthetic A.I.D.A. fixtures: receipt, important letter, and
   blank benefits/form page. Keep them clearly synthetic and out of Git history.

## 2026-08-05 smoke sequence

1. **T0:** mok-tua API, Headroom/LiteLLM, provider catalog, and CHAINS ledger.
2. **T1:** one small Qwen still through mok-tua → Comfy; capture packet,
   provider, workflow/model, output hash, and receipt.
3. **T1 video:** use that still for a short gpu-host I2V clip; require submit,
   status, collect, and resume evidence.
4. **T2 audio:** generate one short synthetic voice line or music bed; record
   normalized format and hash.
5. **T3 optional:** run face/body only if the T1/T2 receipts pass and the
   privacy class is explicit.
6. **Public examples:** package redacted images/video/audio plus manifests;
   never include PHI, real receipts, private paths, LAN identifiers, or keys.

## A.I.D.A. scan best practice

Use a private, operator-controlled drop folder. Stage JPG/JPEG/PNG/PDF files
without parsing, hash them, and retain originals. Normalize a copy only. Route
synthetic or explicitly authorized scans through A.I.D.A. PDF/form ingestion.
Record document class, source hash, parser/model/version, confidence, consent
class, review state, and a C.H.A.I.N.S. receipt ID.

Suggested classes include `receipt`, `bill`, `important_letter`,
`benefits_medicare`, `benefits_medicaid`, `treatment_documentation`,
`announcement`, and `other_reference`. For real caregiving material:

- keep raw scans and extracted text local;
- redact names, member IDs, addresses, dates of birth, barcodes, and account
  numbers before any cloud or GitHub use;
- never let unreviewed extraction drive a care or benefits decision;
- preserve confidence and “needs human review” for ambiguous fields;
- append corrections and deletion/retention decisions rather than overwriting
  the original evidence;
- export only synthetic fixtures and redacted manifests for public examples.

The existing `scripts/stage_scanned_document_drop.sh` is the safe first step.
The next implementation seam is an A.I.D.A. adapter that consumes its manifest
and writes only normalized outputs, context-catalog rows, and CHAINS receipts.

## Release gate

Mok-tua is ready for a release candidate when every advertised lane has either
one receipt-backed smoke artifact or an explicit `staged`, `optional`, or
`blocked` status with the reason recorded. “Installed” and “path present” are
not equivalent to “orchestrated and live.”

