"""Right-rail stack / host stats for conductor TUI."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from tui.petscii import vic_bar

ROOT = Path(__file__).resolve().parents[1]


def _http_json(url: str, timeout: float = 1.2) -> dict[str, Any] | None:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))
    except Exception:
        return None


def sample_gpu_host() -> dict[str, Any]:
    """Best-effort host_monitor sample (api on path)."""
    try:
        import sys

        api = str(ROOT / "api")
        if api not in sys.path:
            sys.path.insert(0, api)
        from host_monitor import sample_host

        return sample_host("gpu-host")
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def sample_local_cpu() -> dict[str, Any]:
    out: dict[str, Any] = {"ok": True, "role": "desk-host"}
    try:
        load1, load5, load15 = os.getloadavg()
        out["load1"] = load1
        out["load5"] = load5
        out["load15"] = load15
    except OSError:
        out["ok"] = False
    try:
        import psutil  # type: ignore

        out["cpu_pct"] = psutil.cpu_percent(interval=0.05)
        mem = psutil.virtual_memory()
        out["ram_used_gb"] = round(mem.used / (1024**3), 1)
        out["ram_total_gb"] = round(mem.total / (1024**3), 1)
        out["ram_pct"] = mem.percent
    except Exception:
        # stdlib fallback: no cpu%
        pass
    return out


def probe_api() -> str:
    port = int(os.environ.get("MOK_TUA_PORT", "8799"))
    data = _http_json(f"http://127.0.0.1:{port}/healthz")
    if data is None:
        data = _http_json(f"http://127.0.0.1:{port}/v1/info")
    if data is None:
        return f"API :{port}  DOWN"
    return f"API :{port}  UP"


def format_stats_panel(
    *,
    gpu_sample: dict[str, Any] | None = None,
    local: dict[str, Any] | None = None,
    last_receipt_line: str | None = None,
    skin: str = "c64",
) -> str:
    gpu_sample = gpu_sample if gpu_sample is not None else sample_gpu_host()
    local = local if local is not None else sample_local_cpu()

    lines: list[str] = []
    if skin in ("c64", "1980crt", "tui-c64-mode-default-1980crt-tui"):
        lines.append("**** SYSTEM STATS ****")
        lines.append(" gpu-host · VIC-II BARS")
    else:
        lines.append("SYSTEM STATS")
        lines.append("gpu-host / desk-host")
    lines.append("────────────────────")

    if gpu_sample.get("ok"):
        gutil = gpu_sample.get("gpu_util_pct")
        gtemp = gpu_sample.get("gpu_temp_c")
        gmu = gpu_sample.get("gpu_mem_used_mib")
        gmt = gpu_sample.get("gpu_mem_total_mib")
        lines.append(f"GPU  {vic_bar(gutil)}")
        if gmu is not None and gmt:
            vram_pct = 100.0 * float(gmu) / float(gmt) if gmt else None
            lines.append(f"VRAM {vic_bar(vram_pct)}")
            lines.append(f"     {gmu:.0f}/{gmt:.0f} MiB")
        elif gmu is not None:
            lines.append(f"VRAM {gmu:.0f} MiB")
        if gtemp is not None:
            lines.append(f"TEMP {gtemp:.0f}°C")
        load = gpu_sample.get("load1")
        if load is not None:
            # map load to soft bar (0–16 → 0–100 heuristic)
            load_pct = min(100.0, float(load) / 16.0 * 100.0)
            lines.append(f"LOAD {vic_bar(load_pct)}")
            lines.append(f"     load1 {load:.2f}")
        ram_u = gpu_sample.get("ram_used_gb")
        ram_t = gpu_sample.get("ram_total_gb")
        if ram_u is not None and ram_t:
            ram_pct = 100.0 * float(ram_u) / float(ram_t)
            lines.append(f"RAM  {vic_bar(ram_pct)}")
            lines.append(f"     {ram_u:.0f}/{ram_t:.0f} G")
        src = gpu_sample.get("source") or "sample"
        lines.append(f"src  {src}")
    else:
        err = gpu_sample.get("error") or "unreachable"
        lines.append("GPU  offline / n/a")
        lines.append(f"     {err[:36]}")

    lines.append("────────────────────")
    lines.append("DESK (this host)")
    if local.get("ok") is not False:
        if local.get("cpu_pct") is not None:
            lines.append(f"CPU  {vic_bar(float(local['cpu_pct']))}")
        if local.get("ram_pct") is not None:
            lines.append(f"RAM  {vic_bar(float(local['ram_pct']))}")
        elif local.get("ram_used_gb") is not None:
            lines.append(
                f"RAM  {local.get('ram_used_gb')}/{local.get('ram_total_gb')} G"
            )
        if local.get("load1") is not None:
            lines.append(f"load {local['load1']:.2f}")
    else:
        lines.append("CPU  n/a")

    lines.append("────────────────────")
    lines.append(probe_api())
    if last_receipt_line:
        lines.append("────────────────────")
        lines.append("LAST RECEIPT")
        # wrap caption
        cap = last_receipt_line
        while cap:
            lines.append(cap[:36])
            cap = cap[36:]

    lines.append("────────────────────")
    lines.append("THUMBS: show · play")
    return "\n".join(lines)
