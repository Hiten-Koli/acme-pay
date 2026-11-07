"""Employee queries. The only module in this slice that knows SQL."""

from typing import Any
from uuid import UUID

from sqlalchemy import ColumnElement, Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from acme_pay.core.errors import NotFoundError
from acme_pay.employees.models import Employee
from acme_pay.employees.schemas import EmployeeFilters, EmployeeSort

_ORDERING: dict[EmployeeSort, tuple[ColumnElement[Any], ...]] = {
    EmployeeSort.NAME: (Employee.last_name.asc(), Employee.first_name.asc()),
    EmployeeSort.NAME_DESC: (Employee.last_name.desc(), Employee.first_name.desc()),
    EmployeeSort.SALARY: (Employee.salary.asc(),),
    EmployeeSort.SALARY_DESC: (Employee.salary.desc(),),
    EmployeeSort.HIRE_DATE: (Employee.hire_date.asc(),),
    EmployeeSort.HIRE_DATE_DESC: (Employee.hire_date.desc(),),
}


def _escape_like(term: str) -> str:
    """Make the LIKE wildcards (percent, underscore) and the escape character match literally."""
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _filtered(filters: EmployeeFilters) -> Select[Employee]:
    query = select(Employee).where(Employee.status == filters.status)
    if filters.country:
        query = query.where(Employee.country_code == filters.country)
    if filters.department:
        query = query.where(Employee.department == filters.department)
    if filters.job_title:
        query = query.where(Employee.job_title == filters.job_title)
    if filters.search:
        pattern = f"%{_escape_like(filters.search.strip())}%"
        full_name = Employee.first_name + " " + Employee.last_name
        query = query.where(
            or_(
                full_name.ilike(pattern, escape="\\"),
                Employee.email.ilike(pattern, escape="\\"),
                Employee.employee_code.ilike(pattern, escape="\\"),
            )
        )
    return query


class EmployeeRepository:
    """Loads and stores employees."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, employee_id: UUID) -> Employee | None:
        """Return the employee with ``employee_id``, or ``None``."""
        return await self._session.get(Employee, employee_id)

    async def get_existing(self, employee_id: UUID) -> Employee:
        """Return the employee with ``employee_id``.

        Raises:
            NotFoundError: If there is no such employee.
        """
        employee = await self.get(employee_id)
        if employee is None:
            raise NotFoundError(f"Employee {employee_id} not found")
        return employee

    async def page(self, filters: EmployeeFilters) -> tuple[list[Employee], int]:
        """Return one page of employees matching ``filters`` and the total match count."""
        query = _filtered(filters)
        total = await self._session.scalar(select(func.count()).select_from(query.subquery()))
        # The id tiebreaker keeps paging stable when sort values repeat.
        ordered = query.order_by(*_ORDERING[filters.sort], Employee.id)
        offset = (filters.page - 1) * filters.page_size
        rows = await self._session.scalars(ordered.offset(offset).limit(filters.page_size))
        return list(rows), total or 0
