"""Strict output.json schema validation utilities."""

from __future__ import annotations

from typing import Any


REQUIRED_TOP_LEVEL_KEYS = {
    "candidate_search_strategy",
    "boolean_query",
    "outreach_message",
    "candidate_summary",
    "pipeline_trace",
}


def validate_output_payload(payload: dict[str, Any]) -> None:
    """Validate assignment-required top-level and nested output schema."""
    if set(payload.keys()) != REQUIRED_TOP_LEVEL_KEYS:
        raise ValueError(
            "Top-level keys must match exactly: "
            "candidate_search_strategy, boolean_query, outreach_message, "
            "candidate_summary, pipeline_trace"
        )

    _validate_candidate_search_strategy(payload["candidate_search_strategy"])
    _validate_boolean_query(payload["boolean_query"])
    _validate_outreach_message(payload["outreach_message"])
    _validate_candidate_summary(payload["candidate_summary"])
    _validate_pipeline_trace(payload["pipeline_trace"])


def _validate_candidate_search_strategy(obj: Any) -> None:
    required = {"target_backgrounds", "target_companies", "keywords", "seniority"}
    if not isinstance(obj, dict) or set(obj.keys()) != required:
        raise ValueError("candidate_search_strategy schema mismatch.")
    if not all(isinstance(x, str) for x in obj["target_backgrounds"]):
        raise ValueError("target_backgrounds must be list[str].")
    if not all(isinstance(x, str) for x in obj["target_companies"]):
        raise ValueError("target_companies must be list[str].")
    if not all(isinstance(x, str) for x in obj["keywords"]):
        raise ValueError("keywords must be list[str].")
    if not isinstance(obj["seniority"], str):
        raise ValueError("seniority must be string.")


def _validate_boolean_query(obj: Any) -> None:
    if not isinstance(obj, dict) or set(obj.keys()) != {"boolean_query"}:
        raise ValueError("boolean_query schema mismatch.")
    if not isinstance(obj["boolean_query"], str):
        raise ValueError("boolean_query.boolean_query must be string.")


def _validate_outreach_message(obj: Any) -> None:
    required = {"outreach_message", "specific_detail", "character_count", "attempts"}
    if not isinstance(obj, dict) or set(obj.keys()) != required:
        raise ValueError("outreach_message schema mismatch.")
    if not isinstance(obj["outreach_message"], str):
        raise ValueError("outreach_message.outreach_message must be string.")
    if not isinstance(obj["specific_detail"], str):
        raise ValueError("outreach_message.specific_detail must be string.")
    if not isinstance(obj["character_count"], int):
        raise ValueError("outreach_message.character_count must be integer.")
    if not isinstance(obj["attempts"], int):
        raise ValueError("outreach_message.attempts must be integer.")


def _validate_candidate_summary(obj: Any) -> None:
    required = {"name", "current_company", "key_skills", "fit_reason", "concerns"}
    if not isinstance(obj, dict) or set(obj.keys()) != required:
        raise ValueError("candidate_summary schema mismatch.")
    if not isinstance(obj["name"], str):
        raise ValueError("candidate_summary.name must be string.")
    if not isinstance(obj["current_company"], str):
        raise ValueError("candidate_summary.current_company must be string.")
    if not all(isinstance(x, str) for x in obj["key_skills"]):
        raise ValueError("candidate_summary.key_skills must be list[str].")
    if not isinstance(obj["fit_reason"], str):
        raise ValueError("candidate_summary.fit_reason must be string.")
    if not isinstance(obj["concerns"], str):
        raise ValueError("candidate_summary.concerns must be string.")


def _validate_pipeline_trace(trace: Any) -> None:
    if not isinstance(trace, list):
        raise ValueError("pipeline_trace must be a list.")

    required = {"step", "action", "attempt", "result", "note"}
    for idx, row in enumerate(trace, start=1):
        if not isinstance(row, dict) or set(row.keys()) != required:
            raise ValueError(f"pipeline_trace entry {idx} schema mismatch.")
        if not isinstance(row["step"], int) or row["step"] < 1 or row["step"] > 5:
            raise ValueError(f"pipeline_trace entry {idx}: invalid step.")
        if not isinstance(row["action"], str):
            raise ValueError(f"pipeline_trace entry {idx}: action must be string.")
        if not isinstance(row["attempt"], int) or row["attempt"] < 1:
            raise ValueError(f"pipeline_trace entry {idx}: attempt must be >= 1.")
        if row["result"] not in {"pass", "retry", "fail"}:
            raise ValueError(f"pipeline_trace entry {idx}: invalid result.")
        if not isinstance(row["note"], str):
            raise ValueError(f"pipeline_trace entry {idx}: note must be string.")
