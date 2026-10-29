from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AIInteractionMetadata(Base):
    __tablename__ = "ai_interaction_metadata"
    __table_args__ = (
        Index("ix_ai_interaction_metadata_user_id", "user_id"),
        Index("ix_ai_interaction_metadata_problem_id", "problem_id"),
    )

    interaction_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.problem_id"), nullable=False)
    feature: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(255), nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    request_status: Mapped[str] = mapped_column(String(100), nullable=False)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="ai_interactions")
    problem: Mapped["Problem"] = relationship(back_populates="ai_interactions")
