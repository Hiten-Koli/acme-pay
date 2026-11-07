from datetime import date
from decimal import Decimal

import pytest

from acme_pay.domain.employment import (
    BusinessRuleViolation,
    CompensationReason,
    EmploymentStatus,
    check_salary_change,
    check_termination,
    currency_for_country,
)
from acme_pay.domain.money import Money

HIRED = date(2024, 3, 1)
CURRENT = Money(Decimal("80000.00"), "EUR")
RAISED = Money(Decimal("88000.00"), "EUR")


def change_salary(
    *,
    new: Money = RAISED,
    effective: date = date(2026, 1, 1),
    reason: CompensationReason = CompensationReason.MERIT,
    status: EmploymentStatus = EmploymentStatus.ACTIVE,
) -> None:
    check_salary_change(
        status=status,
        hire_date=HIRED,
        current=CURRENT,
        new=new,
        effective_date=effective,
        reason=reason,
    )


class TestSalaryChange:
    def test_allows_a_raise_for_an_active_employee(self) -> None:
        change_salary()

    def test_allows_a_downward_correction(self) -> None:
        change_salary(new=Money(Decimal("79000.00"), "EUR"), reason=CompensationReason.CORRECTION)

    def test_rejects_changes_for_terminated_employees(self) -> None:
        with pytest.raises(BusinessRuleViolation, match="terminated"):
            change_salary(status=EmploymentStatus.TERMINATED)

    @pytest.mark.parametrize("amount", ["0", "-1"])
    def test_rejects_non_positive_salaries(self, amount: str) -> None:
        with pytest.raises(BusinessRuleViolation, match="positive"):
            change_salary(new=Money(Decimal(amount), "EUR"))

    def test_rejects_a_change_to_the_same_salary(self) -> None:
        with pytest.raises(BusinessRuleViolation, match="already"):
            change_salary(new=CURRENT)

    def test_rejects_an_effective_date_before_the_hire_date(self) -> None:
        with pytest.raises(BusinessRuleViolation, match="hire date"):
            change_salary(effective=date(2024, 2, 29))

    def test_rejects_hire_as_a_reason_after_hiring(self) -> None:
        with pytest.raises(BusinessRuleViolation, match="hire"):
            change_salary(reason=CompensationReason.HIRE)

    def test_rejects_a_salary_in_another_currency(self) -> None:
        with pytest.raises(BusinessRuleViolation, match="currency"):
            change_salary(new=Money(Decimal("90000.00"), "USD"))


class TestTermination:
    def test_allows_terminating_an_active_employee(self) -> None:
        check_termination(
            status=EmploymentStatus.ACTIVE, hire_date=HIRED, terminated_on=date(2026, 6, 30)
        )

    def test_rejects_terminating_twice(self) -> None:
        with pytest.raises(BusinessRuleViolation, match="already terminated"):
            check_termination(
                status=EmploymentStatus.TERMINATED, hire_date=HIRED, terminated_on=date(2026, 6, 30)
            )

    def test_rejects_a_termination_date_before_the_hire_date(self) -> None:
        with pytest.raises(BusinessRuleViolation, match="hire date"):
            check_termination(
                status=EmploymentStatus.ACTIVE, hire_date=HIRED, terminated_on=date(2024, 1, 1)
            )


class TestCountryCurrency:
    @pytest.mark.parametrize(("country", "currency"), [("DE", "EUR"), ("IN", "INR"), ("US", "USD")])
    def test_pays_employees_in_their_country_currency(self, country: str, currency: str) -> None:
        assert currency_for_country(country) == currency

    def test_rejects_countries_acme_does_not_operate_in(self) -> None:
        with pytest.raises(BusinessRuleViolation, match="not supported"):
            currency_for_country("ZZ")
