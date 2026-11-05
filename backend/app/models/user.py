from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.ai_interaction_metadata import AIInteractionMetadata
    from app.models.daily_activity import DailyActivity
    from app.models.practice_attempt import PracticeAttempt
    from app.models.practice_plan import PracticePlan
    from app.models.user_problem_status import UserProblemStatus


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(100), nullable=False)
    timezone: Mapped[str] = mapped_column(String(100), nullable=False)
    consent_status: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    daily_activities: Mapped[list["DailyActivity"]] = relationship(back_populates="user")
    practice_plans: Mapped[list["PracticePlan"]] = relationship(back_populates="user")
    problem_statuses: Mapped[list["UserProblemStatus"]] = relationship(back_populates="user")
    practice_attempts: Mapped[list["PracticeAttempt"]] = relationship(back_populates="user")
    ai_interactions: Mapped[list["AIInteractionMetadata"]] = relationship(back_populates="user")
