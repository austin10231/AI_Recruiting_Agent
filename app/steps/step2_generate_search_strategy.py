"""Step 2: generate_search_strategy.

Builds candidate sourcing strategy from Step 1 signals.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.llm_client import LLMClient
from app.state import PipelineState


def _load_prompt_template() -> str:
    prompt_path = (
        Path(__file__).resolve().parents[1] / "prompts" / "step2_prompt.txt"
    )
    return prompt_path.read_text(encoding="utf-8")


def _fallback_strategy(signals: dict[str, Any]) -> dict[str, Any]:
    skills = signals.get("required_skills") or ["Python", "LLM"]
    return {
        "target_backgrounds": ["Applied AI Engineer", "ML Engineer"],
        "target_companies": ["AI startups", "product-focused tech teams"],
        "keywords": skills[:5],
        "seniority": "mid-to-senior",
    }


def _normalize_strategy(raw: dict[str, Any]) -> dict[str, Any]:
    def _as_str_list(value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(x).strip() for x in value if str(x).strip()]

    return {
        "target_backgrounds": _as_str_list(raw.get("target_backgrounds")),
        "target_companies": _as_str_list(raw.get("target_companies")),
        "keywords": _as_str_list(raw.get("keywords")),
        "seniority": str(raw.get("seniority", "")).strip() or "not_specified",
    }


def run(state: PipelineState, llm_client: LLMClient) -> dict[str, Any]:
    """Generate candidate search strategy from Step 1 output."""
    prompt_template = _load_prompt_template()
    prompt = prompt_template.replace("<<jd_signals>>", str(state.jd_signals))

    raw = llm_client.generate_json(
        prompt=prompt,
        system_prompt="You are a recruiting strategist. Return JSON only.",
        fallback=_fallback_strategy(state.jd_signals),
    )
    return _normalize_strategy(raw)
