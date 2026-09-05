"""Automated integration tests for FastAPI session and health endpoints."""

import pytest
import httpx
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "database" in data
        assert data["database"]["indexed_chunks"] > 0
        assert "ollama" in data


@pytest.mark.asyncio
async def test_session_lifecycle():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create Session
        create_res = await client.post("/api/sessions", json={"title": "Pytest Test Session"})
        assert create_res.status_code == 201
        sess_data = create_res.json()
        sess_id = sess_data["id"]
        assert sess_data["title"] == "Pytest Test Session"

        # 2. Get Session Detail
        detail_res = await client.get(f"/api/sessions/{sess_id}")
        assert detail_res.status_code == 200
        detail_data = detail_res.json()
        assert detail_data["session"]["id"] == sess_id
        assert isinstance(detail_data["messages"], list)

        # 3. List Sessions
        list_res = await client.get("/api/sessions")
        assert list_res.status_code == 200
        sessions = list_res.json()
        assert any(s["id"] == sess_id for s in sessions)

        # 4. Delete Session
        del_res = await client.delete(f"/api/sessions/{sess_id}")
        assert del_res.status_code == 204

        # 5. Verify Not Found after delete
        not_found_res = await client.get(f"/api/sessions/{sess_id}")
        assert not_found_res.status_code == 404
