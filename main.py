"""Project entrypoint for the AI Recruiting Copilot Agent.

Runs the fixed 5-step pipeline and writes assignment-compatible output.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from app.orchestrator import RecruitingPipelineOrchestrator
from app.output_schema import validate_output_payload
from app.state import PipelineState
from dotenv import load_dotenv


def load_input(input_path: Path) -> dict:
    """Load input JSON and enforce required assignment input fields."""
    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("Input JSON must be an object.")

    job_description = data.get("job_description", "")
    if not isinstance(job_description, str) or not job_description.strip():
        raise ValueError("Input must include a non-empty 'job_description'.")

    notes = data.get("hiring_manager_notes", "")
    if notes is not None and not isinstance(notes, str):
        raise ValueError("'hiring_manager_notes' must be a string if provided.")

    return data


def build_output_payload(state: PipelineState) -> dict:
    """Build strict top-level output schema required by assignment."""
    return {
        "candidate_search_strategy": state.candidate_search_strategy,
        "boolean_query": state.boolean_query,
        "outreach_message": state.outreach_message,
        "candidate_summary": state.candidate_summary,
        "pipeline_trace": state.pipeline_trace,
    }


def main() -> None:
    """Run pipeline end-to-end and write output.json."""
    # Load local .env (if present). Safe because .env is gitignored.
    load_dotenv()

    project_root = Path(__file__).resolve().parent
    input_path = (
        Path(sys.argv[1]).resolve()
        if len(sys.argv) > 1
        else project_root / "data" / "input.json"
    )
    output_path = project_root / "output.json"

    input_data = load_input(input_path)
    state = PipelineState.from_input(input_data)

    orchestrator = RecruitingPipelineOrchestrator()
    final_state = orchestrator.run(state)

    payload = build_output_payload(final_state)
    validate_output_payload(payload)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Pipeline run complete. Wrote {output_path}")


if __name__ == "__main__":
    main()
