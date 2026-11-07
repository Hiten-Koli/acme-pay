"""Compensation change persistence model."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from acme_pay.core.database import Base, string_enum
from acme_pay.domain.employment import CompensationReason


class CompensationChange(Base):
    """One salary decision. Rows are only ever inserted, never updated or deleted."""

    __tablename__ = "compensation_changes"
    __table_args__ = (
        CheckConstraint("new_salary > 0", name="ck_compensation_new_salary_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    employee_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("employees.id", ondelete="RESTRICT"), index=True
    )
    previous_salary: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    new_salary: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(String(3))
    effective_date: Mapped[date]
    reason: Mapped[CompensationReason] = mapped_column(string_enum(CompensationReason, length=30))
    changed_by: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
