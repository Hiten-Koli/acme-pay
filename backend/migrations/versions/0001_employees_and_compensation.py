"""Employees and their append-only compensation history.

Revision ID: 0001
Revises:
Create Date: 2026-11-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SEQUENCE employee_code_seq")
    op.create_table(
        "employees",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "employee_code",
            sa.String(16),
            nullable=False,
            server_default=sa.text("'EMP-' || lpad(nextval('employee_code_seq')::text, 6, '0')"),
        ),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("job_title", sa.String(100), nullable=False),
        sa.Column("department", sa.String(100), nullable=False),
        sa.Column("country_code", sa.String(2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("salary", sa.Numeric(14, 2), nullable=False),
        sa.Column("hire_date", sa.Date(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("active", "terminated", name="employmentstatus", native_enum=False, length=20),
            nullable=False,
        ),
        sa.Column("terminated_on", sa.Date(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint("salary > 0", name="ck_employees_salary_positive"),
        sa.UniqueConstraint("employee_code"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_employees_country_job_title", "employees", ["country_code", "job_title"])
    op.create_index("ix_employees_department", "employees", ["department"])
    op.create_index("ix_employees_status", "employees", ["status"])

    op.create_table(
        "compensation_changes",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "employee_id",
            sa.Uuid(),
            sa.ForeignKey("employees.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("previous_salary", sa.Numeric(14, 2), nullable=True),
        sa.Column("new_salary", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column(
            "reason",
            sa.Enum(
                "hire",
                "merit",
                "promotion",
                "market_adjustment",
                "correction",
                name="compensationreason",
                native_enum=False,
                length=30,
            ),
            nullable=False,
        ),
        sa.Column("changed_by", sa.String(100), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint("new_salary > 0", name="ck_compensation_new_salary_positive"),
    )
    op.create_index("ix_compensation_changes_employee_id", "compensation_changes", ["employee_id"])


def downgrade() -> None:
    op.drop_table("compensation_changes")
    op.drop_table("employees")
    op.execute("DROP SEQUENCE employee_code_seq")
