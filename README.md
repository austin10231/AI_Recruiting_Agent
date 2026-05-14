# AI Recruiting Copilot Agent

A Python-based multi-step recruiting agent for the OCBridge take-home assignment.

## What This Project Does
- Runs a fixed 5-step sequential LLM pipeline
- Produces required `output.json` schema
- Logs real runtime `pipeline_trace`
- Implements Step 4 self-correction loop (max 3 attempts)

Pipeline steps:
1. `extract_jd_signals`
2. `generate_search_strategy`
3. `generate_boolean_query`
4. `generate_outreach_message` (with retry/validation loop)
5. `generate_candidate_summary`

## Quick Start

```bash
cd /Users/mr.tian/Desktop/AI_Recruiting_Agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# then set OPENAI_API_KEY in .env
python main.py
```

Output:
- `output.json`

## Frontend (React + Tailwind)
- Frontend source is in `frontend/`
- Uses `VITE_API_BASE_URL` to call backend API
- Local run:

```bash
cd frontend
npm install
npm run dev
```

## Input Format

`data/input.json`:

```json
{
  "job_description": "required string",
  "hiring_manager_notes": "optional string"
}
```

## Security / API Key
- API key is read from environment variables (`.env` supported).
- Never hardcode API key in source code.
- `.env` is excluded via `.gitignore`.

## Project Structure

```text
AI_Recruiting_Agent/
  main.py
  requirements.txt
  .env.example
  data/input.json
  app/
    orchestrator.py
    llm_client.py
    output_schema.py
    state.py
    prompts/
    steps/
    tracing/
    validators/
```

## Notes
- If `OPENAI_API_KEY` is not configured, the project falls back to mock mode so local orchestration still runs.
- For concise review, detailed run logs are documented in `SAMPLE_RUN.md`.
- Brief design reflection answers are documented in `WRITEUP.md`.
- Cloudflare + Railway deployment steps are documented in `DEPLOYMENT.md`.
