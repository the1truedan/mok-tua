<!-- BEGIN:private-context-reference -->
## Private context contract

- Repository: `mok-tua` (`private`; private/internal only).
- Read the canonical protocol: `grokcode/docs/operations/PRIVATE_REPO_CONTEXT_PROTOCOL.md`.
- Consult the private landscape ledger: `grokcode/data/catalog/private_repo_landscape.json`; checkout state and tests remain authoritative.
- Preserve any local `AGENT_COORDINATION.md` and repo-specific docs; do not copy `.hippo`, secrets, prompts, PHI, or credentials into this file.
- Hippo is recall evidence. Use `HIPPO_CONTEXT_CITATIONS_ONLY=1` when only bounded, repo-relative Markdown citations are needed.
- C.H.I.P.P.E.R. manifests artifacts; C.H.A.I.N.S. records custody and audit receipts. Do not publish or sync automatically.
- For SSH/NFS/sudo, use exact approved paths and bounded commands; unknown or permission-denied is evidence to record, not permission to broaden scope.
- Refresh from the private control repo with: `python3 scripts/build_private_repo_context.py --write-ledger --write-agents --dry-run` (review before applying).
<!-- END:private-context-reference -->
