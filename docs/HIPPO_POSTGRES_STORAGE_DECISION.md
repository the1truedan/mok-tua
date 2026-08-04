# Hippo storage decision

## Short answer

Postgres is a good multi-host database, but the installed Hippo release does
not support it as a drop-in backend. Hippo currently uses SQLite plus markdown
mirrors; setting `DATABASE_URL` or pointing its SQLite file at Postgres will not
work. A direct migration would require an adapter and schema/migration work for
memories, provenance, decay/consolidation, embeddings, conflicts, and global
scope.

## Recommended topology now

```text
Mac / MRGPU / Tower agents
        │  MCP or HTTP
        ▼
Hippo service boundary (one selected host)
        │
        └── local-disk SQLite (never SQLite over NFS)

LiteLLM / Turnstone / Open WebUI / other supported services
        └── existing PostgreSQL + pgvector where their official adapters exist
```

Keep each host's active `.hippo` database on local SSD. Use Hippo's global
promotion, export/import, or an authenticated Hippo MCP/HTTP service for
cross-host context. This removes NFS locking/UID/GID problems without pretending
that independent SQLite files are one transactional database.

## When Postgres becomes worthwhile

Use a shared Postgres Hippo backend only after an adapter is implemented and
tested for concurrent writes, migrations, tenant/project isolation, full-text
search, vector search, backup/restore, and secret filtering. It would then be a
strong choice for many simultaneous clients, centralized backups, and pooled
querying—but it is a software change, not a configuration switch.

Do not put the current `hippo.db` on `/ai-data` NFS. If a centralized service is
needed before a Postgres adapter exists, put the SQLite file on the service
host's local disk and expose only Hippo's MCP/HTTP API. Back up the database and
markdown mirrors independently.

## Existing Postgres candidates

The ai-gateway stack already uses PostgreSQL/pgvector for services that support
it (notably LiteLLM and Turnstone-related components). Those databases should
remain separate by service/database and should not be reused as Hippo's schema
without an explicit migration and ownership boundary.
