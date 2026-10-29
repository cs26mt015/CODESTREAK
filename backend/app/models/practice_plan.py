from datetime import date

from sqlalchemy import Date, ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PracticePlan(Base):
    __tablename__ = "practice_plans"
    __table_args__ = (
        UniqueConstraint("user_id", "plan_date", name="uq_practice_plans_user_plan_date"),
        Index("ix_practice_plans_user_id", "user_id"),
    )

    plan_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    plan_date: Mapped[date] = mapped_column(Date, nullable=False)
    daily_goal: Mapped[int] = mapped_column(Integer, nullable=False)
    completed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    user: Mapped["User"] = relationship(back_populates="practice_plans")
