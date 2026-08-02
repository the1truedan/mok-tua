"""Stage models/workflows into allowlisted ai-data models subfolders."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = Path(os.environ.get("MOCK_TUA_CONFIG", ROOT / "config"))


def models_root() -> Path:
    env = os.environ.get("MOCK_TUA_MODELS_ROOT") or os.environ.get("AI_DATA_MODELS")
    if env:
        return Path(env)
    for cand in (
        Path("/Volumes/ai-data/models"),
        Path("/mnt/ai-data/models"),
        Path("/ai-data/models"),
    ):
        if cand.is_dir():
            return cand
    p = ROOT / "work" / "models"
    p.mkdir(parents=True, exist_ok=True)
    return p


def load_manifest(path: Path | str | None = None) -> dict[str, Any]:
    p = Path(path) if path else CONFIG_DIR / "stage_manifest.yaml"
    if not p.is_file():
        return {"items": [], "error": f"manifest_not_found:{p}"}
    if yaml is None:
        return {"items": [], "error": "pyyaml_missing"}
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {"items": []}


def _allow_subdirs(manifest: dict[str, Any]) -> set[str]:
    return set(manifest.get("allow_subdirs") or ["loras", "diffusion_models", "vae", "text_encoders"])


def _safe_dest(pool: Path, subdir: str, name: str, allowed: set[str]) -> Path:
    sub = subdir.strip("/").replace("..", "")
    if sub not in allowed:
        raise ValueError(f"dest_subdir not allowlisted: {sub}")
    dest_name = Path(name).name
    if ".." in dest_name or dest_name.startswith("/"):
        raise ValueError(f"bad dest_name: {name}")
    dest_dir = pool / sub
    dest_dir.mkdir(parents=True, exist_ok=True)
    return dest_dir / dest_name


def _hf_download(repo: str, file: str, dest: Path, *, dry_run: bool) -> dict[str, Any]:
    hf = shutil.which("hf") or str(Path.home() / ".local/bin/hf")
    if not Path(hf).is_file() and shutil.which("huggingface-cli"):
        # older CLI
        cmd = [
            "huggingface-cli",
            "download",
            repo,
            file,
            "--local-dir",
            str(dest.parent / f"_hf_{repo.replace('/', '_')}"),
        ]
    else:
        stage = dest.parent / f"_hf_stage_{repo.replace('/', '_')}"
        cmd = [hf, "download", repo, file, "--local-dir", str(stage)]
    if dry_run:
        return {"ok": True, "status": "dry_run", "cmd": cmd, "dest": str(dest)}
    stage_dir = Path(cmd[-1])
    stage_dir.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=int(os.environ.get("MOCK_TUA_HF_TIMEOUT", "7200")))
    if proc.returncode != 0:
        return {
            "ok": False,
            "status": "hf_failed",
            "cmd": cmd,
            "stderr": (proc.stderr or "")[-800:],
            "stdout": (proc.stdout or "")[-400:],
        }
    # find downloaded file under stage
    candidates = list(stage_dir.rglob(Path(file).name))
    if not candidates:
        # nested split_files path
        candidates = list(stage_dir.rglob(Path(file).name))
    if not candidates:
        return {"ok": False, "status": "file_not_found_after_download", "stage": str(stage_dir)}
    src = candidates[0]
    if dest.exists() and dest.stat().st_size == src.stat().st_size:
        return {"ok": True, "status": "already_present", "dest": str(dest), "bytes": dest.stat().st_size}
    shutil.copy2(src, dest)
    return {"ok": True, "status": "staged", "dest": str(dest), "bytes": dest.stat().st_size, "from": str(src)}


def stage_item(item: dict[str, Any], *, pool: Path, allowed: set[str], dry_run: bool = True) -> dict[str, Any]:
    iid = item.get("id") or "unknown"
    sub = str(item.get("dest_subdir") or "loras")
    name = str(item.get("dest_name") or Path(str((item.get("source") or {}).get("file") or "model.bin")).name)
    try:
        dest = _safe_dest(pool, sub, name, allowed)
    except ValueError as exc:
        return {"id": iid, "ok": False, "status": "reject", "error": str(exc)}

    if dest.is_file() and dest.stat().st_size > 0 and item.get("skip_if_exists", True):
        return {
            "id": iid,
            "ok": True,
            "status": "already_present",
            "dest": str(dest),
            "bytes": dest.stat().st_size,
        }

    src = item.get("source") or {}
    stype = str(src.get("type") or "hf")

    if stype in ("local_or_hf", "local"):
        rel = src.get("path")
        if rel:
            local = pool / str(rel)
            if local.is_file():
                if dry_run:
                    return {"id": iid, "ok": True, "status": "dry_run_local", "dest": str(local)}
                if local.resolve() != dest.resolve():
                    shutil.copy2(local, dest)
                return {"id": iid, "ok": True, "status": "local_ok", "dest": str(dest), "bytes": dest.stat().st_size}
        if stype == "local":
            return {"id": iid, "ok": False, "status": "local_missing", "path": str(src.get("path"))}
        # fall through to hf if repo provided
        if not src.get("repo"):
            return {"id": iid, "ok": False, "status": "missing", "path": str(src.get("path"))}

    if stype in ("hf", "local_or_hf"):
        repo = src.get("repo")
        file = src.get("file")
        if not repo or not file:
            return {"id": iid, "ok": False, "status": "bad_hf_source", "source": src}
        result = _hf_download(str(repo), str(file), dest, dry_run=dry_run)
        result["id"] = iid
        return result

    return {"id": iid, "ok": False, "status": "unknown_source_type", "type": stype}


def stage_models(
    *,
    manifest_path: Path | str | None = None,
    dry_run: bool = True,
    only_ids: list[str] | None = None,
    required_for: str | None = None,
) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    if manifest.get("error"):
        return {"ok": False, **manifest}
    pool = models_root()
    if manifest.get("pool_root_env") and os.environ.get(str(manifest["pool_root_env"])):
        pool = Path(os.environ[str(manifest["pool_root_env"])])
    allowed = _allow_subdirs(manifest)
    items = list(manifest.get("items") or [])
    if only_ids:
        want = set(only_ids)
        items = [i for i in items if i.get("id") in want]
    if required_for:
        items = [i for i in items if required_for in (i.get("required_for") or []) or not i.get("required_for")]

    results = []
    for item in items:
        if not isinstance(item, dict):
            continue
        results.append(stage_item(item, pool=pool, allowed=allowed, dry_run=dry_run))

    ok = all(r.get("ok") for r in results) if results else True
    missing = [r for r in results if not r.get("ok")]
    present = [r for r in results if r.get("status") in ("already_present", "local_ok", "staged")]
    return {
        "ok": ok,
        "dry_run": dry_run,
        "pool": str(pool),
        "count": len(results),
        "present": len(present),
        "failed": len(missing),
        "results": results,
    }


def inventory_status(*, manifest_path: Path | str | None = None) -> dict[str, Any]:
    return stage_models(manifest_path=manifest_path, dry_run=True)


def stage_workflow_pin(
    pin_name: str,
    *,
    source_path: Path | str | None = None,
    content: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Copy or write an API-format workflow into mok-tua/workflows and return pin meta."""
    wf_dir = ROOT / "workflows"
    wf_dir.mkdir(parents=True, exist_ok=True)
    dest = wf_dir / f"{pin_name}.api.json"
    if content is not None:
        dest.write_text(json.dumps(content, indent=2) + "\n", encoding="utf-8")
        return {"ok": True, "status": "written", "path": str(dest), "node_count": len(content)}
    if source_path:
        src = Path(source_path)
        if not src.is_file():
            return {"ok": False, "status": "source_missing", "path": str(src)}
        data = json.loads(src.read_text(encoding="utf-8"))
        # if UI format, refuse — need API
        if isinstance(data, dict) and "nodes" in data and "last_node_id" in data:
            return {"ok": False, "status": "ui_format_not_api", "path": str(src), "note": "Export Save (API Format) from Comfy"}
        dest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return {"ok": True, "status": "copied", "path": str(dest)}
    return {"ok": False, "status": "need_source_or_content"}
