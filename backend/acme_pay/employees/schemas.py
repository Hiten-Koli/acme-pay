"""Request and response shapes for the employees API."""

from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from acme_pay.domain.employment import EmploymentStatus

MAX_PAGE_SIZE = 100

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Email = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, to_lower=True, max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    ),
]
CountryCode = Annotated[str, StringConstraints(to_upper=True, pattern=r"^[A-Z]{2}$")]
# Annual base salary: positive, at most 12 integer digits and exactly cents.
Salary = Annotated[Decimal, Field(gt=0, max_digits=14, decimal_places=2)]


class EmployeeCreate(BaseModel):
    """A new hire. The currency follows from the country."""

    model_config = ConfigDict(extra="forbid")

    first_name: Text
    last_name: Text
    email: Email
    job_title: Text
    department: Text
    country_code: CountryCode
    salary: Salary
    hire_date: date


class EmployeeUpdate(BaseModel):
    """Profile changes. Salary is excluded: it only changes through compensation history."""

    model_config = ConfigDict(extra="forbid")

    first_name: Text | None = None
    last_name: Text | None = None
    email: Email | None = None
    job_title: Text | None = None
    department: Text | None = None


class TerminationRequest(BaseModel):
    """When the employee leaves."""

    model_config = ConfigDict(extra="forbid")

    terminated_on: date


class EmployeeRead(BaseModel):
    """An employee as returned by the API. ``salary`` is a decimal string in ``currency``."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    employee_code: str
    first_name: str
    last_name: str
    email: str
    job_title: str
    department: str
    country_code: str
    currency: str
    salary: Decimal
    hire_date: date
    status: EmploymentStatus
    terminated_on: date | None


class EmployeeSort(StrEnum):
    """Supported orderings; a leading ``-`` means descending."""

    NAME = "name"
    NAME_DESC = "-name"
    SALARY = "salary"
    SALARY_DESC = "-salary"
    HIRE_DATE = "hire_date"
    HIRE_DATE_DESC = "-hire_date"


class EmployeeFilters(BaseModel):
    """Query parameters for listing employees."""

    search: str | None = None
    country: CountryCode | None = None
    department: str | None = None
    job_title: str | None = None
    status: EmploymentStatus = EmploymentStatus.ACTIVE
    sort: EmployeeSort = EmployeeSort.NAME
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=25, ge=1, le=MAX_PAGE_SIZE)


class EmployeePage(BaseModel):
    """One page of employees plus the total matching the filters."""

    items: list[EmployeeRead]
    total: int
    page: int
    page_size: int
