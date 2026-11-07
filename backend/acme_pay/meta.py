"""Reference options for filters and forms (countries, departments, job titles)."""

from fastapi import APIRouter

from acme_pay.insights.router import Service
from acme_pay.insights.schemas import Options

router = APIRouter(tags=["meta"])


@router.get("/meta/options")
async def options(service: Service) -> Options:
    """Countries ACME operates in, and departments and job titles currently in use."""
    return await service.options()
