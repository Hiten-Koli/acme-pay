"""HTTP endpoints for an employee's salary history."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from acme_pay.compensation.models import CompensationChange
from acme_pay.compensation.schemas import CompensationChangeRead, SalaryChangeRequest
from acme_pay.compensation.service import CompensationService
from acme_pay.core.database import get_session
from acme_pay.core.security import get_current_actor

router = APIRouter(prefix="/employees/{employee_id}/compensation", tags=["compensation"])


def get_compensation_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    actor: Annotated[str, Depends(get_current_actor)],
) -> CompensationService:
    """Build the service for one request."""
    return CompensationService(session, actor)


Service = Annotated[CompensationService, Depends(get_compensation_service)]


@router.get("", response_model=list[CompensationChangeRead])
async def salary_history(service: Service, employee_id: UUID) -> list[CompensationChange]:
    """Return the employee's salary history, newest first."""
    return await service.history(employee_id)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CompensationChangeRead)
async def change_salary(
    service: Service, employee_id: UUID, request: SalaryChangeRequest
) -> CompensationChange:
    """Give the employee a new salary and record why."""
    return await service.change_salary(employee_id, request)
