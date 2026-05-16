# /devpulse/backend/app/services/llm_service.py
from __future__ import annotations

import json
import time
from pathlib import Path

import google.generativeai as genai
from google.api_core import exceptions as g_exceptions
from pydantic import BaseModel
import structlog

from app.config import get_settings
from app.observability.metrics import llm_calls_total, llm_latency_seconds, llm_tokens_used
from app.observability.tracing import tracer

settings = get_settings()
logger = structlog.get_logger()

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"
MODEL_NAME = "gemini-1.5-pro"


genai.configure(api_key=settings.gemini_api_key)


class PostmortemOutput(BaseModel):
    timeline: list[str]
    root_cause: str
    impact: str
    action_items: list[str]
    severity_score: int
    mttr_minutes: int


class RunbookOutput(BaseModel):
    runbook_md: str


class LLMResult(BaseModel):
    postmortem_md: str
    runbook_md: str
    severity_score: int
    mttr_minutes: int
    model_used: str
    tokens_used: int


def _load_prompt(name: str) -> str:
    return (PROMPT_DIR / name).read_text(encoding="utf-8")


def _call_gemini(prompt: str, incident_id: int) -> dict:
    model = genai.GenerativeModel(MODEL_NAME)
    start = time.time()

    with tracer.start_as_current_span("llm.gemini.generate") as span:
        span.set_attribute("model_name", MODEL_NAME)
        span.set_attribute("incident_id", incident_id)
        response = model.generate_content(prompt)
        latency = time.time() - start

        text = response.text or "{}"
        usage = getattr(response, "usage_metadata", None)
        prompt_tokens = getattr(usage, "prompt_token_count", 0) if usage else 0
        completion_tokens = getattr(usage, "candidates_token_count", 0) if usage else 0
        tokens_used = prompt_tokens + completion_tokens

        span.set_attribute("prompt_tokens", prompt_tokens)
        span.set_attribute("completion_tokens", completion_tokens)
        span.set_attribute("latency_ms", int(latency * 1000))

        llm_calls_total.labels(model=MODEL_NAME, success="true").inc()
        llm_latency_seconds.labels(model=MODEL_NAME).observe(latency)
        llm_tokens_used.labels(model=MODEL_NAME).observe(tokens_used)

        logger.info(
            "llm_call",
            event="llm_call",
            model=MODEL_NAME,
            tokens_used=tokens_used,
            latency_ms=int(latency * 1000),
            success=True,
        )

        return {
            "payload": json.loads(text),
            "tokens_used": tokens_used,
        }


def _retry_call(prompt: str, incident_id: int) -> dict:
    delay = 1
    for attempt in range(3):
        try:
            return _call_gemini(prompt, incident_id)
        except (g_exceptions.TooManyRequests, g_exceptions.ServiceUnavailable):
            if attempt == 2:
                llm_calls_total.labels(model=MODEL_NAME, success="false").inc()
                logger.error("llm_call_failed", event="llm_call", success=False)
                raise
            time.sleep(delay)
            delay *= 2
        except Exception:
            llm_calls_total.labels(model=MODEL_NAME, success="false").inc()
            logger.error("llm_call_failed", event="llm_call", success=False)
            raise


def generate_retrospective(raw_input: str, incident_id: int) -> LLMResult:
    # Avoid str.format() here because prompts contain JSON examples with `{}`.
    postmortem_prompt = _load_prompt("postmortem_prompt.txt").replace("{raw_input}", raw_input)
    runbook_prompt = _load_prompt("runbook_prompt.txt").replace("{raw_input}", raw_input)

    postmortem_result = _retry_call(postmortem_prompt, incident_id)
    runbook_result = _retry_call(runbook_prompt, incident_id)

    postmortem = PostmortemOutput(**postmortem_result["payload"])
    runbook = RunbookOutput(**runbook_result["payload"])

    postmortem_md = "\n".join(
        [
            "# Incident Postmortem",
            "## Timeline",
            *[f"- {item}" for item in postmortem.timeline],
            "## Root Cause",
            postmortem.root_cause,
            "## Impact",
            postmortem.impact,
            "## Action Items",
            *[f"- {item}" for item in postmortem.action_items],
        ]
    )

    return LLMResult(
        postmortem_md=postmortem_md,
        runbook_md=runbook.runbook_md,
        severity_score=postmortem.severity_score,
        mttr_minutes=postmortem.mttr_minutes,
        model_used=MODEL_NAME,
        tokens_used=postmortem_result["tokens_used"] + runbook_result["tokens_used"],
    )
