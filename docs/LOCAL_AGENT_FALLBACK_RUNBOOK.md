# Local coding-agent fallback runbook

## Recommended topology

Use **Turnstone as the execution/control-plane API** on gpu-host, with LiteLLM and Headroom behind it. Use **pi and omp as local-only coding executors** through the gateway. Treat **Herdr as an optional operator TUI/multiplexer**, not as a second scheduler. This keeps one owner for workstreams, retries, budgets, and handoffs while Herdr only presents/monitors panes.

```text
repo task -> Turnstone workstream -> Headroom -> LiteLLM -> gpu-host Qwen coder
                         |                         |
                         +-> pi / omp local CLI    +-> tool/model policy
                         +-> Herdr panes (optional)
```

Turnstone is preferred for unattended or multi-step work because it already has a workstream client and gpu-host endpoint. Herdr is preferred for a human-supervised session where several local agents need visible panes and intervention. Do not run both as independent orchestrators for the same task.

## Cloud-credit depletion policy

1. Detect cloud exhaustion or a remaining-credit threshold in the caller; do not wait for repeated provider failures.
2. Freeze the current cloud task and write a handoff containing objective, files changed, tests, unresolved questions, and exact next command.
3. Route the handoff to a new Turnstone workstream using the local `tier-nvidia-agent`/Qwen coder alias exposed by LiteLLM.
4. Ask the local agent first for a read-only plan and repository status. Permit edits only after the plan is logged.
5. Use a two-pass loop: implementation agent, then an independent local review agent. The reviewer must run tests/diff checks and may propose patches but must not silently broaden scope.
6. Require a final handoff artifact in the control-repo `docs/` (or this repo's `docs/`) and a durable session record in AgentsView/Turnstone history.
7. Resume cloud work only when explicitly authorized and only from the local handoff; never assume cloud context survived a provider failure.

## Local roles

- **Planner:** Qwen coder through LiteLLM/Headroom; produces bounded plan and risk list.
- **Implementer:** pi or omp, local-only, with the repository as cwd and an explicit file allowlist.
- **Reviewer:** a fresh pi/omp process with no implementer transcript injected except the diff, tests, and handoff.
- **Operator:** Herdr pane or Turnstone API monitor; can pause/stop/retry but does not edit source.

Use separate sessions and model aliases for planner, implementer, and reviewer. Never use one long-lived chat as all three roles.

## Context and privacy standards

- Headroom is the context compressor; it is not the source of truth. Preserve raw diffs, test output, and handoffs.
- Send only the minimum repository context needed. Do not forward cloud credentials, provider tokens, `.env` files, personal chat exports, or PHI to the local model gateway logs.
- Local-only means no direct `codex`, Claude, Grok, or other cloud CLI invocation from the fallback loop.
- Use bounded path lists; never give an agent an unbounded `/ai-data` walk. Treat NFS as model/artifact storage, not a live SQLite workspace.
- Every delegated task gets a correlation/workstream ID and records model alias, host, start/end time, changed paths, test result, and disposition.

## Safe launch/checks

```sh
# GPU-host control-plane health (read-only; set TURNSTONE_BASE if different)
python3 "$HOME/grokcode/tok_tua/turnstone_client.py" --base http://gpu-host:8090 health
python3 "$HOME/grokcode/tok_tua/turnstone_client.py" --base http://gpu-host:8090 models

# local fallback smoke (choose the repo's approved wrapper)
cd "$HOME/grokcode"
./scripts/tok-tua --help
```

Before edits, capture `git status --short`, branch/commit, and the exact model alias. After edits, run the repo's tests plus `git diff --check`; a reviewer must confirm no generated secrets or unrelated files entered the diff.

## AgentsView history

LM Studio histories are imported with `scripts/import/lmstudio_to_agentsview.py`. AgentsView's live SQLite archive is local APFS under `~/.agentsview/data`; the NFS copy under the shared `ai-data` mount is backup-only. This is intentional: SQLite journals and locks are unreliable on the NFS mount.
