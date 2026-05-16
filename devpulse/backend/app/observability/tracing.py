# /devpulse/backend/app/observability/tracing.py
from __future__ import annotations

from functools import wraps
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

from app.db.session import engine

tracer = trace.get_tracer("devpulse")


def setup_tracing() -> None:
    resource = Resource.create({"service.name": "devpulse"})
    provider = TracerProvider(resource=resource)
    # Simple processor avoids background threads that can emit after stdout/stderr closes (common in tests).
    provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)
    # TODO: Export traces to Jaeger or Grafana Tempo via OTLP exporter — endpoint: OTEL_EXPORTER_OTLP_ENDPOINT env var


def instrument_app_tracing(app) -> None:
    setup_tracing()
    FastAPIInstrumentor.instrument_app(app)
    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)


def traced_route(name: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(name):
                return await func(*args, **kwargs)

        return wrapper

    return decorator
