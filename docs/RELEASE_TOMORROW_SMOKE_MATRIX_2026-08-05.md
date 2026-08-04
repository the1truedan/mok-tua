# mok-tua release-tomorrow smoke matrix

**Earmark:** release-candidate testing on 2026-08-05. This is a gate plan,
not a claim that every provider is live today.

## Common controls

Every live sample gets a run ID, input/output SHA-256, provider ID, host,
workflow/model version, QQQ decision, start/end timestamps, and a
C.H.A.I.N.S. receipt. Small public examples must be synthetic or consented;
PHI and private paths stay local.

## Ordered gates

| Gate | Test | Expected artifact | Pass condition |
|---|---|---|---|
| S0 | `doctor`, provider roster, Headroom/LiteLLM health | JSON status | all required local services explicit |
| S1 | sample Markdown/PDF sides parse | shot ledger | deterministic scenes/shots |
| S2 | one small local still | 512px PNG + receipt | submit/poll/collect and hash match |
| S3 | one short I2V/video clip on MRGPU | low-frame MP4 + receipt | provider adapter proves status and output |
| S4 | one short TTS/audio bed | WAV/MP3 + receipt | normalized audio metadata and hash |
| S5 | resume/retry with same run ID | ledger diff | idempotent and no duplicate publication |
| S6 | public example packaging | redacted manifest | no PHI/secrets/private paths |

## Routing proof for existing presentation images

The committed `docs/assets/pres-smoke/` images have a source-still narrative and
were added in commit `971fbd2`, but the available `work/chains/mok-tua-render.jsonl`
contains only one `ask_packet_emit` event and no artifact hash matching those
five JPEGs. Therefore their provider route cannot be proven from current logs.
They must be labeled **provenance unknown / presentation mockups**, not “mok-tua
generated,” until a matching receipt is found.

For tomorrow’s replacement examples, run the images through `mok_tua_cli.py`
with a fresh run ID and retain the packet, provider response, output hash, and
receipt beside the redacted asset.

## Creative lane sequence

1. local still (small graph, QQQ0);
2. still → short I2V on MRGPU;
3. same shot ledger → short voice/audio bed;
4. package a storyboard sheet plus receipts;
5. only then test optional cloud providers with explicit QQQ and public-safe
   input.

The local Wan/I2V and audio provider gates remain incomplete until their
submit/status/collect adapters produce these receipts.
