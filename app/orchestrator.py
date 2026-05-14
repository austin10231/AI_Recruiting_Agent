"""Pipeline orchestrator.

Runs five distinct sequential steps and logs real execution trace.
"""

from __future__ import annotations

from app.llm_client import LLMClient
from app.state import PipelineState
from app.steps import (
    step1_extract_jd_signals,
    step2_generate_search_strategy,
    step3_generate_boolean_query,
    step4_generate_outreach_message,
    step5_generate_candidate_summary,
)
from app.tracing.trace_utils import append_trace


class RecruitingPipelineOrchestrator:
    """Coordinates five-step pipeline execution in strict order."""

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()

    def run(self, state: PipelineState) -> PipelineState:
        """Execute step-by-step pipeline and update state in place."""
        # Step 1: extract_jd_signals
        try:
            state.jd_signals = step1_extract_jd_signals.run(state, self.llm_client)
            append_trace(
                state.pipeline_trace,
                step=1,
                action="extract_jd_signals",
                attempt=1,
                result="pass",
                note="JD signals extracted.",
            )
        except Exception as exc:
            append_trace(
                state.pipeline_trace,
                step=1,
                action="extract_jd_signals",
                attempt=1,
                result="fail",
                note=f"Step failed: {exc}",
            )

        # Step 2: generate_search_strategy
        try:
            state.candidate_search_strategy = step2_generate_search_strategy.run(
                state, self.llm_client
            )
            append_trace(
                state.pipeline_trace,
                step=2,
                action="generate_search_strategy",
                attempt=1,
                result="pass",
                note="Candidate search strategy generated.",
            )
        except Exception as exc:
            append_trace(
                state.pipeline_trace,
                step=2,
                action="generate_search_strategy",
                attempt=1,
                result="fail",
                note=f"Step failed: {exc}",
            )

        # Step 3: generate_boolean_query
        try:
            state.boolean_query = step3_generate_boolean_query.run(state, self.llm_client)
            append_trace(
                state.pipeline_trace,
                step=3,
                action="generate_boolean_query",
                attempt=1,
                result="pass",
                note="Boolean query generated.",
            )
        except Exception as exc:
            append_trace(
                state.pipeline_trace,
                step=3,
                action="generate_boolean_query",
                attempt=1,
                result="fail",
                note=f"Step failed: {exc}",
            )

        # Step 4: generate_outreach_message (includes explicit retry loop inside step module)
        try:
            state.outreach_message, step4_trace_events = step4_generate_outreach_message.run(
                state, self.llm_client
            )
            state.pipeline_trace.extend(step4_trace_events)
        except Exception as exc:
            append_trace(
                state.pipeline_trace,
                step=4,
                action="generate_outreach_message",
                attempt=1,
                result="fail",
                note=f"Step failed: {exc}",
            )

        # Step 5: generate_candidate_summary
        try:
            state.candidate_summary = step5_generate_candidate_summary.run(
                state, self.llm_client
            )
            append_trace(
                state.pipeline_trace,
                step=5,
                action="generate_candidate_summary",
                attempt=1,
                result="pass",
                note="Candidate summary generated.",
            )
        except Exception as exc:
            append_trace(
                state.pipeline_trace,
                step=5,
                action="generate_candidate_summary",
                attempt=1,
                result="fail",
                note=f"Step failed: {exc}",
            )

        return state
