# Interfaces: GUI · TUI · API (and the C64 canvas)

## Short answer

| Ask | Answer |
|-----|--------|
| Can mok-tua use **vendor GUIs** as-is? | **Yes.** ComfyUI, Director’s Console, LiteLLM Admin, Pinokio — those *are* the established surfaces. mok-tua does not reskin them. |
| Can we show a **C64 320×200 + PETSCII-style** prompt TUI? | **Yes as a skin / mode** for the *conductor* (mok-tua CLI/TUI). Shipped: Textual full-screen (optional) + stdlib REPL fallback, both over CLI verbs. |
| Is that “within available tools”? | **Yes.** Catalog lists GUI + TUI + API. Run: `python3 scripts/mok_tua_cli.py tui --skin c64` or `./scripts/run_tui.sh`. |

## Three layers (do not conflate)

```text
┌─────────────────────────────────────────────────────────┐
│  GUI peers (vendor look — do not reinvent)              │
│  ComfyUI · Director's Console · LiteLLM Admin · Pinokio │
└──────────────────────────▲──────────────────────────────┘
                           │ HTTP / launch recipes
┌──────────────────────────┴──────────────────────────────┐
│  mok-tua conductor                                      │
│  API :8799  ·  CLI  ·  optional TUI (C64 or modern)     │
│  shots · QQQ · stage · smoke · lock · packets           │
└──────────────────────────▲──────────────────────────────┘
                           │ OpenAI-compatible
┌──────────────────────────┴──────────────────────────────┐
│  Headroom / LiteLLM  — model routing for S0 expand      │
└─────────────────────────────────────────────────────────┘
```

### GUI (established vendor UI)

| Tool | Expected interface | How mok-tua ties in |
|------|--------------------|---------------------|
| **ComfyUI** | Dark node graph + templates | `still_provider` / `video_provider` HTTP to `:8188` |
| **Director’s Console** | Storyboard canvas + CPE | Peer launch; camera language → shot fields |
| **LiteLLM Admin** | Models / router / keys / logs | S0 script expand via gateway (Headroom or LiteLLM) |
| **Pinokio** | Install / Start / Update | Process lifecycle for FaceFusion, Wan2GP, etc. |

Docs art: **official upstream screenshots** (or generic live UI with **no lab paths**) framed in a mok-tua navy chrome — not AI “sketch” stand-ins for those products.

### TUI (conductor — optional C64 mode)

**Native C64 constraints** (historical accuracy for the *canvas*):

| Spec | Value |
|------|--------|
| Resolution | **320 × 200** pixels |
| Text | 40 × 25 cells (PETSCII grid) |
| Palette | VIC-II 16 colors (classic blue `#40318D` + light blue text) |
| Input | Line-oriented prompt, not floating chat bubbles |

**Implementation (shipped v0.5.5 conductor):**

1. Verbs stay in `scripts/mok_tua_cli.py` (`doctor`, `providers`, `run`, `smoke`, `lock`, `receipt`, …).  
2. `tui/` is a thin front-end: `tui/bridge.py` spawns the CLI; no second business-logic path.  
3. **Launch workflow (v0.5.10):** CLI PETSCII loader → CLI args / disk menu print → `status`+`software` probes → Textual PETSCII splash → two-pane deck with help+status+media paths.  
4. **Left pane:** CLI argument menu · C64 disk directory · stack status · recent media paths · prompt recommendations (or `--prompt` seed) + RichLog.  
5. **Right pane:** system stats (gpu-host + desk) with **VIC-II style bars** (`████░`); refreshes after status/doctor/show/play.  
6. Skins (`.tcss`): **`c64`** default (aliases `1980crt`, `tui-c64-mode-default-1980crt-tui`) · **`green`** / `matrix` · **`mono`** / `paper` · **`modern`**.  
7. Media: `show PATH` (in-pane still / video thumb for **jpg/png/mp4**) · `play` / `open PATH` (external mpv/timg/open) · `media` lists recent exports.  
8. Full-screen via **Textual** when installed (`pip install -r tui/requirements.txt`); otherwise **stdlib REPL** (`--repl`).  
9. Entry points: `python -m tui`, `mok_tua_cli.py tui`, `./scripts/run_tui.sh`.  
10. Brand short: `docs/assets/exports/mok-tua-petscii-matrix-export.mp4` (loader→µ→CRT→tmux→disk menu).

