from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from acme_pay.assistant.router import get_llm_provider
from acme_pay.assistant.tools import TOOLS
from acme_pay.core.config import get_settings
from acme_pay.insights.service import InsightsService
from acme_pay.seed.generator import generate
from acme_pay.seed.loader import load

pytestmark = [pytest.mark.anyio, pytest.mark.integration]

PERSONAL_FIELDS = {"id", "first_name", "last_name", "email", "employee_code"}
SAMPLE_ARGUMENTS: dict[str, dict[str, Any]] = {
    "org_pay_summary": {},
    "role_pay_by_country": {"job_title": "Software Engineer"},
    "salary_distribution": {"country": "IN"},
    "available_filters": {},
}


def keys_in(value: Any) -> set[str]:
    if isinstance(value, dict):
        return set(value) | {k for v in value.values() for k in keys_in(v)}
    if isinstance(value, list):
        return {k for item in value for k in keys_in(item)}
    return set()


async def test_no_tool_ever_returns_personal_data(session: AsyncSession) -> None:
    dataset = generate(200)
    await load(await session.connection(), dataset)
    names = {e.last_name for e in dataset.employees}
    insights = InsightsService(session)

    for name, tool in TOOLS.items():
        result = await tool.execute(insights, SAMPLE_ARGUMENTS[name])

        assert not keys_in(result) & PERSONAL_FIELDS, name
        assert "@" not in str(result), name
        assert not any(last_name in str(result) for last_name in names), name


async def test_status_reports_whether_the_assistant_is_configured(client: AsyncClient) -> None:
    status = (await client.get("/api/assistant/status")).json()

    assert status == {"enabled": False}


async def test_asking_without_a_configured_model_is_service_unavailable(
    client: AsyncClient,
) -> None:
    response = await client.post("/api/assistant/ask", json={"question": "Median pay in DE?"})

    assert response.status_code == 503
    assert response.headers["content-type"] == "application/problem+json"


def test_provider_is_absent_without_an_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "")
    get_settings.cache_clear()
    try:
        assert get_llm_provider() is None
    finally:
        get_settings.cache_clear()
