"""Validation helpers for Step 4 outreach self-correction."""

from __future__ import annotations


def validate_outreach_message(
    outreach_message: str,
    specific_detail: str,
    max_chars: int = 300,
    require_detail_in_message: bool = True,
) -> tuple[bool, list[str]]:
    """Validate outreach message against assignment constraints."""
    errors: list[str] = []

    if len(outreach_message) >= max_chars:
        errors.append(f"Message must be under {max_chars} characters.")

    detail = specific_detail.strip()
    if not detail:
        errors.append("specific_detail must be non-empty.")
    elif require_detail_in_message and detail.lower() not in outreach_message.lower():
        errors.append("Message must include the exact specific JD detail phrase.")

    return (len(errors) == 0, errors)
