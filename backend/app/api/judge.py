from datetime import UTC, datetime
from functools import lru_cache
from typing import Annotated, Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from app.api.common import get_published_problem
from app.api.dependencies import Database, learner_user
from app.core.config import settings
from app.models.practice_attempt import PracticeAttempt
from app.models.user import User
from app.models.user_problem_status import UserProblemStatus
from app.services.activity import refresh_daily_activity, user_local_date

router = APIRouter(tags=["code execution"])
Learner = Annotated[User, Depends(learner_user)]


class CodeRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    language_id: int = Field(gt=0)
    source_code: str = Field(min_length=1, max_length=64000)
    stdin: str = Field(default="", max_length=64000)


def _judge0_headers() -> dict[str, str]:
    return {"X-Auth-Token": settings.judge0_auth_token}


def _judge0_get(path: str) -> Any:
    try:
        response = httpx.get(
            f"{settings.judge0_api_url.rstrip('/')}{path}",
            headers=_judge0_headers(),
            timeout=settings.judge0_timeout_seconds,
        )
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(status_code=503, detail="Code execution service is unavailable") from exc


@lru_cache(maxsize=1)
def _supported_languages() -> tuple[dict[str, Any], ...]:
    return tuple(_judge0_get("/languages"))


def _require_supported_language(language_id: int) -> None:
    if not any(int(language.get("id", -1)) == language_id for language in _supported_languages()):
        raise HTTPException(status_code=422, detail="Unsupported Judge0 language_id")


def _execute(source_code: str, language_id: int, stdin: str) -> dict[str, Any]:
    try:
        response = httpx.post(
            f"{settings.judge0_api_url.rstrip('/')}/submissions",
            params={"base64_encoded": "false", "wait": "true"},
            headers=_judge0_headers(),
            json={"source_code": source_code, "language_id": language_id, "stdin": stdin},
            timeout=settings.judge0_timeout_seconds,
        )
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(status_code=503, detail="Code execution service is unavailable") from exc


@router.get("/languages", summary="List programming languages supported by Judge0")
def list_languages() -> list[dict[str, Any]]:
    return list(_supported_languages())


@router.post("/problems/{problem_id}/run", summary="Run code against custom input")
def run_code(problem_id: int, payload: CodeRunRequest, db: Database, _user: Learner) -> dict[str, Any]:
    get_published_problem(db, problem_id)
    _require_supported_language(payload.language_id)
    return _execute(payload.source_code, payload.language_id, payload.stdin)


@router.post("/problems/{problem_id}/submit", summary="Submit code against hidden test cases")
def submit_code(problem_id: int, payload: CodeRunRequest, db: Database, user: Learner) -> dict[str, Any]:
    problem = get_published_problem(db, problem_id)
    _require_supported_language(payload.language_id)
    cases = problem.hidden_test_cases or []
    if not cases:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This problem has no judge test cases configured")

    total_runtime = 0.0
    verdict = "Accepted"
    failed_case = None
    result: dict[str, Any] = {}
    for index, case in enumerate(cases, start=1):
        result = _execute(payload.source_code, payload.language_id, case["input"])
        status_description = (result.get("status") or {}).get("description", "Unknown Error")
        if status_description != "Accepted":
            verdict = status_description
            failed_case = index
            break
        actual = (result.get("stdout") or "").strip()
        expected = (case.get("output") or "").strip()
        if actual != expected:
            verdict = "Wrong Answer"
            failed_case = index
            break
        try:
            total_runtime += float(result.get("time") or 0)
        except (TypeError, ValueError):
            pass

    attempt = PracticeAttempt(
        user_id=user.user_id,
        problem_id=problem.problem_id,
        language=str(payload.language_id),
        verdict=verdict,
        execution_time=total_runtime or None,
        memory_used=result.get("memory"),
    )
    db.add(attempt)
    db.flush()
    now = datetime.now(UTC).replace(tzinfo=None)
    progress = db.get(UserProblemStatus, (user.user_id, problem.problem_id))
    if progress is None:
        progress = UserProblemStatus(
            user_id=user.user_id,
            problem_id=problem.problem_id,
            status="solved" if verdict == "Accepted" else "attempted",
            first_attempt_at=now,
            solved_at=now if verdict == "Accepted" else None,
            updated_at=now,
        )
        db.add(progress)
    else:
        if progress.first_attempt_at is None:
            progress.first_attempt_at = now
        if verdict == "Accepted":
            progress.status = "solved"
            progress.solved_at = now
        elif progress.status != "solved":
            progress.status = "attempted"
        progress.updated_at = now
    refresh_daily_activity(db, user, user_local_date(user))
    db.commit()
    return {
        "verdict": verdict,
        "passed": len(cases) if verdict == "Accepted" else (failed_case - 1 if failed_case else 0),
        "total": len(cases),
        "failed_case": failed_case,
        "time": total_runtime,
        "memory": result.get("memory"),
        "attempt_id": attempt.attempt_id,
    }
