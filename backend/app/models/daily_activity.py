from datetime import date

from sqlalchemy import Date, ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DailyActivity(Base):
    __tablename__ = "daily_activity"
    __table_args__ = (
        UniqueConstraint("user_id", "local_date", name="uq_daily_activity_user_local_date"),
        Index("ix_daily_activity_user_id", "user_id"),
    )

    activity_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    local_date: Mapped[date] = mapped_column(Date, nullable=False)
    problems_attempted: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    problems_solved: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    user: Mapped["User"] = relationship(back_populates="daily_activities")
