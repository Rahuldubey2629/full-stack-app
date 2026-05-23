# DevPulse

DevPulse is an AI-powered incident retrospective and runbook generator for DevOps teams.

## Architecture

```
+---------------------+        +-------------------+
|     Frontend        |        |      Backend      |
|  React + Nginx      |<------>| FastAPI + JWT     |
|  http://localhost   |   HTTP | /auth /incidents  |
+----------+----------+        | /retro /runbooks  |
           |                   +---------+---------+
           |                             |
           |                             | async tasks
           v                             v
   +-------+--------+             +------+------+
   |   Redis        |<----------->|  Celery     |
   | broker/result  |             |  worker     |
   +-------+--------+             +------+------+
           |
           |
           v
   +-------+--------+
   |  PostgreSQL    |
   |  incidents     |
   |  retros/runbooks|
   +----------------+
```

## Local run (Docker)

1. Choose an LLM provider:

- Option A (Gemini): create `devpulse/.env`:
  - `cp .env.example .env`
  - set `LLM_PROVIDER=gemini`
  - set `GEMINI_API_KEY=...`

- Option B (Groq): create `devpulse/.env`:
  - `cp .env.example .env`
  - set `LLM_PROVIDER=groq`
  - set `GROQ_API_KEY=...`
  - optionally set `GROQ_MODEL=...`

- Option C (Azure AI Foundry / services.ai.azure.com): create `devpulse/.env`:
  - `cp .env.example .env`
  - set `LLM_PROVIDER=azure_ai`
  - set `AZURE_AI_ENDPOINT=https://<your-resource>.services.ai.azure.com`
    - If you only have a project URL like `.../api/projects/proj-default`, use just the origin.
  - set `AZURE_AI_API_KEY=...`
  - set `AZURE_AI_MODEL=...` (example: `gpt-4o-mini`)

- Option D (Azure OpenAI - deployments): create `devpulse/.env`:
  - `cp .env.example .env`
  - set `LLM_PROVIDER=azure_openai`
  - set `AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com`
    - Some Foundry setups use `*.services.ai.azure.com`; if so, try that origin here.
  - set `AZURE_OPENAI_API_KEY=...`
  - set `AZURE_OPENAI_DEPLOYMENT=...` (this is the deployment name you created)
  - set `AZURE_OPENAI_API_VERSION=2024-12-01-preview` (required for `o4-mini`)

- Option C: export it in your shell:
  - `export LLM_PROVIDER=gemini`
  - `export GEMINI_API_KEY=...`

2. Start the stack:

- `cd devpulse`
- `docker compose up --build`

3. Open the app:

- Frontend: http://localhost:8080
- Backend: http://localhost:8000 (health: `/health`, metrics: `/metrics`)

## Dev workflow (without Docker)

- Backend:
  - `cd devpulse/backend`
  - create venv, `pip install -r requirements.txt`
  - set `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`, `GEMINI_API_KEY`
  - `alembic upgrade head`
  - `uvicorn app.main:app --reload`

- Worker:
  - `cd devpulse/backend`
  - `celery -A app.workers.tasks.celery_app worker --loglevel=INFO`

- Frontend:
  - `cd devpulse/frontend`
  - `npm install`
  - `npm run dev`

## Env vars

Backend reads:

- `DATABASE_URL` (async SQLAlchemy URL, e.g. `postgresql+asyncpg://...`)
- `REDIS_URL`
- `JWT_SECRET`
- `LLM_PROVIDER` (`gemini`, `groq`, `azure_ai`, or `azure_openai`)
- `GEMINI_API_KEY` (required when `LLM_PROVIDER=gemini`)
- `GROQ_API_KEY` (required when `LLM_PROVIDER=groq`)
- `GROQ_MODEL` (optional)
- `AZURE_AI_ENDPOINT` / `AZURE_AI_API_KEY` (for `LLM_PROVIDER=azure_ai`)
- `AZURE_AI_MODEL` / `AZURE_AI_API_VERSION` / `AZURE_AI_CHAT_PATH` (optional; for `LLM_PROVIDER=azure_ai`)
- `AZURE_OPENAI_ENDPOINT` / `AZURE_OPENAI_API_KEY` / `AZURE_OPENAI_DEPLOYMENT` (for `LLM_PROVIDER=azure_openai`)
- `AZURE_OPENAI_API_VERSION` (required for some deployments like `o4-mini`)
- `CORS_ORIGINS` (comma-separated)

## DevOps Next Steps

- Azure DevOps: build/push images, run migrations, deploy to App Service (or AKS).
- Key Vault: store `JWT_SECRET` + `GEMINI_API_KEY`; use managed identity to fetch at runtime.
- APIM: front the FastAPI backend for auth/rate-limiting and enforce schemas.
- Azure Policy: require HTTPS, enforce private networking, restrict public IPs.
- Observability: configure OTLP export (`OTEL_EXPORTER_OTLP_ENDPOINT`) to Grafana Tempo/Jaeger.
