# Universal Hippo session lifecycle

## Outcome

Claude and Codex use Hippo's native detached `SessionEnd` integration. Grok and
Tok sessions launched through `grok-tua`/`tok-tua` run the same finalizer after
the tmux client detaches. Each path performs:

```text
session ends → hippo sleep (learn/consolidate/dedupe/secret-veto/share)
               → hippo capture (actionable lessons from the last transcript)
               → global Hippo store (only eligible high-value memories)
               → tagged recall through Hippo MCP or Headroom
```

The worker is detached so closing a TUI does not interrupt SQLite writes. A
failure is best-effort and never prevents the client from exiting.

## What becomes shared

Hippo is a durable, auditable collective context—not an unrestricted transcript
mirror. Capture extracts actionable lessons, decisions, and procedures; it does
not make every conversational sentence a global memory. Secret filtering and
deduplication run before auto-sharing. Only memories tagged `agent-context` or
`repeated-reminder` are eligible for automatic prompt preload through the
Headroom integration. Breakthroughs that must be deliberately durable should be
recorded explicitly:

```bash
hippo remember "Concise, reusable breakthrough or invariant" \
  --global --tag agent-context --tag breakthrough --pin --verified
```

Every shared memory should be short, operational, and include provenance in its
source metadata. Do not store credentials, tokens, raw private transcripts, or
unbounded logs in the global store.

## Client coverage

| Client | End-of-session path | Prompt-time path |
| --- | --- | --- |
| Claude Code | native `hippo session-end` in `~/.claude/settings.json` | Hippo MCP + pinned UserPromptSubmit hook |
| Codex | Hippo wrapper around the detected `codex` launcher | Hippo MCP / configured AGENTS guidance |
| OpenCode | native `session.idle` plugin at `~/.config/opencode/plugins/hippo.ts` | Hippo MCP |
| Grok | `grok-tua` finalizer after tmux detach | `HIPPO_AUTO_CONTEXT` + Headroom gateway |
| Tok / local CLIs | `tok-tua` finalizer after tmux detach; native client hooks where available | Hippo MCP or Headroom → LiteLLM |
| Native Grok outside wrappers | no discoverable local hook | use `grok-tua` or the Headroom gateway |

Restart Claude/Codex after installing or changing hooks. The next session's
start hook prints the previous consolidation log, making capture visible and
reviewable.

## Verification and recovery

```bash
hippo status
hippo hook list
cat ~/.hippo/logs/claude-code-sleep.log
cat ~/.hippo/logs/codex-sleep.log
cat ~/.hippo/logs/wrapper-session.log
```

To disable wrapper capture temporarily, set `HIPPO_AUTO_CONTEXT=0`. To disable
sharing while retaining local consolidation, run `hippo sleep --no-share`.

The finalizer lives at
`/Users/redacted/mok-tua/scripts/hippo-session-finalize.sh` and is intentionally
small so Grok/Tok wrappers can call it without importing repo Python code.
