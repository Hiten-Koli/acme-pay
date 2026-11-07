"""Pay analytics in SQL. Aggregation happens in PostgreSQL, next to the data.

All queries share one set of CTEs:
  rates  - the latest dated FX rate per currency
  pay    - active employees with their salary converted to USD
  peers  - median salary per peer group (same job title, same country)
  ranked - pay plus each person's compa-ratio against their peer median
Medians use percentile_cont (double precision) and are rounded back to cents.
"""

from collections.abc import Sequence
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import RowMapping, text
from sqlalchemy.ext.asyncio import AsyncSession

from acme_pay.domain.compa_ratio import BAND_HIGH, BAND_LOW, BandPosition

SIGNAL_LIMIT = 5
OUTLIER_LIMIT = 50

_BASE = """
WITH rates AS (
    SELECT DISTINCT ON (currency) currency, rate_to_usd, effective_date
    FROM fx_rates
    ORDER BY currency, effective_date DESC
),
pay AS (
    SELECT e.id, e.employee_code, e.first_name, e.last_name, e.job_title, e.department,
           e.country_code, e.currency, e.salary,
           e.salary * r.rate_to_usd AS salary_usd, r.effective_date AS rate_date
    FROM employees e
    JOIN rates r ON r.currency = e.currency
    WHERE e.status = 'active'
),
peers AS (
    SELECT country_code, job_title,
           percentile_cont(0.5) WITHIN GROUP (ORDER BY salary)::numeric AS median
    FROM pay
    GROUP BY country_code, job_title
),
ranked AS (
    SELECT pay.*, round(peers.median, 2) AS peer_median,
           round(pay.salary / peers.median, 2) AS compa_ratio
    FROM pay
    JOIN peers USING (country_code, job_title)
)
"""


def _median(column: str) -> str:
    return f"round((percentile_cont(0.5) WITHIN GROUP (ORDER BY {column}))::numeric, 2)"


def _percentile(fraction: float, column: str) -> str:
    return f"round((percentile_cont({fraction}) WITHIN GROUP (ORDER BY {column}))::numeric, 2)"


def _optional(column: str, param: str) -> str:
    """A filter that only applies when the bound parameter is not NULL."""
    return f"(CAST(:{param} AS text) IS NULL OR {column} = CAST(:{param} AS text))"


_BANDS = {"band_low": BAND_LOW, "band_high": BAND_HIGH}


class InsightsRepository:
    """Runs the analytics queries."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _all(self, sql: str, **params: Any) -> Sequence[RowMapping]:
        result = await self._session.execute(text(_BASE + sql), params)
        return result.mappings().all()

    async def totals(self) -> RowMapping:
        """Headcount, USD payroll and median, band counts and the latest rate date."""
        [row] = await self._all(
            f"""
            SELECT count(*) AS headcount,
                   coalesce(round(sum(salary_usd), 2), 0) AS payroll_usd,
                   {_median("salary_usd")} AS median_salary_usd,
                   count(*) FILTER (WHERE compa_ratio < :band_low) AS below_band,
                   count(*) FILTER (WHERE compa_ratio > :band_high) AS above_band,
                   max(rate_date) AS rate_date
            FROM ranked
            """,
            **_BANDS,
        )
        return row

    async def by_group(self, *columns: str) -> Sequence[RowMapping]:
        """USD headcount, payroll and median grouped by trusted, code-defined ``columns``."""
        group = ", ".join(columns)
        return await self._all(
            f"""
            SELECT {group}, count(*) AS headcount,
                   round(sum(salary_usd), 2) AS payroll_usd,
                   {_median("salary_usd")} AS median_salary_usd
            FROM pay
            GROUP BY {group}
            ORDER BY payroll_usd DESC
            """
        )

    async def signals(self) -> Sequence[RowMapping]:
        """Peer groups with the largest share of people paid below band."""
        return await self._all(
            f"""
            SELECT country_code, job_title, currency, count(*) AS headcount,
                   count(*) FILTER (WHERE compa_ratio < :band_low) AS below_band,
                   {_median("salary")} AS median_salary
            FROM ranked
            GROUP BY country_code, job_title, currency
            HAVING count(*) FILTER (WHERE compa_ratio < :band_low) > 0
            ORDER BY count(*) FILTER (WHERE compa_ratio < :band_low)::numeric / count(*) DESC,
                     below_band DESC
            LIMIT :limit
            """,
            band_low=BAND_LOW,
            limit=SIGNAL_LIMIT,
        )

    async def benchmarks(self, job_title: str) -> Sequence[RowMapping]:
        """Salary statistics per country for one job title."""
        return await self._all(
            f"""
            SELECT country_code, currency, count(*) AS headcount,
                   min(salary) AS min, {_percentile(0.25, "salary")} AS p25,
                   {_median("salary")} AS median, {_percentile(0.75, "salary")} AS p75,
                   max(salary) AS max, round(avg(salary), 2) AS average,
                   {_percentile(0.25, "salary_usd")} AS p25_usd,
                   {_median("salary_usd")} AS median_usd,
                   {_percentile(0.75, "salary_usd")} AS p75_usd
            FROM pay
            WHERE job_title = :job_title
            GROUP BY country_code, currency
            ORDER BY median_usd DESC
            """,
            job_title=job_title,
        )

    async def histogram(
        self, *, buckets: int, country: str | None, department: str | None, job_title: str | None
    ) -> tuple[Decimal | None, Decimal | None, dict[int, int]]:
        """Bucket salaries (local currency for one country, else USD) into equal widths.

        Returns:
            The lowest and highest amounts, and the count per 1-based bucket number.
        """
        amount = "salary" if country else "salary_usd"
        filters = " AND ".join(
            [
                _optional("country_code", "country"),
                _optional("department", "department"),
                _optional("job_title", "job_title"),
            ]
        )
        rows = await self._all(
            f"""
            , filtered AS (SELECT {amount} AS amount FROM pay WHERE {filters}),
            bounds AS (SELECT min(amount) AS lo, max(amount) AS hi FROM filtered)
            SELECT bounds.lo, bounds.hi,
                   width_bucket(amount, bounds.lo, bounds.hi + 0.01, :buckets) AS bucket,
                   count(*) AS count
            FROM filtered, bounds
            GROUP BY bounds.lo, bounds.hi, bucket
            """,
            buckets=buckets,
            country=country,
            department=department,
            job_title=job_title,
        )
        if not rows:
            return None, None, {}
        return rows[0]["lo"], rows[0]["hi"], {row["bucket"]: row["count"] for row in rows}

    async def outliers(
        self, *, band: BandPosition | None, country: str | None, job_title: str | None
    ) -> Sequence[RowMapping]:
        """Active employees outside the band, most extreme first."""
        band_filter = "(compa_ratio < :band_low OR compa_ratio > :band_high)"
        if band is BandPosition.BELOW:
            band_filter = "compa_ratio < :band_low"
        elif band is BandPosition.ABOVE:
            band_filter = "compa_ratio > :band_high"
        return await self._all(
            f"""
            SELECT id, employee_code, first_name, last_name, job_title, country_code, currency,
                   salary, peer_median, compa_ratio
            FROM ranked
            WHERE {band_filter}
              AND {_optional("country_code", "country")}
              AND {_optional("job_title", "job_title")}
            ORDER BY abs(compa_ratio - 1) DESC, employee_code
            LIMIT :limit
            """,
            **_BANDS,
            country=country,
            job_title=job_title,
            limit=OUTLIER_LIMIT,
        )

    async def peer_stats(self, country_code: str, job_title: str) -> RowMapping:
        """Distribution of active peers' salaries for one country and job title."""
        [row] = await self._all(
            f"""
            SELECT count(*) AS headcount,
                   {_percentile(0.1, "salary")} AS p10, {_percentile(0.25, "salary")} AS p25,
                   {_median("salary")} AS median,
                   {_percentile(0.75, "salary")} AS p75, {_percentile(0.9, "salary")} AS p90
            FROM pay
            WHERE country_code = :country_code AND job_title = :job_title
            """,
            country_code=country_code,
            job_title=job_title,
        )
        return row

    async def latest_rate(self, currency: str) -> tuple[Decimal, date] | None:
        """The most recent USD rate for ``currency``, if any."""
        row = (
            await self._session.execute(
                text(
                    "SELECT rate_to_usd, effective_date FROM fx_rates WHERE currency = :currency "
                    "ORDER BY effective_date DESC LIMIT 1"
                ),
                {"currency": currency},
            )
        ).first()
        return (row.rate_to_usd, row.effective_date) if row else None

    async def distinct_values(self, column: str) -> list[str]:
        """Sorted distinct values of a trusted, code-defined employee ``column`` (active only)."""
        rows = await self._session.execute(
            text(f"SELECT DISTINCT {column} FROM employees WHERE status = 'active' ORDER BY 1")
        )
        return list(rows.scalars())
