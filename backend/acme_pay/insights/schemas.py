"""Response shapes for pay insights. Money amounts are decimal strings."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from acme_pay.domain.compa_ratio import BandPosition
from acme_pay.employees.schemas import Salary


class GroupPay(BaseModel):
    """Headcount and USD pay for one group (a country or a department)."""

    headcount: int
    payroll_usd: Decimal
    median_salary_usd: Decimal


class CountryPay(GroupPay):
    """Pay in one country."""

    country_code: str
    currency: str


class DepartmentPay(GroupPay):
    """Pay in one department."""

    department: str


class Signal(BaseModel):
    """A peer group where people are paid below band: somewhere HR should look."""

    country_code: str
    job_title: str
    currency: str
    headcount: int
    below_band: int
    median_salary: Decimal


class Pulse(BaseModel):
    """Organization-wide pay at a glance (active employees, USD at dated FX rates)."""

    rate_date: date | None
    headcount: int
    payroll_usd: Decimal
    median_salary_usd: Decimal | None
    below_band: int
    above_band: int
    countries: list[CountryPay]
    departments: list[DepartmentPay]
    signals: list[Signal]


class CountryBenchmark(BaseModel):
    """Pay statistics for one role in one country."""

    country_code: str
    currency: str
    headcount: int
    min: Decimal
    p25: Decimal
    median: Decimal
    p75: Decimal
    max: Decimal
    average: Decimal
    p25_usd: Decimal
    median_usd: Decimal
    p75_usd: Decimal


class Benchmarks(BaseModel):
    """One role compared across countries."""

    job_title: str
    countries: list[CountryBenchmark]


class Bucket(BaseModel):
    """One histogram bar: salaries from ``lower`` (inclusive) to ``upper``."""

    lower: Decimal
    upper: Decimal
    count: int


class Distribution(BaseModel):
    """Salary histogram; local currency when filtered to a country, otherwise USD."""

    currency: str
    buckets: list[Bucket]


class Outlier(BaseModel):
    """An active employee paid outside the band for their peer group."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    employee_code: str
    first_name: str
    last_name: str
    job_title: str
    country_code: str
    currency: str
    salary: Decimal
    peer_median: Decimal
    compa_ratio: Decimal
    band: BandPosition


class PeerStats(BaseModel):
    """Active colleagues with the same job title in the same country."""

    country_code: str
    job_title: str
    currency: str
    headcount: int
    p10: Decimal | None
    p25: Decimal | None
    median: Decimal | None
    p75: Decimal | None
    p90: Decimal | None


class PayPosition(BaseModel):
    """Where one employee's salary sits among their peers."""

    salary: Decimal
    compa_ratio: Decimal | None
    band: BandPosition | None
    peers: PeerStats


class PreviewRequest(BaseModel):
    """A proposed new salary to evaluate without saving it."""

    model_config = ConfigDict(extra="forbid")

    new_salary: Salary


class PositionSnapshot(BaseModel):
    """A salary and where it sits against the peer median."""

    salary: Decimal
    compa_ratio: Decimal | None
    band: BandPosition | None


class Preview(BaseModel):
    """The effect of a proposed salary change, before it is made."""

    current: PositionSnapshot
    proposed: PositionSnapshot
    change_amount: Decimal
    change_percent: Decimal
    annual_cost_change_usd: Decimal | None
    peer_median: Decimal | None
