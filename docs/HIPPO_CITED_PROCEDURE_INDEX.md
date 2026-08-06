# Hippo-cited procedure index

Hippo should carry a short reminder plus one of these Git-reviewed Markdown
sources. Headroom may render the citation only (`HIPPO_CONTEXT_CITATIONS_ONLY=1`)
when the receiving CLI can inspect the checkout. Do not copy whole handoff
documents into every prompt.

| Procedure | Canonical source | Use before |
|---|---|---|
| Shared storage/NFS boundaries | `docs/REPEATED_CONTEXT_BUNDLE.md` | any `/mnt/ai-data` or `/Volumes/ai-data` access |
| GPU-host Pinokio paths and staged pulls | `config/pinokio_gpu_staging.json` + `docs/OPERATORS.md` | Pinokio update/pull/install |
| UV host split and corruption handling | `~/grokcode/docs/operations/UV_CACHE_CROSS_HOST_NFS_INCIDENT_2026-08-04.md` | uv/Pinokio dependency pulls |
| Permission repair and probes | `~/grokcode/docs/operations/AI_DATA_NFS_CROSS_PLATFORM_PERMISSIONS_INCIDENT_2026-08-03.md` | chmod/chown/ACL/sudo decisions |
| SSH bounded-command safety | `docs/REPEATED_CONTEXT_BUNDLE.md` | remote health or path checks |
| Comfy/model assurance | `docs/COMFY_ROBUST_NODES.md` + `config/lora_inventory_storyboard_2026-08-02.md` | workflow/model smoke |
| A.I.D.A. scan intake | `docs/DOCUMENT_INTAKE_AIDA_TEST_PLAN.md` | receipt/letter/form processing |

The `~/grokcode` references are operator-local sources and must never be sent
to a cloud provider as absolute paths. Use repository-relative citations or a
short redacted summary when the active agent is not on that checkout.

## Reminder format

```text
Before touching shared storage: cite docs/REPEATED_CONTEXT_BUNDLE.md;
use one bounded SSH command; verify exact path and UID/GID; do not recurse;
record the result before changing anything.
```

