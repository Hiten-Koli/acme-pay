"""HTTP endpoints for employees. Thin: validation in schemas, rules in the service."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from acme_pay.core.database import get_session
from acme_pay.core.security import get_current_actor
from acme_pay.employees.models import Employee
from acme_pay.employees.schemas import (
    EmployeeCreate,
    EmployeeFilters,
    EmployeePage,
    EmployeeRead,
    EmployeeUpdate,
    TerminationRequest,
)
from acme_pay.employees.service import EmployeeService

router = APIRouter(prefix="/employees", tags=["employees"])


def get_employee_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    actor: Annotated[str, Depends(get_current_actor)],
) -> EmployeeService:
    """Build the service for one request."""
    return EmployeeService(session, actor)


Service = Annotated[EmployeeService, Depends(get_employee_service)]


@router.get("")
async def list_employees(
    service: Service, filters: Annotated[EmployeeFilters, Query()]
) -> EmployeePage:
    """Search, filter, sort and page through employees."""
    employees, total = await service.list(filters)
    return EmployeePage(
        items=[EmployeeRead.model_validate(e) for e in employees],
        total=total,
        page=filters.page,
        page_size=filters.page_size,
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=EmployeeRead)
async def hire_employee(service: Service, data: EmployeeCreate) -> Employee:
    """Add a new employee with their starting salary."""
    return await service.hire(data)


@router.get("/{employee_id}", response_model=EmployeeRead)
async def get_employee(service: Service, employee_id: UUID) -> Employee:
    """Return one employee."""
    return await service.get(employee_id)


@router.patch("/{employee_id}", response_model=EmployeeRead)
async def update_employee(service: Service, employee_id: UUID, data: EmployeeUpdate) -> Employee:
    """Update profile fields (not salary)."""
    return await service.update(employee_id, data)


@router.post("/{employee_id}/terminate", response_model=EmployeeRead)
async def terminate_employee(
    service: Service, employee_id: UUID, data: TerminationRequest
) -> Employee:
    """Record that an employee has left."""
    return await service.terminate(employee_id, data)
