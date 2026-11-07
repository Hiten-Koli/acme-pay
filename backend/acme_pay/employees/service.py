"""Employee use cases: hire, update, terminate, find."""

from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from acme_pay.compensation.models import CompensationChange
from acme_pay.core.errors import ConflictError
from acme_pay.domain.employment import (
    CompensationReason,
    EmploymentStatus,
    check_termination,
    currency_for_country,
)
from acme_pay.employees.models import Employee
from acme_pay.employees.repository import EmployeeRepository
from acme_pay.employees.schemas import (
    EmployeeCreate,
    EmployeeFilters,
    EmployeeUpdate,
    TerminationRequest,
)

DUPLICATE_EMAIL = "An employee with this email already exists"


class EmployeeService:
    """Applies HR rules to employee records."""

    def __init__(self, session: AsyncSession, actor: str) -> None:
        self._session = session
        self._actor = actor
        self._employees = EmployeeRepository(session)

    async def get(self, employee_id: UUID) -> Employee:
        """Return an employee.

        Raises:
            NotFoundError: If no employee has ``employee_id``.
        """
        return await self._employees.get_existing(employee_id)

    async def search(self, filters: EmployeeFilters) -> tuple[list[Employee], int]:
        """Return one page of employees matching ``filters`` and the total."""
        return await self._employees.page(filters)

    async def export(self, filters: EmployeeFilters) -> list[Employee]:
        """Return all employees matching ``filters`` for export."""
        return await self._employees.all(filters)

    async def hire(self, data: EmployeeCreate) -> Employee:
        """Create an employee and record their starting salary in the history.

        Raises:
            BusinessRuleViolation: If ACME does not operate in the country.
            ConflictError: If the email is already in use.
        """
        currency = currency_for_country(data.country_code)
        employee = Employee(**data.model_dump(), currency=currency, status=EmploymentStatus.ACTIVE)
        self._session.add(employee)
        await self._flush_unique_email()
        self._session.add(
            CompensationChange(
                employee_id=employee.id,
                previous_salary=None,
                new_salary=data.salary,
                currency=currency,
                effective_date=data.hire_date,
                reason=CompensationReason.HIRE,
                changed_by=self._actor,
            )
        )
        await self._session.commit()
        return employee

    async def update(self, employee_id: UUID, data: EmployeeUpdate) -> Employee:
        """Change profile fields that were provided.

        Raises:
            NotFoundError: If the employee does not exist.
            ConflictError: If the new email is already in use.
        """
        employee = await self.get(employee_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(employee, field, value)
        await self._flush_unique_email()
        await self._session.commit()
        return employee

    async def terminate(self, employee_id: UUID, data: TerminationRequest) -> Employee:
        """Mark an employee as having left, keeping their record and history.

        Raises:
            NotFoundError: If the employee does not exist.
            BusinessRuleViolation: If already terminated or dated before the hire date.
        """
        employee = await self.get(employee_id)
        check_termination(
            status=employee.status, hire_date=employee.hire_date, terminated_on=data.terminated_on
        )
        employee.status = EmploymentStatus.TERMINATED
        employee.terminated_on = data.terminated_on
        await self._session.commit()
        return employee

    async def _flush_unique_email(self) -> None:
        try:
            await self._session.flush()
        except IntegrityError as error:
            await self._session.rollback()
            if "email" in str(error.orig):
                raise ConflictError(DUPLICATE_EMAIL) from error
            raise
