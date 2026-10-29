"""Enforce one daily activity and plan per user and date.

Revision ID: 0002_unique_user_dates
Revises: 0001_initial_schema
Create Date: 2026-10-29
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_unique_user_dates"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    daily_uniques = inspector.get_unique_constraints("daily_activity")
    plan_uniques = inspector.get_unique_constraints("practice_plans")
    if not any(item.get("column_names") == ["user_id", "local_date"] for item in daily_uniques):
        op.create_unique_constraint(
            "uq_daily_activity_user_local_date", "daily_activity", ["user_id", "local_date"]
        )
    if not any(item.get("column_names") == ["user_id", "plan_date"] for item in plan_uniques):
        op.create_unique_constraint(
            "uq_practice_plans_user_plan_date", "practice_plans", ["user_id", "plan_date"]
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    for table_name, columns in (
        ("practice_plans", ["user_id", "plan_date"]),
        ("daily_activity", ["user_id", "local_date"]),
    ):
        constraint = next(
            (
                item
                for item in inspector.get_unique_constraints(table_name)
                if item.get("column_names") == columns
            ),
            None,
        )
        if constraint and constraint.get("name"):
            op.drop_constraint(constraint["name"], table_name, type_="unique")
