# mok-tua milestones

Dated product milestones for the storyboard/render conductor.  
Ledger also mirrored in `~/grokcode/data/progress/milestones.jsonl` (repo=`mok-tua`).

| Version | Date | Milestone ID | Achievement |
|---------|------|--------------|------------|
| **0.1.0** | 2026-07-27 | `2026.07-mok-tua-initial` | Carve-out from mock-tua; scaffold (story parse, stages, Comfy/Headroom, control API, fixtures). Forgejo + GitHub private. |
| **0.3.0** | 2026-08-01→02 | `2026.08-mok-tua-v0.3-tiers` | T0–T4 tier lock, smoke scorecard, GPU-host monitor, discover/audit/stage-app, ask_packet.v1, CHAINS receipts, ROBUST Comfy roster. |
| **0.4.0** | 2026-08-02 | (changelog) | Human-readable README, product map, concept art / vendor GUI frames, ASSETS + INTERFACES + OPERATORS docs. |
| **0.5.0** | 2026-08-02 | `2026.08-mok-tua-v0.5-conductor` | Conductor TUI (C64 + modern skins), CLI `tui` verb, Textual + stdlib REPL bridge over CLI verbs. |
| **0.5.1–0.5.2** | 2026-08-02 | (changelog) | Personal origin note; capability collage (image / I2V / director / voice / movement); Drive still differentiation. |
| **0.5.3** | 2026-08-02 | `2026.08-mok-tua-v0.5-conductor` | Presentation-smoke mockups (silly CEO still → COMDEX / board / cartoon booth / six-panel storyboard). |
| **0.5.4** | 2026-08-05 | `2026.08-mok-tua-full-gamut-staged-smoke` | Full-gamut framework; FramePack shared-models launcher; Pinokio gamut + GPU-host AnimateDiff smoke; Grok-vs-GPU-host I2V provenance incident; C64 TUI re-smoke; staged-pulls branch docs; public flip still human-gated. |
| **ops** | 2026-08-01→02 | `2026.08-mok-tua-comfy-ai-data-wire` | Comfy + ai-data connectivity probe; GPU-host Comfy live; tier smoke **26 pass / 0 hard fail** (`mok_tua_tier_smoke_2026-08-02.json`). |
| **ops** | 2026-08-05 | `2026.08-i2v-grok-vs-gpu-host-context-ambiguity` | Process incident: cloud Grok I2V misread as local GPU; dual-path labeling rules. |

## Evidence (lab / grokcode catalog)

- `~/grokcode/data/catalog/comfy_mok_tua_probe_2026-08-01.{json,md}`
- `~/grokcode/data/catalog/comfy_mok_tua_smoke_result_2026-08-01.json`
- `~/grokcode/data/catalog/mok_tua_tier_smoke_2026-08-02.json`
- `~/grokcode/data/catalog/comfy_gpu_full_stack_2026-08-02.json`
- `~/grokcode/data/catalog/mok_tua_full_gamut_framework_2026-08-05.json`
- `~/grokcode/data/catalog/mok_tua_public_release_packet_2026-08-05.json`
- `docs/reports/GPU_LOCAL_RENDER_SMOKE_2026-08-05.md` · `docs/reports/PINOKIO_GAMUT_SMOKE_2026-08-05.md`
- `~/grokcode/config/comfy_story_orchestration.json` (`mok_tua_sync` pointer)

## Policy (unchanged)

- Vendor GUIs stay as-is (ComfyUI, Director’s Console, LiteLLM Admin, Pinokio).
- mok-tua owns conductor surfaces: **API · CLI · TUI**.
- Private / medical content never auto-uploads; cloud is opt-in and gated.

## Remotes

| Remote | URL pattern |
|--------|-------------|
| Optional private mirror | operator-configured Forgejo/Gitea URL (no LAN in public docs) |
| GitHub | `https://github.com/the1truedan/mok-tua.git` |
