from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.hints import router as hints_router
from app.api.problems import admin_router, router as problems_router
from app.api.practice import router as practice_router
from app.api.progress import recommendation_router, router as progress_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(problems_router)
api_router.include_router(practice_router)
api_router.include_router(progress_router)
api_router.include_router(recommendation_router)
api_router.include_router(hints_router)
api_router.include_router(admin_router)


@api_router.get("/health", tags=["system"], summary="Check API liveness")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
