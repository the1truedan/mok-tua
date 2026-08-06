"""MRGPU (and local) host resource sampling for pulls / loading profiles.

Prefers Prometheus exporters from grokcode metrics_nodes.json when reachable;
falls back to SSH + nvidia-smi / free / loadavg.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
WORK = Path(os.environ.get("WORK_FALLBACK", ROOT / "work"))
SMOKE_DIR = WORK / "smoke"
DEFAULT_MRGPU_HOST = os.environ.get("MRGPU_HOST", "gpu-host")
DEFAULT_SSH = os.environ.get("MRGPU_SSH", f"operator@{DEFAULT_MRGPU_HOST}")
GROKCODE_METRICS = Path.home() / "grokcode" / "config" / "metrics_nodes.json"


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _http_text(url: str, timeout: float = 1.5) -> str | None:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None


def load_metrics_config() -> dict[str, Any]:
    if GROKCODE_METRICS.is_file():
        try:
            return json.loads(GROKCODE_METRICS.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {
        "nodes": {
            "mrgpu": {
                "host": DEFAULT_MRGPU_HOST,
                "node_exporter": f"http://{DEFAULT_MRGPU_HOST}:9100/metrics",
                "gpu_exporter": f"http://{DEFAULT_MRGPU_HOST}:9835/metrics",
                "gpu_fallback_ssh": DEFAULT_SSH,
            }
        }
    }


def _parse_node_exporter(text: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    mem_total = mem_avail = None
    load1 = None
    for line in text.splitlines():
        if line.startswith("#"):
            continue
        if line.startswith("node_memory_MemTotal_bytes "):
            mem_total = float(line.split()[1])
        elif line.startswith("node_memory_MemAvailable_bytes "):
            mem_avail = float(line.split()[1])
        elif line.startswith("node_load1 "):
            load1 = float(line.split()[1])
    if mem_total is not None:
        out["ram_total_gb"] = round(mem_total / (1024**3), 2)
        if mem_avail is not None:
            out["ram_used_gb"] = round((mem_total - mem_avail) / (1024**3), 2)
            out["ram_free_gb"] = round(mem_avail / (1024**3), 2)
    if load1 is not None:
        out["load1"] = load1
    return out


def _parse_gpu_exporter(text: str) -> dict[str, Any]:
    util = temp = mem_used = mem_total = None
    for line in text.splitlines():
        if line.startswith("#"):
            continue
        if "DCGM_FI_DEV_GPU_UTIL" in line or line.startswith("nvidia_smi_utilization_gpu_ratio"):
            try:
                util = float(line.split()[-1])
                if util <= 1.0:
                    util = util * 100.0
            except ValueError:
                pass
        if "DCGM_FI_DEV_GPU_TEMP" in line or "temperature_gpu" in line:
            try:
                temp = float(line.split()[-1])
            except ValueError:
                pass
        if "memory.used" in line or "DCGM_FI_DEV_FB_USED" in line:
            try:
                mem_used = float(line.split()[-1])
            except ValueError:
                pass
        if "memory.total" in line or "DCGM_FI_DEV_FB_FREE" in line:
            pass
    out: dict[str, Any] = {}
    if util is not None:
        out["gpu_util_pct"] = round(util, 1)
    if temp is not None:
        out["gpu_temp_c"] = round(temp, 1)
    if mem_used is not None:
        # exporters vary units; if huge, treat as MiB already-ish
        if mem_used > 100000:
            out["gpu_mem_used_mib"] = round(mem_used / (1024**2), 1)
        else:
            out["gpu_mem_used_mib"] = round(mem_used, 1)
    return out


def sample_mrgpu_ssh(ssh_target: str | None = None, timeout: float = 8.0) -> dict[str, Any]:
    target = ssh_target or DEFAULT_SSH
    remote = (
        "nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu "
        "--format=csv,noheader,nounits 2>/dev/null; "
        "echo '---'; "
        "free -b | awk '/Mem:/{print $2,$3,$7}'; "
        "echo '---'; "
        "cat /proc/loadavg; "
        "echo '---'; "
        "cat /proc/net/dev | awk 'NR>2{rx+=$2;tx+=$10} END{print rx,tx}'"
    )
    try:
        proc = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=3", "-o", "BatchMode=yes", target, remote],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if proc.returncode != 0:
            return {"ok": False, "source": "ssh", "error": (proc.stderr or proc.stdout or "")[:200]}
        parts = (proc.stdout or "").split("---")
        out: dict[str, Any] = {"ok": True, "source": "ssh", "ts": _utc()}
        if parts:
            gpu_line = parts[0].strip().splitlines()
            if gpu_line:
                cols = [c.strip() for c in gpu_line[0].split(",")]
                if len(cols) >= 4:
                    out["gpu_util_pct"] = float(cols[0])
                    out["gpu_mem_used_mib"] = float(cols[1])
                    out["gpu_mem_total_mib"] = float(cols[2])
                    out["gpu_temp_c"] = float(cols[3])
        if len(parts) > 1:
            mem = parts[1].strip().split()
            if len(mem) >= 3:
                total, used, avail = map(float, mem[:3])
                out["ram_total_gb"] = round(total / (1024**3), 2)
                out["ram_used_gb"] = round(used / (1024**3), 2)
                out["ram_free_gb"] = round(avail / (1024**3), 2)
        if len(parts) > 2:
            load = parts[2].strip().split()
            if load:
                out["load1"] = float(load[0])
        if len(parts) > 3:
            net = parts[3].strip().split()
            if len(net) >= 2:
                out["net_rx_bytes"] = int(float(net[0]))
                out["net_tx_bytes"] = int(float(net[1]))
        return out
    except Exception as exc:
        return {"ok": False, "source": "ssh", "error": str(exc)[:200], "ts": _utc()}


def sample_host(node: str = "mrgpu") -> dict[str, Any]:
    cfg = load_metrics_config()
    node_cfg = (cfg.get("nodes") or {}).get(node) or {}
    out: dict[str, Any] = {"ok": False, "node": node, "ts": _utc(), "source": "none"}

    node_url = node_cfg.get("node_exporter")
    gpu_url = node_cfg.get("gpu_exporter")
    if node_url:
        text = _http_text(str(node_url))
        if text:
            out.update(_parse_node_exporter(text))
            out["source"] = "exporter"
            out["ok"] = True
    if gpu_url:
        text = _http_text(str(gpu_url))
        if text:
            out.update(_parse_gpu_exporter(text))
            out["source"] = "exporter" if out.get("source") == "exporter" else "gpu_exporter"
            out["ok"] = True

    # Need GPU detail or full sample failed → SSH fallback
    if not out.get("ok") or out.get("gpu_util_pct") is None:
        ssh = node_cfg.get("gpu_fallback_ssh") or DEFAULT_SSH
        ssh_sample = sample_mrgpu_ssh(str(ssh))
        if ssh_sample.get("ok"):
            merged = {**out, **{k: v for k, v in ssh_sample.items() if k not in ("source",)}}
            merged["source"] = "ssh" if not out.get("ok") else f"{out.get('source')}+ssh"
            merged["ok"] = True
            return merged
        if not out.get("ok"):
            return ssh_sample
    return out


def format_sample_line(sample: dict[str, Any], *, pull_label: str = "") -> str:
    if not sample.get("ok"):
        return f"monitor FAIL: {sample.get('error') or 'unreachable'}"
    ram_u = sample.get("ram_used_gb")
    ram_t = sample.get("ram_total_gb")
    load = sample.get("load1")
    gutil = sample.get("gpu_util_pct")
    gtemp = sample.get("gpu_temp_c")
    gmu = sample.get("gpu_mem_used_mib")
    gmt = sample.get("gpu_mem_total_mib")
    parts = []
    if ram_u is not None and ram_t is not None:
        parts.append(f"RAM {ram_u:.0f}/{ram_t:.0f}G")
    if load is not None:
        parts.append(f"load {load:.2f}")
    if gutil is not None:
        parts.append(f"GPU {gutil:.0f}%")
    if gtemp is not None:
        parts.append(f"{gtemp:.0f}°C")
    if gmu is not None:
        if gmt is not None:
            parts.append(f"VRAM {gmu:.0f}/{gmt:.0f}MiB")
        else:
            parts.append(f"VRAM {gmu:.0f}MiB")
    bar = " | ".join(parts) if parts else "no metrics"
    if pull_label:
        return f"{pull_label}  ·  {bar}"
    return bar


def progress_bar(current: int, total: int, width: int = 24) -> str:
    if total <= 0:
        return "[" + "?" * width + "]"
    frac = max(0.0, min(1.0, current / total))
    filled = int(round(frac * width))
    return "[" + "█" * filled + "░" * (width - filled) + f"] {int(frac * 100):3d}%"


class HostMonitor:
    """Background sampler writing jsonl + optional callback for progress strip."""

    def __init__(
        self,
        node: str = "mrgpu",
        interval: float = 3.0,
        log_path: Path | None = None,
        on_sample: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self.node = node
        self.interval = interval
        self.on_sample = on_sample
        SMOKE_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.log_path = log_path or (SMOKE_DIR / f"{node}_pull_monitor_{stamp}.jsonl")
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self.last: dict[str, Any] = {}
        self.samples: list[dict[str, Any]] = []

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name=f"host-mon-{self.node}", daemon=True)
        self._thread.start()

    def stop(self) -> dict[str, Any]:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=self.interval + 2)
        return {
            "ok": True,
            "node": self.node,
            "samples": len(self.samples),
            "log": str(self.log_path),
            "last": self.last,
        }

    def _run(self) -> None:
        prev_rx = prev_tx = None
        while not self._stop.is_set():
            sample = sample_host(self.node)
            if prev_rx is not None and sample.get("net_rx_bytes") is not None:
                sample["net_rx_delta"] = int(sample["net_rx_bytes"]) - int(prev_rx)
                sample["net_tx_delta"] = int(sample.get("net_tx_bytes") or 0) - int(prev_tx or 0)
            if sample.get("net_rx_bytes") is not None:
                prev_rx = sample["net_rx_bytes"]
                prev_tx = sample.get("net_tx_bytes")
            self.last = sample
            self.samples.append(sample)
            try:
                with self.log_path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(sample, default=str) + "\n")
            except OSError:
                pass
            if self.on_sample:
                try:
                    self.on_sample(sample)
                except Exception:
                    pass
            self._stop.wait(self.interval)


def run_with_monitor(
    fn: Callable[[], Any],
    *,
    node: str | None = "mrgpu",
    label: str = "",
    quiet: bool = False,
) -> tuple[Any, dict[str, Any] | None]:
    """Run fn while optionally sampling host. Returns (result, monitor_summary)."""
    if not node:
        return fn(), None

    def _cb(sample: dict[str, Any]) -> None:
        if quiet:
            return
        line = format_sample_line(sample, pull_label=label or "monitor")
        print(f"\r{line[:120]:<120}", end="", flush=True)

    mon = HostMonitor(node=node, on_sample=_cb if not quiet else None)
    mon.start()
    try:
        result = fn()
    finally:
        summary = mon.stop()
        if not quiet:
            print()  # clear progress line
    return result, summary
