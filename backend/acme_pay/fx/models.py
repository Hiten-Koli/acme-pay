"""FX rate persistence model."""

from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from acme_pay.core.database import Base


class FxRateRecord(Base):
    """USD value of one unit of ``currency`` from ``effective_date`` onwards."""

    __tablename__ = "fx_rates"
    __table_args__ = (CheckConstraint("rate_to_usd > 0", name="ck_fx_rates_positive"),)

    currency: Mapped[str] = mapped_column(String(3), primary_key=True)
    effective_date: Mapped[date] = mapped_column(primary_key=True)
    rate_to_usd: Mapped[Decimal] = mapped_column(Numeric(18, 8))
