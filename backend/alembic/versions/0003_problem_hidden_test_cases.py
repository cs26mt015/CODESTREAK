"""Store private judge test cases on problems.

Revision ID: 0003_problem_hidden_test_cases
Revises: 0002_unique_user_dates
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003_problem_hidden_test_cases"
down_revision: Union[str, None] = "0002_unique_user_dates"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "problems",
        sa.Column("hidden_test_cases", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.alter_column("problems", "hidden_test_cases", server_default=None)


def downgrade() -> None:
    op.drop_column("problems", "hidden_test_cases")
