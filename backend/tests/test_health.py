"""Behaviour of the health endpoint, used by uptime checks and the deploy smoke test."""

import pytest
from httpx import ASGITransport, AsyncClient, Response

from acme_pay.core.database import database_is_reachable
from acme_pay.main import create_app

pytestmark = pytest.mark.anyio


async def get_health(*, database_reachable: bool) -> Response:
    app = create_app()

    async def fake_probe() -> bool:
        return database_reachable

    app.dependency_overrides[database_is_reachable] = fake_probe
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        return await client.get("/api/health")


async def test_reports_ok_when_database_is_reachable() -> None:
    response = await get_health(database_reachable=True)

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


async def test_reports_degraded_when_database_is_unreachable() -> None:
    response = await get_health(database_reachable=False)

    assert response.status_code == 503
    assert response.json() == {"status": "degraded", "database": "unavailable"}
