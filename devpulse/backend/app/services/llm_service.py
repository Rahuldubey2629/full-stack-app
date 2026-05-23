# /devpulse/backend/app/services/llm_service.py
from __future__ import annotations

import json
import time
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import google.generativeai as genai
from google.api_core import exceptions as g_exceptions
import httpx
from pydantic import BaseModel
from pydantic.config import ConfigDict
import structlog

from app.config import get_settings
from app.observability.metrics import llm_calls_total, llm_latency_seconds, llm_tokens_used
from app.observability.tracing import tracer

settings = get_settings()
logger = structlog.get_logger()

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"
DEFAULT_GEMINI_MODEL = "gemini-1.5-flash"
DEFAULT_GROQ_MODEL = "llama-3.1-8b-instant"


class _RetryableLLMError(RuntimeError):
    pass


class _RateLimitError(_RetryableLLMError):
    pass


class _ServiceUnavailableError(_RetryableLLMError):
    pass


def _normalize_model_name(name: str) -> str:
    value = (name or "").strip()
    if not value:
        value = DEFAULT_GEMINI_MODEL
    return value if value.startswith("models/") else f"models/{value}"


@lru_cache
def _resolved_model_name() -> str:
    preferred = _normalize_model_name(getattr(settings, "gemini_model", DEFAULT_GEMINI_MODEL))

    def _preference_key(name: str) -> tuple[int, int, int, str]:
        # Lower is better.
        # 1) Prefer flash models (more likely to have generous quotas)
        # 2) Then pro models
        # 3) Then anything else
        # Within buckets, prefer shorter names and deterministic order.
        value = (name or "").lower()
        bucket = 2
        if "flash" in value:
            bucket = 0
        elif "pro" in value:
            bucket = 1
        return (bucket, len(value), value.count("-"), value)

    try:
        models = list(genai.list_models())
        supported: list[str] = []
        for m in models:
            methods = set(getattr(m, "supported_generation_methods", []) or [])
            if "generateContent" in methods:
                supported.append(getattr(m, "name", ""))

        if preferred in supported:
            return preferred

        # If the preferred model isn't an exact match, try common variants
        # (e.g. "models/gemini-1.5-flash" -> "models/gemini-1.5-flash-latest").
        preferred_base = preferred.removeprefix("models/")
        preferred_candidates = [
            name
            for name in supported
            if name == preferred
            or name.startswith(preferred + "-")
            or (preferred_base and preferred_base in name)
        ]
        if preferred_candidates:
            return sorted(preferred_candidates, key=_preference_key)[0]

        # Otherwise, prefer flash models over pro to avoid picking a model
        # that may be unavailable under the current quota/billing.
        return sorted(supported, key=_preference_key)[0] if supported else preferred
    except Exception:
        return preferred


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

    model_config = ConfigDict(protected_namespaces=())


def _load_prompt(name: str) -> str:
    return (PROMPT_DIR / name).read_text(encoding="utf-8")


def _llm_provider() -> str:
    return (getattr(settings, "llm_provider", "gemini") or "gemini").strip().lower()


def _azure_origin(endpoint: str) -> str:
    value = (endpoint or "").strip()
    if not value:
        return ""
    parsed = urlparse(value)
    if parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}"
    # If user passed a bare host, assume https.
    if value.startswith("//"):
        return f"https:{value}"
    if value.startswith("http://") or value.startswith("https://"):
        return value.rstrip("/")
    return f"https://{value.strip('/')}"


def _extract_json_object(text: str) -> dict[str, Any]:
    value = (text or "").strip()
    if not value:
        return {}
    try:
        obj = json.loads(value)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass

    start = value.find("{")
    end = value.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = value[start : end + 1]
        obj = json.loads(snippet)
        if isinstance(obj, dict):
            return obj
    raise ValueError("Model did not return a JSON object")


