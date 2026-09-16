# mok-tua resource index — design (2026-09-16)

**Status: design only, no code yet.** Written after a 4-pass research review across `~/grokcode`
and `~/mok-tua` (full detail in `grokcode/docs/roadmap/` — this doc is the mok-tua-side design
that consumes those findings). The headline conclusion: **most of the pieces already exist**
across mok-tua and its sibling apps — this design is about consolidating and wiring them, not
building a new subsystem from scratch.

## Goal

A mok-tua-native way to answer, at any time: what render backends exist (Maestro, ComfyUI ×3
hosts, Director's Console), what models/LoRAs are available and where, and how to drive a
multi-host render — without re-deriving any of this ad hoc per session, which is how the current
knowledge (scattered across ~15 docs and config files) accumulated.

## What already exists (don't rebuild these)

1. **Maestro's full API surface** — 190 routes catalogued at
   `grokcode/docs/catalog/MAESTRO_API_ENDPOINTS_2026-09-16.md`. Only ~2 of those
   (`director/pipeline/start`, `director/pipeline/{pid}`) are needed for basic render
   orchestration; the rest is UI-support surface (models/LoRA browsing, CivitAI, editor, etc).
2. **A working multi-backend ComfyUI orchestrator, mostly idle.** Director's Console
   (`/mnt/ai-data/pinokio/api/directorsconsole.pinokio.git`, installed on mrgpu) ships an
   `Orchestrator` FastAPI service (`app/Orchestrator/orchestrator/`) with:
   - `GET /health`, `POST /api/job`, `GET /api/backends`, `GET/POST /api/backends/{id}/status|restart`,
     `GET /api/jobs/{job_id}` — job submission/health/status against a **list of ComfyUI backends**
     defined in `Orchestrator/config.yaml` (currently only one: `mrgpu-8188`, `capabilities: []`).
   - `backends/client.py`'s `ComfyUIClient` speaks real ComfyUI REST+WS (`queue_prompt`,
     `get_history`, `get_queue_status`, progress streaming) — a working async client, not a stub.
   - A `job_groups` router + gallery tooling (scan/dedup/rename/tag/search across output trees).
   - **Currently not running** — only its Vite dev frontend (`:5173`) has been alive since
     2026-09-02; the orchestrator API (`:9820`) and Cinema Prompt Engineering API (`:9800`) are
     both down (`curl` → connection refused as of 2026-09-16).
   - **Speaks ComfyUI only** — no Maestro Director-pipeline adapter. Maestro renders (Fill a
     Bust's whole pipeline) are a separate system this orchestrator doesn't touch today.
3. **The 3-host ComfyUI layout is fully documented**: `grokcode/docs/operations/COMFYUI_THREE_HOST_SHARED.md`.
   Shared source/nodes on the pool, per-host env + `extra_model_paths.yaml`. Ports: mrgpu/m4rv
   `:8188` (mrgpu also isolated H3 `:8189`), Tower `:8190` (CPU-only, manage-only).
4. **A current model/LoRA manifest**: `grokcode/data/catalog/ai_data_models_index.json`
   (2,926 files, 3.28TB, 1,076 CivitAI IDs, 79.4% SHA256 coverage) plus mok-tua's own
   `docs/reports/VIDEO_GEN_MODEL_INVENTORY_AUDIT_2026-09-02.md` (tested-vs-untested per model).
5. **mok-tua's own comfy-mcp research**: `docs/COMFY_MULTI_MACHINE_ORCHESTRATION_MCP_EXPANSION_2026-09-11.md`
   already scoped adopting `Comfy-Org/comfy-mcp` + `comfy-cli` for this exact problem.
6. **Three overlapping app-roster JSON formats already in `config/`**:
   `pinokio_gpu_staging.json` (13 entries, has the best shape — `{id, capabilities[], app_dir,
   ref}` + an `integration_contract` of `health/capabilities/submit/status/cancel/collect`),
   `director_stack_catalog.json` (22 entries, richer per-app fields, already lists Director's
   Console as a T0 orchestrator), and `c64_software_catalog.json` (10 entries, TUI-oriented).
   Plus `config/orchestration.json` (per-host endpoint URLs, already has role/mode) and
   `config/comfy_nodes_mok_tua_roster.json` (custom-node roster, not models).

## Open comparison: adopt Director's Console's Orchestrator, or comfy-mcp, or both?

Not resolved in this pass — needs a decision, not more research:

- **Director's Console's Orchestrator** is Python, already multi-backend-shaped, already has
  health/job/status/backends endpoints, and lives right next to Maestro on mrgpu. Con: it's
  someone else's app (not mok-tua's own code), currently dormant, and its `ComfyUIClient` would
  need importing or reimplementing rather than just calling over HTTP if mok-tua wants tighter
  integration than REST.
