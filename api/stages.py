"""Staged pipeline: estimate, run, resume, stitch."""

from __future__ import annotations

import json
import os
import time
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

from backends import cloud_stub, comfy, headroom
from story_parse import duration_seconds, parse_story_file, parse_story_markdown

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = Path(os.environ.get("MOCK_TUA_CONFIG", ROOT / "config"))


def _json_default(obj: Any) -> Any:
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def dumps(obj: Any) -> str:
    return json.dumps(obj, indent=2, default=_json_default)


def load_json(name: str) -> dict[str, Any]:
    path = CONFIG_DIR / name
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_pricing() -> dict[str, Any]:
    path = CONFIG_DIR / "pricing.yaml"
    if not path.is_file():
        return {"providers": {}}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {"providers": {}}


def work_root() -> Path:
    env = os.environ.get("WORK_ROOT")
    if env and Path(env).is_dir():
        return Path(env)
    orch = load_json("orchestration.json")
    preferred = (orch.get("outputs") or {}).get("work_root_MAC")
    if preferred and Path(preferred).is_dir():
        return Path(preferred)
    fallback = os.environ.get("WORK_FALLBACK", str(ROOT / "work"))
    p = Path(fallback)
    p.mkdir(parents=True, exist_ok=True)
    return p


def endpoint_url(key: str) -> str:
    orch = load_json("orchestration.json")
    env_map = {
        "mac": os.environ.get("COMFY_MAC_URL"),
        "gpu": os.environ.get("COMFY_GPU_URL"),
        "headroom": os.environ.get("HEADROOM_BASE"),
    }
    if env_map.get(key):
        return str(env_map[key])
    ep = (orch.get("endpoints") or {}).get(key) or {}
    return str(ep.get("base_url") or "")


def estimate_shot(
    duration_s: float,
    *,
    kind: str = "video",
    qqq: str | None = None,
) -> dict[str, Any]:
    pricing = load_pricing()
    providers = pricing.get("providers") or {}
    qqq_cfg = load_json("qqq.json")
    mode = qqq or os.environ.get("MOCK_TUA_QQQ", qqq_cfg.get("default_mode") or "QQQ0")
    allowed = set((qqq_cfg.get("modes") or {}).get(mode, {}).get("backends") or providers.keys())

    results: dict[str, Any] = {}
    for name, cfg in providers.items():
        if allowed and name not in allowed and mode == "QQQ0":
            # QQQ0 only local backends
            if not str(name).startswith("local_"):
                continue
        if mode == "QQQ0" and not str(name).startswith("local_"):
            continue
        if mode == "QQQ3" and str(name).startswith("runpod"):
            continue

        cost = float(cfg.get("cost_usd") or 0.0)
        if kind == "still":
            est_time = float(cfg.get("est_still_sec") or 30)
        else:
            rate = float(cfg.get("est_video_sec_per_s") or 10)
            est_time = max(duration_s, 1.0) * rate
            if cfg.get("on_demand_per_hour"):
                cost = (est_time / 3600.0) * float(cfg["on_demand_per_hour"])
            elif cfg.get("spot_per_hour"):
                cost = (est_time / 3600.0) * float(cfg["spot_per_hour"])

        results[name] = {
            "cost_usd": round(cost, 4),
            "est_time_sec": round(est_time, 1),
            "sla": cfg.get("sla"),
            "notes": cfg.get("notes"),
            "clip_sec_typical": cfg.get("clip_sec_typical"),
            "daily_quota_min": cfg.get("daily_quota_min"),
        }

    prefer = (pricing.get("defaults") or {}).get("prefer") or list(results.keys())
    ordered = [p for p in prefer if p in results] + [k for k in results if k not in prefer]
    return {
        "qqq": mode,
        "kind": kind,
        "duration_s": duration_s,
        "targets": {k: results[k] for k in ordered if k in results},
        "recommended": ordered[0] if ordered else None,
    }


def estimate_story(story: dict[str, Any], *, qqq: str | None = None) -> dict[str, Any]:
    total_dur = 0.0
    per_shot: list[dict[str, Any]] = []
    for scene in story.get("scenes") or []:
        for shot in scene.get("shots") or []:
            fields = shot.get("fields") or {}
            d = duration_seconds(fields.get("duration") or scene.get("fields", {}).get("duration") or 5)
            total_dur += d
            kind = "still" if (fields.get("shot_type") or "video") == "still" else "video"
            est = estimate_shot(d, kind=kind, qqq=qqq)
            per_shot.append({"shot_id": shot.get("id"), "duration_s": d, "estimate": est})
    aggregate = estimate_shot(total_dur or 5.0, kind="video", qqq=qqq)
    return {
        "title": story.get("title") or (story.get("meta") or {}).get("title"),
        "shot_count": story.get("shot_count") or len(per_shot),
        "total_duration_s": total_dur,
        "aggregate": aggregate,
        "per_shot": per_shot,
    }


