"""Insights over a tiny hand-computed workforce, so every expected number is checkable.

Active employees (FX: EUR = 1.08 USD, INR = 0.012 USD):
  DE Software Engineers, EUR: 80k, 90k, 100k, 110k, 200k  -> median 100k
  IN Software Engineers, INR: 1.8M, 3.0M                  -> median 2.4M
Plus one terminated DE engineer, who must be ignored everywhere.

USD salaries: 86,400 · 97,200 · 108,000 · 118,800 · 216,000 · 21,600 · 36,000
  payroll 684,000 · median 97,200
Compa-ratios: DE 0.80 0.90 1.00 1.10 2.00 · IN 0.75 1.25 -> 1 below band, 2 above.
"""

from datetime import date
from decimal import Decimal
from typing import Any
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from acme_pay.domain.employment import EmploymentStatus
from acme_pay.employees.models import Employee
from acme_pay.fx.models import FxRateRecord

pytestmark = [pytest.mark.anyio, pytest.mark.integration]

RATE_DATE = date(2026, 10, 1)


@pytest.fixture
async def workforce(session: AsyncSession) -> dict[str, UUID]:
    session.add_all(
        [
            FxRateRecord(currency="EUR", effective_date=date(2025, 1, 1), rate_to_usd=Decimal(2)),
            FxRateRecord(currency="EUR", effective_date=RATE_DATE, rate_to_usd=Decimal("1.08")),
            FxRateRecord(currency="INR", effective_date=RATE_DATE, rate_to_usd=Decimal("0.012")),
        ]
    )
    people = {
        "de_80k": ("DE", "EUR", "80000"),
        "de_90k": ("DE", "EUR", "90000"),
        "de_100k": ("DE", "EUR", "100000"),
        "de_110k": ("DE", "EUR", "110000"),
        "de_200k": ("DE", "EUR", "200000"),
        "in_1_8m": ("IN", "INR", "1800000"),
        "in_3m": ("IN", "INR", "3000000"),
    }
    employees = {
        key: Employee(
            first_name=key,
            last_name="Test",
            email=f"{key}@acme.example",
            job_title="Software Engineer",
            department="Engineering",
            country_code=country,
            currency=currency,
            salary=Decimal(salary),
            hire_date=date(2023, 1, 1),
            status=EmploymentStatus.ACTIVE,
        )
        for key, (country, currency, salary) in people.items()
    }
    leaver = Employee(
        first_name="Gone",
        last_name="Test",
        email="gone@acme.example",
        job_title="Software Engineer",
        department="Engineering",
        country_code="DE",
        currency="EUR",
        salary=Decimal(999999),
        hire_date=date(2020, 1, 1),
        status=EmploymentStatus.TERMINATED,
        terminated_on=date(2024, 1, 1),
    )
    session.add_all([*employees.values(), leaver])
    await session.commit()
    return {key: employee.id for key, employee in employees.items()}


