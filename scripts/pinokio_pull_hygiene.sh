#!/usr/bin/env bash
# Practical order 1–7: make pinokio/api git roots current + pullable.
# Best practices: fetch first; fix UU on wrapper scripts only; never reset --hard
# nested apps with huge dirt without --force-nested; no clean -fdx by default.
#
# Usage:
#   bash scripts/pinokio_pull_hygiene.sh              # dry-run report
#   bash scripts/pinokio_pull_hygiene.sh --live       # execute 1–7
#   bash scripts/pinokio_pull_hygiene.sh --live --force-nested-behind
#
set -euo pipefail

PIN="${PINOKIO_API:-/Volumes/ai-data/pinokio/api}"
LIVE=0
FORCE_NESTED=0
for a in "$@"; do
  case "$a" in
    --live) LIVE=1 ;;
    --force-nested-behind) FORCE_NESTED=1 ;;
    -h|--help) sed -n '1,20p' "$0"; exit 0 ;;
  esac
done

log() { printf '%s\n' "$*"; }
run() {
  if [[ "$LIVE" -eq 1 ]]; then
    log "+ $*"
    "$@"
  else
    log "DRY $*"
  fi
}

if [[ ! -d "$PIN" ]]; then
  log "missing PINOKIO_API=$PIN"
  exit 1
fi

