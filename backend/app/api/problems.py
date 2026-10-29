from typing import Annotated
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from app.api.common import get_admin_problem, get_published_problem, problem_statement, set_problem_tags
from app.api.dependencies import Database, admin_user, optional_current_user
from app.models.ai_interaction_metadata import AIInteractionMetadata
from app.models.practice_attempt import PracticeAttempt
from app.models.problem import Problem
from app.models.tag import Tag
from app.models.user import User
from app.models.user_problem_status import UserProblemStatus
from app.schemas import (
    AdminProblemPage,
    ProblemAdmin,
    ProblemPage,
    ProblemPatch,
    ProblemPublic,
    ProblemWrite,
    PublicationUpdate,
    TagRead,
)

router = APIRouter(tags=["problems"])
admin_router = APIRouter(prefix="/admin/problems", tags=["administration"])
OptionalUser = Annotated[User | None, Depends(optional_current_user)]
AdminUser = Annotated[User, Depends(admin_user)]


@router.get("/problems", response_model=ProblemPage)
def list_problems(
    db: Database,
    user: OptionalUser,
    q: str | None = Query(default=None, max_length=200),
    difficulty: str | None = None,
    tag: str | None = None,
    status_filter: Annotated[
        Literal["not_started", "attempted", "solved"] | None,
        Query(alias="status"),
    ] = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> ProblemPage:
    statement = problem_statement().where(Problem.is_published.is_(True))
    if q:
        statement = statement.where(or_(Problem.title.ilike(f"%{q}%"), Problem.statement.ilike(f"%{q}%")))
    if difficulty:
        statement = statement.where(Problem.difficulty == difficulty)
    if tag:
        statement = statement.where(Problem.tags.any(Tag.name == tag))
    if status_filter:
        if user is None:
            raise HTTPException(status_code=401, detail="Authentication required to filter by status")
        if user.role != "learner":
            raise HTTPException(status_code=403, detail="Learner access required for status filtering")
        statement = statement.where(
            Problem.problem_id.in_(
                select(UserProblemStatus.problem_id).where(
                    UserProblemStatus.user_id == user.user_id,
                    UserProblemStatus.status == status_filter,
                )
            )
        )
    total = db.scalar(select(func.count()).select_from(statement.order_by(None).subquery())) or 0
    items = db.scalars(statement.order_by(Problem.problem_id).offset(offset).limit(limit)).all()
    return ProblemPage(items=items, total=total, offset=offset, limit=limit)


@router.get("/problems/{problem_id}", response_model=ProblemPublic)
def get_problem(problem_id: int, db: Database) -> Problem:
    return get_published_problem(db, problem_id)


@router.get("/tags", response_model=list[TagRead])
def list_tags(db: Database) -> list[Tag]:
    return list(db.scalars(select(Tag).order_by(Tag.name)).all())


@admin_router.get("", response_model=AdminProblemPage)
def list_admin_problems(
    db: Database,
    _admin: AdminUser,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> AdminProblemPage:
    statement = problem_statement()
    total = db.scalar(select(func.count()).select_from(Problem)) or 0
    items = db.scalars(statement.order_by(Problem.problem_id).offset(offset).limit(limit)).all()
    return AdminProblemPage(items=items, total=total, offset=offset, limit=limit)


@admin_router.post("", response_model=ProblemAdmin, status_code=status.HTTP_201_CREATED)
def create_problem(payload: ProblemWrite, db: Database, _admin: AdminUser) -> Problem:
    values = payload.model_dump(exclude={"tags"})
    problem = Problem(**values, is_published=False)
    set_problem_tags(db, problem, payload.tags)
    db.add(problem)
    db.commit()
    return get_admin_problem(db, problem.problem_id)


@admin_router.get("/{problem_id}", response_model=ProblemAdmin)
def get_admin_problem_route(problem_id: int, db: Database, _admin: AdminUser) -> Problem:
    return get_admin_problem(db, problem_id)


@admin_router.patch("/{problem_id}", response_model=ProblemAdmin)
def update_problem(
    problem_id: int, payload: ProblemPatch, db: Database, _admin: AdminUser
) -> Problem:
    problem = get_admin_problem(db, problem_id)
    changes = payload.model_dump(exclude_unset=True)
    if "tags" in changes:
        set_problem_tags(db, problem, changes.pop("tags") or [])
    for field, value in changes.items():
        setattr(problem, field, value)
    db.commit()
    return get_admin_problem(db, problem_id)


@admin_router.delete("/{problem_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_problem(problem_id: int, db: Database, _admin: AdminUser) -> Response:
    problem = get_admin_problem(db, problem_id)
    has_practice_history = db.scalar(
        select(PracticeAttempt.attempt_id)
        .where(PracticeAttempt.problem_id == problem_id)
        .limit(1)
    ) is not None
    has_status_history = db.scalar(
        select(UserProblemStatus.user_id)
        .where(UserProblemStatus.problem_id == problem_id)
        .limit(1)
    ) is not None
    if has_practice_history or has_status_history:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Problem has learner history; unpublish it instead of deleting it",
        )
    db.query(AIInteractionMetadata).filter(AIInteractionMetadata.problem_id == problem_id).delete(
        synchronize_session=False
    )
    db.delete(problem)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@admin_router.put("/{problem_id}/publication", response_model=ProblemAdmin)
def set_publication(
    problem_id: int, payload: PublicationUpdate, db: Database, _admin: AdminUser
) -> Problem:
    problem = get_admin_problem(db, problem_id)
    problem.is_published = payload.is_published
    db.commit()
    return get_admin_problem(db, problem_id)
