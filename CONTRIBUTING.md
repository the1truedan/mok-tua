# Contributing

This repo is developed with AI-assisted tooling (Claude Code, Codex, and
Grok Build) alongside manual work. Commits produced primarily by an AI
agent under human direction carry a trailer identifying the assisting
model:

```
Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Co-authored-by: Codex <noreply@openai.com>
Co-Authored-By: Grok 4.6 <noreply@x.ai>
```

This is a provenance note, not a claim of autonomous authorship — every such
commit was directed, reviewed, and approved by a human before merging.

## GitHub display

The Claude and Codex trailers above map to linked GitHub contributors:
`noreply@anthropic.com` maps to [claude](https://github.com/claude), and
`noreply@openai.com` maps to [codex](https://github.com/codex). xAI has
not claimed `noreply@x.ai`, so Grok stays an unlinked name on commit pages
and does not appear in the Contributors graph. This repo will not invent a
stand-in Grok identity. If xAI later claims the email, existing trailers
become linkable without a rewrite.

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
