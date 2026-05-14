"""Step 4: generate_outreach_message with required self-correction loop.

Implements:
- Outreach generation
- Explicit self-evaluation prompt
- Explicit deterministic validation checks
- Retry up to 3 attempts
- Clear failure trace on exhaustion
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.llm_client import LLMClient
from app.state import PipelineState
from app.tracing.trace_utils import append_trace
from app.validators.outreach_validator import validate_outreach_message


MAX_ATTEMPTS = 3


def _load_prompt_template() -> str:
    prompt_path = (
        Path(__file__).resolve().parents[1] / "prompts" / "step4_prompt.txt"
    )
    return prompt_path.read_text(encoding="utf-8")


def _pick_specific_detail(state: PipelineState) -> str:
    details = state.jd_signals.get("jd_specific_details")
    if isinstance(details, list):
        for item in details:
            text = str(item).strip()
            if text:
                return text

    skills = state.jd_signals.get("required_skills")
    if isinstance(skills, list):
        for item in skills:
            text = str(item).strip()
            if text:
                return text

    return "startup environment"


def _fallback_generation(detail: str) -> dict[str, str]:
    message = (
        f"Hi, your work on {detail} looks relevant to our startup AI role. "
        "Would you be open to a quick intro chat this week?"
    )
    return {
        "outreach_message": message,
        "specific_detail": detail,
    }


def _build_evaluation_prompt(message: str, specific_detail: str) -> str:
    """Visible evaluation prompt required by assignment."""
    return (
        "Evaluate the outreach message against these rules and return JSON only:\n"
        "1) under_300_chars: true only if message length < 300\n"
        "2) includes_specific_jd_detail: true only if message contains the exact specific_detail phrase\n"
        "Return schema:\n"
        "{\"under_300_chars\": bool, \"includes_specific_jd_detail\": bool, \"reason\": string}\n\n"
        f"specific_detail: {specific_detail}\n"
        f"message: {message}"
    )


def _normalize_generation(raw: dict[str, Any], default_detail: str) -> tuple[str, str]:
    message = str(raw.get("outreach_message", "")).strip()
    detail = str(raw.get("specific_detail", "")).strip() or default_detail
    return message, detail


def run(state: PipelineState, llm_client: LLMClient) -> tuple[dict, list[dict]]:
    """Generate outreach with retry loop and trace entries."""
    prompt_template = _load_prompt_template()
    step_traces: list[dict] = []

    specific_detail = _pick_specific_detail(state)
    feedback = ""
    last_message = ""

    for attempt in range(1, MAX_ATTEMPTS + 1):
        generation_prompt = prompt_template.replace("<<jd_signals>>", str(state.jd_signals)).replace("<<candidate_search_strategy>>", str(state.candidate_search_strategy)).replace("<<boolean_query>>", str(state.boolean_query)).replace("<<specific_detail>>", specific_detail).replace("<<feedback>>", feedback or "N/A").replace("<<attempt>>", str(attempt)).replace("<<max_attempts>>", str(MAX_ATTEMPTS))

        raw = llm_client.generate_json(
            prompt=generation_prompt,
            system_prompt=(
                "You are a recruiter writing concise, personalized outreach. "
                "Return JSON only."
            ),
            fallback=_fallback_generation(specific_detail),
        )
        message, used_detail = _normalize_generation(raw, specific_detail)
        last_message = message

        # Explicit evaluation prompt call (required visibility in code).
        eval_raw = llm_client.generate_json(
            prompt=_build_evaluation_prompt(message, used_detail),
            system_prompt="You are a strict validator. Return JSON only.",
            fallback={
                "under_300_chars": len(message) < 300,
                "includes_specific_jd_detail": used_detail.lower() in message.lower(),
                "reason": "fallback evaluation",
            },
        )

        # Deterministic code-side checks (required explicit validation logic).
        is_valid, errors = validate_outreach_message(
            outreach_message=message,
            specific_detail=used_detail,
            max_chars=300,
            require_detail_in_message=True,
        )

        model_under_300 = bool(eval_raw.get("under_300_chars", False))
        model_has_detail = bool(eval_raw.get("includes_specific_jd_detail", False))
        model_reason = str(eval_raw.get("reason", "")).strip()

        # Must pass deterministic checks. Model evaluation is logged for transparency.
        if is_valid and model_under_300 and model_has_detail:
            append_trace(
                step_traces,
                step=4,
                action="generate_outreach_message",
                attempt=attempt,
                result="pass",
                note="Outreach passed validation checks.",
            )
            return (
                {
                    "outreach_message": message,
                    "specific_detail": used_detail,
                    "character_count": len(message),
                    "attempts": attempt,
                },
                step_traces,
            )

        reason_parts = []
        if errors:
            reason_parts.extend(errors)
        if not model_under_300:
            reason_parts.append("Model evaluation failed under_300_chars.")
        if not model_has_detail:
            reason_parts.append("Model evaluation failed includes_specific_jd_detail.")
        if model_reason:
            reason_parts.append(f"Model reason: {model_reason}")

        reason = " ".join(reason_parts) or "Validation failed."
        feedback = (
            "Revise previous outreach to fix validation errors: "
            f"{reason} Keep under 300 chars and include exact detail: {used_detail}."
        )

        if attempt < MAX_ATTEMPTS:
            append_trace(
                step_traces,
                step=4,
                action="generate_outreach_message",
                attempt=attempt,
                result="retry",
                note=reason,
            )

    # Graceful failure after max attempts.
    fail_message = f"Hi, your {specific_detail} experience is relevant to our startup AI role. Open to a short chat?"
    append_trace(
        step_traces,
        step=4,
        action="generate_outreach_message",
        attempt=MAX_ATTEMPTS,
        result="fail",
        note=(
            "Outreach generation failed after 3 attempts. "
            "Pipeline continued gracefully."
        ),
    )
    return (
        {
            "outreach_message": fail_message or last_message,
            "specific_detail": specific_detail,
            "character_count": len(fail_message or last_message),
            "attempts": MAX_ATTEMPTS,
        },
        step_traces,
    )
