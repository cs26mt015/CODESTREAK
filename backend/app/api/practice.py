from datetime import UTC, date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select

from app.api.common import get_published_problem
from app.api.dependencies import Database, learner_user
from app.models.daily_activity import DailyActivity
from app.models.practice_attempt import PracticeAttempt
from app.models.practice_plan import PracticePlan
from app.models.user import User
from app.models.user_problem_status import UserProblemStatus
from app.schemas import (
    AttemptCreate,
    AttemptPage,
    AttemptRead,
    PracticePlanRead,
    PracticePlanUpdate,
    ProblemStatusRead,
    ProblemStatusUpdate,
)
from app.services.activity import refresh_daily_activity, user_local_date

router = APIRouter(tags=["practice"])
CurrentUser = Annotated[User, Depends(learner_user)]


def _now_utc_naive() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def _status_read(problem_id: int, row: UserProblemStatus | None) -> ProblemStatusRead:
    if row is None:
        return ProblemStatusRead(
            problem_id=problem_id,
            status="not_started",
            first_attempt_at=None,
            solved_at=None,
            updated_at=_now_utc_naive(),
        )
    return ProblemStatusRead(
        problem_id=problem_id,
        status=row.status,
        first_attempt_at=row.first_attempt_at,
        solved_at=row.solved_at,
        updated_at=row.updated_at,
    )


@router.post("/attempts", response_model=AttemptRead, status_code=status.HTTP_201_CREATED)
def record_attempt(payload: AttemptCreate, db: Database, user: CurrentUser) -> PracticeAttempt:
    get_published_problem(db, payload.problem_id)
    now = _now_utc_naive()
    attempt = PracticeAttempt(
        user_id=user.user_id,
        problem_id=payload.problem_id,
        language=payload.language,
        verdict=payload.outcome,
        attempted_at=now,
    )
    problem_status = db.get(UserProblemStatus, (user.user_id, payload.problem_id))
    if problem_status is None:
        problem_status = UserProblemStatus(
            user_id=user.user_id,
            problem_id=payload.problem_id,
            status=payload.outcome,
            first_attempt_at=now,
            solved_at=now if payload.outcome == "solved" else None,
            updated_at=now,
        )
        db.add(problem_status)
    else:
        if problem_status.first_attempt_at is None:
            problem_status.first_attempt_at = now
        if payload.outcome == "solved" and problem_status.status != "solved":
            problem_status.status = "solved"
            problem_status.solved_at = now
        elif problem_status.status != "solved":
            problem_status.status = "attempted"
        problem_status.updated_at = now
    db.add(attempt)
    db.flush()
    refresh_daily_activity(db, user, user_local_date(user))
    db.commit()
    db.refresh(attempt)
    return attempt


@router.get("/attempts", response_model=AttemptPage)
def list_attempts(
    db: Database,
    user: CurrentUser,
    problem_id: int | None = Query(default=None, gt=0),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> AttemptPage:
    statement = select(PracticeAttempt).where(PracticeAttempt.user_id == user.user_id)
    if problem_id is not None:
        statement = statement.where(PracticeAttempt.problem_id == problem_id)
    total = db.scalar(select(func.count()).select_from(statement.subquery())) or 0
    rows = db.scalars(
        statement.order_by(PracticeAttempt.attempted_at.desc(), PracticeAttempt.attempt_id.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    return AttemptPage(items=rows, total=total, offset=offset, limit=limit)


@router.get("/problems/{problem_id}/status", response_model=ProblemStatusRead)
def get_problem_status(problem_id: int, db: Database, user: CurrentUser) -> ProblemStatusRead:
    get_published_problem(db, problem_id)
    row = db.get(UserProblemStatus, (user.user_id, problem_id))
    return _status_read(problem_id, row)


@router.put("/problems/{problem_id}/status", response_model=ProblemStatusRead)
def update_problem_status(
    problem_id: int, payload: ProblemStatusUpdate, db: Database, user: CurrentUser
) -> ProblemStatusRead:
    get_published_problem(db, problem_id)
    now = _now_utc_naive()
    row = db.get(UserProblemStatus, (user.user_id, problem_id))
    if row is None:
        row = UserProblemStatus(
            user_id=user.user_id,
            problem_id=problem_id,
            status=payload.status,
            first_attempt_at=now if payload.status in {"attempted", "solved"} else None,
            solved_at=now if payload.status == "solved" else None,
            updated_at=now,
        )
        db.add(row)
    else:
        previous_status = row.status
        row.status = payload.status
        if payload.status in {"attempted", "solved"} and row.first_attempt_at is None:
            row.first_attempt_at = now
        if payload.status == "solved":
            if previous_status != "solved" or row.solved_at is None:
                row.solved_at = now
        else:
            row.solved_at = None
        row.updated_at = now
    local_day = user_local_date(user)
    db.flush()
    refresh_daily_activity(db, user, local_day)
    db.commit()
    db.refresh(row)
    return _status_read(problem_id, row)


@router.get("/plans", response_model=list[PracticePlanRead])
def list_plans(
    db: Database,
    user: CurrentUser,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[PracticePlan]:
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=422, detail="start_date must be on or before end_date")
    statement = select(PracticePlan).where(PracticePlan.user_id == user.user_id)
    if start_date:
        statement = statement.where(PracticePlan.plan_date >= start_date)
    if end_date:
        statement = statement.where(PracticePlan.plan_date <= end_date)
    return list(db.scalars(statement.order_by(PracticePlan.plan_date)).all())


@router.put("/plans/{plan_date}", response_model=PracticePlanRead)
def upsert_plan(
    plan_date: date, payload: PracticePlanUpdate, db: Database, user: CurrentUser
) -> PracticePlan:
    row = db.scalar(
        select(PracticePlan).where(
            PracticePlan.user_id == user.user_id,
            PracticePlan.plan_date == plan_date,
        )
    )
    if row is None:
        activity = db.scalar(
            select(DailyActivity).where(
                DailyActivity.user_id == user.user_id,
                DailyActivity.local_date == plan_date,
            )
        )
        row = PracticePlan(
            user_id=user.user_id,
            plan_date=plan_date,
            daily_goal=payload.daily_goal,
            completed_count=activity.problems_solved if activity else 0,
        )
        db.add(row)
    else:
        row.daily_goal = payload.daily_goal
    db.commit()
    db.refresh(row)
    return row


@router.delete("/plans/{plan_date}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(plan_date: date, db: Database, user: CurrentUser) -> Response:
    row = db.scalar(
        select(PracticePlan).where(
            PracticePlan.user_id == user.user_id,
            PracticePlan.plan_date == plan_date,
        )
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Practice plan not found")
    db.delete(row)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
