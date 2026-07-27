"""MOCK-TUA FastAPI — job staging, estimates, hybrid local/cloud routing."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import stages
from story_parse import parse_story_markdown

app = FastAPI(
    title="MOCK-TUA",
    version="0.1.0",
    description="Shot-driven storyboard + tiered staged rendering orchestrator (M4RV hybrid).",
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


class ResumeRequest(BaseModel):
    last_good_frame: Optional[int] = None


@app.get("/healthz")
def healthz() -> dict[str, Any]:
    return stages.health()


@app.get("/v1/info")
def info() -> dict[str, Any]:
    return {
        "service": "mock-tua-api",
        "version": "0.1.0",
        "mvp_chain": stages.load_json("orchestration.json").get("mvp_chain"),
        "work_root": str(stages.work_root()),
        "docs": str(ROOT / "README.md"),
    }


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
        )
    except Exception as exc:  # surface path/JSON errors in API response
        raise HTTPException(500, f"run_failed: {exc}") from exc


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


@app.get("/v1/probe/comfy")
def probe_comfy() -> dict[str, Any]:
    h = stages.health()
    return {"m4rv": h.get("comfy_m4rv"), "mrgpu": h.get("comfy_mrgpu")}


def main() -> None:
    import uvicorn

    host = os.environ.get("MOCK_TUA_HOST", "0.0.0.0")
    port = int(os.environ.get("MOCK_TUA_PORT", "8799"))
    uvicorn.run("app:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
