# Mac context-history surfaces

## Current state

Hippo already provides a local read-only web dashboard at `http://127.0.0.1:3333/` (Hippo Brain Observatory). Its API currently reports 22 memories, 0 open conflicts, and 0% embedding coverage for the active `mok-tua` store. The dashboard exposes memory text, so keep it localhost-only and do not publish it through a LAN reverse proxy without authentication/redaction.

PasteBar is present at `~/Library/Application Support/app.anothervision.pasteBar/pastebar-db.data`. It is SQLite with 3,480 clipboard-history rows. Clipboard content can contain credentials, PHI, copied code, and private text; it must not be bulk-injected into Hippo or AgentsView.

No Histr application/database was found in the Mac application-support paths or indexed filesystem. If “Histr” means shell history, Atuin is present at `~/.local/share/atuin/history.db` and omp has `~/.omp/agent/history.db`; those should be treated as separate command-history sources.

## Recommended contextualization

Use a two-tier design:

1. **Context index (safe by default):** expose only counts, timestamps, source application, content type, hashes, language, and explicit favorites/pins from PasteBar/Histr. This can appear as a “clipboard/shell context” panel beside Hippo and AgentsView.
2. **Explicit promotion:** when the user selects a specific clipboard or history item, run PII/secret screening and show a preview. Only an explicit “promote to Hippo” action writes a summarized/redacted memory with source and retention tag.

Do not make AgentsView scrape clipboard history automatically. AgentsView remains the session-history viewer; Hippo remains the durable memory layer; the context panel is a read-only bridge with explicit promotion.

## Useful context commands

```sh
hippo status
hippo context --auto --budget 1500
open http://127.0.0.1:3333/
```

The next integration should be a small local adapter that reads PasteBar/Atuin in immutable/read-only mode and serves metadata plus redacted previews. It should never write the source databases and should default to localhost binding.
