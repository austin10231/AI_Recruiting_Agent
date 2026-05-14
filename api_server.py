"""HTTP API wrapper for Railway deployment.

This keeps the existing pipeline modules unchanged and exposes a simple
POST endpoint for frontend consumption.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.orchestrator import RecruitingPipelineOrchestrator
from app.output_schema import validate_output_payload
from app.state import PipelineState

load_dotenv()

app = FastAPI(title="AI Recruiting Copilot API", version="1.0.0")


class PipelineInput(BaseModel):
    """Request payload for pipeline execution."""

    job_description: str = Field(..., min_length=1)
    hiring_manager_notes: str | None = ""


def _allowed_origins() -> list[str]:
    """Read CORS origins from env.

    Example:
    CORS_ORIGINS=https://your-frontend.pages.dev,https://your-domain.com
    """
    raw = os.getenv("CORS_ORIGINS", "*").strip()
    if raw == "*":
        return ["*"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    """Basic health endpoint for Railway checks."""
    return {"status": "ok"}


@app.post("/api/run-pipeline")
def run_pipeline(payload: PipelineInput) -> dict:
    """Execute the 5-step recruiting pipeline and return required schema."""
    try:
        state = PipelineState.from_input(payload.model_dump())
        orchestrator = RecruitingPipelineOrchestrator()
        final_state = orchestrator.run(state)

        output = {
            "candidate_search_strategy": final_state.candidate_search_strategy,
            "boolean_query": final_state.boolean_query,
            "outreach_message": final_state.outreach_message,
            "candidate_summary": final_state.candidate_summary,
            "pipeline_trace": final_state.pipeline_trace,
        }
        validate_output_payload(output)
        return output
    except Exception as exc:  # pragma: no cover - deployment safety path
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {exc}")
