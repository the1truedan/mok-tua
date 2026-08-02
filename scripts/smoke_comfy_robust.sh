#!/usr/bin/env bash
# ROBUST capability smoke for mok-tua Comfy worker (object_info + roster).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
COMFY_URL="${COMFY_gpu-host_URL:-${COMFY_URL:-http://REDACTED-LAN-IP:8188}}"
ROSTER="${ROOT}/config/comfy_nodes_mok_tua_roster.json"
CN="${COMFY_CUSTOM_NODES:-/Volumes/ai-data/comfyui/custom_nodes}"
# On gpu-host:
if [ ! -d "$CN" ] && [ -d /mnt/ai-data/comfyui/custom_nodes ]; then
  CN=/mnt/ai-data/comfyui/custom_nodes
fi
OUT_DIR="${WORK_FALLBACK:-$ROOT/work}/smoke"
mkdir -p "$OUT_DIR"
STAMP=$(date -u +%Y-%m-%d)
OUT_JSON="${OUT_DIR}/comfy_robust_smoke_${STAMP}.json"

python3 - <<PY
import json, os, sys, urllib.request
from pathlib import Path
from datetime import datetime, timezone

comfy = os.environ.get("COMFY_URL", "$COMFY_URL")
roster_path = Path("$ROSTER")
cn = Path("$CN")
out_path = Path("$OUT_JSON")

roster = json.loads(roster_path.read_text()) if roster_path.is_file() else {}
required = roster.get("required_have") or []
install_now = [x["id"] for x in (roster.get("install_now") or [])]
avoid = [x["id"] for x in (roster.get("avoid") or [])]
keys = roster.get("smoke_object_info_keys") or []

def http_json(url, timeout=20):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read().decode())

report = {
    "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "comfy_url": comfy,
    "custom_nodes_root": str(cn),
    "checks": [],
    "summary": {},
}

# system
try:
    stats = http_json(comfy.rstrip("/") + "/system_stats", timeout=8)
    report["comfyui_version"] = (stats.get("system") or {}).get("comfyui_version")
    report["checks"].append({"name": "system_stats", "status": "PASS", "detail": report["comfyui_version"]})
except Exception as e:
    report["checks"].append({"name": "system_stats", "status": "FAIL", "detail": str(e)})
    report["summary"] = {"ok": False, "hard_fail": True}
    out_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["summary"]))
    sys.exit(1)

# disk presence
for name in required + install_now:
    disabled = (cn / f"{name}.DISABLED_MOK_TUA").is_dir() or (cn / f"{name}.DISABLED_DUP").is_dir()
    present = (cn / name).is_dir()
    if present:
        st = "PASS"
        det = "present"
    elif disabled and name in avoid:
        st = "PASS"
        det = "disabled_as_planned"
    elif name in avoid:
        st = "SKIP"
        det = "avoid_list_absent"
    else:
        st = "FAIL"
        det = "missing"
    report["checks"].append({"name": f"disk:{name}", "status": st, "detail": det})

# avoid should not be active
for name in avoid:
    if (cn / name).is_dir() and not str(name).endswith("DISABLED"):
        report["checks"].append({"name": f"avoid_active:{name}", "status": "FAIL", "detail": "should be disabled"})
    else:
        report["checks"].append({"name": f"avoid_ok:{name}", "status": "PASS", "detail": "not_active"})

# object_info
try:
    oi = http_json(comfy.rstrip("/") + "/object_info", timeout=30)
    report["nodes_total"] = len(oi)
    for k in keys:
        hits = [x for x in oi if k == x or k.lower() in x.lower()]
        # ColorMatch soft
        ok = bool(hits) or (k == "ColorMatch" and any("ColorMatch" in x for x in oi))
        if k == "INTConstant":
            ok = any(x == "INTConstant" or x.startswith("INTConstant") for x in oi) or any("KJ" in x for x in list(oi)[:5])
            # KJNodes often registers INTConstant exactly
            ok = "INTConstant" in oi or any("Constant" in x and "INT" in x for x in oi)
        report["checks"].append({
            "name": f"node:{k}",
            "status": "PASS" if ok else "FAIL",
            "detail": (hits[:2] if hits else "missing"),
        })
    # KJNodes signal
    kj = "INTConstant" in oi or any("ImageResizeKJv2" in x or x.startswith("Something") for x in oi)
    # broader
    kj = any(
        x in oi for x in ("INTConstant", "FloatConstant", "ConditioningSetMaskAndCombine", "ImageResizeKJv2", "GetImageRangeFromBatch")
    ) or any("KJ" in x for x in oi)
    report["checks"].append({"name": "kjnodes_loaded", "status": "PASS" if kj else "FAIL", "detail": "scan"})
except Exception as e:
    report["checks"].append({"name": "object_info", "status": "FAIL", "detail": str(e)})

pass_n = sum(1 for c in report["checks"] if c["status"] == "PASS")
fail_n = sum(1 for c in report["checks"] if c["status"] == "FAIL")
skip_n = sum(1 for c in report["checks"] if c["status"] == "SKIP")
hard = any(c["name"] == "system_stats" and c["status"] == "FAIL" for c in report["checks"])
report["summary"] = {
    "ok": fail_n == 0 and not hard,
    "pass": pass_n,
    "fail": fail_n,
    "skip": skip_n,
    "hard_fail": hard,
}
out_path.write_text(json.dumps(report, indent=2) + "\n")
print(f"mok-tua comfy robust smoke ok={report['summary']['ok']} pass={pass_n} fail={fail_n} skip={skip_n}")
for c in report["checks"]:
    if c["status"] == "FAIL":
        print(f"  FAIL {c['name']}: {c.get('detail')}")
print(f"wrote {out_path}")
sys.exit(0 if report["summary"]["ok"] else 1)
PY
