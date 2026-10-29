from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.daily_activity import DailyActivity
from app.models.practice_attempt import PracticeAttempt
from app.models.practice_plan import PracticePlan
from app.models.user import User
from app.models.user_problem_status import UserProblemStatus


def user_local_date(user: User, now: datetime | None = None) -> date:
    current = now or datetime.now(UTC)
    return current.astimezone(ZoneInfo(user.timezone)).date()


def utc_bounds(local_day: date, timezone: str) -> tuple[datetime, datetime]:
    zone = ZoneInfo(timezone)
    start_local = datetime.combine(local_day, time.min, tzinfo=zone)
    end_local = datetime.combine(local_day + timedelta(days=1), time.min, tzinfo=zone)
    return (
        start_local.astimezone(UTC).replace(tzinfo=None),
        end_local.astimezone(UTC).replace(tzinfo=None),
    )


def refresh_daily_activity(db: Session, user: User, local_day: date) -> DailyActivity | None:
    start_utc, end_utc = utc_bounds(local_day, user.timezone)
    attempt_problem_ids = set(
        db.scalars(
            select(PracticeAttempt.problem_id)
            .where(
                PracticeAttempt.user_id == user.user_id,
                PracticeAttempt.attempted_at >= start_utc,
                PracticeAttempt.attempted_at < end_utc,
            )
            .distinct()
        ).all()
    )
    status_problem_ids = set(
        db.scalars(
            select(UserProblemStatus.problem_id)
            .where(
                UserProblemStatus.user_id == user.user_id,
                UserProblemStatus.first_attempt_at >= start_utc,
                UserProblemStatus.first_attempt_at < end_utc,
            )
            .distinct()
        ).all()
    )
    solved_count = db.scalar(
        select(func.count())
        .select_from(UserProblemStatus)
        .where(
            UserProblemStatus.user_id == user.user_id,
            UserProblemStatus.status == "solved",
            UserProblemStatus.solved_at >= start_utc,
            UserProblemStatus.solved_at < end_utc,
        )
    ) or 0
    attempted_count = len(attempt_problem_ids | status_problem_ids)
    attempted_count = max(attempted_count, solved_count)

    activity = db.scalar(
        select(DailyActivity).where(
            DailyActivity.user_id == user.user_id,
            DailyActivity.local_date == local_day,
        )
    )
    if attempted_count == 0 and solved_count == 0:
        if activity is not None:
            db.delete(activity)
        plan = db.scalar(
            select(PracticePlan).where(
                PracticePlan.user_id == user.user_id,
                PracticePlan.plan_date == local_day,
            )
        )
        if plan is not None:
            plan.completed_count = 0
        return None

    if activity is None:
        activity = DailyActivity(user_id=user.user_id, local_date=local_day)
        db.add(activity)
    activity.problems_attempted = attempted_count
    activity.problems_solved = solved_count
    plan = db.scalar(
        select(PracticePlan).where(
            PracticePlan.user_id == user.user_id,
            PracticePlan.plan_date == local_day,
        )
    )
    if plan is not None:
        plan.completed_count = solved_count
    return activity


def streak_counts(db: Session, user: User, today: date | None = None) -> tuple[int, int]:
    today = today or user_local_date(user)
    activity_dates = set(
        db.scalars(
            select(DailyActivity.local_date).where(
                DailyActivity.user_id == user.user_id,
                DailyActivity.local_date <= today,
                (DailyActivity.problems_attempted > 0) | (DailyActivity.problems_solved > 0),
            )
        ).all()
    )
    if not activity_dates:
        return 0, 0

    longest = current_run = 0
    previous: date | None = None
    for day in sorted(activity_dates):
        current_run = current_run + 1 if previous == day - timedelta(days=1) else 1
        longest = max(longest, current_run)
        previous = day

    end_day = today if today in activity_dates else today - timedelta(days=1)
    if end_day not in activity_dates:
        return 0, longest
    current = 0
    while end_day in activity_dates:
        current += 1
        end_day -= timedelta(days=1)
    return current, longest
