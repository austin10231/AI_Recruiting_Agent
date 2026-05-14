"""Pipeline state contracts and default output schema builders."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def default_candidate_search_strategy() -> dict[str, Any]:
    """Return required candidate_search_strategy output shape."""
    return {
        "target_backgrounds": [],
        "target_companies": [],
        "keywords": [],
        "seniority": "",
    }


def default_boolean_query() -> dict[str, Any]:
    """Return required boolean_query output shape."""
    return {"boolean_query": ""}


def default_outreach_message() -> dict[str, Any]:
    """Return required outreach_message output shape."""
    return {
        "outreach_message": "",
        "specific_detail": "",
        "character_count": 0,
        "attempts": 0,
    }


def default_candidate_summary() -> dict[str, Any]:
    """Return required candidate_summary output shape."""
    return {
        "name": "",
        "current_company": "",
        "key_skills": [],
        "fit_reason": "",
        "concerns": "",
    }


@dataclass
class PipelineState:
    """Single state container passed across all pipeline steps."""

    job_description: str
    hiring_manager_notes: str = ""

    jd_signals: dict[str, Any] = field(default_factory=dict)
    candidate_search_strategy: dict[str, Any] = field(
        default_factory=default_candidate_search_strategy
    )
    boolean_query: dict[str, Any] = field(default_factory=default_boolean_query)
    outreach_message: dict[str, Any] = field(default_factory=default_outreach_message)
    candidate_summary: dict[str, Any] = field(default_factory=default_candidate_summary)

    pipeline_trace: list[dict[str, Any]] = field(default_factory=list)
    internal_context: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_input(cls, payload: dict[str, Any]) -> "PipelineState":
        """Create state from assignment input payload."""
        return cls(
            job_description=payload.get("job_description", "").strip(),
            hiring_manager_notes=payload.get("hiring_manager_notes", "").strip(),
        )

