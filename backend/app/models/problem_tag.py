from sqlalchemy import ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProblemTag(Base):
    __tablename__ = "problem_tags"
    __table_args__ = (Index("ix_problem_tags_tag_id", "tag_id"),)

    problem_id: Mapped[int] = mapped_column(
        ForeignKey("problems.problem_id"), primary_key=True, nullable=False
    )
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.tag_id"), primary_key=True, nullable=False)
