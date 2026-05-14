"""Step 3: generate_boolean_query.

Generates one sourcing-style Boolean query from strategy context.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.llm_client import LLMClient
from app.state import PipelineState


def _load_prompt_template() -> str:
    prompt_path = (
        Path(__file__).resolve().parents[1] / "prompts" / "step3_prompt.txt"
    )
    return prompt_path.read_text(encoding="utf-8")


def _fallback_query(strategy: dict[str, Any]) -> dict[str, str]:
    keywords = strategy.get("keywords") or ["Python", "LLM"]
    if len(keywords) >= 2:
        query = f'("{keywords[0]}" OR "{keywords[1]}") AND startup'
    else:
        query = '("LLM" OR "Generative AI") AND Python AND startup'
    return {"boolean_query": query}


def _normalize_query(raw: dict[str, Any]) -> dict[str, str]:
    return {
        "boolean_query": str(raw.get("boolean_query", "")).strip()
        or '("LLM" OR "Generative AI") AND Python AND startup'
    }


def run(state: PipelineState, llm_client: LLMClient) -> dict[str, str]:
    """Generate Boolean query from Step 1 + Step 2 outputs."""
    prompt_template = _load_prompt_template()
    prompt = prompt_template.replace("<<jd_signals>>", str(state.jd_signals)).replace("<<candidate_search_strategy>>", str(state.candidate_search_strategy))

    raw = llm_client.generate_json(
        prompt=prompt,
        system_prompt="You are a sourcing expert. Return JSON only.",
        fallback=_fallback_query(state.candidate_search_strategy),
    )
    return _normalize_query(raw)
