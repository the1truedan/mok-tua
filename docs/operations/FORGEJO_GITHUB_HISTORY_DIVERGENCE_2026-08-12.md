# Why `forgejo/main` and `github/main` can't be merged or rebased (2026-08-12)

**Read this before running `git rebase forgejo/main`, `git merge forgejo/main`,
or anything else that assumes these two remotes share history — they don't,
and that's intentional. This doc exists because someone (an agent, in this
case) hit exactly that surprise and burned time on it.**

## The symptom

```
$ git fetch forgejo && git rebase forgejo/main
Rebasing (1/36)Auto-merging README.md
CONFLICT (add/add): Merge conflict in README.md
Auto-merging api/app.py
CONFLICT (add/add): Merge conflict in api/app.py
... (15+ more add/add conflicts on core files)
```

`git merge-base main forgejo/main` returns **nothing** — there is no common
ancestor. This is not a normal "behind by N commits" situation; standard
fast-forward/rebase/merge tooling does not apply here.

## What's actually going on

Both remotes' root commits share the identical message
(`Initial commit — MOCK-TUA storyboard/render orchestrator (renamed
mok-tua)`) and the identical author timestamp — but different tree content
and different commit hashes. That's the signature of two independent
`git init` + commit passes done at the same moment, not one shared history
that later forked.

Diffing the two root trees shows the real difference: host-specific
references (real internal hostnames, direct GPU-host URLs) on the
`forgejo` side, replaced with generic placeholders (e.g. `<gpu-host-ip>`)
on the `github` side. Checked as of this doc's date, that pattern still
holds at the current tips — `github/main` has zero tracked files with real
internal hostnames/IPs; `forgejo/main` still carries at least one (an
internal ops doc, appropriately not mirrored to the public side).

**Read: this looks like a deliberate design choice, not an accident.**
`forgejo` (private) was seeded as the real, unredacted history. `github`
(public) was seeded separately, already-scrubbed, from day one — rather
than "scrub in place on one shared history and flip visibility," which
would leave the pre-scrub commits permanently recoverable via `git log`/
reflog on the public remote. Starting the public side from an unrelated
root avoids that risk entirely.

## What this means practically

- **Don't rebase, merge, or fast-forward between these two remotes.** It
  will either fail outright (like above) or, if forced through, either leak
  real hostnames into the public history or destroy the intentional scrub.
  Both outcomes are worse than the inconvenience of separate pushes.
- **Push new commits to each remote independently.** There's no tooling
  today that automatically propagates a change from one side to the other —
  each commit that should exist on both sides needs to be created/pushed to
  each remote on its own terms (and scrubbed appropriately for `github` if
  it touches anything host-specific).
- **The two histories will keep diverging in commit count** (47 vs 52 as of
  this check) — that's expected and not a problem to "fix," as long as the
  *content* that's supposed to be public stays in sync with what's supposed
  to be public.
- If you need to check whether the public side has drifted out of sync with
  what it should show, diff specific files directly
  (`git diff main forgejo/main -- <path>`) rather than trying to diff or
  merge the whole tree.

## Origin of this doc

Found while adding a `CONTRIBUTING.md` AI-attribution note to `mok-tua` —
pushing to `github` worked cleanly, but the same local branch couldn't push
to `forgejo` (`non-fast-forward`), and a naive `git rebase forgejo/main`
produced the conflict storm above. Worked around by creating the same file
independently against `forgejo/main`'s own current HEAD via its API instead
of trying to reconcile the two histories.
