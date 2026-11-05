from contextlib import contextmanager
from types import SimpleNamespace

import pytest

from app.models import Problem, User
from app.seed import STARTER_PROBLEMS, _ensure_problem, _ensure_user, seed_demo_data
from app.seed_catalog import ADDITIONAL_PROBLEMS


def test_catalog_contains_at_least_fifty_unique_complete_problems():
    problems = (*STARTER_PROBLEMS, *ADDITIONAL_PROBLEMS)
    assert len(problems) >= 50
    assert len({problem["title"] for problem in problems}) == len(problems)
    assert all(problem["hidden_test_cases"] and problem["tags"] for problem in problems)
    assert all(problem["sample_input"] is not None and problem["sample_output"] is not None for problem in problems)


def test_seed_demo_data_is_idempotent_and_can_be_disabled(
    db_session, monkeypatch, capsys
):
    from app import seed

    @contextmanager
    def transaction():
        try:
            yield db_session
            db_session.commit()
        except Exception:
            db_session.rollback()
            raise

    monkeypatch.setattr(seed, "SessionLocal", SimpleNamespace(begin=transaction))
    monkeypatch.setattr(seed.settings, "app_env", "development")
    monkeypatch.setenv("SEED_DEMO_DATA", "true")
    monkeypatch.setenv("SEED_LEARNER_EMAIL", "learner@example.com")
    monkeypatch.setenv("SEED_ADMIN_EMAIL", "admin@example.com")

    seed_demo_data()
    seed_demo_data()
    assert db_session.query(User).count() == 2
    assert db_session.query(Problem).count() == 50
    assert "ready" in capsys.readouterr().out

    monkeypatch.setenv("SEED_DEMO_DATA", "false")
    seed_demo_data()
    assert db_session.query(Problem).count() == 50
    assert "disabled" in capsys.readouterr().out


def test_seed_user_rejects_role_conflict_and_migrates_legacy_email(db_session):
    _ensure_user(
        db_session,
        name="Old Demo Learner",
        email="learner@codestreak.local",
        password="A-long-test-password-123!",
        role="learner",
    )
    db_session.commit()
    _ensure_user(
        db_session,
        name="Demo Learner",
        email="learner@example.com",
        password="A-long-test-password-123!",
        role="learner",
    )
    db_session.commit()
    assert db_session.query(User).one().email == "learner@example.com"
    with pytest.raises(ValueError, match="already exists with role"):
        _ensure_user(
            db_session,
            name="Different Role",
            email="learner@example.com",
            password="A-long-test-password-123!",
            role="admin",
        )


def test_seed_problem_only_inserts_missing_problems(db_session):
    problem_data = STARTER_PROBLEMS[0]
    _ensure_problem(db_session, problem_data)
    _ensure_problem(db_session, problem_data)
    db_session.commit()
    assert db_session.query(Problem).count() == 1
