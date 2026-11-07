"""Employment lifecycle and salary-change rules."""

from datetime import date
from enum import StrEnum

from acme_pay.domain.money import Money

# Countries ACME operates in, with the currency employees there are paid in.
COUNTRY_CURRENCIES: dict[str, str] = {
    "US": "USD",
    "CA": "CAD",
    "BR": "BRL",
    "GB": "GBP",
    "DE": "EUR",
    "FR": "EUR",
    "IN": "INR",
    "SG": "SGD",
    "JP": "JPY",
    "AU": "AUD",
}


class EmploymentStatus(StrEnum):
    """Whether someone currently works at ACME."""

    ACTIVE = "active"
    TERMINATED = "terminated"


class CompensationReason(StrEnum):
    """Why a salary was set or changed."""

    HIRE = "hire"
    MERIT = "merit"
    PROMOTION = "promotion"
    MARKET_ADJUSTMENT = "market_adjustment"
    CORRECTION = "correction"


class BusinessRuleViolation(ValueError):  # noqa: N818 - reads as a domain term, not an error type
    """Raised when a requested change breaks an HR business rule."""


def currency_for_country(country_code: str) -> str:
    """Return the currency employees in ``country_code`` are paid in.

    Raises:
        BusinessRuleViolation: If ACME does not operate in that country.
    """
    try:
        return COUNTRY_CURRENCIES[country_code]
    except KeyError:
        raise BusinessRuleViolation(f"Country {country_code!r} is not supported") from None


def check_salary_change(
    *,
    status: EmploymentStatus,
    hire_date: date,
    current: Money,
    new: Money,
    effective_date: date,
    reason: CompensationReason,
) -> None:
    """Validate a salary change against HR rules.

    Raises:
        BusinessRuleViolation: If any rule is broken; the message says which.
    """
    if status is EmploymentStatus.TERMINATED:
        raise BusinessRuleViolation("Salary cannot change for a terminated employee")
    if reason is CompensationReason.HIRE:
        raise BusinessRuleViolation("'hire' is only used for the starting salary")
    if new.currency != current.currency:
        raise BusinessRuleViolation(f"Salary must stay in the employee currency {current.currency}")
    if new.amount <= 0:
        raise BusinessRuleViolation("Salary must be positive")
    if new.amount == current.amount:
        raise BusinessRuleViolation("Salary is already this amount")
    if effective_date < hire_date:
        raise BusinessRuleViolation("A salary change cannot take effect before the hire date")


def check_termination(*, status: EmploymentStatus, hire_date: date, terminated_on: date) -> None:
    """Validate a termination against HR rules.

    Raises:
        BusinessRuleViolation: If the employee is already terminated or the date is invalid.
    """
    if status is EmploymentStatus.TERMINATED:
        raise BusinessRuleViolation("Employee is already terminated")
    if terminated_on < hire_date:
        raise BusinessRuleViolation("Termination cannot be before the hire date")
