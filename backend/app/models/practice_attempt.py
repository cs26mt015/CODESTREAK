from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PracticeAttempt(Base):
    __tablename__ = "practice_attempts"
    __table_args__ = (
        Index("ix_practice_attempts_user_id", "user_id"),
        Index("ix_practice_attempts_problem_id", "problem_id"),
    )

    attempt_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.problem_id"), nullable=False)
    language: Mapped[str] = mapped_column(String(100), nullable=False)
    verdict: Mapped[str] = mapped_column(String(100), nullable=False)
    attempted_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    execution_time: Mapped[float | None] = mapped_column(Float, nullable=True)
    memory_used: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user: Mapped["User"] = relationship(back_populates="practice_attempts")
    problem: Mapped["Problem"] = relationship(back_populates="practice_attempts")
