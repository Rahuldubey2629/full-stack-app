# /devpulse/backend/app/workers/tasks.py
from __future__ import annotations

import asyncio

from celery import Celery
from sqlalchemy import select

from app.config import get_settings
from app.db.models import Incident, Retrospective, Runbook
from app.db.session import AsyncSessionLocal
from app.services.llm_service import generate_retrospective

settings = get_settings()
celery_app = Celery("devpulse", broker=settings.redis_url, backend=settings.redis_url)


@celery_app.task(name="generate_retrospective")
def generate_retrospective_task(incident_id: int) -> int:
    async def _run():
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Incident).where(Incident.id == incident_id))
            incident = result.scalar_one_or_none()
            if not incident:
                return 0
            llm_result = generate_retrospective(incident.raw_input, incident.id)
            retro = Retrospective(
                incident_id=incident.id,
                postmortem_md=llm_result.postmortem_md,
                runbook_md=llm_result.runbook_md,
                severity_score=llm_result.severity_score,
                mttr_minutes=llm_result.mttr_minutes,
                model_used=llm_result.model_used,
                tokens_used=llm_result.tokens_used,
            )
            session.add(retro)
            session.add(
                Runbook(
                    incident_id=incident.id,
                    runbook_md=llm_result.runbook_md,
                    model_used=llm_result.model_used,
                    tokens_used=llm_result.tokens_used,
                )
            )
            await session.commit()
            return retro.id

    return asyncio.run(_run())


@celery_app.task(name="generate_runbook")
def generate_runbook_task(incident_id: int) -> int:
    async def _run():
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Incident).where(Incident.id == incident_id))
            incident = result.scalar_one_or_none()
            if not incident:
                return 0
            llm_result = generate_retrospective(incident.raw_input, incident.id)
            runbook = Runbook(
                incident_id=incident.id,
                runbook_md=llm_result.runbook_md,
                model_used=llm_result.model_used,
                tokens_used=llm_result.tokens_used,
            )
            session.add(runbook)
            await session.commit()
            return runbook.id

    return asyncio.run(_run())