| Command | Effect |
|---------|--------|
| `python3 scripts/mok_tua_cli.py tui` | PETSCII intro + CLI help + status → C64 deck |
| `… tui --no-intro` | Skip CLI preflight print (TUI still boots) |
| `… tui --no-status` | Skip status/software probes (offline-friendly) |
| `… tui --skin green` | Green phosphor on black |
| `… tui --skin mono` | White text on black |
| `… tui --skin modern` | Modern navy TUI |
| `… tui --prompt "…"` | Seed left intro with prompt text |
| `… tui --repl` | Line-oriented (no Textual) |
| In-TUI: `D` / `doctor` | CLI doctor (+ refresh stats) |
| In-TUI: `R` / `run [path]` | Dry-run story (default fixture) |
| In-TUI: `P` `S` `L` `T` `W` `M` `H` `Q` | providers · smoke · lock · status · software · media · help · quit |
| In-TUI: `menu` | C64 disk directory (args · prompts · caps) |
| In-TUI: `show` / `play` / `open` / `receipt stamp` | jpg/png/mp4 + provenance |

**C64 font note:** true PETSCII ROM font is a **terminal font** choice (Kitty/WezTerm/iTerm). The TUI ships block-element demoscene logos + VIC-II palette; it cannot force C64 ROM glyphs in every emulator.

Mock (docs art): `docs/assets/mokup-c64-tui.png` · source `docs/assets/mokups/c64-tui.html`.  
True **320×200 framebuffer** remains the screenshot canvas; the live TUI uses terminal cells with the same palette and prompt discipline.

### Software catalog (demoscene “game disks”) · v0.5.9

Each tool is a **disk**. Insert = path + port probe (no spawn). Launch = load screen + recipe.

| CLI | Effect |
|-----|--------|
| `software` | List catalog with RUNNING / DISK_READY / DISK_NOT_FOUND |
| `disk COMFYUI` | Insert-disk probe + banner for one title |
| `disk framepack --splash` | PETSCII load screen for that tool |
| `gpu-prep` | Dry-run free-VRAM plan |
| `gpu-prep --live` | Comfy `POST /free` unload models (allowlisted) |

Catalog source: `config/c64_software_catalog.json` (synced from director stack + launch recipes).  
Progress: uv-like bars via `api/progress.py` (Rich when installed).  
GPU law: one active renderer; free Comfy between segments; never kill unknown PIDs.

```bash
python3 scripts/mok_tua_cli.py software
python3 scripts/mok_tua_cli.py disk sm_comfy --splash
python3 scripts/mok_tua_cli.py gpu-prep --profile video --live
```

**Not in scope for C64 skin:** reimplementing Comfy’s node graph in PETSCII. That stays GUI.

### Provenance (screenshots / clips)

```bash
python3 scripts/mok_tua_cli.py receipt stamp PATH --renderer gpu_comfy_animatediff \
  --qqq QQQ0 --prompt "…" --model DreamShaper_8 --wall-clock-s 48
# optional burn-in caption bar:
python3 scripts/mok_tua_cli.py receipt stamp PATH --renderer … --burn-caption
python3 scripts/mok_tua_cli.py receipt show PATH
```

Sidecar: `<artifact>.receipt.json` (renderer, model, host_role, prompt, wall_clock_s, tokens, gpu/cpu).  
See I2V incident rules: every clip needs `renderer` + `qqq` + `gpu_evidence`.

### API

- `GET /healthz`, `GET /v1/info`, `GET /v1/providers`, `POST /v1/runs`, OpenAI tools bridge.  
- Always available; GUI and TUI are clients of the same conductor.

## Integration rule (robust)

- **mok-tua** owns shot ledger, privacy gates (QQQ), staging, audit.  
- **Vendors** own their look-and-feel and GPU process life.  
- Showcase vendor UIs with **their** chrome; showcase mok-tua TUI with **deliberate retro or modern** skins; never paste live health JSON or home paths into the public README.

## Status

| Surface | Status |
|---------|--------|
| API | Live |
| CLI | Live |
| TUI (`tui/`) | **Live** — Textual skins + stdlib REPL; bridge → CLI |
| Vendor GUI ties | Live via providers + launch recipes |
| C64 TUI | **Live skin** (`--skin c64`) + docs mock for true 320×200 art |
