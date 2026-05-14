# Deployment Guide (Cloudflare Frontend + Railway Backend)

This project is ready for frontend/backend separation:
- Frontend: `frontend/` (React + Vite + Tailwind) -> Cloudflare Pages
- Backend: FastAPI wrapper in `api_server.py` -> Railway

## 1) Deploy Backend to Railway

1. Create a new Railway project from this GitHub repo.
2. Set service root to repo root (default).
3. Railway will detect `railway.json` and use:
   - Start command: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`
4. Add environment variables in Railway:
   - `OPENAI_API_KEY=<your_real_key>`
   - `OPENAI_MODEL=gpt-4o-mini` (optional)
   - `OPENAI_TEMPERATURE=` (optional, recommended empty for model default)
   - `CORS_ORIGINS=https://<your-pages-domain>,https://<your-custom-domain>`
5. Deploy and copy your backend URL, for example:
   - `https://your-backend.up.railway.app`
6. Verify backend:
   - `GET https://your-backend.up.railway.app/health` -> `{\"status\":\"ok\"}`

## 2) Deploy Frontend to Cloudflare Pages

1. In Cloudflare Pages, create a project from the same GitHub repo.
2. Set:
   - Root directory: `frontend`
   - Build command: `npm run build`
   - Build output directory: `dist`
3. Add environment variables in Pages:
   - `VITE_API_BASE_URL=https://your-backend.up.railway.app`
   - `VITE_PIPELINE_ENDPOINT=/api/run-pipeline`
4. Deploy.

## 3) Post-Deploy Connection Check

1. Open your Cloudflare frontend URL.
2. Paste a JD and click **Run Pipeline**.
3. Confirm network call goes to:
   - `https://your-backend.up.railway.app/api/run-pipeline`
4. Confirm response includes:
   - `candidate_search_strategy`
   - `boolean_query`
   - `outreach_message`
   - `candidate_summary`
   - `pipeline_trace`

## 4) Secrets Safety Checklist

- Never commit `.env`.
- Keep `.env.example` only.
- Put real secrets only in Railway environment variables.
- Do not expose OpenAI key in frontend code or Cloudflare frontend env vars.