# Collect git roots: outer + common nested
mapfile -t ROOTS < <(
  for d in "$PIN"/*/; do
    [[ -d "$d" ]] || continue
    [[ -e "$d/.git" ]] && echo "$d"
    for sub in app facefusion ComfyUI applio; do
      [[ -e "$d$sub/.git" ]] && echo "$d$sub"
    done
  done | sed 's:/*$::' | sort -u
)

log "=== pinokio pull hygiene  live=$LIVE  roots=${#ROOTS[@]}  pin=$PIN ==="

# ── 1. Fetch all ────────────────────────────────────────────────────────────
log ""
log "=== 1) fetch --prune ==="
for g in "${ROOTS[@]}"; do
  if git -C "$g" remote get-url origin >/dev/null 2>&1; then
    if [[ "$LIVE" -eq 1 ]]; then
      if git -C "$g" fetch --prune origin 2>/dev/null; then
        log "fetch ok  $g"
      else
        log "fetch FAIL $g"
      fi
    else
      log "DRY fetch $g"
    fi
  else
    log "no origin  $g"
  fi
done

# ── 2. Resolve UU on pinokio wrapper scripts ────────────────────────────────
log ""
log "=== 2) resolve UU install.js/update.js (theirs) ==="
for g in "${ROOTS[@]}"; do
  # only outer wrappers typically
  base=$(basename "$(dirname "$g")")
  leaf=$(basename "$g")
  unmerged=$(git -C "$g" diff --name-only --diff-filter=U 2>/dev/null || true)
  [[ -z "$unmerged" ]] && continue
  log "CONFLICT $g"
  log "$unmerged" | sed 's/^/  /'
  for f in install.js update.js reset.js start.js; do
    if git -C "$g" ls-files -u -- "$f" 2>/dev/null | grep -q .; then
      if [[ "$LIVE" -eq 1 ]]; then
        git -C "$g" checkout --theirs -- "$f" 2>/dev/null || git -C "$g" checkout HEAD -- "$f" 2>/dev/null || true
        git -C "$g" add -- "$f" 2>/dev/null || true
        log "  resolved --theirs $f"
      else
        log "  DRY resolve --theirs $f"
      fi
    fi
  done
  if [[ "$LIVE" -eq 1 ]]; then
    # finish merge/rebase if needed
    if [[ -f "$g/.git/MERGE_HEAD" ]] || [[ -d "$g/.git/rebase-merge" ]] || [[ -d "$g/.git/rebase-apply" ]]; then
      git -C "$g" -c core.editor=true commit --no-edit -m "chore: resolve pinokio script merge conflicts (theirs)" 2>/dev/null \
        || git -C "$g" rebase --continue 2>/dev/null \
        || log "  still mid-merge — manual: $g"
    fi
    left=$(git -C "$g" diff --name-only --diff-filter=U 2>/dev/null || true)
    [[ -n "$left" ]] && log "  still unmerged: $left"
  fi
done

# ── helpers ─────────────────────────────────────────────────────────────────
behind_of() {
  git -C "$1" rev-list --count HEAD..@{u} 2>/dev/null || echo ""
}
ahead_of() {
  git -C "$1" rev-list --count @{u}..HEAD 2>/dev/null || echo ""
}
dirty_n() {
  git -C "$1" status --porcelain 2>/dev/null | wc -l | tr -d ' '
}

# ── 3. Clean + pull repos that are behind ───────────────────────────────────
log ""
log "=== 3) behind>0 → clean light + pull --ff-only ==="
for g in "${ROOTS[@]}"; do
  b=$(behind_of "$g")
  [[ -z "$b" || "$b" == "0" ]] && continue
  a=$(ahead_of "$g")
  d=$(dirty_n "$g")
  log "BEHIND $b ahead=${a:-?} dirty=$d  $g"

  if [[ "${a:-0}" -gt 0 ]]; then
    log "  DIVERGED ahead=$a — step 5 policy (skip auto ff-only)"
    continue
  fi

  if [[ "$LIVE" -eq 1 ]]; then
    # Critical: NFS AppleDouble inside .git/objects/pack breaks pull/stash
    # (non-monotonic index ._*pack*.idx). Never stash -u over NFS pinokio.
    for f in "$g/.git/objects/pack"/._*; do
      [[ -e "$f" ]] && rm -f "$f"
    done
    find "$g" -maxdepth 2 -name '._*' -type f -delete 2>/dev/null || true
    for f in install.js update.js reset.js start.js; do
      if git -C "$g" ls-files --error-unmatch "$f" >/dev/null 2>&1; then
        git -C "$g" checkout -- "$f" 2>/dev/null || true
      fi
    done
    d2=$(dirty_n "$g")
    if [[ "$d2" -gt 0 ]]; then
      if [[ "$FORCE_NESTED" -eq 1 ]] || [[ "$d2" -lt 20 ]]; then
        # tracked-only stash (no -u — AppleDouble/untracked hangs NFS)
        git -C "$g" stash push -m "pinokio-hygiene $(date -u +%Y%m%dT%H%M%SZ)" 2>/dev/null || true
      else
        log "  SKIP pull still dirty=$d2 (use --force-nested-behind to stash tracked)"
        continue
      fi
    fi
    if git -C "$g" pull --ff-only 2>&1; then
      log "  PULLED ok"
    else
      log "  PULL failed"
    fi
  else
    log "  DRY would light-clean + pull --ff-only"
  fi
done

# ── 4. facefusion nested: reattach branch ───────────────────────────────────
log ""
log "=== 4) facefusion nested branch ==="
FF="$PIN/facefusion-pinokio.git/facefusion"
if [[ -e "$FF/.git" ]]; then
  br=$(git -C "$FF" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "?")
  log "facefusion HEAD=$br"
  if [[ "$br" == "HEAD" ]]; then
    if [[ "$LIVE" -eq 1 ]]; then
      git -C "$FF" fetch origin 2>/dev/null || true
      if git -C "$FF" show-ref --verify --quiet refs/remotes/origin/master; then
        git -C "$FF" checkout -B master origin/master
      elif git -C "$FF" show-ref --verify --quiet refs/remotes/origin/main; then
        git -C "$FF" checkout -B main origin/main
      else
        log "  no origin/main|master"
      fi
      git -C "$FF" pull --ff-only 2>&1 || log "  pull soft-fail"
    else
      log "  DRY checkout tracking branch + pull"
    fi
  else
    log "  already on branch $br"
  fi
else
  log "no $FF"
fi

# ── 5. chatterbox diverge ───────────────────────────────────────────────────
log ""
log "=== 5) chatterbox diverged — best practice: reset to origin if pinokio noise ==="
CB="$PIN/chatterbox-tts-app.git"
if [[ -e "$CB/.git" ]]; then
  a=$(ahead_of "$CB"); b=$(behind_of "$CB")
  log "chatterbox ahead=${a:-?} behind=${b:-?}"
  if [[ "${a:-0}" -gt 0 && "${b:-0}" -gt 0 ]]; then
    if [[ "$LIVE" -eq 1 && "$FORCE_NESTED" -eq 1 ]]; then
      git -C "$CB" fetch origin
      branch=$(git -C "$CB" rev-parse --abbrev-ref HEAD)
      # prefer @{u}
      if git -C "$CB" rev-parse --verify @{u} >/dev/null 2>&1; then
        git -C "$CB" reset --hard @{u}
        log "  reset --hard @{u} on $branch"
      else
        log "  no @{u}; skip"
      fi
    else
      log "  DIVERGED — re-run with --live --force-nested-behind to reset --hard @{u}"
      log "  (local ahead commits usually pinokio install noise)"
    fi
  fi
fi

# ── 6. Bulk wrapper noise + AppleDouble (outer pinokio only) ────────────────
log ""
log "=== 6) bulk wrapper noise + AppleDouble (outers, light) ==="
for d in "$PIN"/*/; do
  d=${d%/}
  [[ -e "$d/.git" ]] || continue
  # skip if still unmerged
  if git -C "$d" diff --name-only --diff-filter=U 2>/dev/null | grep -q .; then
    log "skip dirty-conflict outer $d"
    continue
  fi
  if [[ "$LIVE" -eq 1 ]]; then
    n_ad=$(find "$d" -maxdepth 2 -name '._*' -type f 2>/dev/null | wc -l | tr -d ' ')
    find "$d" -maxdepth 2 -name '._*' -type f -delete 2>/dev/null || true
    for f in install.js update.js reset.js start.js; do
      if git -C "$d" ls-files --error-unmatch "$f" >/dev/null 2>&1; then
        # only restore if modified and not intentionally different from index with conflict
        if ! git -C "$d" diff --quiet -- "$f" 2>/dev/null; then
          git -C "$d" checkout -- "$f" 2>/dev/null || true
        fi
      fi
    done
    # drop untracked AppleDouble from index view
    git -C "$d" clean -fd -- '**/._*' 2>/dev/null || true
    log "outer cleaned appledouble≈$n_ad  $d"
  else
    log "DRY light-clean outer $d"
  fi
done

# ── 7. Do NOT force-pull huge nested dirt — report only ─────────────────────
log ""
log "=== 7) huge nested dirty (inspect only; no auto reset) ==="
for g in "${ROOTS[@]}"; do
  case "$g" in
    */app|*/facefusion|*/ComfyUI|*/applio) ;;
    *) continue ;;
  esac
  d=$(dirty_n "$g")
  b=$(behind_of "$g")
  [[ "${d:-0}" -lt 40 ]] && continue
  log "NESTED dirty=$d behind=${b:-?}  $g"
