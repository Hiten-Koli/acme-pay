"""Write a generated dataset to PostgreSQL, replacing existing data."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from acme_pay.seed.generator import Dataset

_EMPLOYEE_COLUMNS = (
    "id",
    "first_name",
    "last_name",
    "email",
    "job_title",
    "department",
    "country_code",
    "currency",
    "salary",
    "hire_date",
    "status",
    "terminated_on",
)
_CHANGE_COLUMNS = (
    "id",
    "employee_id",
    "previous_salary",
    "new_salary",
    "currency",
    "effective_date",
    "reason",
    "changed_by",
)
SEED_AUTHOR = "Seed import"


async def load(connection: AsyncConnection, dataset: Dataset) -> None:
    """Replace all employees, salary history and FX rates with ``dataset``.

    Uses PostgreSQL COPY, which loads tens of thousands of rows in well under a second.
    Runs inside the caller's transaction, so a failure leaves the old data intact.
    """
    await connection.execute(text("TRUNCATE compensation_changes, employees, fx_rates"))
    await connection.execute(text("ALTER SEQUENCE employee_code_seq RESTART"))
    raw = await connection.get_raw_connection()
    copy = raw.driver_connection.copy_records_to_table  # type: ignore[union-attr]

    await copy(
        "fx_rates",
        columns=("currency", "effective_date", "rate_to_usd"),
        records=[(r.currency, r.effective_date, r.rate_to_usd) for r in dataset.fx_rates],
    )
    await copy(
        "employees",
        columns=_EMPLOYEE_COLUMNS,
        records=[
            (
                e.id,
                e.first_name,
                e.last_name,
                e.email,
                e.job_title,
                e.department,
                e.country_code,
                e.currency,
                e.salary,
                e.hire_date,
                e.status.value,
                e.terminated_on,
            )
            for e in dataset.employees
        ],
    )
    await copy(
        "compensation_changes",
        columns=_CHANGE_COLUMNS,
        records=[
            (
                c.id,
                c.employee_id,
                c.previous_salary,
                c.new_salary,
                c.currency,
                c.effective_date,
                c.reason.value,
                SEED_AUTHOR,
            )
            for c in dataset.changes
        ],
    )
