# Contributing

This repo is developed with AI-assisted tooling (Claude Code, Grok Build,
and others) alongside manual work. Commits produced primarily by an AI
agent under human direction carry a trailer identifying the assisting
model:

```
Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Co-Authored-By: Grok 4.6 <noreply@x.ai>
```

This is a provenance note, not a claim of autonomous authorship — every such
commit was directed, reviewed, and approved by a human before merging.

## Context stack (development process)

Human-directed sessions keep durable context in three layers:

- **Hippo** — approved project recall (citations, not raw transcripts)
- **PMB** — structured lessons, decisions, and goals
- **AgentsView** — session *index* (IDs only; not a prompt dump)

Production services for local chat, history search, embeddings, git
forge, and observability run on a self-hosted NAS/tower, not a required
cloud SoR. Details stay in the private control repo.

For everything else (commit style, versioning), follow the patterns already
in `git log`, `HANDOFF.md`, and tagged releases rather than a separate
process document.
