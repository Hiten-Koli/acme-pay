"""Dated FX rates to the USD reporting currency.

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "fx_rates",
        sa.Column("currency", sa.String(3), primary_key=True),
        sa.Column("effective_date", sa.Date(), primary_key=True),
        sa.Column("rate_to_usd", sa.Numeric(18, 8), nullable=False),
        sa.CheckConstraint("rate_to_usd > 0", name="ck_fx_rates_positive"),
    )


def downgrade() -> None:
    op.drop_table("fx_rates")
