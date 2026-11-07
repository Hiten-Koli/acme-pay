"""Compensation history queries."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from acme_pay.compensation.models import CompensationChange


class CompensationRepository:
    """Reads an employee's salary history."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def history(self, employee_id: UUID) -> list[CompensationChange]:
        """Return all changes for an employee, newest first."""
        rows = await self._session.scalars(
            select(CompensationChange)
            .where(CompensationChange.employee_id == employee_id)
            .order_by(
                CompensationChange.effective_date.desc(), CompensationChange.created_at.desc()
            )
        )
        return list(rows)
