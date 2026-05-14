"""Step 5: generate_candidate_summary.

Generates final candidate summary card.
Mock candidate data is generated internally (assignment-compliant).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.llm_client import LLMClient
from app.state import PipelineState


def _load_prompt_template() -> str:
    prompt_path = (
        Path(__file__).resolve().parents[1] / "prompts" / "step5_prompt.txt"
    )
    return prompt_path.read_text(encoding="utf-8")


def _fallback_summary() -> dict[str, Any]:
    return {
        "name": "Alex Chen",
        "current_company": "NovaAI",
        "key_skills": ["Python", "LLM", "MLOps"],
        "fit_reason": "Strong match with JD focus on LLM feature delivery in startup settings.",
        "concerns": "Need deeper validation of domain depth and leadership scope.",
    }


def _normalize_summary(raw: dict[str, Any]) -> dict[str, Any]:
    skills = raw.get("key_skills")
    if not isinstance(skills, list):
        skills = []
    skills = [str(x).strip() for x in skills if str(x).strip()][:5]

    return {
        "name": str(raw.get("name", "")).strip() or "Mock Candidate",
        "current_company": str(raw.get("current_company", "")).strip() or "Unknown",
        "key_skills": skills[:5] if len(skills) >= 3 else (skills + ["Python", "LLM", "AI"])[
            :3
        ],
        "fit_reason": str(raw.get("fit_reason", "")).strip()
        or "Matches core role requirements.",
        "concerns": str(raw.get("concerns", "")).strip()
        or "Requires deeper validation in live screening.",
    }


def run(state: PipelineState, llm_client: LLMClient) -> dict[str, Any]:
    """Generate candidate summary card using all prior pipeline context."""
    prompt_template = _load_prompt_template()

    # Internal mock candidate seed (not external assignment input).
    state.internal_context["mock_candidate_seed"] = {
        "name_hint": "Alex Chen",
        "company_hint": "NovaAI",
    }

    prompt = prompt_template.replace("<<jd_signals>>", str(state.jd_signals)).replace("<<candidate_search_strategy>>", str(state.candidate_search_strategy)).replace("<<boolean_query>>", str(state.boolean_query)).replace("<<outreach_message>>", str(state.outreach_message)).replace("<<mock_candidate_seed>>", str(state.internal_context["mock_candidate_seed"]))

    raw = llm_client.generate_json(
        prompt=prompt,
        system_prompt=(
            "You are a recruiting copilot assistant. "
            "Generate one concise candidate summary card in JSON only."
        ),
        fallback=_fallback_summary(),
    )
    normalized = _normalize_summary(raw)
    state.internal_context["mock_candidate"] = normalized
    return normalized
