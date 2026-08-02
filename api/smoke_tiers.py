"""T0–T4 smoke scorecard for mok-tua director stack."""

from __future__ import annotations

import json
import os
import socket
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = Path(os.environ.get("MOCK_TUA_CONFIG", ROOT / "config"))
WORK = Path(os.environ.get("WORK_FALLBACK", ROOT / "work"))
SMOKE_DIR = WORK / "smoke"
AI_DATA = Path(os.environ.get("AI_DATA_ROOT", "/Volumes/ai-data"))
API_BASE = os.environ.get("MOCK_TUA_URL", "http://127.0.0.1:8799")
COMFY_gpu-host = os.environ.get("COMFY_gpu-host_URL", "http://REDACTED-LAN-IP:8188")
COMFY_LOCAL = os.environ.get("COMFY_LOCAL_URL", "http://127.0.0.1:8188")

# Minimal Comfy object_info keys for T4 storyboard/video path
T4_NODE_KEYS = [
    "VHS_LoadVideo",
    "VHS_VideoCombine",
    "DWPreprocessor",
    "OpenposePreprocessor",
    "IPAdapterModelLoader",
    "ADE_AnimateDiffLoaderGen1",
    "ADE_AnimateDiffLoaderV1Advanced",
    "KSampler",
]


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _tcp(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _http_json(url: str, timeout: float = 4.0) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return {"ok": True, "status": resp.status, "data": json.loads(body) if body.startswith("{") or body.startswith("[") else body[:200]}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200]}


def _check(name: str, ok: bool, detail: str = "", *, hard: bool = False) -> dict[str, Any]:
    return {
        "name": name,
        "status": "PASS" if ok else "FAIL",
        "ok": ok,
        "detail": detail,
        "hard": hard,
    }


def _skip(name: str, detail: str) -> dict[str, Any]:
    return {"name": name, "status": "SKIP", "ok": True, "detail": detail, "hard": False}


def smoke_t0() -> list[dict[str, Any]]:
    checks = []
    cat_path = CONFIG_DIR / "director_stack_catalog.json"
    checks.append(_check("catalog_json", cat_path.is_file(), str(cat_path), hard=True))
    if cat_path.is_file():
        cat = json.loads(cat_path.read_text(encoding="utf-8"))
        apps = cat.get("apps") or []
        checks.append(_check("catalog_apps", len(apps) >= 5, f"count={len(apps)}"))
        tiers = cat.get("tiers") or {}
        checks.append(_check("tiers_defined", all(k in tiers for k in (
            "T0_orchestrators", "T1_vid_gen", "T2_audio_music", "T3_face_body", "T4_comfy_graphs"
        )), f"keys={list(tiers.keys())}"))

    hz = _http_json(f"{API_BASE}/healthz", timeout=2.0)
    checks.append(_check("api_healthz", hz.get("ok") is True, hz.get("error") or "up", hard=False))

    # directors_console ports (may be down — soft unless we required launch)
    for port, label in ((5173, "ui"), (9800, "cpe"), (9820, "orch")):
        ok = _tcp("127.0.0.1", port)
        checks.append(_check(f"directors_console_{label}", ok, f"127.0.0.1:{port}"))

    # path present
    dc = AI_DATA / "pinokio/api/directorsconsole.pinokio.git"
    checks.append(_check("directors_console_path", dc.is_dir(), str(dc)))
    return checks