def _run_dir(run_id: str) -> Path:
    d = work_root() / "runs" / run_id
    d.mkdir(parents=True, exist_ok=True)
    (d / "mac").mkdir(exist_ok=True)
    (d / "gpu").mkdir(exist_ok=True)
    (d / "frames").mkdir(exist_ok=True)
    return d


def create_run_from_markdown(
    text: str,
    *,
    dry_run: bool | None = None,
    qqq: str | None = None,
    live_still: bool | None = None,
    expand_script: str | None = None,
) -> dict[str, Any]:
    if dry_run is None:
        dry_run = os.environ.get("MOCK_TUA_DRY_RUN", "1") not in ("0", "false", "False")
    if live_still is None:
        live_still = os.environ.get("MOCK_TUA_LIVE_STILL", "0") in ("1", "true", "True")

    story = parse_story_markdown(text)
    run_id = time.strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    rdir = _run_dir(run_id)
    (rdir / "story.md").write_text(text, encoding="utf-8")
    (rdir / "story.json").write_text(dumps(story), encoding="utf-8")

    stages: list[dict[str, Any]] = []
    orch = load_json("orchestration.json")
    still_defs = orch.get("still_defaults") or {}

    # S0 optional LLM expand
    if expand_script:
        s0 = headroom.expand_script_to_shots(expand_script, dry_run=dry_run)
        stages.append({"stage": "script_to_shots", "result": s0})
        (rdir / "s0_expand.json").write_text(dumps(s0), encoding="utf-8")

    # estimates
    est = estimate_story(story, qqq=qqq)
    stages.append({"stage": "estimate", "result": est})
    (rdir / "estimate.json").write_text(dumps(est), encoding="utf-8")

    mac_url = endpoint_url("mac")
    gpu_url = endpoint_url("gpu")
    checkpoint = str(still_defs.get("checkpoint") or "DreamShaper_8_pruned.safetensors")

    shot_results: list[dict[str, Any]] = []
    for scene in story.get("scenes") or []:
        for shot in scene.get("shots") or []:
            fields = shot.get("fields") or {}
            prompt = str(fields.get("prompt") or shot.get("title") or "storyboard panel")
            seed = fields.get("seed")
            if isinstance(seed, str) and seed.isdigit():
                seed = int(seed)
            elif not isinstance(seed, int):
                seed = None

            # S1/S2 stills on MAC
            still = comfy.submit_still(
                mac_url,
                prompt,
                checkpoint=checkpoint,
                seed=seed,
                dry_run=dry_run or not live_still,
                host_key="mac",
                width=int(still_defs.get("width") or 768),
                height=int(still_defs.get("height") or 768),
                steps=int(still_defs.get("steps") or 20),
                cfg=float(still_defs.get("cfg") or 7.0),
                filename_prefix=f"mock_tua_{shot.get('id')}",
            )
            stages.append({"stage": "storyboard_panel", "shot_id": shot.get("id"), "result": still})

            # S3 video route (dry by default — push metadata for GPU)
            video_payload = {
                "shot_id": shot.get("id"),
                "host_key": "gpu",
                "base_url": gpu_url,
                "prompt": prompt,
                "duration_s": duration_seconds(fields.get("duration") or 5),
                "status": "dry_run" if dry_run else "planned",
                "ok": True,
                "note": "Video graphs require GPU Comfy + Wan/I2V workflow pin; v1 records plan + probe",
            }
            if not dry_run:
                probe = comfy.probe(gpu_url)
                video_payload["probe"] = probe
                video_payload["ok"] = bool(probe.get("ok"))
                video_payload["status"] = "reachable" if probe.get("ok") else "unreachable"
            stages.append({"stage": "i2v_or_wan_animate", "shot_id": shot.get("id"), "result": video_payload})

            resume = {
                "shot_id": shot.get("id"),
                "workflow_hash": comfy.seed_from_prompt(prompt),
                "last_good_frame": fields.get("last_good_frame"),
                "last_good_path": None,
                "seed": still.get("seed"),
                "backend": "gpu",
                "status": fields.get("status") or "pending",
            }
            shot_results.append(
                {
                    "shot_id": shot.get("id"),
                    "still": still,
                    "video": video_payload,
                    "resume": resume,
                }
            )

    # S5 stitch placeholder
    stitch = {
        "status": "pending",
        "ok": True,
        "note": "Stitch when all shot clips complete; use ffmpeg concat on work/runs/<id>/",
        "output": str(rdir / "final.mp4"),
    }
    stages.append({"stage": "stitch", "result": stitch})

    state = {
        "run_id": run_id,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dry_run": dry_run,
        "live_still": live_still and not dry_run,
        "qqq": qqq or os.environ.get("MOCK_TUA_QQQ", "QQQ0"),
        "title": story.get("title"),
        "shot_count": story.get("shot_count"),
        "run_dir": str(rdir),
        "stages": stages,
        "shots": shot_results,
        "endpoints": {"mac": mac_url, "gpu": gpu_url, "headroom": endpoint_url("headroom")},
    }
    (rdir / "run.json").write_text(dumps(state), encoding="utf-8")
    _append_audit(run_id, {"event": "run_created", "shot_count": state["shot_count"]})
    return state


