"""Assignment-aligned pipeline trace helper utilities."""

from __future__ import annotations


VALID_RESULTS = {"pass", "retry", "fail"}


def make_trace_entry(
    step: int,
    action: str,
    attempt: int,
    result: str,
    note: str = "",
) -> dict[str, object]:
    """Create one trace entry in required assignment format.

    Required keys:
    - step (integer 1..5)
    - action (step name)
    - attempt (attempt number inside step)
    - result (pass/retry/fail)
    - note (optional explanation)
    """
    if step < 1 or step > 5:
        raise ValueError("Trace 'step' must be an integer in [1, 5].")
    if attempt < 1:
        raise ValueError("Trace 'attempt' must be >= 1.")
    if result not in VALID_RESULTS:
        raise ValueError("Trace 'result' must be one of: pass, retry, fail.")

    return {
        "step": step,
        "action": action,
        "attempt": attempt,
        "result": result,
        "note": note,
    }


def append_trace(
    trace_list: list[dict[str, object]],
    step: int,
    action: str,
    attempt: int,
    result: str,
    note: str = "",
) -> None:
    """Append a validated trace entry to pipeline trace list."""
    trace_list.append(
        make_trace_entry(
            step=step,
            action=action,
            attempt=attempt,
            result=result,
            note=note,
        )
    )