def by(items: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {item[key]: item for item in items}


class TestPulse:
    async def test_summarizes_the_active_workforce_in_usd(
        self, client: AsyncClient, workforce: dict[str, UUID]
    ) -> None:
        pulse = (await client.get("/api/insights/pulse")).json()

        assert pulse["headcount"] == 7
        assert pulse["payroll_usd"] == "684000.00"
        assert pulse["median_salary_usd"] == "97200.00"
        assert pulse["below_band"] == 1
        assert pulse["above_band"] == 2
        assert pulse["rate_date"] == "2026-10-01"

    async def test_breaks_payroll_down_by_country(
        self, client: AsyncClient, workforce: dict[str, UUID]
    ) -> None:
        countries = by(
            (await client.get("/api/insights/pulse")).json()["countries"], "country_code"
        )

        assert countries["DE"]["headcount"] == 5
        assert countries["DE"]["payroll_usd"] == "626400.00"
        assert countries["DE"]["median_salary_usd"] == "108000.00"
        assert countries["IN"]["payroll_usd"] == "57600.00"

    async def test_signals_peer_groups_with_people_below_band(
        self, client: AsyncClient, workforce: dict[str, UUID]
    ) -> None:
        [signal] = (await client.get("/api/insights/pulse")).json()["signals"]

        assert signal["country_code"] == "IN"
        assert signal["job_title"] == "Software Engineer"
        assert signal["below_band"] == 1
        assert signal["headcount"] == 2


async def test_benchmarks_a_role_across_countries(
    client: AsyncClient, workforce: dict[str, UUID]
) -> None:
    response = await client.get(
        "/api/insights/benchmarks", params={"job_title": "Software Engineer"}
    )

    de = by(response.json()["countries"], "country_code")["DE"]
    assert de["currency"] == "EUR"
    assert (de["min"], de["p25"], de["median"], de["p75"], de["max"]) == (
        "80000.00",
        "90000.00",
        "100000.00",
        "110000.00",
        "200000.00",
    )
    assert de["average"] == "116000.00"
    assert de["median_usd"] == "108000.00"


async def test_distribution_buckets_cover_everyone(
    client: AsyncClient, workforce: dict[str, UUID]
) -> None:
    distribution = (await client.get("/api/insights/distribution", params={"country": "DE"})).json()

    assert distribution["currency"] == "EUR"
    assert sum(bucket["count"] for bucket in distribution["buckets"]) == 5


async def test_outliers_lists_people_outside_band_with_their_ratio(
    client: AsyncClient, workforce: dict[str, UUID]
) -> None:
    outliers = (await client.get("/api/insights/outliers", params={"band": "below"})).json()

    [outlier] = outliers
    assert outlier["id"] == str(workforce["in_1_8m"])
    assert outlier["compa_ratio"] == "0.75"
    assert outlier["peer_median"] == "2400000.00"


class TestPayPosition:
    async def test_places_an_employee_among_their_peers(
        self, client: AsyncClient, workforce: dict[str, UUID]
    ) -> None:
        position = (await client.get(f"/api/employees/{workforce['de_200k']}/pay-position")).json()

        assert position["compa_ratio"] == "2.00"
        assert position["band"] == "above"
        assert position["peers"]["headcount"] == 5
        assert position["peers"]["median"] == "100000.00"

    async def test_previews_a_raise_before_it_is_saved(
        self, client: AsyncClient, workforce: dict[str, UUID]
    ) -> None:
        url = f"/api/employees/{workforce['in_1_8m']}/compensation/preview"

        preview = (await client.post(url, json={"new_salary": "2160000.00"})).json()

        assert preview["current"] == {
            "salary": "1800000.00",
            "compa_ratio": "0.75",
            "band": "below",
        }
        assert preview["proposed"] == {
            "salary": "2160000.00",
            "compa_ratio": "0.90",
            "band": "within",
        }
        assert preview["change_percent"] == "20.00"
        assert preview["annual_cost_change_usd"] == "4320.00"
        history = (await client.get(f"/api/employees/{workforce['in_1_8m']}/compensation")).json()
        assert history == []


async def test_options_list_countries_with_names_and_currencies(
    client: AsyncClient, workforce: dict[str, UUID]
) -> None:
    options = (await client.get("/api/meta/options")).json()

    assert by(options["countries"], "code")["DE"] == {
        "code": "DE",
        "name": "Germany",
        "currency": "EUR",
    }
    assert options["departments"] == ["Engineering"]
    assert options["job_titles"] == ["Software Engineer"]


async def test_exports_the_filtered_directory_as_csv(
    client: AsyncClient, workforce: dict[str, UUID]
) -> None:
    response = await client.get("/api/employees/export.csv", params={"country": "IN"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    lines = response.text.strip().splitlines()
    assert lines[0].startswith("employee_code,first_name,last_name")
    assert len(lines) == 3
