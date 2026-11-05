from datetime import UTC, date, datetime, timedelta

import pytest
from pydantic import ValidationError

from app.api.common import set_problem_tags
from app.core.security import create_access_token, hash_password, verify_password
from app.models.daily_activity import DailyActivity
from app.models.problem import Problem
from app.models.tag import Tag
from app.models.user import User
from app.models.user_problem_status import UserProblemStatus
from app.schemas import ProblemPatch, ProblemWrite, UserUpdate
from app.services.activity import (
    refresh_daily_activity,
    streak_counts,
    user_local_date,
    utc_bounds,
)


def test_password_hashing_and_token_creation():
    password = "another-long-password-123!"
    encoded = hash_password(password)
    assert encoded != password
    assert verify_password(password, encoded)
    assert not verify_password("wrong-password", encoded)
    assert isinstance(create_access_token(17), str)


def test_input_schema_trimming_limits_and_empty_updates():
    payload = ProblemWrite.model_validate(
        {"title": "  Add  ", "difficulty": " Easy ", "statement": "  Add numbers  ", "tags": ["Math", " Math "]}
    )
    assert payload.title == "Add"
    assert payload.difficulty == "Easy"
    assert payload.tags == ["Math"]
    with pytest.raises(ValidationError):
        ProblemPatch.model_validate({})
    with pytest.raises(ValidationError):
        ProblemPatch.model_validate({"hidden_test_cases": None})
    with pytest.raises(ValidationError):
        UserUpdate.model_validate({})
    with pytest.raises(ValidationError):
        ProblemWrite.model_validate({"title": " ", "difficulty": "Easy", "statement": "x"})


def test_set_problem_tags_reuses_case_insensitive_tags(db_session):
    existing = Tag(name="Arrays")
    problem = Problem(
        title="Tags", difficulty="Easy", statement="S", hidden_test_cases=[], is_published=False
    )
    db_session.add_all([existing, problem])
    db_session.commit()
    set_problem_tags(db_session, problem, ["Arrays", "Math"])
    db_session.commit()
    assert {tag.name for tag in problem.tags} == {"Arrays", "Math"}
    set_problem_tags(db_session, problem, [])
    assert problem.tags == []


def test_timezone_conversion_and_utc_day_bounds(make_user):
    user = make_user(timezone="Asia/Kolkata")
    instant = datetime(2026, 1, 1, 20, 0, tzinfo=UTC)
    assert user_local_date(user, instant) == date(2026, 1, 2)
    start, end = utc_bounds(date(2026, 1, 2), "Asia/Kolkata")
    assert start == datetime(2026, 1, 1, 18, 30)
    assert end - start == timedelta(days=1)


def test_refresh_activity_syncs_attempt_solved_and_plan_counts(
    db_session, make_user, make_problem
):
    from app.models.practice_attempt import PracticeAttempt
    from app.models.practice_plan import PracticePlan

    user = make_user(timezone="UTC")
    problem = make_problem()
    today = date.today()
    now = datetime.now(UTC).replace(tzinfo=None)
    plan = PracticePlan(user_id=user.user_id, plan_date=today, daily_goal=4, completed_count=0)
    db_session.add(plan)
    db_session.add(PracticeAttempt(user_id=user.user_id, problem_id=problem.problem_id, language="C++", verdict="Accepted", attempted_at=now))
    db_session.add(UserProblemStatus(user_id=user.user_id, problem_id=problem.problem_id, status="solved", first_attempt_at=now, solved_at=now))
    db_session.flush()

    activity = refresh_daily_activity(db_session, user, today)
    db_session.commit()
    assert activity.problems_attempted == 1
    assert activity.problems_solved == 1
    assert plan.completed_count == 1
    refreshed_activity = refresh_daily_activity(db_session, user, today)
    assert refreshed_activity.activity_id == activity.activity_id

    db_session.delete(db_session.query(PracticeAttempt).one())
    status = db_session.query(UserProblemStatus).one()
    status.first_attempt_at = None
    status.solved_at = None
    status.status = "attempted"
    db_session.flush()
    refreshed = refresh_daily_activity(db_session, user, today)
    db_session.commit()
    assert refreshed is None
    assert plan.completed_count == 0
    assert db_session.query(DailyActivity).count() == 0


def test_streak_counts_empty_gaps_and_current_run(db_session, make_user):
    user = make_user(timezone="UTC")
    today = date(2026, 5, 10)
    assert streak_counts(db_session, user, today) == (0, 0)
    db_session.add_all(
        [
            DailyActivity(user_id=user.user_id, local_date=date(2026, 5, 1), problems_attempted=1, problems_solved=0),
            DailyActivity(user_id=user.user_id, local_date=date(2026, 5, 2), problems_attempted=1, problems_solved=0),
            DailyActivity(user_id=user.user_id, local_date=date(2026, 5, 4), problems_attempted=2, problems_solved=1),
            DailyActivity(user_id=user.user_id, local_date=date(2026, 5, 8), problems_attempted=1, problems_solved=0),
            DailyActivity(user_id=user.user_id, local_date=date(2026, 5, 9), problems_attempted=1, problems_solved=0),
        ]
    )
    db_session.commit()
    assert streak_counts(db_session, user, today) == (2, 2)
    assert streak_counts(db_session, user, date(2026, 5, 7)) == (0, 2)

