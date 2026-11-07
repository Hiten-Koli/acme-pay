"""Compensation use cases: change a salary, read the history."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from acme_pay.compensation.models import CompensationChange
from acme_pay.compensation.repository import CompensationRepository
from acme_pay.compensation.schemas import SalaryChangeRequest
from acme_pay.domain.employment import check_salary_change
from acme_pay.domain.money import Money
from acme_pay.employees.repository import EmployeeRepository


class CompensationService:
    """Changes salaries so that the current salary and its history never disagree."""

    def __init__(self, session: AsyncSession, actor: str) -> None:
        self._session = session
        self._actor = actor
        self._employees = EmployeeRepository(session)
        self._changes = CompensationRepository(session)

    async def history(self, employee_id: UUID) -> list[CompensationChange]:
        """Return an employee's salary history, newest first.

        Raises:
            NotFoundError: If the employee does not exist.
        """
        await self._employees.get_existing(employee_id)
        return await self._changes.history(employee_id)

    async def change_salary(
        self, employee_id: UUID, request: SalaryChangeRequest
    ) -> CompensationChange:
        """Set a new salary and record the change, atomically.

        Raises:
            NotFoundError: If the employee does not exist.
            BusinessRuleViolation: If the change breaks an HR rule.
        """
        employee = await self._employees.get_existing(employee_id)
        check_salary_change(
            status=employee.status,
            hire_date=employee.hire_date,
            current=employee.current_salary,
            new=Money(request.new_salary, employee.currency),
            effective_date=request.effective_date,
            reason=request.reason,
        )
        change = CompensationChange(
            employee_id=employee.id,
            previous_salary=employee.salary,
            new_salary=request.new_salary,
            currency=employee.currency,
            effective_date=request.effective_date,
            reason=request.reason,
            changed_by=self._actor,
        )
        employee.salary = request.new_salary
        self._session.add(change)
        await self._session.commit()
        return change
