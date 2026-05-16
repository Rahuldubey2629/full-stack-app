# /devpulse/backend/app/api/retrospectives.py


from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.db.models import Incident, Retrospective, User
from app.db.session import get_session
from app.observability.tracing import traced_route
from app.workers.tasks import celery_app, generate_retrospective_task

router = APIRouter()


class RetrospectiveGenerateRequest(BaseModel):
    incident_id: int


class RetrospectiveResponse(BaseModel):
    id: int
    incident_id: int
    postmortem_md: str
    runbook_md: str
    severity_score: int
    mttr_minutes: int
    model_used: str
    tokens_used: int

    class Config:
        from_attributes = True


@router.post("/generate")
@traced_route("retrospectives.generate")
async def generate_retrospective(
    data: RetrospectiveGenerateRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User, Depends(get_current_user)],
):
    result = await session.execute(
        select(Incident).where(Incident.id == data.incident_id, Incident.created_by == user.id)
    )
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    task = generate_retrospective_task.delay(incident.id)
    return {"task_id": task.id}


@router.get("/{retro_id}", response_model=RetrospectiveResponse)
@traced_route("retrospectives.get")
async def get_retrospective(
    retro_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User, Depends(get_current_user)],
):
    result = await session.execute(
        select(Retrospective).join(Incident).where(
            Retrospective.id == retro_id,
            Incident.created_by == user.id,
        )
    )
    retro = result.scalar_one_or_none()
    if not retro:
        raise HTTPException(status_code=404, detail="Retrospective not found")
    return retro


@router.get("/tasks/{task_id}")
@traced_route("retrospectives.task_status")
async def get_retrospective_task_status(
    task_id: str,
    user: Annotated[User, Depends(get_current_user)],
):
    # Note: Celery task results are not user-scoped by default.
    # In production, include user_id in task args/result and enforce it here.
    result = celery_app.AsyncResult(task_id)
    payload: dict = {"task_id": task_id, "state": result.state}
    if result.successful():
        payload["retrospective_id"] = result.result
    if result.failed():
        payload["error"] = str(result.result)
    return payload
