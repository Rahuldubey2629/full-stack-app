# /devpulse/backend/app/api/incidents.py


from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.db.models import Incident, User
from app.db.session import get_session
from app.observability.tracing import traced_route

router = APIRouter()


class IncidentCreate(BaseModel):
    title: str
    description: str
    raw_input: str
    severity_label: str


class IncidentResponse(BaseModel):
    id: int
    title: str
    description: str
    raw_input: str
    severity_label: str
    status: str
    created_by: int

    class Config:
        from_attributes = True


@router.post("/", response_model=IncidentResponse)
@traced_route("incidents.create")
async def create_incident(
    data: IncidentCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User, Depends(get_current_user)],
):
    incident = Incident(
        title=data.title,
        description=data.description,
        raw_input=data.raw_input,
        severity_label=data.severity_label,
        created_by=user.id,
    )
    session.add(incident)
    await session.commit()
    await session.refresh(incident)
    return incident


@router.get("/", response_model=list[IncidentResponse])
@traced_route("incidents.list")
async def list_incidents(
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User, Depends(get_current_user)],
):
    result = await session.execute(select(Incident).where(Incident.created_by == user.id))
    return list(result.scalars().all())


@router.get("/{incident_id}", response_model=IncidentResponse)
@traced_route("incidents.get")
async def get_incident(
    incident_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User, Depends(get_current_user)],
):
    result = await session.execute(
        select(Incident).where(Incident.id == incident_id, Incident.created_by == user.id)
    )
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident
