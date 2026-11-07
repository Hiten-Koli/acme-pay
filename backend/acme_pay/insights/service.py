"""Insight use cases: combine SQL aggregates with the domain's pay rules."""

from decimal import ROUND_HALF_EVEN, Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from acme_pay.domain.compa_ratio import BandPosition, band_position, compa_ratio
from acme_pay.domain.employment import COUNTRY_CURRENCIES, COUNTRY_NAMES
from acme_pay.domain.money import CENT, Money
from acme_pay.employees.repository import EmployeeRepository
from acme_pay.insights.repository import InsightsRepository
from acme_pay.insights.schemas import (
    Benchmarks,
    Bucket,
    Country,
    CountryBenchmark,
    CountryPay,
    DepartmentPay,
    Distribution,
    Options,
    Outlier,
    PayPosition,
    PeerStats,
    PositionSnapshot,
    Preview,
    Pulse,
    Signal,
)

HISTOGRAM_BUCKETS = 12
REPORTING_CURRENCY = "USD"
HUNDRED = Decimal(100)


def _snapshot(salary: Decimal, currency: str, median: Decimal | None) -> PositionSnapshot:
    if median is None or median <= 0:
        return PositionSnapshot(salary=salary, compa_ratio=None, band=None)
    ratio = compa_ratio(Money(salary, currency), peer_median=Money(median, currency))
    return PositionSnapshot(salary=salary, compa_ratio=ratio, band=band_position(ratio))


class InsightsService:
    """Answers HR's questions about how the organization pays people."""

    def __init__(self, session: AsyncSession) -> None:
        self._insights = InsightsRepository(session)
        self._employees = EmployeeRepository(session)

    async def pulse(self) -> Pulse:
        """Organization-wide pay summary with breakdowns and signals."""
        totals = await self._insights.totals()
        countries = await self._insights.by_group("country_code", "currency")
        departments = await self._insights.by_group("department")
        signals = await self._insights.signals()
        return Pulse(
            **totals,
            countries=[CountryPay.model_validate(dict(row)) for row in countries],
            departments=[DepartmentPay.model_validate(dict(row)) for row in departments],
            signals=[Signal.model_validate(dict(row)) for row in signals],
        )

    async def options(self) -> Options:
        """Countries ACME operates in, and departments and job titles currently in use."""
        countries = sorted(
            (
                Country(code=code, name=COUNTRY_NAMES[code], currency=currency)
                for code, currency in COUNTRY_CURRENCIES.items()
            ),
            key=lambda country: country.name,
        )
        return Options(
            countries=countries,
            departments=await self._insights.distinct_values("department"),
            job_titles=await self._insights.distinct_values("job_title"),
        )

    async def benchmarks(self, job_title: str) -> Benchmarks:
        """Compare one role's pay across countries."""
        rows = await self._insights.benchmarks(job_title)
        return Benchmarks(
            job_title=job_title,
            countries=[CountryBenchmark.model_validate(dict(row)) for row in rows],
        )

    async def distribution(
        self, *, country: str | None, department: str | None, job_title: str | None
    ) -> Distribution:
        """Salary histogram in equal-width buckets."""
        lowest, highest, counts = await self._insights.histogram(
            buckets=HISTOGRAM_BUCKETS, country=country, department=department, job_title=job_title
        )
        currency = (
            COUNTRY_CURRENCIES.get(country, REPORTING_CURRENCY) if country else REPORTING_CURRENCY
        )
        if lowest is None or highest is None:
            return Distribution(currency=currency, buckets=[])
        width = (highest + CENT - lowest) / HISTOGRAM_BUCKETS
        buckets = [
            Bucket(
                lower=(lowest + width * index).quantize(CENT),
                upper=(lowest + width * (index + 1)).quantize(CENT),
                count=counts.get(index + 1, 0),
            )
            for index in range(HISTOGRAM_BUCKETS)
        ]
        return Distribution(currency=currency, buckets=buckets)

    async def outliers(
        self, *, band: BandPosition | None, country: str | None, job_title: str | None
    ) -> list[Outlier]:
        """Active employees paid outside the band for their peer group."""
        rows = await self._insights.outliers(band=band, country=country, job_title=job_title)
        return [Outlier.model_validate(dict(row)) for row in rows]

    async def pay_position(self, employee_id: UUID) -> PayPosition:
        """Where an employee's salary sits among their peers.

        Raises:
            NotFoundError: If the employee does not exist.
        """
        employee = await self._employees.get_existing(employee_id)
        peers = await self._peers(employee.country_code, employee.job_title, employee.currency)
        snapshot = _snapshot(employee.salary, employee.currency, peers.median)
        return PayPosition(
            salary=employee.salary,
            compa_ratio=snapshot.compa_ratio,
            band=snapshot.band,
            peers=peers,
        )

    async def preview(self, employee_id: UUID, new_salary: Decimal) -> Preview:
        """Evaluate a proposed salary without saving anything.

        Raises:
            NotFoundError: If the employee does not exist.
        """
        employee = await self._employees.get_existing(employee_id)
        peers = await self._peers(employee.country_code, employee.job_title, employee.currency)
        change = new_salary - employee.salary
        rate = await self._insights.latest_rate(employee.currency)
        return Preview(
            current=_snapshot(employee.salary, employee.currency, peers.median),
            proposed=_snapshot(new_salary, employee.currency, peers.median),
            change_amount=change,
            change_percent=(change / employee.salary * HUNDRED).quantize(
                CENT, rounding=ROUND_HALF_EVEN
            ),
            annual_cost_change_usd=(change * rate[0]).quantize(CENT) if rate else None,
            peer_median=peers.median,
        )

    async def _peers(self, country_code: str, job_title: str, currency: str) -> PeerStats:
        row = await self._insights.peer_stats(country_code, job_title)
        return PeerStats(country_code=country_code, job_title=job_title, currency=currency, **row)
