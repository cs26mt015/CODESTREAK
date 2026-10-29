from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select

from app.api.common import get_published_problem
from app.api.dependencies import Database, learner_user
from app.core.config import settings
from app.models.ai_interaction_metadata import AIInteractionMetadata
from app.models.user import User
from app.schemas import HintRequest, HintResponse

router = APIRouter(tags=["hints"])
CurrentUser = Annotated[User, Depends(learner_user)]
MAX_HINT_REQUESTS_PER_WINDOW = 5
HINT_WINDOW = timedelta(minutes=10)


@router.post(
    "/problems/{problem_id}/hints",
    response_model=HintResponse,
    responses={
        429: {"description": "Hint request limit reached"},
        503: {"description": "Hint provider is not configured or unavailable"},
    },
)
def request_hint(
    problem_id: int,
    payload: HintRequest,
    db: Database,
    user: CurrentUser,
) -> HintResponse:
    problem = get_published_problem(db, problem_id)
    now = datetime.now(UTC).replace(tzinfo=None)
    recent_count = db.scalar(
        select(func.count())
        .select_from(AIInteractionMetadata)
        .where(
            AIInteractionMetadata.user_id == user.user_id,
            AIInteractionMetadata.created_at >= now - HINT_WINDOW,
        )
    ) or 0
    if recent_count >= MAX_HINT_REQUESTS_PER_WINDOW:
        raise HTTPException(status_code=429, detail="Hint request limit reached. Try again later.")

    db.add(
        AIInteractionMetadata(
            user_id=user.user_id,
            problem_id=problem.problem_id,
            feature=f"hint_level_{payload.level}",
            model=settings.hint_provider if settings.hint_provider != "disabled" else "unconfigured",
            input_tokens=0,
            output_tokens=0,
            estimated_cost=None,
            request_status=(
                "provider_unconfigured" if settings.hint_provider == "disabled" else "provider_unavailable"
            ),
            latency_ms=0,
            created_at=now,
        )
    )
    db.commit()
    if settings.hint_provider == "disabled":
        detail = "AI hint service is not configured"
    else:
        detail = "The configured AI hint provider is not available in this deployment"
    raise HTTPException(status_code=503, detail=detail)
