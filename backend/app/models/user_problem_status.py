from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserProblemStatus(Base):
    __tablename__ = "user_problem_status"
    __table_args__ = (Index("ix_user_problem_status_problem_id", "problem_id"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.problem_id"), primary_key=True)
    status: Mapped[str] = mapped_column(String(100), nullable=False)
    first_attempt_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    solved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="problem_statuses")
    problem: Mapped["Problem"] = relationship(back_populates="statuses")
