# /devpulse/backend/tests/test_api.py
import pytest
from httpx import AsyncClient

import os

# Ensure required settings exist for import-time configuration.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("JWT_SECRET", "test_secret")
os.environ.setdefault("GEMINI_API_KEY", "test_key")

from app.main import app


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
