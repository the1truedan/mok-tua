# Changelog

All notable changes to **mok-tua** are documented here.  
Format inspired by [Keep a Changelog](https://keepachangelog.com/). Dates are local lab (America/New_York context).

## [0.5.7] — 2026-08-05

### Added

- **Transparency capability poster** (`products-capabilities.png`): vertical stack of **individual**
  real cards with path + prompt/command under each photo (not faux multi-app promo).
- **IRL UI captures** under `docs/assets/capabilities/ui/`: PETSCII boot, two-pane deck, CLI REPL,
  ComfyUI, FramePack Gradio, Director’s Console.
- **Individual storyboard panels** `docs/assets/capabilities/panels/01–06-*.jpg` + per-panel receipts.
- Regen script: `scripts/regen_ceo_ipadapter_panels_0_5_7.py` (IPAdapter plus-face img2img on gpu-host).
- Smoke stamp: `docs/reports/capability_stamp_0.5.7.json`.

### Changed

- CEO storyboard + face polish re-rendered via **ip-adapter-plus-face_sd15** + img2img from
  `00-ceo-source-still.jpg` (forehead “ceo” preserved on polish).
- README capability section documents sausage-made captions and 0.5.7 tested set.
- Package TUI version **0.5.7**.

### Fixed (example retouches — no SemVer bump)

- **Hero player black-blade glitch:** `hero-prompt-to-product.jpg` right-hand player used a multi-frame
  AnimateDiff strip crop that showed a black triangle across the forehead. Recomposed with a **single
  clean FaceID closeup** (`capabilities/panels/03-closeup.jpg`); regen of
  `product-capabilities/product-capabilities-07-hero.jpg` + index. Compose law: never paste multi-frame
  AD strip into hero player.
- Face polish + AD strip earlier retouches (gentle denoise; black-triangle frame filter).
- Split `product-capabilities/product-capabilities-NN-*.jpg` cards (bandwidth) replace tall mega-PNG.

### Honest residuals

- FramePack mp4 `artifact_ok` finalize · Wan live ports · Director backends registry empty · InstantID.
- FaceID PLUS V2 is live (padded InsightFace ref); identity still stylized DreamShaper.

## [0.5.6] — 2026-08-05

### Added

- **Smoke-tested capability stamp** (`docs/reports/SMOKE_TESTED_CAPABILITIES_2026-08-05.md`, `capability_stamp_0.5.6.json`).
- **CEO-identity example assets (gpu-host Comfy):**
  - `example-storyboard-sheet.jpg` hybrid storyboard (prompt-locked wide + LoadImage CU)
  - `example-face-polish.jpg` img2img polish (BEFORE = `00-ceo-source-still`)
  - `ceo-i2v-frame-strip.jpg` from AnimateDiff short loop (GPU peak 100%; mp4 in `work/`)
- **Accurate `products-capabilities.png`** — still → conductor → stills/polish/loop (not Drive crop montage).
- Live TUI documentation stills: `mokup-c64-tui-live*.png` (PETSCII boot + two-pane).
- Receipts under `docs/assets/receipts/` + sidecars; regen helper `scripts/regen_ceo_capability_assets.py`.

### Changed

- Capability collage HTML rewritten for workflow accuracy and citation footers.
- README illustrative outputs point at CEO gpu-host examples (not generic instructor / stock polish).
- **PETSCII boot legibility:** fixed 5×5 glyph widths (M was 4/5/6 and shattered CLI alignment);
  inverse loader colors (light-blue paper + deep ink) in Textual themes + REPL ANSI;
  regen `mokup-c64-tui-live-boot.png`.

### Honest limits

- IPAdapter FaceID weights staged; InsightFace FaceID residual (see 0.5.7).
- Pres-smoke 01–04 still route-unknown mocks (unchanged).
- FramePack UI I2V mp4 finalize and Wan live ports remain pending / honest skip.

## [0.5.5] — 2026-08-05

### Added

- **Artifact receipts** (`api/artifact_receipt.py`, CLI `receipt show|stamp`): sidecar `.receipt.json` with renderer, model, host_role, prompt, wall_clock_s, tokens, gpu/cpu; optional `--burn-caption` via ffmpeg.
- **Conductor TUI 0.5.5:** PETSCII demoscene **MOK-TUA** loading splash → **two-pane** deck (left intro/log, right VIC-II stat bars).
- Skins: `c64` default (aliases `1980crt`, `tui-c64-mode-default-1980crt-tui`) · `green`/`matrix` · `mono`/`paper` · `modern`.
- TUI media verbs: `show` / `thumb` / `play` (in-pane stills + external mpv/timg/open).
- CLI `tui --prompt "…"` seeds left-pane launch intro.
- FramePack launch recipe wiring on private branch (port **7864**, shared models, runtime registry) — from prior dirty tree.

### Changed

- `docs/INTERFACES.md` documents split deck, provenance CLI, font/theme notes.
- Unit tests expanded (receipt + petscii/skin/media command resolve).

## [0.5.4] — 2026-08-05

### Added

- **Full-gamut gpu-host framework** (`docs/roadmap/FULL_GAMUT_gpu-host_FRAMEWORK_2026-08-05.md`): orchestration → video → audio → identity/body → social ladder; Adobe Character Animator explicitly **back-burner**; shared `/mnt/ai-data/models` law.
- **FramePack shared-models launcher** (`scripts/run_framepack_shared_models.sh`): `hf_download` → shared `hf_hub`, host-local uv venv, `--install-deps` batch, NFS write fallback, offline-by-default when hub present.
- **Ops docs:** FramePack shared models, I2V Grok-vs-gpu-host provenance **incident**, full-gamut session handoff, protect-after-public sequencing, overnight storyboard→clip runbook, demo dual-path proof.
- **Smoke reports:** Pinokio gamut HTTP/pterm matrix; gpu-host local Comfy stills + AnimateDiff generative video (GPU peak 100%).
- **TODO.md** open/closed operator board; LA Dark One April Fools sides fixture (public-safe).
- Pinokio staging config: `framepack_studio.shared_models` + role-label host addresses (`gpu-host`).

### Changed

- Tracked LAN addresses scrubbed to role labels in configs/docs where still private-prep.
- `.hippo/` gitignored; REPEATED_CONTEXT_BUNDLE + OPERATORS extended for staged pulls and provenance rules.
- C64 conductor TUI reconfirmed (`tui --skin c64` REPL READY. smoke).

### Incident / policy

- **Cloud Grok Imagine I2V must not be labeled as gpu-host local.** Hybrid demo kept as QQQ1 evidence; canonical local proof is AnimateDiff/Comfy receipt path. See `docs/operations/I2V_GROK_VS_gpu-host_CONTEXT_AMBIGUITY_INCIDENT_2026-08-05.md`.

### Not in this version

- Public visibility flip (human-gated).
- FramePack end-to-end I2V job receipt (deps/map ready; UI smoke next).
- Wan Gradio live ports (honest skip at probe).
- **wait-what** skill install — earmark only for plain-English GitHub posts ([mattpocock/skills](https://github.com/mattpocock/skills)); see `docs/roadmap/WAIT_WHAT_GITHUB_PLAIN_ENGLISH_EARMARK_2026-08-05.md`.

## [0.5.3] — 2026-08-02

### Added

- **Presentation smoke** set (`docs/assets/pres-smoke/`): source “ceo” still → COMDEX keynote mock, functions-board demo, cartoon NVIDIA-booth hangout, six-panel storyboard. Same face identity throughout; mock stills only (no full video). Wired into README as primary silly/disclosure examples.

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
