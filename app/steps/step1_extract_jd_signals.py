"""Step 1: extract_jd_signals.

Parses JD into structured recruiting signals for downstream steps.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.llm_client import LLMClient
from app.state import PipelineState


def _load_prompt_template() -> str:
    prompt_path = (
        Path(__file__).resolve().parents[1] / "prompts" / "step1_prompt.txt"
    )
    return prompt_path.read_text(encoding="utf-8")


def _fallback_jd_signals() -> dict[str, Any]:
    return {
        "role_type": "AI Engineer",
        "required_skills": ["Python", "LLM", "Generative AI"],
        "seniority_indicators": ["ambiguous"],
        "company_stage": "startup_or_early_stage",
        "missing_information": ["location", "compensation"],
        "jd_specific_details": ["LLM-powered features", "startup environment"],
    }


def _normalize_signals(raw: dict[str, Any]) -> dict[str, Any]:
    def _as_str_list(value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(x).strip() for x in value if str(x).strip()]

    required_skills = _as_str_list(raw.get("required_skills"))
    jd_details = _as_str_list(raw.get("jd_specific_details"))

    return {
        "role_type": str(raw.get("role_type", "")).strip() or "AI role",
        "required_skills": required_skills,
        "seniority_indicators": _as_str_list(raw.get("seniority_indicators"))
        or ["ambiguous"],
        "company_stage": str(raw.get("company_stage", "")).strip()
        or "unknown",
        "missing_information": _as_str_list(raw.get("missing_information")),
        "jd_specific_details": jd_details or required_skills[:2] or ["AI product"],
    }


def run(state: PipelineState, llm_client: LLMClient) -> dict[str, Any]:
    """Extract structured signals from JD and optional manager notes."""
    prompt_template = _load_prompt_template()
    prompt = prompt_template.replace("<<job_description>>", state.job_description).replace("<<hiring_manager_notes>>", state.hiring_manager_notes or "N/A")

    raw = llm_client.generate_json(
        prompt=prompt,
        system_prompt="You are a recruiting analysis assistant. Return JSON only.",
        fallback=_fallback_jd_signals(),
    )
    return _normalize_signals(raw)
