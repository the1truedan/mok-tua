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

## mok-ups (code-built, not AI sketches)

| File | What |
|------|------|
| `mokup-litellm-routing.png` | Synthetic routing table in LiteLLM Admin style |
| `mokup-c64-tui.png` | C64 320×200 PETSCII-style conductor TUI concept |
| `mokups/*.html` | Sources for the above |

## Product art

| File | Use |
|------|-----|
| `hero-prompt-to-product.jpg` | README hero |
| `products-capabilities.png` | **Annotated** capability collage (C64 strip + 5 lanes) — prefer this |
| `products-capabilities.jpg` | JPEG twin of the above |
| `example-storyboard-sheet.jpg` | Example stills sheet |
| `example-face-polish.jpg` | Face polish look |
| `08-product-map.png` | Product map |
| `concept-*.jpg` | Optional abstract metaphors (not substitutes for vendor UIs) |
| `mokups/capability-collage.html` | Source for annotated collage (Chrome headless → PNG) |

## Attribution

- **Director’s Console** screenshots © project authors — [NickPittas/DirectorsConsole](https://github.com/NickPittas/DirectorsConsole) (used for documentation of integration).  
- **ComfyUI** UI © Comfy-Org / contributors.  
- **LiteLLM** Admin sample © BerriAI / contributors.  
- mok-tua frames and routing/C64 mok-ups: this project.
