from datetime import UTC, datetime
from typing import Annotated
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import Database, current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.models.ai_interaction_metadata import AIInteractionMetadata
from app.models.daily_activity import DailyActivity
from app.models.practice_attempt import PracticeAttempt
from app.models.practice_plan import PracticePlan
from app.models.user import User
from app.models.user_problem_status import UserProblemStatus
from app.schemas import AuthResponse, LoginRequest, RegisterRequest, UserRead, UserUpdate

router = APIRouter(prefix="/auth", tags=["authentication"])
CurrentUser = Annotated[User, Depends(current_user)]


def _validate_timezone(timezone: str) -> None:
    try:
        ZoneInfo(timezone)
    except ZoneInfoNotFoundError:
        raise HTTPException(status_code=422, detail="Unknown IANA timezone")


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Database) -> AuthResponse:
    _validate_timezone(payload.timezone)
    email = str(payload.email).lower()
    if db.scalar(select(User.user_id).where(User.email == email)) is not None:
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    user = User(
        name=payload.name.strip(),
        email=email,
        password_hash=hash_password(payload.password),
        role="learner",
        timezone=payload.timezone,
        consent_status="accepted",
        created_at=datetime.now(UTC).replace(tzinfo=None),
        updated_at=datetime.now(UTC).replace(tzinfo=None),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    db.refresh(user)
    return AuthResponse(access_token=create_access_token(user.user_id), user=user)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Database) -> AuthResponse:
    email = str(payload.email).lower()
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return AuthResponse(access_token=create_access_token(user.user_id), user=user)


@router.get("/me", response_model=UserRead)
def get_me(user: CurrentUser) -> User:
    return user


@router.patch("/me", response_model=UserRead)
def update_me(payload: UserUpdate, user: CurrentUser, db: Database) -> User:
    changes = payload.model_dump(exclude_unset=True)
    if "timezone" in changes and changes["timezone"] is not None:
        _validate_timezone(changes["timezone"])
    if "email" in changes and changes["email"] is not None:
        changes["email"] = str(changes["email"]).lower()
        existing = db.scalar(
            select(User.user_id).where(User.email == changes["email"], User.user_id != user.user_id)
        )
        if existing is not None:
            raise HTTPException(status_code=409, detail="An account with this email already exists")
    if "name" in changes and changes["name"] is not None:
        changes["name"] = changes["name"].strip()
    for field, value in changes.items():
        setattr(user, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Profile update conflicts with existing data")
    db.refresh(user)
    return user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(user: CurrentUser, db: Session) -> Response:
    for model in (
        AIInteractionMetadata,
        UserProblemStatus,
        PracticeAttempt,
        DailyActivity,
        PracticePlan,
    ):
        db.execute(delete(model).where(model.user_id == user.user_id))
    db.delete(user)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