- **comfy-mcp/comfy-cli** (mok-tua's own prior research) is the "standard" tool-ecosystem path —
  better long-term interoperability with other MCP clients, but nothing installed yet and no
  multi-backend job manager built in (comfy-mcp talks to one ComfyUI instance; the multi-backend
  piece would still need to be mok-tua's own code or Director's Console's).
- **Recommendation for the next session to decide, not default to**: use Director's Console's
  Orchestrator as the multi-backend ComfyUI job router (it already exists and does exactly this),
  and adopt comfy-mcp only if/when an MCP-speaking client (not mok-tua itself) needs to reach
  ComfyUI directly. Don't build a third ComfyUI client.

## Proposed module shape (not yet built)

A single `resource_index` module in mok-tua that:

1. **Reconciles the roster** — one JSON (or the existing `pinokio_gpu_staging.json` extended,
   not a new 4th file) following its `integration_contract` shape, with entries for: Maestro
   (mrgpu, `launch.py` :42005), Director's Console Orchestrator (mrgpu :9820, once started),
   ComfyUI ×3 (mrgpu :8188/:8189, m4rv :8188/:8288, tower :8190), each with real
   `capabilities: []` filled in (currently empty even in Director's Console's own config) —
   this is genuinely new work, not consolidation.
2. **Joins, doesn't re-catalog, the model/LoRA data** — a thin reader over
   `grokcode/data/catalog/ai_data_models_index.json` + mok-tua's own
   `VIDEO_GEN_MODEL_INVENTORY_AUDIT_2026-09-02.md`, keyed by filename/SHA256.
3. **Exposes Maestro's API catalog as structured data** — parse
   `grokcode/docs/catalog/MAESTRO_API_ENDPOINTS_2026-09-16.md` (or regenerate from source the
   same way) into the roster entry's `capabilities[]` rather than hand-maintaining a duplicate
   list.
4. **Routes multi-GPU ComfyUI jobs through Director's Console's Orchestrator** (once its config
   is extended to list m4rv/tower backends and it's actually running) instead of mok-tua
   reimplementing job distribution.

## What this explicitly does NOT do

- Does not touch Maestro's 190-route surface beyond documenting it — Maestro stays mrgpu-only,
  driven directly via its own API (as Fill a Bust's `shot_common.py` already does).
- Does not stand up a new ComfyUI orchestrator — reuses Director's Console's if adopted.
- Does not build a 4th model catalog — joins the two that exist.
- Does not build a new memory/session WebUI (unrelated scope, but noted since the concurrent
  grok-build session explicitly decided against that for its own domain — same principle
  applies here: don't add a parallel index where one already exists).

## Next steps (follow-on session, code)

1. Decide the Director's-Console-vs-comfy-mcp question above.
2. Start Director's Console's Orchestrator on mrgpu, confirm `/health` and `/api/backends`
   actually work, then extend `config.yaml`'s `backends:` list to m4rv/tower.
3. Write the roster-reconciliation script/module (reads the 3 existing JSONs + the two docs
   above, writes one canonical roster).
4. Wire the model/LoRA join reader.
