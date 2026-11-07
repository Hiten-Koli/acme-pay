"""Request and response shapes for the compensation API."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from acme_pay.domain.employment import CompensationReason
from acme_pay.employees.schemas import Salary


class SalaryChangeRequest(BaseModel):
    """A new salary for an employee, in their own currency."""

    model_config = ConfigDict(extra="forbid")

    new_salary: Salary
    effective_date: date
    reason: CompensationReason


class CompensationChangeRead(BaseModel):
    """One entry in an employee's salary history. Amounts are decimal strings."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    previous_salary: Decimal | None
    new_salary: Decimal
    currency: str
    effective_date: date
    reason: CompensationReason
    changed_by: str
    created_at: datetime
