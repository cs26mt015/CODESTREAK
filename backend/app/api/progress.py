from datetime import date, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import case, func, select

from app.api.common import problem_statement
from app.api.dependencies import Database, learner_user
from app.models.daily_activity import DailyActivity
from app.models.practice_plan import PracticePlan
from app.models.problem import Problem
from app.models.problem_tag import ProblemTag
from app.models.tag import Tag
from app.models.user import User
from app.models.user_problem_status import UserProblemStatus
from app.schemas import (
    DailyActivityRead,
    ProgressSummary,
    ProblemPublic,
    Recommendation,
    StreakSummary,
)
from app.services.activity import streak_counts, user_local_date

router = APIRouter(tags=["progress"])
recommendation_router = APIRouter(tags=["recommendations"])
CurrentUser = Annotated[User, Depends(learner_user)]


@router.get("/progress/activity", response_model=list[DailyActivityRead])
def get_activity(
    db: Database,
    user: CurrentUser,
    start_date: date,
    end_date: date,
) -> list[DailyActivity]:
    if start_date > end_date:
        raise HTTPException(status_code=422, detail="start_date must be on or before end_date")
    if end_date - start_date > timedelta(days=366):
        raise HTTPException(status_code=422, detail="Date range cannot exceed 367 days")
    return list(
        db.scalars(
            select(DailyActivity)
            .where(
                DailyActivity.user_id == user.user_id,
                DailyActivity.local_date >= start_date,
                DailyActivity.local_date <= end_date,
            )
            .order_by(DailyActivity.local_date)
        ).all()
    )


@router.get("/progress/streaks", response_model=StreakSummary)
def get_streaks(db: Database, user: CurrentUser) -> StreakSummary:
    current, longest = streak_counts(db, user)
    return StreakSummary(current_streak=current, longest_streak=longest, timezone=user.timezone)


@router.get("/progress/summary", response_model=ProgressSummary)
def get_progress_summary(db: Database, user: CurrentUser) -> ProgressSummary:
    today = user_local_date(user)
    solved_filter = (
        UserProblemStatus.user_id == user.user_id,
        UserProblemStatus.status == "solved",
    )
    total_solved = db.scalar(
        select(func.count()).select_from(UserProblemStatus).where(*solved_filter)
    ) or 0
    current, longest = streak_counts(db, user, today)
    plan = db.scalar(
        select(PracticePlan).where(
            PracticePlan.user_id == user.user_id,
            PracticePlan.plan_date == today,
        )
    )
    activity = db.scalar(
        select(DailyActivity).where(
            DailyActivity.user_id == user.user_id,
            DailyActivity.local_date == today,
        )
    )
    topic_rows = db.execute(
        select(Tag.name, func.count(func.distinct(UserProblemStatus.problem_id)))
        .join(ProblemTag, ProblemTag.tag_id == Tag.tag_id)
        .join(Problem, Problem.problem_id == ProblemTag.problem_id)
        .join(UserProblemStatus, UserProblemStatus.problem_id == Problem.problem_id)
        .where(*solved_filter)
        .group_by(Tag.name)
        .order_by(Tag.name)
    ).all()
    difficulty_rows = db.execute(
        select(Problem.difficulty, func.count(func.distinct(UserProblemStatus.problem_id)))
        .join(UserProblemStatus, UserProblemStatus.problem_id == Problem.problem_id)
        .where(*solved_filter)
        .group_by(Problem.difficulty)
        .order_by(Problem.difficulty)
    ).all()
    return ProgressSummary(
        total_solved=total_solved,
        current_streak=current,
        longest_streak=longest,
        daily_goal=plan.daily_goal if plan else 0,
        completed_today=activity.problems_solved if activity else 0,
        by_topic=[{"name": name, "solved": count} for name, count in topic_rows],
        by_difficulty=[{"name": name, "solved": count} for name, count in difficulty_rows],
    )


@recommendation_router.get("/recommendations/next", response_model=Recommendation)
def get_recommendation(db: Database, user: CurrentUser) -> Recommendation:
    solved_problem_ids = select(UserProblemStatus.problem_id).where(
        UserProblemStatus.user_id == user.user_id,
        UserProblemStatus.status == "solved",
    )
    difficulty_rank = case(
        (Problem.difficulty.ilike("easy"), 0),
        (Problem.difficulty.ilike("medium"), 1),
        (Problem.difficulty.ilike("hard"), 2),
        else_=3,
    )
    base = problem_statement().where(
        Problem.is_published.is_(True),
        Problem.problem_id.not_in(solved_problem_ids),
    )
    weakest_tag_id = db.scalar(
        select(Tag.tag_id)
        .join(ProblemTag, ProblemTag.tag_id == Tag.tag_id)
        .join(UserProblemStatus, UserProblemStatus.problem_id == ProblemTag.problem_id)
        .where(*(
            UserProblemStatus.user_id == user.user_id,
            UserProblemStatus.status == "solved",
        ))
        .group_by(Tag.tag_id, Tag.name)
        .order_by(func.count(func.distinct(ProblemTag.problem_id)), Tag.name)
        .limit(1)
    )
    problem = None
    if weakest_tag_id is not None:
        problem = db.scalar(
            base.where(Problem.tags.any(Tag.tag_id == weakest_tag_id))
            .order_by(difficulty_rank, Problem.problem_id)
            .limit(1)
        )
    if problem is None:
        problem = db.scalar(base.order_by(difficulty_rank, Problem.problem_id).limit(1))
    if problem is None:
        return Recommendation(problem=None, message="No unsolved published problems are available right now.")
    return Recommendation(problem=ProblemPublic.model_validate(problem), message="Recommended next problem")
