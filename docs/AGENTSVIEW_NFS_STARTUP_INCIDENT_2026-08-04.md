# AgentsView apparent crash / startup incident (2026-08-04)

## Finding

The web UI was not actually crashing in the current run. The old endpoint `127.0.0.1:42026` is down because Pinokio relaunched AgentsView on `127.0.0.1:42028` (LAN `desk-host:42029`). The current process is healthy (`/api/ping` returns `ok: true`, AgentsView v0.40.0).

## Log evidence

The earlier NFS-backed run logged:

`startup sync worker ran but did not complete: startup worker: sync worker emitted 0 terminal results`

This happened while the archive lived under the shared `ai-data` mount and during the 513-session backfill. After moving the live archive to a local APFS path under `~/.agentsview/data`, the next startup completed the 368-session backfill and incremental syncs resumed normally.

## Operator action

Use the Pinokio status URL rather than a cached port. Current local URL: `http://127.0.0.1:42028`. Do not delete SQLite journals on the NFS copy; preserve the NFS tree as backup-only and perform imports against the local APFS archive.
