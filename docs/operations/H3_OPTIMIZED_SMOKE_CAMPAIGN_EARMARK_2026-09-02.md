# H3-optimized smoke campaign — earmark (2026-09-02)

**2026-09-12 update:** isolated ComfyUI **H3 VocalLock_V3** (not Maestro’s H3 picker) is
**PASS** — verse batch 5/5 scenes. Stamp:
[docs/reports/SMOKE_TESTED_CAPABILITIES_2026-09-12.md](../reports/SMOKE_TESTED_CAPABILITIES_2026-09-12.md).
The Maestro `compatible_model_paths` block on a differently-named Ref2VA file
([VIDEO_GEN_MODEL_INVENTORY_AUDIT_2026-09-02.md](../reports/VIDEO_GEN_MODEL_INVENTORY_AUDIT_2026-09-02.md))
still stands for the **Maestro Sol Engine** path. Do not treat that block as “H3 cannot
lip-sync.”

**Gated: do not run until the user's overnight `mrgpu` pull finishes.** No GPU/bandwidth
contention with that pull or the shared home connection. See
`docs/reports/VIDEO_GEN_MODEL_INVENTORY_AUDIT_2026-09-02.md` for the full inventory and this
session's already-completed tests (LTX-2.5 and MiniMax H3 ref2va were both attempted
same-session and are **not** in this list — they're blocked on real download-required weight
mismatches, documented there, not deferred here).

## Process (learned the hard way this session — follow this order)

1. **Check `GET /api/v1/models/{model_type}/debug` on Maestro first.** If a
   `compatible_model_paths` key is present, it's a hard allowlist — cross-check any staged
   shared-pool file against it *before* symlinking or downloading anything. If absent,
   compatibility can only be confirmed by an actual load attempt.
2. `mok-tua gpu-prep --live --stop-competitors --min-free-mib 12000` (both `:8188` and the
   candidate's actual serving port) before every job — same OOM-clear discipline as the render
   smoke test.
3. Submit via direct `curl -X POST http://<maestro>/api/v1/generate` (proven pattern — see the
   render smoke report for the exact tunnel/field-name setup), never via the GUI (its file
   pickers trigger native OS dialogs invisible to browser automation).
4. **Budget a hard timeout.** If a job sits at "Loading model" with zero VRAM/CPU/disk activity
   for more than ~2 minutes, treat it as broken and cancel via
   `POST /api/v1/cancel/{job_id}` — don't wait indefinitely (LTX-2.5 this session hung 13+ min
   before being cancelled).
5. Wire `image_start` + `image_prompt_type: "S"` in from the start for any narrative shot (not
   as an afterthought) — but use a **shot-appropriate** reference still, not a generic style
   image. Generate that still first via mok-tua's own still pipeline if one doesn't exist yet.

## Prioritized candidates (remaining, after LTX-2.5 and H3 ref2va were tried and blocked this session)

1. **HunyuanVideo 1.5** (staged, 8.3GB t2v distilled, `hunyuan_1_5_480_i2v.json` and 6 sibling
   profiles exist). `GET /api/v1/models/hunyuan_1_5_480_i2v/debug` was checked this
   session — **no `compatible_model_paths` key**, so compatibility can't be pre-verified the
   H3 way; budget the step-4 timeout when actually testing. Architecture differs from LTX/H3
   (`t2v_class`/`i2v_class` fields, no native audio) — genuinely new capability, not a variant
   of something already proven.
2. **Ovi** (Wan2.2 Ovi v1.1) — dual video+audio-native model, structurally different audio
   mechanism (separate `URLs2` audio-model weights + inline `<S>`/`<E>` speaker-tag prompting,
   not `audio_prompt_type`/`audio_guide`). `hunyuan`-style debug check also has no
   `compatible_model_paths` key — same caution applies. Needs a fresh HF download (both video
   and audio model halves) — highest download cost of this list.
3. **CogVideoX1.5 / Mochi** — both fully staged (29GB / 20-30GB) but **orphaned**: no Maestro
   `defaults/*.json` profile references either at all. Would need either a hand-written profile
   (risky, unproven — mirrors the LTX-2.5 hang risk, possibly worse with zero existing profile
   to crib from) or a different runner entirely (e.g. calling the `cogvideox1.5/` diffusers
   checkpoint directly via a `diffusers` Python script, bypassing Maestro). Lower priority
   until a concrete runner path exists.
4. **Kandinsky5 / LongCat** — no weights staged anywhere in either the shared pool or Maestro's
   own ckpts; these are fresh downloads with zero head start. Lowest priority — only worth
   pulling if 1–3 don't pan out or a specific need arises.

## Remote fallback (already proven reachable this session, real API — see audit doc §4)

If local candidates keep hitting the LTX-2.5/H3-ref2va pattern (staged-but-incompatible), the
three HF Spaces confirmed reachable this session (`MiniMaxAI/MiniMax-H3-Turbo-Lora`,
`Lightricks/LTX-2-3`, `zai-org/CogVideoX-5B-Space`) are a real, working alternative — but
`zai-org/CogVideoX-5B-Space` at least needs an authenticated HF token to clear the anonymous
ZeroGPU quota limit hit this session. That's an account/token decision for the user, not
something to resolve unilaterally.

## Not in scope for this earmark

- Any actual download or GPU job — this is a staging document only, per the gate above.
- CogVideoX/Mochi profile-writing — flagged as needing a design decision (custom Maestro
  profile vs. a separate diffusers-based runner), not started.