done

# ── Summary scoreboard ──────────────────────────────────────────────────────
log ""
log "=== scoreboard (post) ==="
behind_n=0; conflict_n=0; dirty_n=0; clean_n=0; diverged_n=0
for g in "${ROOTS[@]}"; do
  u=$(git -C "$g" diff --name-only --diff-filter=U 2>/dev/null | wc -l | tr -d ' ')
  b=$(behind_of "$g")
  a=$(ahead_of "$g")
  d=$(dirty_n "$g")
  if [[ "${u:-0}" -gt 0 ]]; then conflict_n=$((conflict_n+1))
  elif [[ -n "$b" && "$b" -gt 0 && -n "$a" && "$a" -gt 0 ]]; then diverged_n=$((diverged_n+1))
  elif [[ -n "$b" && "$b" -gt 0 ]]; then behind_n=$((behind_n+1))
  elif [[ "${d:-0}" -gt 0 ]]; then dirty_n=$((dirty_n+1))
  else clean_n=$((clean_n+1))
  fi
done
log "conflict=$conflict_n  behind=$behind_n  diverged=$diverged_n  dirty_current=$dirty_n  clean=$clean_n"
if [[ "$LIVE" -eq 0 ]]; then
  log ""
  log "Re-run with:  bash scripts/pinokio_pull_hygiene.sh --live"
  log "Chatterbox hard reset + aggressive stash:  ... --live --force-nested-behind"
fi
