"""mok-tua FastAPI — stage models, ingest sides, batch storyboard runs."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

import providers
import stage_models
import stages
from sides_ingest import ingest_sides_bytes, ingest_sides_file, markdown_from_plain_sides
from story_parse import parse_story_markdown

app = FastAPI(
    title="mok-tua",
    version="0.7.0",
    description=(
        "Shot-driven storyboard orchestrator. Stage models to ai-data, ingest "
        "PDF/FDX/MD sides, run local multi-angle+next-scene or cloud stills. "
        "Conductor TUI: PETSCII intro → CLI help → status → show/play media."
    ),
)

ROOT = Path(__file__).resolve().parents[1]


class EstimateRequest(BaseModel):
    markdown: Optional[str] = None
    duration_s: float = 5.0
    kind: str = "video"
    qqq: Optional[str] = None


class RunRequest(BaseModel):
    markdown: str = Field(..., description="Story elements markdown")
    dry_run: Optional[bool] = None
    live_still: Optional[bool] = None
    qqq: Optional[str] = None
    expand_script: Optional[str] = None
    still_provider: Optional[str] = Field(
        None,
        description="local_sd_minimal | local_qwen_edit | grok_imagine | nano_banana",
    )
    video_provider: Optional[str] = Field(
        None,
        description="local_wan | local_animatediff | seedance_cloud | grok_imagine_video",
    )
    next_scene: Optional[bool] = Field(
        None,
        description="Force Next Scene: prefix on panel prompts (default: when continue_from set)",
    )
    quality_stills: bool = Field(
        False,
        description="Use quality model for Grok Imagine when still_provider=grok_imagine",
    )


class ResumeRequest(BaseModel):
    last_good_frame: Optional[int] = None


class StageModelsRequest(BaseModel):
    dry_run: bool = True
    only_ids: Optional[list[str]] = None
    required_for: Optional[str] = Field(
        None, description="e.g. local_qwen_edit — only items required for that provider"
    )


class SidesTextRequest(BaseModel):
    text: str = Field(..., description="Plain sides / screenplay text")
    title: str = "Sides import"
    style_lock: str = "clean cinematic still, consistent character, storyboard panel"
    run: bool = False
    dry_run: Optional[bool] = True
    live_still: Optional[bool] = False
    still_provider: Optional[str] = None
    video_provider: Optional[str] = None
    qqq: Optional[str] = None


class BatchRunRequest(BaseModel):
    """Batch multiple markdown stories or paths into separate runs."""

    items: list[dict[str, Any]] = Field(
        ...,
        description="List of {markdown} or {path} or {text,title}",
    )
    dry_run: Optional[bool] = True
    live_still: Optional[bool] = False
    still_provider: Optional[str] = None
    video_provider: Optional[str] = None
    qqq: Optional[str] = None


class ToolCallRequest(BaseModel):
    """Open WebUI / tool-negotiator shaped call: name + arguments."""

    name: str = Field(..., description="stage_models | run_storyboard | ingest_sides | inventory")
    arguments: dict[str, Any] = Field(default_factory=dict)


@app.get("/healthz")
def healthz() -> dict[str, Any]:
    return stages.health()


@app.get("/v1/info")
def info() -> dict[str, Any]:
    orch = stages.load_json("orchestration.json")
    return {
        "service": "mok-tua-api",
        "version": "0.7.0",
        "mvp_chain": orch.get("mvp_chain"),
        "work_root": str(stages.work_root()),
        "docs": str(ROOT / "README.md"),
        "still_providers": orch.get("still_providers"),
        "video_providers": orch.get("video_providers"),
        "defaults": orch.get("defaults"),
        "integration_earmarks": orch.get("integration_earmarks"),
        "tools": ["stage_models", "run_storyboard", "ingest_sides", "inventory", "batch_runs", "providers", "launch", "doctor", "tui"],
        "workflow_pins": {
            k: {
                "status": (v or {}).get("status"),
                "tags": (v or {}).get("tags"),
                "path": (v or {}).get("path"),
                "builder": (v or {}).get("builder"),
            }
            for k, v in (orch.get("workflow_pins") or {}).items()
        },
    }


@app.get("/v1/tools/openai")
def openai_tools_schema() -> dict[str, Any]:
    """OpenAI-compatible tools list for Open WebUI / LiteLLM tool calling."""
    return {
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "mok_tua_inventory",
                    "description": "Check whether storyboard models are present on the ai-data pool.",
                    "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "mok_tua_stage_models",
                    "description": (
                        "Stage HF models into allowlisted /ai-data/models subfolders "
                        "(loras, diffusion_models, vae, text_encoders). dry_run default true."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "dry_run": {"type": "boolean", "default": True},
                            "required_for": {
                                "type": "string",
                                "description": "local_qwen_edit or omit for all",
                            },
                        },
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "mok_tua_run_storyboard",
                    "description": (
                        "Parse story markdown and create a mok-tua run (panels + video plan). "
                        "Use dry_run=true for estimates without GPU spend."
                    ),
                    "parameters": {
                        "type": "object",
                        "required": ["markdown"],
                        "properties": {
                            "markdown": {"type": "string"},
                            "dry_run": {"type": "boolean", "default": True},
                            "live_still": {"type": "boolean", "default": False},
                            "still_provider": {
                                "type": "string",
                                "enum": [
                                    "local_sd_minimal",
                                    "local_qwen_edit",
                                    "grok_imagine",
                                    "nano_banana",
                                ],
                            },
                            "video_provider": {"type": "string"},
                            "qqq": {"type": "string", "enum": ["QQQ0", "QQQ1", "QQQ3"]},
                        },
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "mok_tua_ingest_sides",
                    "description": (
                        "Convert plain sides / screenplay text into mok-tua story markdown. "
                        "Optionally create a run."
                    ),
                    "parameters": {
                        "type": "object",
                        "required": ["text"],
                        "properties": {
                            "text": {"type": "string"},
                            "title": {"type": "string"},
                            "run": {"type": "boolean", "default": False},
                            "dry_run": {"type": "boolean", "default": True},
                            "still_provider": {"type": "string"},
                        },
                    },
                },
            },
        ]
    }


@app.post("/v1/tools/call")
def tool_call(req: ToolCallRequest) -> dict[str, Any]:
    """Cross-platform tool negotiator entry (Open WebUI → this endpoint)."""
    name = req.name
    args = req.arguments or {}
    if name in ("inventory", "mok_tua_inventory"):
        return stage_models.inventory_status()
    if name in ("stage_models", "mok_tua_stage_models"):
        return stage_models.stage_models(
            dry_run=bool(args.get("dry_run", True)),
            only_ids=args.get("only_ids"),
            required_for=args.get("required_for"),
        )
    if name in ("run_storyboard", "mok_tua_run_storyboard"):
        md = args.get("markdown") or ""
        if not str(md).strip():
            raise HTTPException(400, "markdown required")
        return stages.create_run_from_markdown(
            str(md),
            dry_run=args.get("dry_run"),
            live_still=args.get("live_still"),
            qqq=args.get("qqq"),
            still_provider=args.get("still_provider"),
            video_provider=args.get("video_provider"),
            next_scene=args.get("next_scene"),
            quality_stills=bool(args.get("quality_stills", False)),
        )
    if name in ("ingest_sides", "mok_tua_ingest_sides"):
        text = args.get("text") or ""
        if not str(text).strip():
            raise HTTPException(400, "text required")
        md = markdown_from_plain_sides(
            str(text),
            title=str(args.get("title") or "Sides import"),
            style_lock=str(
                args.get("style_lock")
                or "clean cinematic still, consistent character, storyboard panel"
            ),
        )
        out: dict[str, Any] = {"ok": True, "markdown": md}
        if args.get("run"):
            out["run"] = stages.create_run_from_markdown(
                md,
                dry_run=args.get("dry_run", True),
                live_still=args.get("live_still", False),
                still_provider=args.get("still_provider"),
                video_provider=args.get("video_provider"),
                qqq=args.get("qqq"),
            )
        return out
    if name in ("providers", "mok_tua_providers"):
        return providers.list_providers(
            tier=args.get("tier"),
            role=args.get("role"),
            bleeding_only=bool(args.get("bleed")),
            probe=not bool(args.get("no_probe")),
        )
    if name in ("doctor", "mok_tua_doctor"):
        return providers.doctor()
    if name in ("launch", "mok_tua_launch"):
        target = args.get("target") or args.get("provider") or args.get("chain")
        if not target:
            raise HTTPException(400, "target required")
        dry = bool(args.get("dry_run", True))
        if target in ("demo", "video", "face", "audio", "body", "full"):
            return providers.launch_chain(str(target), dry_run=dry)
        return providers.launch_provider(
            str(target),
            dry_run=dry,
            force=bool(args.get("force")),
            port=args.get("port"),
        )
    raise HTTPException(400, f"unknown_tool:{name}")


@app.post("/v1/parse")
def parse_story(body: dict[str, str]) -> dict[str, Any]:
    md = body.get("markdown") or ""
    if not md.strip():
        raise HTTPException(400, "markdown required")
    return parse_story_markdown(md)


@app.post("/v1/estimate")
def estimate(req: EstimateRequest) -> dict[str, Any]:
    if req.markdown:
        story = parse_story_markdown(req.markdown)
        return stages.estimate_story(story, qqq=req.qqq)
    return stages.estimate_shot(req.duration_s, kind=req.kind, qqq=req.qqq)


@app.post("/v1/stage/models")
def stage_models_endpoint(req: StageModelsRequest) -> dict[str, Any]:
    return stage_models.stage_models(
        dry_run=req.dry_run,
        only_ids=req.only_ids,
        required_for=req.required_for,
    )


@app.get("/v1/stage/inventory")
def stage_inventory() -> dict[str, Any]:
    return stage_models.inventory_status()


@app.post("/v1/sides/from_text")
def sides_from_text(req: SidesTextRequest) -> dict[str, Any]:
    md = markdown_from_plain_sides(req.text, title=req.title, style_lock=req.style_lock)
    out: dict[str, Any] = {"ok": True, "markdown": md, "title": req.title}
    if req.run:
        out["run"] = stages.create_run_from_markdown(
            md,
            dry_run=req.dry_run,
            live_still=req.live_still,
            still_provider=req.still_provider,
            video_provider=req.video_provider,
            qqq=req.qqq,
        )
    return out


@app.post("/v1/sides/from_file")
async def sides_from_file(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    run: bool = Form(False),
    dry_run: bool = Form(True),
    live_still: bool = Form(False),
    still_provider: Optional[str] = Form(None),
    video_provider: Optional[str] = Form(None),
    qqq: Optional[str] = Form(None),
) -> dict[str, Any]:
    data = await file.read()
    name = file.filename or "sides.txt"
    result = ingest_sides_bytes(data, name, title=title)
    if not result.get("ok"):
        raise HTTPException(400, result.get("error") or "ingest_failed")
    if run:
        result["run"] = stages.create_run_from_markdown(
            result["markdown"],
            dry_run=dry_run,
            live_still=live_still,
            still_provider=still_provider,
            video_provider=video_provider,
            qqq=qqq,
        )
    return result


@app.post("/v1/sides/from_path")
def sides_from_path(body: dict[str, Any]) -> dict[str, Any]:
    path = body.get("path")
    if not path:
        raise HTTPException(400, "path required")
    result = ingest_sides_file(path, title=body.get("title"))
    if not result.get("ok"):
        raise HTTPException(400, result.get("error") or "ingest_failed")
    if body.get("run"):
        result["run"] = stages.create_run_from_markdown(
            result["markdown"],
            dry_run=body.get("dry_run", True),
            live_still=body.get("live_still", False),
            still_provider=body.get("still_provider"),
            video_provider=body.get("video_provider"),
            qqq=body.get("qqq"),
        )
    return result


@app.post("/v1/runs")
def create_run(req: RunRequest) -> dict[str, Any]:
    if not req.markdown.strip():
        raise HTTPException(400, "markdown required")
    try:
        return stages.create_run_from_markdown(
            req.markdown,
            dry_run=req.dry_run,
            live_still=req.live_still,
            qqq=req.qqq,
            expand_script=req.expand_script,
            still_provider=req.still_provider,
            video_provider=req.video_provider,
            next_scene=req.next_scene,
            quality_stills=req.quality_stills,
        )
    except Exception as exc:  # surface path/JSON errors in API response
        raise HTTPException(500, f"run_failed: {exc}") from exc


@app.post("/v1/runs/batch")
def batch_runs(req: BatchRunRequest) -> dict[str, Any]:
    runs = []
    for raw in req.items:
        md = raw.get("markdown")
        if not md and raw.get("path"):
            ing = ingest_sides_file(raw["path"], title=raw.get("title"))
            if not ing.get("ok"):
                runs.append({"ok": False, "error": ing.get("error"), "path": raw.get("path")})
                continue
            md = ing["markdown"]
        if not md and raw.get("text"):
            md = markdown_from_plain_sides(str(raw["text"]), title=str(raw.get("title") or "batch"))
        if not md:
            runs.append({"ok": False, "error": "need markdown|path|text"})
            continue
        try:
            state = stages.create_run_from_markdown(
                str(md),
                dry_run=req.dry_run,
                live_still=req.live_still,
                still_provider=req.still_provider or raw.get("still_provider"),
                video_provider=req.video_provider or raw.get("video_provider"),
                qqq=req.qqq or raw.get("qqq"),
            )
            runs.append(
                {
                    "ok": True,
                    "run_id": state.get("run_id"),
                    "shot_count": state.get("shot_count"),
                    "still_provider": state.get("still_provider"),
                }
            )
        except Exception as exc:
            runs.append({"ok": False, "error": str(exc)})
    return {"ok": all(r.get("ok") for r in runs), "count": len(runs), "runs": runs}


@app.get("/v1/runs")
def list_runs(limit: int = 20) -> dict[str, Any]:
    return {"runs": stages.list_runs(limit=limit)}


@app.get("/v1/runs/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    result = stages.load_run(run_id)
    if not result.get("ok"):
        raise HTTPException(404, result.get("error") or "not found")
    return result


@app.post("/v1/runs/{run_id}/shots/{shot_id}/resume")
def resume(run_id: str, shot_id: str, req: ResumeRequest) -> dict[str, Any]:
    result = stages.resume_shot(run_id, shot_id, last_good_frame=req.last_good_frame)
    if not result.get("ok"):
        raise HTTPException(404, result.get("error") or "not found")
    return result



class LaunchRequest(BaseModel):
    dry_run: bool = True
    force: bool = False
    port: Optional[int] = None


@app.get("/v1/providers")
def list_providers(
    tier: Optional[str] = None,
    role: Optional[str] = None,
    bleed: bool = False,
    probe: bool = True,
) -> dict[str, Any]:
    return providers.list_providers(tier=tier, role=role, bleeding_only=bleed, probe=probe)


@app.get("/v1/doctor")
def doctor() -> dict[str, Any]:
    return providers.doctor()


@app.post("/v1/providers/{provider_id}/launch")
def launch_provider(provider_id: str, req: LaunchRequest) -> dict[str, Any]:
    if provider_id in ("demo", "video", "face", "audio", "body", "full"):
        return providers.launch_chain(provider_id, dry_run=req.dry_run)
    return providers.launch_provider(
        provider_id, dry_run=req.dry_run, force=req.force, port=req.port
    )


@app.post("/v1/providers/{provider_id}/stop")
def stop_provider(provider_id: str) -> dict[str, Any]:
    return providers.stop_provider(provider_id)


@app.post("/v1/providers/{provider_id}/pull")
def pull_provider(provider_id: str, dry_run: bool = True) -> dict[str, Any]:
    return providers.pull_provider(provider_id, dry_run=dry_run)


@app.get("/v1/probe/comfy")
def probe_comfy() -> dict[str, Any]:
    h = stages.health()
    return {"desk-host": h.get("comfy_desk"), "gpu-host": h.get("comfy_gpu")}


def main() -> None:
    import uvicorn

    host = os.environ.get("MOCK_TUA_HOST", "0.0.0.0")
    port = int(os.environ.get("MOCK_TUA_PORT", "8799"))
    uvicorn.run("app:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