def _call_gemini(prompt: str, incident_id: int) -> dict:
    model_name = _resolved_model_name()
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(model_name)
    start = time.time()

    with tracer.start_as_current_span("llm.gemini.generate") as span:
        span.set_attribute("model_name", model_name)
        span.set_attribute("incident_id", incident_id)
        try:
            response = model.generate_content(prompt)
        except g_exceptions.TooManyRequests as e:
            raise _RateLimitError(str(e)) from e
        except g_exceptions.ServiceUnavailable as e:
            raise _ServiceUnavailableError(str(e)) from e
        latency = time.time() - start

        text = response.text or "{}"
        usage = getattr(response, "usage_metadata", None)
        prompt_tokens = getattr(usage, "prompt_token_count", 0) if usage else 0
        completion_tokens = getattr(usage, "candidates_token_count", 0) if usage else 0
        tokens_used = prompt_tokens + completion_tokens

        span.set_attribute("prompt_tokens", prompt_tokens)
        span.set_attribute("completion_tokens", completion_tokens)
        span.set_attribute("latency_ms", int(latency * 1000))

        llm_calls_total.labels(model=model_name, success="true").inc()
        llm_latency_seconds.labels(model=model_name).observe(latency)
        llm_tokens_used.labels(model=model_name).observe(tokens_used)

        logger.info(
            "llm_call",
            model=model_name,
            tokens_used=tokens_used,
            latency_ms=int(latency * 1000),
            success=True,
        )

        return {"payload": _extract_json_object(text), "tokens_used": tokens_used, "model_used": model_name}


def _call_groq(prompt: str, incident_id: int) -> dict:
    model = (getattr(settings, "groq_model", "") or "").strip() or DEFAULT_GROQ_MODEL
    base_url = (getattr(settings, "groq_base_url", "") or "").strip() or "https://api.groq.com/openai/v1/chat/completions"
    api_key = (getattr(settings, "groq_api_key", "") or "").strip()
    start = time.time()

    # Strong instruction for JSON-only output.
    system = (
        "You are a helpful assistant that outputs ONLY valid JSON. "
        "Do not include markdown fences, comments, or extra text."
    )

    with tracer.start_as_current_span("llm.groq.chat_completions") as span:
        span.set_attribute("model_name", model)
        span.set_attribute("incident_id", incident_id)

        try:
            with httpx.Client(timeout=60.0) as client:
                resp = client.post(
                    base_url,
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": model,
                        "temperature": 0.2,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": prompt},
                        ],
                    },
                )
        except httpx.RequestError as e:
            raise _ServiceUnavailableError(str(e)) from e

        latency = time.time() - start
        span.set_attribute("latency_ms", int(latency * 1000))

        if resp.status_code in (429,):
            raise _RateLimitError(resp.text)
        if resp.status_code in (500, 502, 503, 504):
            raise _ServiceUnavailableError(resp.text)
        if resp.is_error:
            # Non-retryable
            raise RuntimeError(f"Groq HTTP {resp.status_code}: {resp.text}")

        data = resp.json()
        content = (
            (((data.get("choices") or [])[0] or {}).get("message") or {}).get("content")
            if isinstance(data, dict)
            else None
        )
        payload = _extract_json_object(content or "")

        usage = data.get("usage") if isinstance(data, dict) else None
        tokens_used = int((usage or {}).get("total_tokens") or 0) if isinstance(usage, dict) else 0

        llm_calls_total.labels(model=f"groq:{model}", success="true").inc()
        llm_latency_seconds.labels(model=f"groq:{model}").observe(latency)
        llm_tokens_used.labels(model=f"groq:{model}").observe(tokens_used)

        logger.info(
            "llm_call",
            model=f"groq:{model}",
            tokens_used=tokens_used,
            latency_ms=int(latency * 1000),
            success=True,
        )

        return {"payload": payload, "tokens_used": tokens_used, "model_used": f"groq:{model}"}


