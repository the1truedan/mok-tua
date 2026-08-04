# Repeated lab-context bundle

These are the compact procedural facts worth recalling before any cloud or local agent prompt. They are intentionally operational, not a transcript.

1. **Storage:** NFS `ai-data` is for models, artifacts, repositories, and backups. Keep live SQLite/databases, locks, journals, and high-churn indexes on local disk. Use bounded, allowlisted walks; never scan all of `/ai-data` by default.
2. **Network:** use the documented SSH host/user and strict bounded commands with connect timeouts. Tower (`192.168.1.2`) and MRGPU (`192.168.1.5`) are single-command-at-a-time operations; do not probe repeatedly or run unbounded remote file walks.
3. **Gateway:** Headroom is the context-budget/compression layer before LiteLLM. Turnstone owns MRGPU workstreams; pi/omp are local executors; Herdr is a supervised TUI, not a competing scheduler. Cloud fallback requires a handoff and independent local review.
4. **Paths:** `/ai-data`/`/mnt/ai-data` is the canonical shared model/artifact tree. Pinokio and Stability Matrix configs must not retain stale `/Volumes/2TB` model/cache paths. UV caches are host-split and use copy link mode on NFS.
5. **Permissions:** repair ownership/mode for the exact subtree, then run a bounded read/write/execute probe as `dtm`; do not chmod the entire share recursively. Record NFS-version differences and the exact path in an incident note.
6. **History/memory:** AgentsView is session history, Hippo is durable approved context, and raw PasteBar/clipboard/chat exports are not automatic memory input. Promote only reviewed, redacted reminders tagged `agent-context` or `repeated-reminder`.
7. **Documentation:** `~/grokcode/docs` is the operational source of truth. Every incident or cloud-credit handoff records objective, host, paths, commands, changed files, tests, unresolved risks, and next action.
