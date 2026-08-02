"""Discover new Pinokio/GitHub options and audit before staging into catalog."""

from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = Path(os.environ.get("MOCK_TUA_CONFIG", ROOT / "config"))
AI_DATA = Path(os.environ.get("AI_DATA_ROOT", "/Volumes/ai-data"))
GROKCODE = Path.home() / "grokcode"
SCAN_DOCKER = GROKCODE / "scan-all-dockerfiles.sh"
STAGING_SCRIPT = GROKCODE / "scripts" / "github_staging_repos.py"

VIDEO_HINTS = re.compile(
    r"wan|comfy|framepack|ltx|hunyuan|animate|video|storyboard|director|facefusion|"
    r"dreamtalk|freemocap|liveportrait|ace-?step|tts|whisper|mocap|pose|lipsync",
    re.I,
)


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _catalog_ids_and_paths() -> tuple[set[str], set[str]]:
    from providers import load_catalog, resolve_app_path

    cat = load_catalog()
    ids = set()
    paths = set()
    for app in cat.get("apps") or []:
        ids.add(str(app.get("id")))
        p = resolve_app_path(app)
        if p:
            paths.add(str(p.resolve()) if p.exists() else str(p))
            paths.add(str(p))
    for t in cat.get("pull_targets_not_on_pool") or []:
        ids.add(str(t.get("id")))
    return ids, paths


def discover(
    *,
    source: str = "all",
    limit: int = 50,
) -> dict[str, Any]:
    """Find apps on pool not yet in director_stack_catalog."""
    known_ids, known_paths = _catalog_ids_and_paths()
    candidates: list[dict[str, Any]] = []

    sources = {source} if source != "all" else {"pinokio", "github_mirrors", "catalog_gaps"}

    if "pinokio" in sources:
        root = AI_DATA / "pinokio" / "api"
        if root.is_dir():
            for child in sorted(root.iterdir()):
                if not child.is_dir():
                    continue
                if not VIDEO_HINTS.search(child.name) and not (child / "pinokio.json").exists():
                    # still include pinokio apps with pinokio.json
                    if not any((child / n).exists() for n in ("install.js", "start.js", "pinokio.js")):
                        continue
                resolved = str(child)
                if any(resolved == kp or resolved.startswith(kp + os.sep) for kp in known_paths if kp):
                    continue
                # id-ish already known?
                slug = child.name.replace(".pinokio.git", "").replace(".git", "").lower()
                if slug.replace("-", "_") in known_ids or slug in known_ids:
                    continue
                candidates.append({
                    "id": slug.replace("-", "_")[:40],
                    "name": child.name,
                    "path": resolved,
                    "source": "pinokio",
                    "hint": "pinokio_api_scan",
                })

    if "github_mirrors" in sources:
        root = AI_DATA / "github"
        if root.is_dir():
            for child in sorted(root.iterdir())[:500]:
                if not child.is_dir():
                    continue
                if not VIDEO_HINTS.search(child.name):
                    continue
                resolved = str(child)
                if resolved in known_paths:
                    continue
                candidates.append({
                    "id": child.name.lower().replace("-", "_")[:40],
                    "name": child.name,
                    "path": resolved,
                    "source": "github_mirrors",
                    "hint": "github_pool_scan",
                })

    if "catalog_gaps" in sources:
        from providers import load_catalog

        cat = load_catalog()
        for t in cat.get("pull_targets_not_on_pool") or []:
            candidates.append({
                "id": t.get("id"),
                "name": t.get("id"),
                "url": t.get("url"),
                "source": "catalog_gaps",
                "hint": t.get("via"),
                "roles": t.get("roles"),
            })

    # de-dupe by id
    seen = set()
    unique = []
    for c in candidates:
        cid = str(c.get("id"))
        if cid in seen:
            continue
        seen.add(cid)
        unique.append(c)
        if len(unique) >= limit:
            break

    return {
        "ok": True,
        "ts": _utc(),
        "count": len(unique),
        "candidates": unique,
        "sources": sorted(sources),
    }


