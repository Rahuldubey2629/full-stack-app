# /devpulse/backend/app/api/auth.py


from datetime import datetime, timedelta
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.models import User
from app.db.session import get_session
from app.observability.logging import bind_user_id
from app.observability.tracing import traced_route

router = APIRouter()
settings = get_settings()

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    email: str
    password: str
    team_id: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


def _create_token(subject: str, token_type: str, minutes: int) -> str:
    payload = {
        "sub": subject,
        "type": token_type,
        "exp": datetime.utcnow() + timedelta(minutes=minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


async def _get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


@router.post("/register", response_model=TokenResponse)
@traced_route("auth.register")
async def register(data: RegisterRequest, session: Annotated[AsyncSession, Depends(get_session)]):
    existing = await _get_user_by_email(session, data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=data.email,
        hashed_password=pwd_context.hash(data.password),
        team_id=data.team_id,
    )
    session.add(user)
    await session.commit()

    access_token = _create_token(user.email, "access", settings.jwt_access_minutes)
    refresh_token = _create_token(user.email, "refresh", settings.jwt_refresh_minutes)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse)
@traced_route("auth.login")
async def login(data: LoginRequest, session: Annotated[AsyncSession, Depends(get_session)]):
    user = await _get_user_by_email(session, data.email)
    if not user or not pwd_context.verify(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = _create_token(user.email, "access", settings.jwt_access_minutes)
    refresh_token = _create_token(user.email, "refresh", settings.jwt_refresh_minutes)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
@traced_route("auth.refresh")
async def refresh(data: RefreshRequest):
    try:
        payload = jwt.decode(data.refresh_token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    email = payload.get("sub")
    access_token = _create_token(email, "access", settings.jwt_access_minutes)
    refresh_token = _create_token(email, "refresh", settings.jwt_refresh_minutes)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    email = payload.get("sub")
    user = await _get_user_by_email(session, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    bind_user_id(str(user.id))
    return user