def smoke_t1() -> list[dict[str, Any]]:
    checks = []
    for url, label in ((COMFY_gpu-host, "gpu-host"), (COMFY_LOCAL, "local")):
        r = _http_json(f"{url}/system_stats", timeout=3.0)
        detail = ""
        if r.get("ok") and isinstance(r.get("data"), dict):
            sys_ = (r["data"] or {}).get("system") or {}
            detail = f"comfy={sys_.get('comfyui_version')} ram_free={sys_.get('ram_free')}"
        else:
            detail = r.get("error") or "down"
        # gpu-host is hard for video path; local soft
        checks.append(_check(f"comfy_{label}", r.get("ok") is True, detail, hard=(label == "gpu-host")))

    wan = AI_DATA / "pinokio/api/wan2gp.git"
    checks.append(_check("wan2gp_path", wan.is_dir(), str(wan)))
    # Gradio range soft
    gradio = any(_tcp("127.0.0.1", p) for p in range(7860, 7870))
    checks.append(_check("wan2gp_or_gradio_live", gradio, "ports 7860-7869") if gradio else _skip("wan2gp_or_gradio_live", "not running (path-only ok)"))

    pkg = AI_DATA / "stability-matrix/mac-Data/Packages"
    fp: list[Path] = []
    if pkg.is_dir():
        try:
            fp = [p for p in pkg.iterdir() if p.is_dir() and "framepack" in p.name.lower()]
        except OSError:
            fp = []
    # soft: FramePack is optional long-form; path miss is not hard-fail
    if fp:
        checks.append(_check("framepack_path", True, str(fp[0])))
    else:
        checks.append(_skip("framepack_path", f"no FramePack* under {pkg} (optional)"))
    return checks


def smoke_t2() -> list[dict[str, Any]]:
    checks = []
    for rel, name in (
        ("pinokio/api/ace-step.pinokio.git", "ace_step"),
        ("pinokio/api/TTS-Story.git", "tts_story"),
        ("pinokio/api/Qwen3-TTS-Pinokio.git", "qwen3_tts"),
    ):
        p = AI_DATA / rel
        checks.append(_check(f"{name}_path", p.is_dir(), str(p)))
    return checks


def smoke_t3() -> list[dict[str, Any]]:
    checks = []
    for rel, name in (
        ("pinokio/api/facefusion-pinokio.git", "facefusion"),
        ("pinokio/api/FreeMoCap.pinokio.git", "freemocap"),
        ("pinokio/api/dreamtalk.git", "dreamtalk"),
        ("models/liveportrait", "liveportrait_models"),
        ("models/insightface", "insightface_models"),
        ("models/controlnet", "openpose_controlnet"),
    ):
        p = AI_DATA / rel
        ok = p.exists()
        detail = str(p)
        if ok and p.is_dir():
            try:
                n = sum(1 for _ in p.iterdir())
                detail = f"{p} entries≈{n}"
            except OSError:
                pass
        checks.append(_check(f"{name}_path", ok, detail))
    return checks


