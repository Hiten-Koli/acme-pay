"""Generate a realistic, fully deterministic workforce with salary histories."""

import random
import uuid
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_EVEN, Decimal

from acme_pay.domain.employment import COUNTRY_CURRENCIES, CompensationReason, EmploymentStatus
from acme_pay.seed.reference import (
    COUNTRIES,
    FIRST_NAMES,
    FX_RATES_TO_USD,
    LAST_NAMES,
    ROLES,
    UNDERPAID_GROUPS,
)

DEFAULT_SEED = 42
AS_OF = date(2026, 10, 1)  # Fixed "today" so the dataset never changes between runs.
EARLIEST_HIRE = date(2015, 1, 1)
PAY_SPREAD = 0.13  # Log-normal sigma of individual pay around the role/country level.
TERMINATED_SHARE = 0.05
RAISE_RANGE = (0.025, 0.08)  # Yearly merit raise, as a fraction.
PROMOTION_SHARE = 0.12  # Chance that a yearly change is a promotion (larger raise).
PROMOTION_RANGE = (0.10, 0.18)
CENT = Decimal("0.01")
PAY_ROUNDING = Decimal(100)  # Salaries are offered in round hundreds.
# Share of an underpaid group that is actually underpaid. It must be a minority: if most of
# a group were underpaid, the group's own median would drop and nobody would look out of band.
UNDERPAID_SHARE = 0.3


@dataclass(frozen=True, slots=True)
class SeedEmployee:
    """One generated employee (current state)."""

    id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    job_title: str
    department: str
    country_code: str
    currency: str
    salary: Decimal
    hire_date: date
    status: EmploymentStatus
    terminated_on: date | None


@dataclass(frozen=True, slots=True)
class SeedChange:
    """One generated salary-history entry."""

    id: uuid.UUID
    employee_id: uuid.UUID
    previous_salary: Decimal | None
    new_salary: Decimal
    currency: str
    effective_date: date
    reason: CompensationReason


@dataclass(frozen=True, slots=True)
class SeedFxRate:
    """One generated FX rate."""

    currency: str
    rate_to_usd: Decimal
    effective_date: date


@dataclass(frozen=True, slots=True)
class Dataset:
    """Everything the loader writes, in insertion order."""

    employees: list[SeedEmployee]
    changes: list[SeedChange]
    fx_rates: list[SeedFxRate]


def generate(count: int, seed: int = DEFAULT_SEED) -> Dataset:
    """Generate ``count`` employees with salary histories, plus FX rates.

    The same ``count`` and ``seed`` always produce an identical dataset.
    """
    rng = random.Random(seed)
    roles = [
        (department, title, base, weight)
        for department, titles in ROLES.items()
        for title, (base, weight) in titles.items()
    ]
    countries = list(COUNTRIES)
    employees: list[SeedEmployee] = []
    changes: list[SeedChange] = []

    for index in range(count):
        department, title, base_usd, _ = rng.choices(roles, weights=[r[3] for r in roles])[0]
        country = rng.choices(countries, weights=[COUNTRIES[c][0] for c in countries])[0]
        employee = _employee(rng, index, department, title, base_usd, country)
        employees.append(employee)
        changes.extend(_history(rng, employee))

    fx_rates = [SeedFxRate(c, rate, AS_OF) for c, rate in FX_RATES_TO_USD.items()]
    return Dataset(employees=employees, changes=changes, fx_rates=fx_rates)


def _uuid(rng: random.Random) -> uuid.UUID:
    return uuid.UUID(int=rng.getrandbits(128), version=4)


def _round_pay(amount: Decimal) -> Decimal:
    rounded = (amount / PAY_ROUNDING).quantize(Decimal(1), rounding=ROUND_HALF_EVEN)
    return (rounded * PAY_ROUNDING).quantize(CENT)


def _employee(
    rng: random.Random, index: int, department: str, title: str, base_usd: int, country: str
) -> SeedEmployee:
    currency = COUNTRY_CURRENCIES[country]
    level_usd = Decimal(base_usd) * COUNTRIES[country][1]
    for group_country, group_title, multiplier in UNDERPAID_GROUPS:
        if (country, title) == (group_country, group_title) and rng.random() < UNDERPAID_SHARE:
            level_usd *= multiplier
    individual_usd = level_usd * Decimal(str(round(rng.lognormvariate(0, PAY_SPREAD), 4)))
    salary = _round_pay(individual_usd / FX_RATES_TO_USD[currency])

    hire_date = EARLIEST_HIRE + timedelta(days=rng.randrange((AS_OF - EARLIEST_HIRE).days))
    terminated_on = None
    status = EmploymentStatus.ACTIVE
    if rng.random() < TERMINATED_SHARE and hire_date < AS_OF:
        status = EmploymentStatus.TERMINATED
        terminated_on = hire_date + timedelta(days=rng.randint(1, (AS_OF - hire_date).days))

    first, last = rng.choice(FIRST_NAMES), rng.choice(LAST_NAMES)
    return SeedEmployee(
        id=_uuid(rng),
        first_name=first,
        last_name=last,
        email=f"{first}.{last}.{index + 1:05d}@acme.example".lower(),
        job_title=title,
        department=department,
        country_code=country,
        currency=currency,
        salary=salary,
        hire_date=hire_date,
        status=status,
        terminated_on=terminated_on,
    )


def _history(rng: random.Random, employee: SeedEmployee) -> list[SeedChange]:
    """Yearly raises on hire anniversaries, worked backwards from the current salary."""
    last_day = employee.terminated_on or AS_OF
    anniversaries = []
    year = 1
    while (anniversary := _add_years(employee.hire_date, year)) <= last_day:
        anniversaries.append(anniversary)
        year += 1

    steps: list[tuple[date, CompensationReason, Decimal]] = []
    for anniversary in anniversaries:
        if rng.random() < PROMOTION_SHARE:
            steps.append((anniversary, CompensationReason.PROMOTION, _pct(rng, PROMOTION_RANGE)))
        else:
            steps.append((anniversary, CompensationReason.MERIT, _pct(rng, RAISE_RANGE)))

    # Salaries before each raise, from the most recent backwards; the last equals today's.
    salaries = [employee.salary]
    for _, _, raise_pct in reversed(steps):
        salaries.append(_round_pay(salaries[-1] / (1 + raise_pct)))
    salaries.reverse()

    history = [
        SeedChange(
            _uuid(rng),
            employee.id,
            None,
            salaries[0],
            employee.currency,
            employee.hire_date,
            CompensationReason.HIRE,
        )
    ]
    transitions = zip(steps, salaries[:-1], salaries[1:], strict=True)
    for (effective, reason, _), previous, new in transitions:
        if new != previous:
            history.append(
                SeedChange(
                    _uuid(rng), employee.id, previous, new, employee.currency, effective, reason
                )
            )
    return history


def _pct(rng: random.Random, bounds: tuple[float, float]) -> Decimal:
    return Decimal(str(round(rng.uniform(*bounds), 4)))


def _add_years(day: date, years: int) -> date:
    try:
        return day.replace(year=day.year + years)
    except ValueError:  # 29 February in a non-leap year
        return day.replace(year=day.year + years, day=28)
