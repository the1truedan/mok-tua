# Interfaces: GUI · TUI · API (and the C64 canvas)

## Short answer

| Ask | Answer |
|-----|--------|
| Can mok-tua use **vendor GUIs** as-is? | **Yes.** ComfyUI, Director’s Console, LiteLLM Admin, Pinokio — those *are* the established surfaces. mok-tua does not reskin them. |
| Can we show a **C64 320×200 + PETSCII-style** prompt TUI? | **Yes as a skin / mode** for the *conductor* (mok-tua CLI/TUI). Spec is mock-complete; implementation is a thin `textual`/`rich` (or curses) front-end over existing CLI commands. |
| Is that “within available tools”? | **Yes.** Catalog already lists GUI + TUI + API launch modes. `tui/` is empty today — CLI covers the same verbs. |

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

**Implementation path (available stack):**

1. Keep verbs in `scripts/mok_tua_cli.py` (`doctor`, `providers`, `run`, `smoke`, `lock`, …).  
2. Add `tui/` with **Textual** or **rich.live** full-screen app.  
3. Optional skin: CSS/theme that forces 40-column monospaced layout + C64 colors (or true 320×200 framebuffer for demos).  
4. Alternate modern TUI skin for day-to-day ops.

Mock: `docs/assets/mokup-c64-tui.png` · source `docs/assets/mokups/c64-tui.html`.

**Not in scope for C64 skin:** reimplementing Comfy’s node graph in PETSCII. That stays GUI.

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
| TUI (`tui/`) | Scaffold empty — mock + design in this doc |
| Vendor GUI ties | Live via providers + launch recipes |
| C64 TUI | Design + mock; implement as theme on Textual when ready |