def smoke_t4() -> list[dict[str, Any]]:
    checks = []
    cat_path = CONFIG_DIR / "director_stack_catalog.json"
    globs = []
    if cat_path.is_file():
        cat = json.loads(cat_path.read_text(encoding="utf-8"))
        globs = cat.get("sm_workflow_pins_bleed") or []
    wf_root = AI_DATA / "stability-matrix/mac-Data/Workflows"
    present = 0
    samples = []
    if wf_root.is_dir() and globs:
        for g in globs:
            hits = list(wf_root.glob(g))
            if hits:
                present += 1
                samples.append(hits[0].name)
        checks.append(_check("sm_workflow_pins", present >= max(1, len(globs) // 3), f"{present}/{len(globs)} globs hit; e.g. {samples[:3]}"))
    else:
        checks.append(_skip("sm_workflow_pins", f"workflows root missing or no globs: {wf_root}"))

    # Comfy nodes via object_info (subset)
    r = _http_json(f"{COMFY_gpu-host}/object_info", timeout=8.0)
    if not r.get("ok"):
        checks.append(_check("comfy_object_info", False, r.get("error") or "unreachable", hard=True))
        return checks
    data = r.get("data") if isinstance(r.get("data"), dict) else {}
    found = []
    missing = []
    for key in T4_NODE_KEYS:
        # fuzzy: ADE has multiple names
        if key in data:
            found.append(key)
        else:
            # partial match
            hit = any(key.split("_")[0] in k for k in data if key.startswith("ADE") and "AnimateDiff" in k)
            if hit or any(k == key for k in data):
                found.append(key)
            else:
                # broader: any key containing core token
                token = key.replace("ADE_", "").split("_")[0]
                if any(token in k for k in data):
                    found.append(key)
                else:
                    missing.append(key)
    # soften AnimateDiff dual names
    ad_ok = any("AnimateDiff" in k for k in data)
    ipa_ok = any("IPAdapter" in k for k in data)
    vhs_ok = any(k.startswith("VHS_") for k in data)
    checks.append(_check("nodes_VHS", vhs_ok, f"count≈{sum(1 for k in data if k.startswith('VHS_'))}"))
    checks.append(_check("nodes_AnimateDiff", ad_ok, "ADE present" if ad_ok else "missing"))
    checks.append(_check("nodes_IPAdapter", ipa_ok, "IPAdapter present" if ipa_ok else "missing"))
    checks.append(_check("nodes_pose", any(x in data for x in ("DWPreprocessor", "OpenposePreprocessor")), "DW/OpenPose"))
    checks.append(_check("comfy_node_catalog_size", len(data) > 100, f"nodes={len(data)}"))
    if missing:
        checks.append(_skip("exact_node_keys", f"fuzzy missing: {missing[:6]}"))
    return checks


def run_smoke(tiers: list[str] | None = None) -> dict[str, Any]:
    order = ["T0", "T1", "T2", "T3", "T4"]
    want = {t.upper().replace("T0_ORCHESTRATORS", "T0") for t in (tiers or order)}
    # normalize T0_orchestrators etc.
    norm = set()
    for t in want:
        if t.startswith("T0"):
            norm.add("T0")
        elif t.startswith("T1"):
            norm.add("T1")
        elif t.startswith("T2"):
            norm.add("T2")
        elif t.startswith("T3"):
            norm.add("T3")
        elif t.startswith("T4"):
            norm.add("T4")
        else:
            norm.add(t)
    runners = {
        "T0": smoke_t0,
        "T1": smoke_t1,
        "T2": smoke_t2,
        "T3": smoke_t3,
        "T4": smoke_t4,
    }
    by_tier: dict[str, list[dict[str, Any]]] = {}
    all_checks: list[dict[str, Any]] = []
    for t in order:
        if t not in norm:
            continue
        checks = runners[t]()
        by_tier[t] = checks
        all_checks.extend(checks)

    hard_fail = [c for c in all_checks if c.get("hard") and not c.get("ok")]
    soft_fail = [c for c in all_checks if not c.get("hard") and c.get("status") == "FAIL"]
    pass_n = sum(1 for c in all_checks if c.get("status") == "PASS")
    skip_n = sum(1 for c in all_checks if c.get("status") == "SKIP")
    fail_n = sum(1 for c in all_checks if c.get("status") == "FAIL")

    report = {
        "ok": len(hard_fail) == 0,
        "ts": _utc(),
        "api_base": API_BASE,
        "comfy_gpu-host": COMFY_gpu-host,
        "summary": {
            "pass": pass_n,
            "fail": fail_n,
            "skip": skip_n,
            "hard_fail": len(hard_fail),
            "total": len(all_checks),
        },
        "tiers": by_tier,
        "hard_failures": hard_fail,
        "soft_failures": soft_fail,
    }

    SMOKE_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_path = SMOKE_DIR / f"tier_smoke_{stamp}.json"
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    report["path"] = str(out_path)
    return report


def format_smoke_table(report: dict[str, Any]) -> str:
    lines = [
        f"mok-tua T0–T4 smoke  ok={report.get('ok')}  "
        f"pass={report['summary']['pass']} fail={report['summary']['fail']} "
        f"skip={report['summary']['skip']} hard_fail={report['summary']['hard_fail']}",
        "",
    ]
    for tier, checks in (report.get("tiers") or {}).items():
        lines.append(f"== {tier} ==")
        for c in checks:
            mark = {"PASS": "✓", "FAIL": "✗", "SKIP": "·"}.get(c["status"], "?")
            hard = " [HARD]" if c.get("hard") and c["status"] == "FAIL" else ""
            lines.append(f"  {mark} {c['name']:<32} {c['status']:<4}{hard}  {c.get('detail') or ''}"[:120])
        lines.append("")
    if report.get("path"):
        lines.append(f"wrote {report['path']}")
    return "\n".join(lines)
