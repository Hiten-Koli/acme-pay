from typing import Any

import pytest
from httpx import AsyncClient

pytestmark = [pytest.mark.anyio, pytest.mark.integration]

UNKNOWN_ID = "00000000-0000-0000-0000-000000000000"


async def hire(client: AsyncClient) -> dict[str, Any]:
    response = await client.post(
        "/api/employees",
        json={
            "first_name": "Ada",
            "last_name": "Lovelace",
            "email": "ada@acme.example",
            "job_title": "Software Engineer",
            "department": "Engineering",
            "country_code": "DE",
            "salary": "85000.00",
            "hire_date": "2024-03-01",
        },
    )
    assert response.status_code == 201, response.text
    body: dict[str, Any] = response.json()
    return body


def salary_change(**overrides: str) -> dict[str, str]:
    return {"new_salary": "93500.00", "effective_date": "2026-01-01", "reason": "merit"} | overrides


async def test_history_starts_with_the_starting_salary(client: AsyncClient) -> None:
    employee = await hire(client)

    response = await client.get(f"/api/employees/{employee['id']}/compensation")

    assert response.status_code == 200
    [entry] = response.json()
    assert entry["reason"] == "hire"
    assert entry["previous_salary"] is None
    assert entry["new_salary"] == "85000.00"
    assert entry["currency"] == "EUR"
    assert entry["changed_by"] == "HR Manager"


async def test_a_raise_updates_the_salary_and_is_recorded(client: AsyncClient) -> None:
    employee = await hire(client)
    url = f"/api/employees/{employee['id']}/compensation"

    response = await client.post(url, json=salary_change())

    assert response.status_code == 201
    assert response.json()["previous_salary"] == "85000.00"
    assert response.json()["new_salary"] == "93500.00"
    updated = await client.get(f"/api/employees/{employee['id']}")
    assert updated.json()["salary"] == "93500.00"


async def test_history_is_newest_first(client: AsyncClient) -> None:
    employee = await hire(client)
    url = f"/api/employees/{employee['id']}/compensation"
    await client.post(url, json=salary_change())
    await client.post(
        url,
        json=salary_change(new_salary="105000.00", effective_date="2026-07-01", reason="promotion"),
    )

    history = (await client.get(url)).json()

    assert [entry["reason"] for entry in history] == ["promotion", "merit", "hire"]


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"new_salary": "85000.00"}, "already"),
        ({"effective_date": "2024-01-01"}, "hire date"),
        ({"reason": "hire"}, "starting salary"),
    ],
)
async def test_rejects_changes_that_break_hr_rules(
    client: AsyncClient, change: dict[str, str], message: str
) -> None:
    employee = await hire(client)

    response = await client.post(
        f"/api/employees/{employee['id']}/compensation", json=salary_change(**change)
    )

    assert response.status_code == 422
    assert message in response.json()["detail"]


async def test_rejects_changes_for_terminated_employees(client: AsyncClient) -> None:
    employee = await hire(client)
    await client.post(
        f"/api/employees/{employee['id']}/terminate", json={"terminated_on": "2026-06-30"}
    )

    response = await client.post(
        f"/api/employees/{employee['id']}/compensation", json=salary_change()
    )

    assert response.status_code == 422


async def test_rejected_change_leaves_salary_and_history_untouched(client: AsyncClient) -> None:
    employee = await hire(client)
    url = f"/api/employees/{employee['id']}/compensation"

    await client.post(url, json=salary_change(effective_date="2024-01-01"))

    assert len((await client.get(url)).json()) == 1
    assert (await client.get(f"/api/employees/{employee['id']}")).json()["salary"] == "85000.00"


@pytest.mark.parametrize("method", ["GET", "POST"])
async def test_unknown_employee_is_not_found(client: AsyncClient, method: str) -> None:
    response = await client.request(
        method, f"/api/employees/{UNKNOWN_ID}/compensation", json=salary_change()
    )

    assert response.status_code == 404
