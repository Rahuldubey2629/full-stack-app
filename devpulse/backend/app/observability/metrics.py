# /devpulse/backend/app/observability/metrics.py
from __future__ import annotations

import time
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from starlette.responses import Response

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "route", "status_code"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["route"],
)

llm_calls_total = Counter(
    "llm_calls_total",
    "Total LLM calls",
    ["model", "success"],
)

llm_latency_seconds = Histogram(
    "llm_latency_seconds",
    "LLM latency",
    ["model"],
)

llm_tokens_used = Histogram(
    "llm_tokens_used",
    "LLM tokens used",
    ["model"],
)

db_connections_active = Gauge(
    "db_connections_active",
    "Active DB connections",
)


# TODO: Scrape /metrics via Prometheus. Add to prometheus.yml scrape_configs. Then import devpulse-dashboard.json into Grafana


def instrument_app(app):
    @app.middleware("http")
    async def metrics_middleware(request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        route_obj = request.scope.get("route")
        route = getattr(route_obj, "path", request.url.path)
        http_requests_total.labels(
            method=request.method,
            route=route,
            status_code=response.status_code,
        ).inc()
        http_request_duration_seconds.labels(route=route).observe(duration)
        return response


def metrics_response() -> Response:
    return Response(generate_latest(), media_type="text/plain")
