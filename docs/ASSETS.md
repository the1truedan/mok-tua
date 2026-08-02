# Visual assets (screenshots & product art)

Folder: `docs/assets/`

## Live lab captures (integrated components)

| File | What it is | Why it matters |
|------|------------|----------------|
| `04-comfyui-queue.png` | ComfyUI open on the lab Mac | The “picture factory” that draws stills / video graphs |
| `05-directors-console.png` | Director’s Console UI | Human control surface peer to mok-tua |
| `06-grafana-bees.png` | Grafana **ai-data / bees** board | Shared model pool size, reclaim candidates, bees health |
| `07-card-health.png` | Styled `GET /healthz` | mok-tua API is up + Comfy peers report in |
| `07-card-info.png` | Styled `GET /v1/info` | Defaults, providers, locked still pipeline |
| `07-card-providers.png` | Styled `GET /v1/providers` | Menu of engines mok-tua can call |
| `07-card-doctor.png` | Styled `GET /v1/doctor` | Stack health scorecard |
| `01`–`03` | Raw browser views of the same JSON | Unstyled fallbacks |

## Product art (illustrative, not a single live render job)

| File | Use |
|------|-----|
| `hero-prompt-to-product.jpg` | README hero — panels → video metaphor |
| `products-capabilities.jpg` | Storyboard · face · music · motion collage |
| `example-storyboard-sheet.jpg` | Six-panel storyboard look |
| `example-face-polish.jpg` | Face-consistency / polish look |
| `08-product-map.png` | Exact-text product map (HTML → screenshot) |
| `product-map.html` | Source for the product map screenshot |

## Re-capture notes

```bash
# Live UIs (examples)
chromium --headless=new --screenshot=docs/assets/04-comfyui-queue.png \
  --window-size=1440,900 http://127.0.0.1:8188/

# Product map
chromium --headless=new --screenshot=docs/assets/08-product-map.png \
  --window-size=1400,1100 file://$PWD/docs/assets/product-map.html
```

Do not commit secrets, auth cookies, or PHI into assets.
