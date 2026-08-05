# Earmark — Matt Pocock `wait-what` for plain-English GitHub posts

**Date:** 2026-08-05  
**Status:** **earmark only** (not installed · not required for flip)  
**Stamp:** `2026.08-wait-what-github-plain-english-earmark`  
**Upstream:** [github.com/mattpocock/skills](https://github.com/mattpocock/skills)  
**Skill:** [`skills/productivity/wait-what`](https://github.com/mattpocock/skills/blob/main/skills/productivity/wait-what/SKILL.md)

---

## Why

Public mok-tua (and related MANAGER) GitHub surfaces should read cleanly for **native English speakers who are not AI aficionados** — operators, curious devs, friends of the lab — not as insider agent-stack prose.

Matt Pocock’s **`/wait-what`** skill is the fit:

> When a message doesn’t land, **re-pitch**: a little context, **plain English** (skill cites **ASD-STE100 Simplified Technical English**), and project vocabulary from `CONTEXT.md` when present.

That is the opposite of “AI afficionado” posting: no unearned jargon parade, no process theater, no assuming the reader lives in Pinokio/Comfy/QQQ land.

---

## Audience rule (public README / Release notes / PR bodies)

| Write for | Avoid writing for |
|-----------|-------------------|
| Someone who can use GitHub and run a CLI | Someone who already knows Headroom, CHAINS, QQQ, pterm |
| Short sentences, concrete verbs | Stack acronyms without a one-line gloss |
| What it does → why it helps → how to try | Capability matrices as the first paragraph |
| Honest skips (“this path is cloud”) | Vibes that hide provenance (see I2V Grok vs gpu-host incident) |

**Lab-private docs** (ops handoffs, receipts, gamut reports) keep full jargon.  
**Public-facing** README intro, GH Release body, and social captions get a **wait-what pass** before publish.

---

## When to use (earmark workflow)

| Trigger | Action |
|---------|--------|
| Pre-public flip README polish | Operator (or agent with skill installed) runs wait-what on intro + “what is this” |
| GH Release notes for demo video | Re-pitch: 3–5 plain sentences + link to proof path names only |
| PR description for external reviewers | Same pass if the PR is the public story |
| Mid-thread: “huh?” on a draft | Fire wait-what on the last paragraph |

**Not for:** internal runbooks, NFS/SSH ops, PHI paths, Hippo body text.

---

## Install options (later — do not block flip)

From [mattpocock/skills](https://github.com/mattpocock/skills) README:

```bash
# Editable copy into a tooling repo / agent skills dir (operator choice)
npx skills@latest add mattpocock/skills
# Ensure wait-what (and optionally setup-matt-pocock-skills, grill-me) are selected
```

Or Claude plugin: `claude plugins install mattpocock-skills` / `/plugin install mattpocock-skills`.

**Lab note:** Grok Build already ships a local **grilling** skill family; wait-what is complementary (re-pitch for humans), not a replacement for grill-before-code.

---

## Sibling skills worth the same earmark list (optional)

| Skill | Use if… |
|-------|---------|
| `wait-what` | **Primary** — plain re-pitch for public posts |
| `grill-me` / `grilling` | Align before a big public-message rewrite |
| `writing-for-agents` | Only when editing AGENTS.md for agents (not public humans) |
| `handoff` | Compact session → doc (lab ops; not GH marketing) |

Prefer **wait-what** for GitHub *human* front door. Do not paste agent handoff tone into Release notes.

---

## Acceptance (when executed)

- [ ] Public README first screen: no raw LAN, no PHI, no unexplained acronym stack  
- [ ] A non-AI-native peer can say what the product does in one sentence after reading  
- [ ] Cloud vs local video proof still labeled (provenance law)  
- [ ] Skill cited as optional tooling, not a product dependency  

---

## Related

- `docs/PUBLIC_RELEASE_PROTECT_BRANCH_2026-08-05.md`  
- `docs/operations/I2V_GROK_VS_gpu-host_CONTEXT_AMBIGUITY_INCIDENT_2026-08-05.md`  
- `HANDOFF.md` · `TODO.md` P2 item  
- Upstream license: see repo LICENSE before redistributing skill text  
