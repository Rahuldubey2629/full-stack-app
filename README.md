# full-stack-app

This repo contains **DevPulse**, an AI-powered incident retrospective and runbook generator.

## Quick start (local)

- `cd devpulse`
- `cp .env.example .env` (optional)
- `export GEMINI_API_KEY=...` (or set it in `.env`)
- `docker compose up --build`

Open:

- Frontend: http://localhost:8080
- Backend: http://localhost:8000 (health: `/health`, metrics: `/metrics`)

## Project docs

- DevPulse details: [devpulse/README.md](devpulse/README.md)
