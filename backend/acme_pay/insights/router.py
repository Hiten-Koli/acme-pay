"""HTTP endpoints for pay insights."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from acme_pay.core.database import get_session
from acme_pay.domain.compa_ratio import BandPosition
from acme_pay.employees.schemas import CountryCode
from acme_pay.insights.schemas import (
    Benchmarks,
    Distribution,
    Outlier,
    PayPosition,
    Preview,
    PreviewRequest,
    Pulse,
)
from acme_pay.insights.service import InsightsService

router = APIRouter(tags=["insights"])


def get_insights_service(session: Annotated[AsyncSession, Depends(get_session)]) -> InsightsService:
    """Build the service for one request."""
    return InsightsService(session)


Service = Annotated[InsightsService, Depends(get_insights_service)]
OptionalCountry = Annotated[CountryCode | None, Query()]


@router.get("/insights/pulse")
async def pulse(service: Service) -> Pulse:
    """Organization-wide pay at a glance."""
    return await service.pulse()


@router.get("/insights/benchmarks")
async def benchmarks(
    service: Service, job_title: Annotated[str, Query(min_length=1)]
) -> Benchmarks:
    """Compare one role's pay across countries."""
    return await service.benchmarks(job_title)


@router.get("/insights/distribution")
async def distribution(
    service: Service,
    country: OptionalCountry = None,
    department: str | None = None,
    job_title: str | None = None,
) -> Distribution:
    """Salary histogram (local currency for one country, otherwise USD)."""
    return await service.distribution(country=country, department=department, job_title=job_title)


@router.get("/insights/outliers")
async def outliers(
    service: Service,
    band: BandPosition | None = None,
    country: OptionalCountry = None,
    job_title: str | None = None,
) -> list[Outlier]:
    """People paid outside the band for their peer group, most extreme first."""
    return await service.outliers(band=band, country=country, job_title=job_title)


@router.get("/employees/{employee_id}/pay-position")
async def pay_position(service: Service, employee_id: UUID) -> PayPosition:
    """Where one employee's salary sits among their peers."""
    return await service.pay_position(employee_id)


@router.post("/employees/{employee_id}/compensation/preview")
async def preview_salary_change(
    service: Service, employee_id: UUID, request: PreviewRequest
) -> Preview:
    """Show the effect of a proposed salary without saving it."""
    return await service.preview(employee_id, request.new_salary)
