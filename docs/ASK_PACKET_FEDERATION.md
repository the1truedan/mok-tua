# Ask-packet federation (Johnny + CHIPPER + CHAINS × mok-tua)

**Status:** Phase A schemas + Phase B lab award (dry-run). **Not** a public GPU marketplace.

## Why

mok-tua is the **demand** broker (estimate, QQQ, resume). Johnny/CHIPPER supply the **BOM** (what models/workflows). CHAINS supplies **settlement provenance** (who accepted what). The missing piece is a thin **award** over **node advertisements** keyed by `tier_lock` residency.

## Three faces

| Layer | Question | Artifact |
|-------|----------|----------|
| Johnny / CHIPPER | *What* | Content-addressed requires[] — inventory ids / digests, never weight blobs |
| mok-tua pricing + tier_lock | *How much / where* | `expect.wall_sec_*`, `lock_ref`, QQQ |
| CHAINS (`mok-tua-render`) | *Who, prove later* | `prev_hash` + `content_hash` on render chain only |

**Never** interleave render receipts with caregiving/PHI custody chains.

## Hard rules

1. **Provenance ≠ verification.** A receipt proves the log wasn’t altered; it does not prove the node ran your Qwen pin. v1: trusted nodes + optional later spot-audit.
2. **PHI is unbroadcastable.** `data_class: phi | phi-adjacent` cannot emit crowd-routable packets (`emit` raises).
3. **Crowd / federation for `public` only.** Internal may use **trusted** lab nodes (desk-host/gpu-host/tower).
4. **Manifest public, payload sealed.** Prompts live in `payload_ref` (local_path or future x25519/age).
5. **Mac NPU** is an LLM/embedding tier (MLX), not shareable video UNet supply.

## Schemas

- `schemas/ask_packet.v1.json`
- `schemas/ask_receipt.v1.json`
- `schemas/node_advertisement.v1.json`

## CLI

```bash
cd ~/mok-tua
python3 scripts/mok_tua_cli.py nodes seed
python3 scripts/mok_tua_cli.py nodes list
python3 scripts/mok_tua_cli.py packet emit fixtures/sample_instructor_story.md \
  --data-class public --qqq QQQ3 --allow-crowd
python3 scripts/mok_tua_cli.py packet award work/packets/<id>/packet.json
python3 scripts/mok_tua_cli.py packet award work/packets/<id>/packet.json --live
python3 scripts/mok_tua_cli.py chains verify
```

## Node join key

```text
lock_ref = T1_vid_gen@<blake2b of tier_lock slice>
```

Nodes advertise `lock_hashes_resident`. Award scores lock match first.

## Phases

| Phase | Scope |
|-------|--------|
| A | Schemas + docs + pricing earmark (done) |
| B | Trusted federation index + dry-run award (this tree) |
| C | Spot-audit + reputation from expect/actual |
| D | Friends’ boxes / optional market adapters (not token theater) |

## Related

- `config/tier_lock_T0-T4.json`, `config/pricing.yaml` (`crowd_federated`)
- `config/crowd_nodes.json` (seeded)
- `work/chains/mok-tua-render.jsonl`
- Johnny layout: `johnny-appleseed-chipper` examples
- ADR: grokcode `docs/adr/0003-custody-is-tamper-evident-not-legally-immutable.md`
