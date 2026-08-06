# Public release · protect-this-branch sequencing (2026-08-05)

## Problem

GitHub free accounts **cannot** enable branch protection or rulesets on **private** repos:

```text
HTTP 403 — Upgrade to GitHub Pro or make this repository public to enable this feature.
```

So “Protect this branch” is unavailable until visibility is **public** (or the org upgrades).

## Fix order

| Step | Action | Owner |
|------|--------|-------|
| 1 | Credential scrub (`git remote -v` no userinfo) | ✅ done (E-lite) |
| 2 | LAN/home path scrub in tracked tree (`gpu-host` / `control-host` / `desk-host`) | ✅ this session |
| 3 | `.hippo/` gitignored (never publish local memories) | ✅ this session |
| 4 | Push private tip; operator review | pre-16:20 |
| 4b | **wait-what plain-English pass** on public front door (README intro, Release draft) — native speakers, not AI aficionados | earmark: `docs/roadmap/WAIT_WHAT_GITHUB_PLAIN_ENGLISH_EARMARK_2026-08-05.md` · upstream [mattpocock/skills](https://github.com/mattpocock/skills) |
| 5 | Human `gh repo edit … --visibility public` | **human go only** |
| 6 | Immediately enable `main` protection (no force-push) | same minute as flip |
| 7 | Optional GH Release + demo video asset (GPU-host proof preferred; Release body wait-what clean) | same packet |

## Commands (human go only)

```bash
cd ~/mok-tua
git remote -v
# expect no userinfo; github + optional forgejo

# final scrub gate (hard FAIL if any absolute home path or RFC1918 IP)
git grep -nE '192\.168\.|/Users/[A-Za-z0-9._-]+/' && echo FAIL || echo scrub_ok

# FLIP — only after explicit operator “go”
gh repo edit the1truedan/mok-tua --visibility public

# Protect main (free public repos support this)
gh api -X PUT "repos/the1truedan/mok-tua/branches/main/protection" \
  --input - <<'JSON'
{
  "required_status_checks": null,
  "enforce_admins": true,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
JSON
```

## Related

- `docs/OPERATORS.md` § Public flip + branch protection  
- Control-repo: `docs/operations/PRIVATE_TO_PUBLIC_NEXT_SWITCH_PREP_2026-08-05.md`  
- Demo evidence: `docs/DEMO_VIDEO_PROOF_2026-08-05.md` (when written)  
- Gamut smoke: `docs/reports/PINOKIO_GAMUT_SMOKE_2026-08-05.md` (when written)

*Do not flip from unattended agents.*
