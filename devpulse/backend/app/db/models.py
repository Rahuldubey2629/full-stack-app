# /devpulse/backend/app/db/models.py
from __future__ import annotations

from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class User(Base, SoftDeleteMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    team_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    incidents: Mapped[list["Incident"]] = relationship(back_populates="creator")


class Incident(Base, SoftDeleteMixin):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    raw_input: Mapped[str] = mapped_column(Text)
    severity_label: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default="open")
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    creator: Mapped[User] = relationship(back_populates="incidents")
    retrospectives: Mapped[list["Retrospective"]] = relationship(back_populates="incident")


class Retrospective(Base, SoftDeleteMixin):
    __tablename__ = "retrospectives"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"))
    postmortem_md: Mapped[str] = mapped_column(Text)
    runbook_md: Mapped[str] = mapped_column(Text)
    severity_score: Mapped[int] = mapped_column(Integer)
    mttr_minutes: Mapped[int] = mapped_column(Integer)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    model_used: Mapped[str] = mapped_column(String(128))
    tokens_used: Mapped[int] = mapped_column(Integer)

    incident: Mapped[Incident] = relationship(back_populates="retrospectives")


class Runbook(Base, SoftDeleteMixin):
    __tablename__ = "runbooks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"))
    runbook_md: Mapped[str] = mapped_column(Text)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    model_used: Mapped[str] = mapped_column(String(128))
    tokens_used: Mapped[int] = mapped_column(Integer)
