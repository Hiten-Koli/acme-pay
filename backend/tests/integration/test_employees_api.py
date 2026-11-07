from typing import Any

import pytest
from httpx import AsyncClient

pytestmark = [pytest.mark.anyio, pytest.mark.integration]

PROBLEM_JSON = "application/problem+json"


def new_employee(**overrides: Any) -> dict[str, Any]:
    employee = {
        "first_name": "Ada",
        "last_name": "Lovelace",
        "email": "ada.lovelace@acme.example",
        "job_title": "Software Engineer",
        "department": "Engineering",
        "country_code": "DE",
        "salary": "85000.00",
        "hire_date": "2024-03-01",
    }
    return employee | overrides


async def create(client: AsyncClient, **overrides: Any) -> dict[str, Any]:
    response = await client.post("/api/employees", json=new_employee(**overrides))
    assert response.status_code == 201, response.text
    body: dict[str, Any] = response.json()
    return body


class TestCreate:
    async def test_creates_an_active_employee_paid_in_their_country_currency(
        self, client: AsyncClient
    ) -> None:
        employee = await create(client)

        assert employee["status"] == "active"
        assert employee["currency"] == "EUR"
        assert employee["salary"] == "85000.00"
        assert employee["employee_code"].startswith("EMP-")

    async def test_normalizes_email_to_lowercase(self, client: AsyncClient) -> None:
        employee = await create(client, email="Ada.Lovelace@ACME.example")

        assert employee["email"] == "ada.lovelace@acme.example"

    async def test_rejects_a_duplicate_email_as_a_conflict(self, client: AsyncClient) -> None:
        await create(client)

        response = await client.post("/api/employees", json=new_employee(first_name="Other"))

        assert response.status_code == 409
        assert response.headers["content-type"] == PROBLEM_JSON
        assert "email" in response.json()["detail"]

    async def test_rejects_an_unsupported_country(self, client: AsyncClient) -> None:
        response = await client.post("/api/employees", json=new_employee(country_code="ZZ"))

        assert response.status_code == 422
        assert response.headers["content-type"] == PROBLEM_JSON

    @pytest.mark.parametrize(
        "field", [{"salary": "-1"}, {"salary": "12.345"}, {"email": "not-an-email"}]
    )
    async def test_rejects_invalid_input_as_problem_details(
        self, client: AsyncClient, field: dict[str, str]
    ) -> None:
        response = await client.post("/api/employees", json=new_employee(**field))

        assert response.status_code == 422
        assert response.headers["content-type"] == PROBLEM_JSON
        assert response.json()["errors"]


class TestReadAndUpdate:
    async def test_reads_an_employee_by_id(self, client: AsyncClient) -> None:
        created = await create(client)

        response = await client.get(f"/api/employees/{created['id']}")

        assert response.status_code == 200
        assert response.json() == created

    async def test_unknown_employee_is_not_found(self, client: AsyncClient) -> None:
        response = await client.get("/api/employees/00000000-0000-0000-0000-000000000000")

        assert response.status_code == 404
        assert response.headers["content-type"] == PROBLEM_JSON

    async def test_updates_profile_fields(self, client: AsyncClient) -> None:
        created = await create(client)

        response = await client.patch(
            f"/api/employees/{created['id']}", json={"job_title": "Senior Software Engineer"}
        )

        assert response.status_code == 200
        assert response.json()["job_title"] == "Senior Software Engineer"
        assert response.json()["first_name"] == "Ada"

    async def test_salary_cannot_be_changed_through_profile_updates(
        self, client: AsyncClient
    ) -> None:
        created = await create(client)

        response = await client.patch(f"/api/employees/{created['id']}", json={"salary": "1.00"})

        assert response.status_code == 422


class TestTerminate:
    async def test_terminates_an_employee_and_keeps_the_record(self, client: AsyncClient) -> None:
        created = await create(client)

        response = await client.post(
            f"/api/employees/{created['id']}/terminate", json={"terminated_on": "2026-06-30"}
        )

        assert response.status_code == 200
        assert response.json()["status"] == "terminated"
        assert response.json()["terminated_on"] == "2026-06-30"

    async def test_terminating_twice_breaks_a_business_rule(self, client: AsyncClient) -> None:
        created = await create(client)
        url = f"/api/employees/{created['id']}/terminate"
        await client.post(url, json={"terminated_on": "2026-06-30"})

        response = await client.post(url, json={"terminated_on": "2026-07-01"})

        assert response.status_code == 422
        assert "already terminated" in response.json()["detail"]


class TestList:
    async def test_pages_through_active_employees_with_a_total(self, client: AsyncClient) -> None:
        for n in range(3):
            await create(client, email=f"person{n}@acme.example")

        response = await client.get("/api/employees", params={"page": 1, "page_size": 2})

        page = response.json()
        assert response.status_code == 200
        assert page["total"] == 3
        assert len(page["items"]) == 2

    async def test_filters_by_country_and_department(self, client: AsyncClient) -> None:
        await create(client, email="de@acme.example")
        await create(client, email="in@acme.example", country_code="IN")
        await create(client, email="sales@acme.example", department="Sales")

        response = await client.get(
            "/api/employees", params={"country": "DE", "department": "Engineering"}
        )

        assert [e["email"] for e in response.json()["items"]] == ["de@acme.example"]

    async def test_searches_by_name_email_or_code(self, client: AsyncClient) -> None:
        await create(client)
        await create(client, first_name="Grace", last_name="Hopper", email="grace@acme.example")

        response = await client.get("/api/employees", params={"search": "hopp"})

        assert [e["last_name"] for e in response.json()["items"]] == ["Hopper"]

    async def test_search_treats_wildcards_literally(self, client: AsyncClient) -> None:
        await create(client)

        response = await client.get("/api/employees", params={"search": "%"})

        assert response.json()["total"] == 0

    async def test_excludes_terminated_employees_unless_asked(self, client: AsyncClient) -> None:
        leaver = await create(client)
        await client.post(
            f"/api/employees/{leaver['id']}/terminate", json={"terminated_on": "2026-06-30"}
        )

        active = await client.get("/api/employees")
        terminated = await client.get("/api/employees", params={"status": "terminated"})

        assert active.json()["total"] == 0
        assert terminated.json()["total"] == 1

    async def test_sorts_by_salary_descending(self, client: AsyncClient) -> None:
        await create(client, email="low@acme.example", salary="50000.00")
        await create(client, email="high@acme.example", salary="150000.00")

        response = await client.get("/api/employees", params={"sort": "-salary"})

        assert [e["email"] for e in response.json()["items"]] == [
            "high@acme.example",
            "low@acme.example",
        ]
