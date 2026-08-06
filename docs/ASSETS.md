# Visual assets

Folder: `docs/assets/`

## Policy

| Allowed | Forbidden in public README |
|---------|----------------------------|
| Official upstream screenshots (attributed) | Live lab `/healthz`, provider JSON dumps |
| Generic ComfyUI UI (no home paths) | LAN IPs, usernames, hostnames |
| Polished **mok-ups** (HTML → PNG) | Secrets, keys, Grafana login |
| Product hero / example stills | PHI or caregiver data |

## Vendor / proper GUI (mok-framed)

| File | Source |
|------|--------|
| `mokup-comfyui.png` | Live ComfyUI **template gallery** (generic UI) + navy frame |
| `mokup-directors-console.png` | Official [DirectorsConsole Images](https://github.com/NickPittas/DirectorsConsole/tree/main/Images) storyboard canvas |
| `mokup-directors-cpe.png` | Same repo — CPE film presets |
| `mokup-litellm-admin-sample.png` | Upstream LiteLLM Admin sample asset |
| `vendor/*` | Raw downloads / captures used to build frames |
| `vendor/comfyui-complex-image-hiresfix.png` | Official ComfyUI **2-pass hiresfix** image graph (distinct from video) |
| `vendor/comfyui-complex-video-i2v-wan.png` | Community **Wan 2.2 I2V** complex video graph |
| `vendor/drive-source-still-i2v.jpg` | Drive source still for storyboard + I2V examples (file id `1ylwLiKiYcFtHT-jhBBIfrOoc2mcQJ_il`) |

## mok-ups (code-built, not AI sketches)

| File | What |
|------|------|
| `mokup-litellm-routing.png` | Synthetic routing table in LiteLLM Admin style |
| `mokup-c64-tui.png` | C64 320×200 PETSCII-style conductor TUI concept |
| `mokups/*.html` | Sources for the above |

## Presentation smoke (`pres-smoke/`)

Silly **self-identity** chain: one Drive/source still → presentation mockups (not full video).

| File | What |
|------|------|
| `pres-smoke/00-ceo-source-still.jpg` | Starter still (“ceo” forehead) — prompt fodder / LoadImage |
| `pres-smoke/01-comdex-stage-keynote.jpg` | Full-body COMDEX-style keynote mock |
| `pres-smoke/02-functions-board-demo.jpg` | Points at mok-tua functions list |
| `pres-smoke/03-cartoon-nvidia-ceo-hangout.jpg` | Blatant cartoon buddy hangout (caricature) |
| `pres-smoke/04-comdex-storyboard-sheet.jpg` | Six-panel presentation storyboard |

Prefer these over generic generated faces when documenting “face locked through the pipeline.”

## Product art

| File | Use |
|------|-----|
| `hero-prompt-to-product.jpg` | README hero |
| `products-capabilities.png` | **0.5.7 transparency poster** — individual IRL cards + path/prompt under each (prefer this) |
| `products-capabilities.jpg` | JPEG twin of the above |
| `capabilities/ui/*` | IRL screenshots: TUI boot/deck, CLI, Comfy, FramePack, Director |
| `capabilities/panels/*` | Individual IPAdapter plus-face storyboard panels + receipts |
| `example-storyboard-sheet.jpg` | **MRGPU** CEO hybrid storyboard (replaces old instructor woman sheet) |
| `example-face-polish.jpg` | **MRGPU** CEO img2img polish (BEFORE = source still) |
| `ceo-i2v-frame-strip.jpg` | AnimateDiff frame strip from CEO short loop |
| `mokup-c64-tui-live*.png` | Real TUI boot/deck documentation stills (0.5.5+) |
| `receipts/*.receipt.json` | Provenance sidecars for regenerated assets |
| `08-product-map.png` | Product map |
| `concept-*.jpg` | Optional abstract metaphors (not substitutes for vendor UIs) |
| `mokups/capability-collage.html` | Source for annotated collage (Chrome headless → PNG) |

## Attribution

- **Director’s Console** screenshots © project authors — [NickPittas/DirectorsConsole](https://github.com/NickPittas/DirectorsConsole) (used for documentation of integration).  
- **ComfyUI** UI © Comfy-Org / contributors.  
- **LiteLLM** Admin sample © BerriAI / contributors.  
- mok-tua frames and routing/C64 mok-ups: this project.
