# /devpulse/backend/app/api/runbooks.py


from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.db.models import Incident, Runbook, User
from app.db.session import get_session
from app.observability.tracing import traced_route
from app.workers.tasks import celery_app, generate_runbook_task

router = APIRouter()


class RunbookGenerateRequest(BaseModel):
    incident_id: int


class RunbookResponse(BaseModel):
    id: int
    incident_id: int
    runbook_md: str
    model_used: str
    tokens_used: int

    class Config:
        from_attributes = True


@router.post("/generate")
@traced_route("runbooks.generate")
async def generate_runbook(
    data: RunbookGenerateRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User, Depends(get_current_user)],
):
    result = await session.execute(
        select(Incident).where(Incident.id == data.incident_id, Incident.created_by == user.id)
    )
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    task = generate_runbook_task.delay(incident.id)
    return {"task_id": task.id}


@router.get("/{runbook_id}", response_model=RunbookResponse)
@traced_route("runbooks.get")
async def get_runbook(
    runbook_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User, Depends(get_current_user)],
):
    result = await session.execute(
        select(Runbook).join(Incident).where(Runbook.id == runbook_id, Incident.created_by == user.id)
    )
    runbook = result.scalar_one_or_none()
    if not runbook:
        raise HTTPException(status_code=404, detail="Runbook not found")
    return runbook


@router.get("/tasks/{task_id}")
@traced_route("runbooks.task_status")
async def get_runbook_task_status(
    task_id: str,
    user: Annotated[User, Depends(get_current_user)],
):
    result = celery_app.AsyncResult(task_id)
    payload: dict = {"task_id": task_id, "state": result.state}
    if result.successful():
        payload["runbook_id"] = result.result
    if result.failed():
        payload["error"] = str(result.result)
    return payload
