"""Create the initial schema from ERD.pdf.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-10-29
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=100), nullable=False),
        sa.Column("timezone", sa.String(length=100), nullable=False),
        sa.Column("consent_status", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "problems",
        sa.Column("problem_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("difficulty", sa.String(length=100), nullable=False),
        sa.Column("statement", sa.Text(), nullable=False),
        sa.Column("constraints", sa.Text(), nullable=True),
        sa.Column("sample_input", sa.Text(), nullable=True),
        sa.Column("sample_output", sa.Text(), nullable=True),
        sa.Column("editorial_notes", sa.Text(), nullable=True),
        sa.Column("reference_solution", sa.Text(), nullable=True),
        sa.Column("is_published", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("problem_id"),
    )
    op.create_table(
        "tags",
        sa.Column("tag_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("tag_id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "ai_interaction_metadata",
        sa.Column("interaction_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("problem_id", sa.Integer(), nullable=False),
        sa.Column("feature", sa.String(length=100), nullable=False),
        sa.Column("model", sa.String(length=255), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=False),
        sa.Column("output_tokens", sa.Integer(), nullable=False),
        sa.Column("estimated_cost", sa.Float(), nullable=True),
        sa.Column("request_status", sa.String(length=100), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.problem_id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("interaction_id"),
    )
    op.create_index("ix_ai_interaction_metadata_problem_id", "ai_interaction_metadata", ["problem_id"])
    op.create_index("ix_ai_interaction_metadata_user_id", "ai_interaction_metadata", ["user_id"])
    op.create_table(
        "daily_activity",
        sa.Column("activity_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("local_date", sa.Date(), nullable=False),
        sa.Column("problems_attempted", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("problems_solved", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("activity_id"),
    )
    op.create_index("ix_daily_activity_user_id", "daily_activity", ["user_id"])
    op.create_table(
        "practice_attempts",
        sa.Column("attempt_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("problem_id", sa.Integer(), nullable=False),
        sa.Column("language", sa.String(length=100), nullable=False),
        sa.Column("verdict", sa.String(length=100), nullable=False),
        sa.Column("attempted_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("execution_time", sa.Float(), nullable=True),
        sa.Column("memory_used", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.problem_id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("attempt_id"),
    )
    op.create_index("ix_practice_attempts_problem_id", "practice_attempts", ["problem_id"])
    op.create_index("ix_practice_attempts_user_id", "practice_attempts", ["user_id"])
    op.create_table(
        "practice_plans",
        sa.Column("plan_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("plan_date", sa.Date(), nullable=False),
        sa.Column("daily_goal", sa.Integer(), nullable=False),
        sa.Column("completed_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("plan_id"),
    )
    op.create_index("ix_practice_plans_user_id", "practice_plans", ["user_id"])
    op.create_table(
        "problem_tags",
        sa.Column("problem_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.problem_id"]),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.tag_id"]),
        sa.PrimaryKeyConstraint("problem_id", "tag_id"),
    )
    op.create_index("ix_problem_tags_tag_id", "problem_tags", ["tag_id"])
    op.create_table(
        "user_problem_status",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("problem_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=100), nullable=False),
        sa.Column("first_attempt_at", sa.DateTime(), nullable=True),
        sa.Column("solved_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.problem_id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("user_id", "problem_id"),
    )
    op.create_index("ix_user_problem_status_problem_id", "user_problem_status", ["problem_id"])


def downgrade() -> None:
    op.drop_index("ix_user_problem_status_problem_id", table_name="user_problem_status")
    op.drop_table("user_problem_status")
    op.drop_index("ix_problem_tags_tag_id", table_name="problem_tags")
    op.drop_table("problem_tags")
    op.drop_index("ix_practice_plans_user_id", table_name="practice_plans")
    op.drop_table("practice_plans")
    op.drop_index("ix_practice_attempts_user_id", table_name="practice_attempts")
    op.drop_index("ix_practice_attempts_problem_id", table_name="practice_attempts")
    op.drop_table("practice_attempts")
    op.drop_index("ix_daily_activity_user_id", table_name="daily_activity")
    op.drop_table("daily_activity")
    op.drop_index("ix_ai_interaction_metadata_user_id", table_name="ai_interaction_metadata")
    op.drop_index("ix_ai_interaction_metadata_problem_id", table_name="ai_interaction_metadata")
    op.drop_table("ai_interaction_metadata")
    op.drop_table("tags")
    op.drop_table("problems")
    op.drop_table("users")
