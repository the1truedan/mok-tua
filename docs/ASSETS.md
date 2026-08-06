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

## Pre-FaceID vs post-FaceID (cite labels)

| Label | Use when |
|-------|----------|
| **(pre-FaceID)** | Ken Burns comic zoompan, hybrid Grok I2V, prompt-lock-only storyboards, stock-hero art — **not** FaceID selfie lock |
| **(post-FaceID)** | FaceID PLUS V2 CEO panels / polish / AD strip / hero compose; brand PETSCII Matrix export (era packaging) |

Canonical table: [`docs/assets/exports/README.md`](assets/exports/README.md).

## Product art

| File | Era | Use |
|------|-----|-----|
| `hero-prompt-to-product.jpg` | **(post-FaceID)** | README hero — CEO FaceID storyboard wall + clean player |
| `product-capabilities/product-capabilities-NN-*.jpg` | **(post-FaceID)** | Split capability cards (preferred over tall mega-PNG) |
| `product-capabilities-index.jpg` | **(post-FaceID)** | Thumbnail index of split cards |
| `products-capabilities.png` / `.jpg` | **(post-FaceID)** packaging | Legacy path = small index only |
| `capabilities/ui/*` | either (UI chrome) | IRL screenshots: TUI / CLI / Comfy / FramePack / Director |
| `capabilities/panels/*` | **(post-FaceID)** | FaceID PLUS V2 storyboard panels |
| `example-storyboard-sheet.jpg` | **(post-FaceID)** | MRGPU FaceID 6-panel CEO storyboard |
| `example-face-polish.jpg` | **(post-FaceID)** | FaceID gentle polish (BEFORE = source still) |
| `ceo-i2v-frame-strip.jpg` | **(post-FaceID)** | AnimateDiff + FaceID strip (glitch-filtered) |
| `exports/mok-tua-petscii-matrix-export.mp4` | **(post-FaceID)** era · brand | Boot → µ rain → PETSCII MOK-TUA → rain-out (**not** a face demo) |
| `mokup-c64-tui-live*.png` | pre or post (UI) | Real TUI boot/deck stills |
| `receipts/*.receipt.json` | match asset era | Provenance sidecars |
| `08-product-map.png` | n/a | Product map |
| `concept-*.jpg` | **(pre-FaceID)** style | Abstract metaphors only |
| `mokups/capability-collage.html` | source | Collage HTML |

### (pre-FaceID) motion demos (staging — not git blobs)

| File | Cite as |
|------|---------|
| `manager_vibe_demo_local_kenburns.mp4` | **(pre-FaceID)** · ffmpeg Ken Burns |
| `manager_mrgpu_stills_kenburns_cpu_stitch.mp4` | **(pre-FaceID)** · CPU stitch |
| `manager_vibe_demo_hybrid_12s.mp4` | **(pre-FaceID)** · Grok I2V hybrid · ≠ MRGPU |

Staging roots under `/Volumes/ai-data/work/social-staging/2026-08/` — see `DEMO_VIDEO_PROOF_2026-08-05.md`.

## Attribution

- **Director’s Console** screenshots © project authors — [NickPittas/DirectorsConsole](https://github.com/NickPittas/DirectorsConsole) (used for documentation of integration).  
- **ComfyUI** UI © Comfy-Org / contributors.  
- **LiteLLM** Admin sample © BerriAI / contributors.  
- mok-tua frames and routing/C64 mok-ups: this project.
