from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.problem import Problem
from app.models.tag import Tag


def problem_statement():
    return select(Problem).options(selectinload(Problem.tags))


def get_published_problem(db: Session, problem_id: int) -> Problem:
    problem = db.scalar(
        problem_statement().where(Problem.problem_id == problem_id, Problem.is_published.is_(True))
    )
    if problem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    return problem


def get_admin_problem(db: Session, problem_id: int) -> Problem:
    problem = db.scalar(problem_statement().where(Problem.problem_id == problem_id))
    if problem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    return problem


def set_problem_tags(db: Session, problem: Problem, names: list[str]) -> None:
    tags_by_name = {
        tag.name.casefold(): tag
        for tag in db.scalars(select(Tag).where(Tag.name.in_(names))).all()
    } if names else {}
    for name in names:
        if name.casefold() not in tags_by_name:
            tag = Tag(name=name)
            db.add(tag)
            tags_by_name[name.casefold()] = tag
    problem.tags = [tags_by_name[name.casefold()] for name in names]
