import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from acme_pay.domain.employment import EmploymentStatus
from acme_pay.seed.generator import generate
from acme_pay.seed.loader import load

pytestmark = [pytest.mark.anyio, pytest.mark.integration]


async def test_loaded_employees_and_history_are_served_by_the_api(
    session: AsyncSession, client: AsyncClient
) -> None:
    dataset = generate(50)
    await load(await session.connection(), dataset)

    page = (await client.get("/api/employees", params={"page_size": 100})).json()
    active = [e for e in dataset.employees if e.status is EmploymentStatus.ACTIVE]
    assert page["total"] == len(active)

    first = dataset.employees[0]
    history = (await client.get(f"/api/employees/{first.id}/compensation")).json()
    assert history[0]["new_salary"] == str(first.salary)
    assert history[-1]["reason"] == "hire"


async def test_loading_twice_replaces_rather_than_duplicates(
    session: AsyncSession, client: AsyncClient
) -> None:
    connection = await session.connection()
    await load(connection, generate(20))
    await load(connection, generate(20))

    page = (await client.get("/api/employees", params={"status": "active"})).json()
    terminated = (await client.get("/api/employees", params={"status": "terminated"})).json()
    assert page["total"] + terminated["total"] == 20