def _call_azure_ai(prompt: str, incident_id: int) -> dict:
    origin = _azure_origin(getattr(settings, "azure_ai_endpoint", ""))
    chat_path = (getattr(settings, "azure_ai_chat_path", "") or "").strip() or "/models/chat/completions"
    api_version = (getattr(settings, "azure_ai_api_version", "") or "").strip() or "2024-05-01-preview"
    model = (getattr(settings, "azure_ai_model", "") or "").strip() or "gpt-4o-mini"
    api_key = (getattr(settings, "azure_ai_api_key", "") or "").strip()

    if not origin:
        raise RuntimeError("AZURE_AI_ENDPOINT is not set")
    if not api_key:
        raise RuntimeError("AZURE_AI_API_KEY is not set")

    if not chat_path.startswith("/"):
        chat_path = "/" + chat_path

    url = f"{origin}{chat_path}?api-version={api_version}"
    start = time.time()

    system = (
        "You are a helpful assistant that outputs ONLY valid JSON. "
        "Do not include markdown fences, comments, or extra text."
    )

    with tracer.start_as_current_span("llm.azure_ai.chat_completions") as span:
        span.set_attribute("model_name", model)
        span.set_attribute("incident_id", incident_id)

        try:
            with httpx.Client(timeout=60.0) as client:
                resp = client.post(
                    url,
                    headers={"api-key": api_key},
                    json={
                        "model": model,
                        "temperature": 0.2,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": prompt},
                        ],
                    },
                )
        except httpx.RequestError as e:
            raise _ServiceUnavailableError(str(e)) from e

        latency = time.time() - start
        span.set_attribute("latency_ms", int(latency * 1000))

        if resp.status_code in (429,):
            raise _RateLimitError(resp.text)
        if resp.status_code in (500, 502, 503, 504):
            raise _ServiceUnavailableError(resp.text)
        if resp.is_error:
            raise RuntimeError(f"Azure AI HTTP {resp.status_code}: {resp.text}")

        data = resp.json()
        content = (
            (((data.get("choices") or [])[0] or {}).get("message") or {}).get("content")
            if isinstance(data, dict)
            else None
        )
        payload = _extract_json_object(content or "")

        usage = data.get("usage") if isinstance(data, dict) else None
        tokens_used = int((usage or {}).get("total_tokens") or 0) if isinstance(usage, dict) else 0

        label = f"azure_ai:{model}"
        llm_calls_total.labels(model=label, success="true").inc()
        llm_latency_seconds.labels(model=label).observe(latency)
        llm_tokens_used.labels(model=label).observe(tokens_used)

        logger.info(
            "llm_call",
            model=label,
            tokens_used=tokens_used,
            latency_ms=int(latency * 1000),
            success=True,
        )

        return {"payload": payload, "tokens_used": tokens_used, "model_used": label}


