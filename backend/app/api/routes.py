from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/health", tags=["health"], summary="Check API health")
def health_check() -> dict[str, str]:
    """Return a simple liveness response. This does not check database connectivity."""
    return {"status": "ok"}
