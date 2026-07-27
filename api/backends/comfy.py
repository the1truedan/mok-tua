"""Thin ComfyUI HTTP client (compatible with grokcode ComfyUIClient)."""

from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
from typing import Any


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


def probe(base_url: str, *, timeout: float = 10.0) -> dict[str, Any]:
    client = ComfyClient(base_url, timeout=timeout)
    try:
        stats = client.system_stats()
        return {"ok": bool(stats.get("ok")), "base_url": base_url, "stats": stats}
    except ConnectionError as exc:
        return {"ok": False, "base_url": base_url, "error": str(exc)}


def submit_still(
    base_url: str,
    prompt: str,
    *,
    checkpoint: str = "DreamShaper_8_pruned.safetensors",
    seed: int | None = None,
    dry_run: bool = True,
    host_key: str = "m4rv",
    width: int = 768,
    height: int = 768,
    steps: int = 20,
    cfg: float = 7.0,
    filename_prefix: str = "mock_tua_still",
) -> dict[str, Any]:
    resolved_seed = seed_from_prompt(prompt, seed)
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
    payload: dict[str, Any] = {
        "host_key": host_key,
        "base_url": base_url,
        "checkpoint": checkpoint,
        "seed": resolved_seed,
        "prompt_preview": prompt[:200],
        "node_count": len(graph),
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
    return payload
