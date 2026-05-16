# /devpulse/backend/app/observability/logging.py
from __future__ import annotations

import contextvars
import logging

import structlog
from opentelemetry import trace

user_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("user_id", default=None)


def bind_user_id(user_id: str | None) -> None:
    user_id_var.set(user_id)


def _add_trace_context(_, __, event_dict: dict) -> dict:
    span = trace.get_current_span()
    span_context = span.get_span_context()
    event_dict["trace_id"] = format(span_context.trace_id, "032x") if span_context.trace_id else None
    event_dict["span_id"] = format(span_context.span_id, "016x") if span_context.span_id else None
    event_dict["user_id"] = user_id_var.get()
    return event_dict


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO)
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            _add_trace_context,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )
