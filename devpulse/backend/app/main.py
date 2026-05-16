# /devpulse/backend/app/main.py
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, incidents, retrospectives, runbooks
from app.config import get_settings
from app.middleware.request_id import RequestIdMiddleware
from app.observability.logging import configure_logging
from app.observability.metrics import instrument_app, metrics_response
from app.observability.tracing import instrument_app_tracing

settings = get_settings()

configure_logging()

app = FastAPI(title="DevPulse", version="1.0.0")

# TODO: Add Sentry SDK for error tracking — sentry_sdk.init(dsn=SENTRY_DSN)

app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

instrument_app_tracing(app)
instrument_app(app)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
app.include_router(retrospectives.router, prefix="/retro", tags=["retrospectives"])
app.include_router(runbooks.router, prefix="/runbooks", tags=["runbooks"])


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/ready")
async def ready() -> dict:
    # Minimal readiness; extend with DB/Redis checks as needed.
    return {"status": "ready"}


@app.get("/metrics")
async def metrics(request: Request):
    return metrics_response()
