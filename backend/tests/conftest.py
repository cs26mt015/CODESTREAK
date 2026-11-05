from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Problem, Tag, User


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine, expire_on_commit=False) as session:
        yield session
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def client(db_session):
    def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def make_user(db_session):
    def factory(role="learner", email=None, name=None, timezone="UTC"):
        number = db_session.query(User).count() + 1
        user = User(
            name=name or f"Test User {number}",
            email=email or f"user{number}@example.com",
            password_hash=hash_password("A-long-test-password-123!"),
            role=role,
            timezone=timezone,
            consent_status="accepted",
            created_at=datetime.now(UTC).replace(tzinfo=None),
            updated_at=datetime.now(UTC).replace(tzinfo=None),
        )
        db_session.add(user)
        db_session.commit()
        return user

    return factory


@pytest.fixture
def make_problem(db_session):
    def factory(title="Sample Problem", published=True, tags=None, hidden_test_cases=None):
        problem = Problem(
            title=title,
            difficulty="Easy",
            statement="Read input and print the expected output.",
            constraints="1 <= n <= 10",
            sample_input="1",
            sample_output="1",
            editorial_notes="Use a direct approach.",
            reference_solution="int main() {}",
            hidden_test_cases=hidden_test_cases or [{"input": "1", "output": "1"}],
            is_published=published,
        )
        for tag_name in tags or []:
            tag = db_session.query(Tag).filter_by(name=tag_name).one_or_none()
            if tag is None:
                tag = Tag(name=tag_name)
            problem.tags.append(tag)
        db_session.add(problem)
        db_session.commit()
        return problem

    return factory


@pytest.fixture
def auth_headers():
    def factory(user):
        return {"Authorization": f"Bearer {create_access_token(user.user_id)}"}

    return factory