def resume_shot(run_id: str, shot_id: str, *, last_good_frame: int | None = None) -> dict[str, Any]:
    rdir = work_root() / "runs" / run_id
    run_path = rdir / "run.json"
    if not run_path.is_file():
        return {"ok": False, "error": "run_not_found", "run_id": run_id}
    state = json.loads(run_path.read_text(encoding="utf-8"))
    updated = False
    for shot in state.get("shots") or []:
        if shot.get("shot_id") != shot_id:
            continue
        resume = shot.setdefault("resume", {})
        if last_good_frame is not None:
            resume["last_good_frame"] = last_good_frame
            resume["last_good_path"] = str(rdir / "frames" / f"{last_good_frame:04d}.png")
        resume["status"] = "resume_planned"
        resume["backend"] = "gpu"
        resume["note"] = "Re-queue I2V with start frame = last_good_frame (VideoHelperSuite skip_first_frames)"
        updated = True
        break
    if not updated:
        return {"ok": False, "error": "shot_not_found", "shot_id": shot_id}
    state["stages"].append(
        {
            "stage": "resume_segment",
            "shot_id": shot_id,
            "result": {"ok": True, "last_good_frame": last_good_frame},
        }
    )
    run_path.write_text(dumps(state), encoding="utf-8")
    _append_audit(run_id, {"event": "resume", "shot_id": shot_id, "last_good_frame": last_good_frame})
    return {"ok": True, "run_id": run_id, "shot_id": shot_id, "state": state}


def load_run(run_id: str) -> dict[str, Any]:
    run_path = work_root() / "runs" / run_id / "run.json"
    if not run_path.is_file():
        return {"ok": False, "error": "run_not_found"}
    return {"ok": True, "run": json.loads(run_path.read_text(encoding="utf-8"))}


def list_runs(limit: int = 20) -> list[dict[str, Any]]:
    root = work_root() / "runs"
    if not root.is_dir():
        return []
    rows = []
    for p in sorted(root.iterdir(), reverse=True):
        if not p.is_dir():
            continue
        rp = p / "run.json"
        if not rp.is_file():
            continue
        try:
            data = json.loads(rp.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        rows.append(
            {
                "run_id": data.get("run_id") or p.name,
                "title": data.get("title"),
                "shot_count": data.get("shot_count"),
                "dry_run": data.get("dry_run"),
                "created_at": data.get("created_at"),
            }
        )
        if len(rows) >= limit:
            break
    return rows


def health() -> dict[str, Any]:
    mac = comfy.probe(endpoint_url("mac"))
    gpu = comfy.probe(endpoint_url("gpu"))
    return {
        "ok": True,
        "service": "mock-tua-api",
        "work_root": str(work_root()),
        "comfy_mac": mac,
        "comfy_gpu": gpu,
        "headroom": endpoint_url("headroom"),
        "qqq": os.environ.get("MOCK_TUA_QQQ", "QQQ0"),
        "dry_run": os.environ.get("MOCK_TUA_DRY_RUN", "1") not in ("0", "false"),
    }


def _append_audit(run_id: str, event: dict[str, Any]) -> None:
    path = work_root() / "runs" / run_id / "audit.jsonl"
    event = {**event, "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, default=_json_default) + "\n")


def create_run_from_file(path: Path | str, **kwargs: Any) -> dict[str, Any]:
    text = Path(path).read_text(encoding="utf-8")
    return create_run_from_markdown(text, **kwargs)
