# Brief Write-Up

## 1) What would you improve with another week?
- Improve prompt robustness with prompt-version testing on diverse JD styles.
- Add stronger parser recovery for malformed model outputs.
- Add basic UI controls for editing JD and viewing per-step trace in real time.
- Add lightweight tests for schema compliance and retry-loop behavior.

## 2) What did you notice that was not explicitly stated?
- The assignment strongly implies that observability (`pipeline_trace`) is as important as output quality.
- Schema exactness matters as much as model quality because evaluator tooling depends on strict keys.
- Step 4 quality depends on both generation and deterministic validation, not generation alone.

## 3) Why five steps instead of one? What breaks if Steps 1 and 2 are collapsed?
- Five steps make reasoning explicit, debuggable, and auditable.
- If Steps 1 and 2 are collapsed, JD parsing assumptions become hidden and harder to inspect.
- Collapsing early steps also weakens traceability and makes targeted prompt iteration more difficult.

## 4) Which parts used AI vs your own judgment?
- AI-assisted: prompt drafting, JSON extraction formatting, outreach wording generation.
- Human judgment: architecture boundaries, retry-loop policy, schema strictness, validation design, and tradeoff decisions for readability vs complexity.

