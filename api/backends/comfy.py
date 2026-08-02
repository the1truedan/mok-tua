"""Thin ComfyUI HTTP client (compatible with grokcode ComfyUIClient)."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

# Path used for model-pool existence checks (Qwen edit unet fallback)

ROOT = Path(__file__).resolve().parents[2]


def build_minimal_still_graph(
    prompt: str,
    *,
    negative: str = "blurry, low quality, watermark, text",
    checkpoint: str,
    seed: int,
    width: int = 768,
    height: int = 768,
    steps: int = 20,
    cfg: float = 7.0,
    sampler_name: str = "euler",
    scheduler: str = "normal",
    filename_prefix: str = "mock_tua_still",
) -> dict[str, Any]:
    return {
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": checkpoint}},
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": width, "height": height, "batch_size": 1},
        },
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["4", 1]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": negative, "clip": ["4", 1]}},
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": sampler_name,
                "scheduler": scheduler,
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0],
            },
        },
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": filename_prefix, "images": ["8", 0]},
        },
    }


def seed_from_prompt(prompt: str, seed: int | None = None) -> int:
    if seed is not None:
        return int(seed)
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % (2**31 - 1)


class ComfyClient:
    def __init__(self, base_url: str, *, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(
        self,
        method: str,
        path: str,
        *,
        data: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[int, bytes]:
        url = f"{self.base_url}{path}"
        req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return resp.status, resp.read()
        except urllib.error.HTTPError as exc:
            body = exc.read() if hasattr(exc, "read") else b""
            return exc.code, body
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise ConnectionError(f"ComfyUI unreachable at {url}: {exc}") from exc

    def system_stats(self) -> dict[str, Any]:
        status, body = self._request("GET", "/system_stats")
        if status != 200:
            return {"ok": False, "status": status}
        try:
            return {"ok": True, "stats": json.loads(body.decode("utf-8"))}
        except json.JSONDecodeError:
            return {"ok": False, "status": status, "error": "invalid_json"}

    def queue_prompt(self, prompt: dict[str, Any], *, client_id: str | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"prompt": prompt}
        if client_id:
            payload["client_id"] = client_id
        data = json.dumps(payload).encode("utf-8")
        status, body = self._request(
            "POST",
            "/prompt",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        try:
            parsed = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            parsed = {"raw": body[:1000].decode("utf-8", errors="replace")}
        return {"ok": status == 200, "status": status, "result": parsed}

    def history(self, prompt_id: str) -> dict[str, Any]:
        status, body = self._request("GET", f"/history/{prompt_id}")
        if status != 200:
            return {"ok": False, "status": status}
        try:
            return {"ok": True, "history": json.loads(body.decode("utf-8"))}
        except json.JSONDecodeError:
            return {"ok": False, "status": status, "error": "invalid_json"}

    def wait_for_prompt(
        self,
        prompt_id: str,
        *,
        timeout_s: float = 600.0,
        poll_s: float = 2.0,
    ) -> dict[str, Any]:
        """Poll /history/{prompt_id} until outputs appear or timeout."""
        deadline = time.time() + max(timeout_s, 1.0)
        last: dict[str, Any] = {}
        while time.time() < deadline:
            last = self.history(prompt_id)
            if last.get("ok"):
                hist = last.get("history") or {}
                entry = hist.get(prompt_id) if isinstance(hist, dict) else None
                if isinstance(entry, dict):
                    status_obj = entry.get("status") or {}
                    if status_obj.get("completed") or entry.get("outputs"):
                        return {
                            "ok": True,
                            "status": "completed",
                            "prompt_id": prompt_id,
                            "outputs": entry.get("outputs"),
                            "status_detail": status_obj,
                        }
                    if status_obj.get("status_str") == "error":
                        return {
                            "ok": False,
                            "status": "error",
                            "prompt_id": prompt_id,
                            "status_detail": status_obj,
                        }
            time.sleep(poll_s)
        return {
            "ok": False,
            "status": "timeout",
            "prompt_id": prompt_id,
            "last": last,
            "timeout_s": timeout_s,
        }


def probe(base_url: str, *, timeout: float = 10.0) -> dict[str, Any]:
    client = ComfyClient(base_url, timeout=timeout)
    try:
        stats = client.system_stats()
        return {"ok": bool(stats.get("ok")), "base_url": base_url, "stats": stats}
    except ConnectionError as exc:
        return {"ok": False, "base_url": base_url, "error": str(exc)}


def _resolve_pin_path(path_str: str) -> Path | None:
    p = Path(path_str)
    if p.is_file():
        return p
    rel = ROOT / path_str
    if rel.is_file():
        return rel
    # path relative to workflows/
    wf = ROOT / "workflows" / path_str
    if wf.is_file():
        return wf
    return None


def load_workflow_pin(pin: dict[str, Any] | None) -> dict[str, Any]:
    """
    Load a workflow pin definition.

    Returns {ok, graph?, mode, path?, note?} where mode is:
      - inline_minimal: use build_minimal_still_graph
      - api_graph: ready Comfy API prompt dict
      - placeholder: pin file missing or empty nodes
      - missing: no pin
    """
    if not pin:
        return {"ok": False, "mode": "missing", "note": "no pin"}

    if pin.get("type") == "inline" or pin.get("builder") == "build_minimal_still_graph":
        return {"ok": True, "mode": "inline_minimal", "pin": pin}

    path_str = pin.get("path")
    if not path_str:
        return {"ok": False, "mode": "missing", "note": "pin has no path", "pin": pin}

    path = _resolve_pin_path(str(path_str))
    if path is None:
        return {
            "ok": False,
            "mode": "placeholder",
            "path": path_str,
            "note": f"workflow file not found: {path_str}",
            "pin": pin,
        }

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "ok": False,
            "mode": "placeholder",
            "path": str(path),
            "note": f"failed to load workflow: {exc}",
            "pin": pin,
        }

    # Comfy API format is a flat dict of node_id -> {class_type, inputs}
    # UI exports may nest under "nodes" or "prompt"
    graph: dict[str, Any] | None = None
    if isinstance(data, dict):
        if data.get("nodes") == {} or data.get("nodes") is None and data.get("_meta"):
            # explicit placeholder
            meta = data.get("_meta") or {}
            if meta.get("status") == "placeholder" or not any(
                isinstance(v, dict) and v.get("class_type") for v in data.values()
            ):
                return {
                    "ok": False,
                    "mode": "placeholder",
                    "path": str(path),
                    "note": meta.get("note") or "placeholder workflow — export real API graph",
                    "meta": meta,
                    "pin": pin,
                }
        if all(isinstance(v, dict) and "class_type" in v for k, v in data.items() if not str(k).startswith("_")):
            graph = {k: v for k, v in data.items() if not str(k).startswith("_")}
        elif isinstance(data.get("prompt"), dict):
            graph = data["prompt"]
        elif isinstance(data.get("nodes"), dict) and data["nodes"]:
            # not always API format; treat as unusable for queue
            return {
                "ok": False,
                "mode": "placeholder",
                "path": str(path),
                "note": "UI-format workflow (nodes list); need API export",
                "pin": pin,
            }

    if not graph:
        return {
            "ok": False,
            "mode": "placeholder",
            "path": str(path),
            "note": "no API-format nodes in workflow JSON",
            "pin": pin,
        }

    return {"ok": True, "mode": "api_graph", "graph": graph, "path": str(path), "pin": pin}


def inject_prompt_into_graph(
    graph: dict[str, Any],
    prompt: str,
    *,
    seed: int | None = None,
    negative: str | None = None,
) -> dict[str, Any]:
    """Best-effort override of text/prompt and seed inputs in an API graph."""
    out = copy.deepcopy(graph)
    text_keys = ("text", "prompt", "positive", "string")
    for _nid, node in out.items():
        if not isinstance(node, dict):
            continue
        inputs = node.get("inputs")
        if not isinstance(inputs, dict):
            continue
        class_type = str(node.get("class_type") or "")
        # CLIP / text encode
        if "CLIPTextEncode" in class_type or "TextEncode" in class_type:
            # first positive-looking empty or any text
            for key in text_keys:
                if key in inputs:
                    # skip if this looks like negative and we have separate negative
                    title = str((node.get("_meta") or {}).get("title") or "").lower()
                    if "negative" in title and negative is not None:
                        inputs[key] = negative
                    elif "negative" not in title:
                        inputs[key] = prompt
                        break
        for key in text_keys:
            if key in inputs and isinstance(inputs[key], str) and "negative" not in key.lower():
                # only rewrite short placeholders or empty
                if len(inputs[key]) < 8 or inputs[key] in ("", "positive", "prompt"):
                    inputs[key] = prompt
        if seed is not None and "seed" in inputs:
            inputs["seed"] = int(seed)
        if seed is not None and "noise_seed" in inputs:
            inputs["noise_seed"] = int(seed)
    return out


def submit_still(
    base_url: str,
    prompt: str,
    *,
    checkpoint: str = "DreamShaper_8_pruned.safetensors",
    seed: int | None = None,
    dry_run: bool = True,
    host_key: str = "mac",
    width: int = 768,
    height: int = 768,
    steps: int = 20,
    cfg: float = 7.0,
    filename_prefix: str = "mock_tua_still",
    workflow_pin: dict[str, Any] | None = None,
    provider: str = "local_sd_minimal",
) -> dict[str, Any]:
    resolved_seed = seed_from_prompt(prompt, seed)
    pin_load = load_workflow_pin(workflow_pin)
    graph: dict[str, Any]
    graph_mode = pin_load.get("mode") or "inline_minimal"
    pin = workflow_pin or {}

    # Locked Qwen storyboard builder (multi-angle + next-scene)
    if provider == "local_qwen_edit" or pin.get("builder") == "qwen_edit_storyboard":
        try:
            from qwen_graph import build_qwen_edit_storyboard_graph

            unet = os.environ.get(
                "MOCK_TUA_QWEN_UNET",
                "qwen_image_edit_2509_fp8_e4m3fn.safetensors",
            )
            # fallback to base image unet if edit not staged yet
            pool = Path(os.environ.get("MOCK_TUA_MODELS_ROOT", "/Volumes/ai-data/models"))
            if not (pool / "diffusion_models" / unet).is_file():
                alt = "qwen_image_fp8_e4m3fn.safetensors"
                if (pool / "diffusion_models" / alt).is_file():
                    unet = alt
            graph = build_qwen_edit_storyboard_graph(
                prompt,
                seed=resolved_seed,
                width=width,
                height=height,
                steps=int(os.environ.get("MOCK_TUA_QWEN_STEPS", "8")),
                cfg=float(os.environ.get("MOCK_TUA_QWEN_CFG", "1.0")),
                filename_prefix=filename_prefix,
                unet_name=unet,
            )
            graph_mode = "qwen_edit_builder"
        except Exception as exc:
            graph = build_minimal_still_graph(
                prompt,
                checkpoint=checkpoint,
                seed=resolved_seed,
                width=width,
                height=height,
                steps=steps,
                cfg=cfg,
                filename_prefix=filename_prefix,
            )
            graph_mode = f"qwen_builder_fallback:{exc}"
    elif graph_mode == "api_graph" and pin_load.get("graph"):
        graph = inject_prompt_into_graph(pin_load["graph"], prompt, seed=resolved_seed)
    else:
        # minimal graph always works; qwen pin falls back until real API export exists
        graph = build_minimal_still_graph(
            prompt,
            checkpoint=checkpoint,
            seed=resolved_seed,
            width=width,
            height=height,
            steps=steps,
            cfg=cfg,
            filename_prefix=filename_prefix,
        )
        if graph_mode == "placeholder":
            graph_mode = "inline_minimal_fallback"

    payload: dict[str, Any] = {
        "host_key": host_key,
        "base_url": base_url,
        "provider": provider,
        "checkpoint": checkpoint,
        "seed": resolved_seed,
        "prompt_preview": prompt[:200],
        "node_count": len(graph),
        "graph_mode": graph_mode,
        "pin_note": pin_load.get("note"),
        "pin_path": pin_load.get("path"),
    }
    if dry_run:
        payload.update({"status": "dry_run", "ok": True})
        return payload
    client = ComfyClient(base_url)
    try:
        stats = client.system_stats()
    except ConnectionError as exc:
        payload.update({"status": "unreachable", "ok": False, "error": str(exc)})
        return payload
    if not stats.get("ok"):
        payload.update({"status": "stats_failed", "ok": False, "stats": stats})
        return payload
    queue = client.queue_prompt(graph, client_id=f"mock-tua-{int(time.time())}")
    result = queue.get("result") if isinstance(queue.get("result"), dict) else {}
    prompt_id = result.get("prompt_id") if isinstance(result, dict) else None
    payload.update(
        {
            "status": "queued" if queue.get("ok") else "queue_failed",
            "ok": bool(queue.get("ok")),
            "prompt_id": prompt_id,
            "queue": queue,
        }
    )
    wait = os.environ.get("MOCK_TUA_COMFY_WAIT", "1") not in ("0", "false", "False")
    if payload.get("ok") and prompt_id and wait:
        timeout_s = float(os.environ.get("MOCK_TUA_COMFY_WAIT_S", "600"))
        done = client.wait_for_prompt(str(prompt_id), timeout_s=timeout_s)
        payload["wait"] = done
        payload["status"] = done.get("status") or payload["status"]
        payload["ok"] = bool(done.get("ok"))
        if done.get("outputs"):
            payload["outputs"] = done["outputs"]
    return payload


def plan_video(
    base_url: str,
    prompt: str,
    *,
    host_key: str = "gpu-host",
    duration_s: float = 5.0,
    dry_run: bool = True,
    workflow_pin: dict[str, Any] | None = None,
    provider: str = "local_wan",
    start_image: str | None = None,
) -> dict[str, Any]:
    """Plan or queue a video workflow pin (Wan / AnimateDiff)."""
    pin_load = load_workflow_pin(workflow_pin)
    payload: dict[str, Any] = {
        "host_key": host_key,
        "base_url": base_url,
        "provider": provider,
        "prompt_preview": (prompt or "")[:200],
        "duration_s": duration_s,
        "start_image": start_image,
        "pin_mode": pin_load.get("mode"),
        "pin_path": pin_load.get("path") or (workflow_pin or {}).get("path"),
        "pin_note": pin_load.get("note"),
    }

    if dry_run or pin_load.get("mode") in ("placeholder", "missing"):
        payload.update(
            {
                "ok": True,
                "status": "dry_run" if dry_run else "pin_pending",
                "note": pin_load.get("note")
                or "Video graphs require gpu-host Comfy + Wan/AD workflow pin API export",
            }
        )
        if not dry_run:
            probe_r = probe(base_url)
            payload["probe"] = probe_r
            payload["ok"] = bool(probe_r.get("ok"))
            if probe_r.get("ok") and pin_load.get("mode") != "api_graph":
                payload["status"] = "reachable_pin_pending"
        return payload

    if pin_load.get("mode") != "api_graph":
        payload.update({"ok": False, "status": "no_graph"})
        return payload

    graph = inject_prompt_into_graph(pin_load["graph"], prompt)
    client = ComfyClient(base_url)
    try:
        stats = client.system_stats()
    except ConnectionError as exc:
        payload.update({"status": "unreachable", "ok": False, "error": str(exc)})
        return payload
    if not stats.get("ok"):
        payload.update({"status": "stats_failed", "ok": False, "stats": stats})
        return payload
    queue = client.queue_prompt(graph, client_id=f"mock-tua-vid-{int(time.time())}")
    result = queue.get("result") if isinstance(queue.get("result"), dict) else {}
    prompt_id = result.get("prompt_id") if isinstance(result, dict) else None
    payload.update(
        {
            "status": "queued" if queue.get("ok") else "queue_failed",
            "ok": bool(queue.get("ok")),
            "prompt_id": prompt_id,
            "queue": queue,
        }
    )
    wait = os.environ.get("MOCK_TUA_COMFY_WAIT", "1") not in ("0", "false", "False")
    if payload.get("ok") and prompt_id and wait:
        timeout_s = float(os.environ.get("MOCK_TUA_COMFY_WAIT_S", "1800"))
        done = client.wait_for_prompt(str(prompt_id), timeout_s=timeout_s)
        payload["wait"] = done
        payload["status"] = done.get("status") or payload["status"]
        payload["ok"] = bool(done.get("ok"))
        if done.get("outputs"):
            payload["outputs"] = done["outputs"]
    return payload
