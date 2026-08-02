# mok-tua milestones

Dated product milestones for the storyboard/render conductor.  
Ledger also mirrored in `~/grokcode/data/progress/milestones.jsonl` (repo=`mok-tua`).

| Version | Date | Milestone ID | Achievement |
|---------|------|--------------|------------|
| **0.1.0** | 2026-07-27 | `2026.07-mok-tua-initial` | Carve-out from mock-tua; scaffold (story parse, stages, Comfy/Headroom, control API, fixtures). Forgejo + GitHub private. |
| **0.3.0** | 2026-08-01→02 | `2026.08-mok-tua-v0.3-tiers` | T0–T4 tier lock, smoke scorecard, MRGPU monitor, discover/audit/stage-app, ask_packet.v1, CHAINS receipts, ROBUST Comfy roster. |
| **0.4.0** | 2026-08-02 | (changelog) | Human-readable README, product map, concept art / vendor GUI frames, ASSETS + INTERFACES + OPERATORS docs. |
| **0.5.0** | 2026-08-02 | `2026.08-mok-tua-v0.5-conductor` | Conductor TUI (C64 + modern skins), CLI `tui` verb, Textual + stdlib REPL bridge over CLI verbs. |
| **0.5.1–0.5.2** | 2026-08-02 | (changelog) | Personal origin note; capability collage (image / I2V / director / voice / movement); Drive still differentiation. |
| **0.5.3** | 2026-08-02 | `2026.08-mok-tua-v0.5-conductor` | Presentation-smoke mockups (silly CEO still → COMDEX / board / cartoon booth / six-panel storyboard). |
| **ops** | 2026-08-01→02 | `2026.08-mok-tua-comfy-ai-data-wire` | Comfy + ai-data connectivity probe; MRGPU Comfy live; tier smoke **26 pass / 0 hard fail** (`mok_tua_tier_smoke_2026-08-02.json`). |

## Evidence (lab / grokcode catalog)

- `~/grokcode/data/catalog/comfy_mok_tua_probe_2026-08-01.{json,md}`
- `~/grokcode/data/catalog/comfy_mok_tua_smoke_result_2026-08-01.json`
- `~/grokcode/data/catalog/mok_tua_tier_smoke_2026-08-02.json`
- `~/grokcode/data/catalog/comfy_mrgpu_full_stack_2026-08-02.json`
- `~/grokcode/config/comfy_story_orchestration.json` (`mok_tua_sync` pointer)

## Policy (unchanged)

- Vendor GUIs stay as-is (ComfyUI, Director’s Console, LiteLLM Admin, Pinokio).
- mok-tua owns conductor surfaces: **API · CLI · TUI**.
- Private / medical content never auto-uploads; cloud is opt-in and gated.

## Remotes

| Remote | URL pattern |
|--------|-------------|
| Forgejo | `http://192.168.1.2:33333/the1truedan/mok-tua.git` |
| GitHub (private) | `https://github.com/the1truedan/mok-tua.git` |
