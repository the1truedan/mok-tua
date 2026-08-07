# Blade Runner title cards (Rands) — aesthetic lane

**Status:** template scaffold · parallel to C64/PETSCII brand shorts  
**Inspiration:** [Rands — Blade Runner Title Cards](https://randsinrepose.com/archives/blade-runner-title-cards/)  
**Does not replace:** C64 TUI / PETSCII Matrix export

## Law

| Rule | Detail |
|------|--------|
| Typography mood | ALL-CAPS · tight tracking · Goudy Oldstyle *feel* (web: Georgia / `Goudy Old Style` / serif fallback) |
| Layout | Centered block · generous black field · few words · emotional spacing |
| Motion path | Still → optional subtle push-in / grain (same simplicity as CEO **blink** smoke) |
| Honest labeling | Receipt must say renderer (HTML still · WAN · AnimateDiff · MiniMax H3) |
| Not FaceID demos | Title cards are **brand / module explainers**, not identity tests |

## Files

| Path | Role |
|------|------|
| `title-card.html` | Browser/static title card (edit `data-*` or query params) |
| `cards/*.html` | Preset module openers |
| `exports/` | Rendered PNG/MP4 smokes (git-friendly posters only; large mp4 optional) |

## Smoke recipe (parity with blink)

1. Open `title-card.html?line1=M.A.N.A.G.E.R.&line2=CONDUCTOR` → screenshot or headless Chrome PNG.  
2. Optional I2V: WAN Lightning or AnimateDiff — prompt  
   `static title card, subtle film grain, very slow push-in, no face morph, no text rewrite`.  
3. Optional H3 (after Comfy ≥0.30): same still as I2V + **explicit** VO line in prompt.  
4. Stamp receipt under `docs/assets/receipts/` with path + prompt + seed.

## Use cases

- Module function reels / viral shorts openers  
- PowerPoint-style explainers for M.A.N.A.G.E.R. surfaces  
- Social staging title beats (not medical content)

## Related

- PETSCII Matrix: `docs/assets/exports/README.md`  
- Control plan: grokcode `docs/operations/VIDEO_GEN_ROBUST_EXPANSION.md`  
- Grok recon pin: share `3ea6f4e3-65d6-47b3-bcb9-677c1347f24c`
