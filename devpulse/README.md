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

1. Set env var for Gemini:

- Option A (recommended): create `devpulse/.env`:
  - `cp .env.example .env`
  - set `GEMINI_API_KEY=...`

- Option B: export it in your shell:
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
- `GEMINI_API_KEY`
- `CORS_ORIGINS` (comma-separated)

## DevOps Next Steps

- Azure DevOps: build/push images, run migrations, deploy to App Service (or AKS).
- Key Vault: store `JWT_SECRET` + `GEMINI_API_KEY`; use managed identity to fetch at runtime.
- APIM: front the FastAPI backend for auth/rate-limiting and enforce schemas.
- Azure Policy: require HTTPS, enforce private networking, restrict public IPs.
- Observability: configure OTLP export (`OTEL_EXPORTER_OTLP_ENDPOINT`) to Grafana Tempo/Jaeger.