def _git_audit(path: Path) -> dict[str, Any]:
    repo = path
    if not (path / ".git").is_dir() and (path / "app" / ".git").is_dir():
        repo = path / "app"
    if not (repo / ".git").exists() and not (path / ".git").is_dir():
        return {"ok": False, "error": "not_a_git_repo", "path": str(path)}

    def run(args: list[str]) -> str:
        try:
            p = subprocess.run(
                ["git", "-C", str(repo), *args],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return (p.stdout or p.stderr or "").strip()
        except Exception as exc:
            return f"err:{exc}"

    porcelain = run(["status", "--porcelain"])
    head = run(["rev-parse", "HEAD"])[:12]
    branch = run(["rev-parse", "--abbrev-ref", "HEAD"])
    # unmerged
    unmerged = [ln for ln in porcelain.splitlines() if ln.startswith("UU") or ln.startswith("AA")]
    dirty_n = len([ln for ln in porcelain.splitlines() if ln.strip()])
    behind = run(["rev-list", "--count", "HEAD..@{u}"]) if "@{u}" in run(["status", "-sb"]) or True else "?"
    try:
        behind_n = int(run(["rev-list", "--count", "HEAD..@{u}"]))
    except Exception:
        behind_n = None

    pull_safe = dirty_n == 0 and not unmerged and (behind_n is None or behind_n >= 0)
    if unmerged:
        pull_safe = False
    if dirty_n > 0:
        pull_safe = False

    return {
        "ok": True,
        "path": str(repo),
        "head": head,
        "branch": branch,
        "dirty_count": dirty_n,
        "unmerged": unmerged[:10],
        "behind": behind_n,
        "pull_safe": pull_safe and not unmerged,
        "pinokio_wrapper_dirty": dirty_n > 0 and any(
            x in porcelain for x in ("install.js", "reset.js", "start.js")
        ),
    }


def audit(
    target: str,
    *,
    trivy: bool = False,
    docker: bool = False,
    osv: bool = False,
) -> dict[str, Any]:
    """Audit a catalog id, filesystem path, or URL (path-only for URL)."""
    from providers import app_by_id, resolve_app_path

    path: Path | None = None
    app = app_by_id(target)
    if app:
        path = resolve_app_path(app)
    elif Path(target).exists():
        path = Path(target)
    elif target.startswith("http"):
        return {
            "ok": True,
            "status": "url_only",
            "url": target,
            "checks": {
                "git": {"ok": False, "error": "clone_not_performed"},
                "note": "Stage as earmark; clone via pinokio/github staging before pull",
            },
            "verdict": "earmark",
        }
    else:
        return {"ok": False, "error": "unknown_target", "target": target}

    checks: dict[str, Any] = {}
    if path and path.exists():
        checks["git"] = _git_audit(path)
        # Dockerfiles present?
        dfs = list(path.rglob("Dockerfile"))[:20] if path.is_dir() else []
        checks["dockerfiles"] = {"count": len(dfs), "samples": [str(p.relative_to(path)) for p in dfs[:5]]}
    else:
        checks["git"] = {"ok": False, "error": "path_missing", "path": str(path)}

    # Optional external tools (earmarks — run if binary/script exists)
    if docker and SCAN_DOCKER.is_file() and path:
        checks["docker_scan"] = {
            "ok": True,
            "status": "earmark",
            "script": str(SCAN_DOCKER),
            "note": "Run manually: bash scan-all-dockerfiles.sh (repo-wide). Scoped scan TBD.",
        }
    if trivy:
        trivy_bin = subprocess.run(["which", "trivy"], capture_output=True, text=True)
        if trivy_bin.returncode == 0 and path:
            try:
                proc = subprocess.run(
                    ["trivy", "fs", "--severity", "HIGH,CRITICAL", "--exit-code", "0", str(path)],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                checks["trivy"] = {
                    "ok": proc.returncode == 0,
                    "stdout_tail": (proc.stdout or "")[-1500:],
                    "stderr_tail": (proc.stderr or "")[-400:],
                }
            except Exception as exc:
                checks["trivy"] = {"ok": False, "error": str(exc)}
        else:
            checks["trivy"] = {"ok": False, "status": "earmark", "note": "trivy not installed"}
    if osv:
        osv_bin = subprocess.run(["which", "osv-scanner"], capture_output=True, text=True)
        if osv_bin.returncode == 0 and path:
            try:
                proc = subprocess.run(
                    ["osv-scanner", "-r", str(path)],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                checks["osv"] = {
                    "ok": proc.returncode in (0, 1),
                    "stdout_tail": (proc.stdout or "")[-1500:],
                }
            except Exception as exc:
                checks["osv"] = {"ok": False, "error": str(exc)}
        else:
            checks["osv"] = {
                "ok": False,
                "status": "earmark",
                "note": "osv-scanner not installed; see supafix github_scanner / grokcode staging",
            }

    git = checks.get("git") or {}
    if git.get("unmerged"):
        verdict = "block_conflict"
    elif not git.get("ok"):
        verdict = "block_missing"
    elif git.get("pull_safe"):
        verdict = "pull_ok"
    elif git.get("pinokio_wrapper_dirty"):
        verdict = "prefer_nested_or_skip"
    elif git.get("dirty_count", 0) > 50:
        verdict = "skip_very_dirty"
    elif git.get("dirty_count", 0) > 0:
        verdict = "skip_dirty"
    else:
        verdict = "review"

    return {
        "ok": True,
        "target": target,
        "path": str(path) if path else None,
        "checks": checks,
        "verdict": verdict,
        "ts": _utc(),
        "staging_tool": str(STAGING_SCRIPT) if STAGING_SCRIPT.is_file() else None,
    }


def stage_candidate(
    candidate_id: str,
    *,
    promote: bool = False,
    force_earmark: bool = False,
) -> dict[str, Any]:
    """Append to pull_targets_not_on_pool (earmark) or note promote path.

    Promote (write into apps[]) is deliberate and requires clean audit — still
    writes an earmark proposal file rather than auto-editing catalog unless promote.
    """
    disc = discover(source="all", limit=200)
    cand = next((c for c in disc["candidates"] if c.get("id") == candidate_id), None)
    if not cand and not force_earmark:
        # allow staging known catalog gap by id
        from providers import load_catalog

        cat = load_catalog()
        cand = next((t for t in (cat.get("pull_targets_not_on_pool") or []) if t.get("id") == candidate_id), None)
        if cand:
            cand = {**cand, "source": "catalog_gaps"}
    if not cand:
        return {"ok": False, "error": "candidate_not_found", "id": candidate_id}

    audit_r = audit(str(cand.get("path") or cand.get("url") or candidate_id))
    if audit_r.get("verdict") in ("block_conflict",) and not force_earmark:
        return {"ok": False, "error": "audit_blocked", "audit": audit_r}

    proposal = {
        "ts": _utc(),
        "id": candidate_id,
        "candidate": cand,
        "audit_verdict": audit_r.get("verdict"),
        "promote": promote,
        "action": "promote_to_apps" if promote else "earmark_pull_target",
    }
    out_dir = ROOT / "work" / "staging"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"stage_{candidate_id}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    path.write_text(json.dumps(proposal, indent=2) + "\n", encoding="utf-8")

    # If earmark and not already in catalog gaps, append to catalog file
    if not promote:
        cat_path = CONFIG_DIR / "director_stack_catalog.json"
        cat = json.loads(cat_path.read_text(encoding="utf-8"))
        gaps = cat.setdefault("pull_targets_not_on_pool", [])
        if not any(g.get("id") == candidate_id for g in gaps):
            gaps.append({
                "id": candidate_id,
                "url": cand.get("url") or cand.get("path"),
                "via": cand.get("source") or "discover",
                "roles": cand.get("roles") or ["discovered"],
            })
            cat_path.write_text(json.dumps(cat, indent=2) + "\n", encoding="utf-8")
            proposal["catalog_updated"] = str(cat_path)
        else:
            proposal["catalog_updated"] = False

    return {"ok": True, "proposal": proposal, "path": str(path), "audit": audit_r}
