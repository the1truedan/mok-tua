# Changelog

All notable changes to **mok-tua** are documented here.  
Format inspired by [Keep a Changelog](https://keepachangelog.com/). Dates are local lab (America/New_York context).

## [0.5.2] — 2026-08-02

### Changed

- Capability collage regenerated for **differentiation + no crop**:
  - Image lane = complex **2-pass hiresfix** Comfy graph (not templates gallery).
  - Video lane = complex **Wan 2.2 I2V** graph with Drive **source still** inset.
  - Storyboard angle strip + movement identity use the same Drive still.
  - Full-page layout (`object-fit: contain`, stacked cards) so graphs are not clipped.
- Asset stage: `vendor/comfyui-complex-image-hiresfix.png`, `vendor/comfyui-complex-video-i2v-wan.png`, `vendor/drive-source-still-i2v.jpg`.

## [0.5.1] — 2026-08-02

### Changed

- README **personal origin** note: Pinokio + Stability Matrix on Mac/Linux, the “how does everything talk?” gap, Gateway Tech hardware museum nostalgia, C64 deck lineage with ai-gateway.
- **Capability collage** rewritten and annotated: C64 conductor strip on top; lanes for **image gen**, **video gen**, **director orchestration**, **voice gen**, **movement gen** using real Comfy / Director’s Console chrome where available (`docs/assets/mokups/capability-collage.html` → `products-capabilities.png`).

## [0.5.0] — 2026-08-02

### Added

- **Conductor TUI** under `tui/`:
  - Skins: **`c64`** (VIC-II blue, line-oriented READY. prompt) and **`modern`** (navy ops chrome).
  - **Textual** full-screen app when `textual` is installed (`tui/requirements.txt`).
  - **Stdlib REPL** fallback (`--repl` or auto if Textual missing).
  - **Bridge** (`tui/bridge.py`) spawns `scripts/mok_tua_cli.py` — no second business-logic path.
  - Entry points: `python -m tui`, `mok_tua_cli.py tui`, `./scripts/run_tui.sh`.
- CLI verb **`tui`** with `--skin` / `--repl`.
- Unit tests: `tests/test_tui_bridge.py`.
- Docs: `docs/INTERFACES.md` status → Live; README + OPERATORS TUI sections.

### Interface policy (unchanged, now implemented)

- Vendor GUIs (ComfyUI, Director’s Console, LiteLLM Admin, Pinokio) stay **as-is**.
- mok-tua owns conductor surfaces: **API · CLI · TUI**.
- C64 skin is a deliberate aesthetic option, not a reimplementation of Comfy’s node graph.

### Docs / assets (prior same-day work retained)

- Polished mok-ups: ComfyUI, Directors Console (official GitHub frames), LiteLLM routing, C64 mock.
- No lab dumps, LAN IPs, or home paths in public README art.

## [0.4.0] — 2026-08-02

### Changed

- Human-readable README (plain English product story, mermaid flow, product map).
- Replaced identifying live lab screenshots with concept art, then **vendor GUI + mok-ups**.
- Added `docs/ASSETS.md`, `docs/INTERFACES.md`, operator body split to `docs/OPERATORS.md`.

## [0.3.0] — 2026-08-02

### Added

- T0–T4 tier lock, smoke scorecard, gpu-host monitor, discover/audit/stage-app.
- ask_packet.v1 federation, CHAINS receipts, trusted node award.
- ROBUST Comfy roster / install scripts.

## [0.2.0] — 2026-08

### Added

- Providers catalog, sides ingest, multi-angle stills, CLI launch/pull, cloud dry-run providers.

## [0.1.0] — 2026-07-27

### Added

- Initial scaffold: story parse, stages, Comfy/Headroom, control API, fixtures.
