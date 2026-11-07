"""Reference options for filters and forms (countries, departments, job titles)."""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from acme_pay.core.database import get_session
from acme_pay.domain.employment import COUNTRY_CURRENCIES, COUNTRY_NAMES
from acme_pay.insights.repository import InsightsRepository

router = APIRouter(tags=["meta"])


class Country(BaseModel):
    """A country ACME operates in."""

    code: str
    name: str
    currency: str


class Options(BaseModel):
    """Values the UI offers in dropdowns."""

    countries: list[Country]
    departments: list[str]
    job_titles: list[str]


@router.get("/meta/options")
async def options(session: Annotated[AsyncSession, Depends(get_session)]) -> Options:
    """Countries ACME operates in, and departments and job titles currently in use."""
    repository = InsightsRepository(session)
    countries = sorted(
        (
            Country(code=code, name=COUNTRY_NAMES[code], currency=currency)
            for code, currency in COUNTRY_CURRENCIES.items()
        ),
        key=lambda country: country.name,
    )
    return Options(
        countries=countries,
        departments=await repository.distinct_values("department"),
        job_titles=await repository.distinct_values("job_title"),
    )