def _call_azure_openai(prompt: str, incident_id: int) -> dict:
    # Azure OpenAI uses a deployment name in the URL:
    #   POST {endpoint}/openai/deployments/{deployment}/chat/completions?api-version=...
    origin = _azure_origin(getattr(settings, "azure_openai_endpoint", "") or getattr(settings, "azure_ai_endpoint", ""))
    api_key = (getattr(settings, "azure_openai_api_key", "") or getattr(settings, "azure_ai_api_key", "")).strip()
    deployment = (getattr(settings, "azure_openai_deployment", "") or "").strip()
    api_version = (getattr(settings, "azure_openai_api_version", "") or "2024-05-01-preview").strip()

    if not origin:
        raise RuntimeError("AZURE_OPENAI_ENDPOINT (or AZURE_AI_ENDPOINT) is not set")
    if not api_key:
        raise RuntimeError("AZURE_OPENAI_API_KEY (or AZURE_AI_API_KEY) is not set")
    if not deployment:
        raise RuntimeError("AZURE_OPENAI_DEPLOYMENT is not set (this is the deployment name you created in Azure)")

    url = f"{origin}/openai/deployments/{deployment}/chat/completions"
    start = time.time()

    system = (
        "You are a helpful assistant that outputs ONLY valid JSON. "
        "Do not include markdown fences, comments, or extra text."
    )

    with tracer.start_as_current_span("llm.azure_openai.chat_completions") as span:
        span.set_attribute("deployment", deployment)
        span.set_attribute("incident_id", incident_id)

        try:
            with httpx.Client(timeout=60.0) as client:
                resp = client.post(
                    url,
                    params={"api-version": api_version},
                    headers={"api-key": api_key},
                    json={
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": prompt},
                        ],
                    },
                )
        except httpx.RequestError as e:
            raise _ServiceUnavailableError(str(e)) from e

        latency = time.time() - start
        span.set_attribute("latency_ms", int(latency * 1000))

        if resp.status_code in (429,):
            raise _RateLimitError(resp.text)
        if resp.status_code in (500, 502, 503, 504):
            raise _ServiceUnavailableError(resp.text)
        if resp.is_error:
            raise RuntimeError(f"Azure OpenAI HTTP {resp.status_code}: {resp.text}")

        data = resp.json()
        content = (
            (((data.get("choices") or [])[0] or {}).get("message") or {}).get("content")
            if isinstance(data, dict)
            else None
        )
        payload = _extract_json_object(content or "")

        usage = data.get("usage") if isinstance(data, dict) else None
        tokens_used = int((usage or {}).get("total_tokens") or 0) if isinstance(usage, dict) else 0

        label = f"azure_openai:{deployment}"
        llm_calls_total.labels(model=label, success="true").inc()
        llm_latency_seconds.labels(model=label).observe(latency)
        llm_tokens_used.labels(model=label).observe(tokens_used)

        logger.info(
            "llm_call",
            model=label,
            tokens_used=tokens_used,
            latency_ms=int(latency * 1000),
            success=True,
        )

        return {"payload": payload, "tokens_used": tokens_used, "model_used": label}


def _retry_call(prompt: str, incident_id: int) -> dict:
    delay = 1
    for attempt in range(3):
        try:
            provider = _llm_provider()
            if provider == "groq":
                return _call_groq(prompt, incident_id)
            if provider == "azure_ai":
                return _call_azure_ai(prompt, incident_id)
            if provider == "azure_openai":
                return _call_azure_openai(prompt, incident_id)
            return _call_gemini(prompt, incident_id)
        except (_RateLimitError, _ServiceUnavailableError):
            if attempt == 2:
                model_label = (
                    f"groq:{getattr(settings, 'groq_model', DEFAULT_GROQ_MODEL)}"
                    if _llm_provider() == "groq"
                    else f"azure_ai:{getattr(settings, 'azure_ai_model', 'gpt-4o-mini')}"
                    if _llm_provider() == "azure_ai"
                    else f"azure_openai:{getattr(settings, 'azure_openai_deployment', '')}"
                    if _llm_provider() == "azure_openai"
                    else _resolved_model_name()
                )
                llm_calls_total.labels(model=model_label, success="false").inc()
                logger.error("llm_call_failed", success=False)
                raise
            time.sleep(delay)
            delay *= 2
        except Exception:
            model_label = (
                f"groq:{getattr(settings, 'groq_model', DEFAULT_GROQ_MODEL)}"
                if _llm_provider() == "groq"
                else f"azure_ai:{getattr(settings, 'azure_ai_model', 'gpt-4o-mini')}"
                if _llm_provider() == "azure_ai"
                else f"azure_openai:{getattr(settings, 'azure_openai_deployment', '')}"
                if _llm_provider() == "azure_openai"
                else _resolved_model_name()
            )
            llm_calls_total.labels(model=model_label, success="false").inc()
            logger.error("llm_call_failed", success=False)
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
        model_used=str(runbook_result.get("model_used") or postmortem_result.get("model_used") or ""),
        tokens_used=postmortem_result["tokens_used"] + runbook_result["tokens_used"],
    )
