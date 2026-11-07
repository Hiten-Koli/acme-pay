from collections import Counter, defaultdict
from decimal import Decimal
from itertools import pairwise
from uuid import UUID

import pytest

from acme_pay.domain.employment import COUNTRY_CURRENCIES, CompensationReason, EmploymentStatus
from acme_pay.seed.generator import AS_OF, Dataset, SeedChange, generate

SAMPLE_SIZE = 600


@pytest.fixture(scope="module")
def dataset() -> Dataset:
    return generate(SAMPLE_SIZE)


def test_generates_the_requested_number_of_employees(dataset: Dataset) -> None:
    assert len(dataset.employees) == SAMPLE_SIZE


def test_is_deterministic(dataset: Dataset) -> None:
    assert generate(SAMPLE_SIZE) == dataset


def test_emails_are_unique(dataset: Dataset) -> None:
    emails = [e.email for e in dataset.employees]
    assert len(set(emails)) == len(emails)


def test_employees_are_paid_in_their_country_currency(dataset: Dataset) -> None:
    for employee in dataset.employees:
        assert employee.currency == COUNTRY_CURRENCIES[employee.country_code]


def test_salaries_are_positive_whole_cents(dataset: Dataset) -> None:
    for employee in dataset.employees:
        assert employee.salary > 0
        assert employee.salary == employee.salary.quantize(Decimal("0.01"))


def test_covers_every_country_acme_operates_in(dataset: Dataset) -> None:
    assert {e.country_code for e in dataset.employees} == set(COUNTRY_CURRENCIES)


def test_most_employees_are_active(dataset: Dataset) -> None:
    statuses = Counter(e.status for e in dataset.employees)
    assert statuses[EmploymentStatus.ACTIVE] > 0.9 * SAMPLE_SIZE
    assert statuses[EmploymentStatus.TERMINATED] > 0


def test_dates_are_consistent(dataset: Dataset) -> None:
    for employee in dataset.employees:
        assert employee.hire_date <= AS_OF
        if employee.terminated_on is not None:
            assert employee.hire_date <= employee.terminated_on <= AS_OF


def test_history_chains_from_starting_salary_to_current_salary(dataset: Dataset) -> None:
    by_employee: defaultdict[UUID, list[SeedChange]] = defaultdict(list)
    for change in dataset.changes:
        by_employee[change.employee_id].append(change)

    for employee in dataset.employees:
        history = by_employee[employee.id]
        assert history[0].reason is CompensationReason.HIRE
        assert history[0].previous_salary is None
        assert history[0].effective_date == employee.hire_date
        for before, after in pairwise(history):
            assert after.previous_salary == before.new_salary
            assert after.effective_date > before.effective_date
        assert history[-1].new_salary == employee.salary


def test_provides_a_rate_for_every_currency(dataset: Dataset) -> None:
    assert {rate.currency for rate in dataset.fx_rates} == set(COUNTRY_CURRENCIES.values())
