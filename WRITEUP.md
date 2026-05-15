# Brief Write-Up 

## 1) What would you improve with another week?
- I would add a small evaluation set (different JD styles) and run prompt A/B checks, so prompt changes are measured instead of guessed.
- I would add a few focused tests around schema output and Step 4 retry behavior, because those are the easiest places to regress.
- I would improve failure messages in `pipeline_trace` so debugging bad runs is faster.
- I would add simple run artifacts (inputs + outputs + timestamp) for better reproducibility.

## 2) What did you notice that was not explicitly stated?
- The assignment is not only about generation quality; it is also about whether the pipeline is easy to inspect and reason about.
- Exact output keys matter a lot. Small schema drift can break downstream evaluation even if text quality looks good.
- Step 4 is the reliability checkpoint of the whole flow. Without deterministic validation, "good looking output" is not enough.

## 3) Why five steps instead of one? What breaks if Steps 1 and 2 are collapsed?
- Five steps make each decision explicit. If something is wrong, I can isolate the failing stage quickly.
- If I collapse Steps 1 and 2, JD interpretation and search planning become mixed, which makes prompt tuning and debugging much harder.
- Separate early steps also make trace logs more meaningful for reviewers.

## 4) Which parts used AI vs your own judgment?
- AI-assisted parts: drafting prompt wording, generating query/outreach text, and helping iterate phrasing quickly.
- My judgment: pipeline boundaries, data contracts, retry/validation rules, error-handling behavior, and what to keep simple vs modular.

## -- Mutian He