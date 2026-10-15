from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.app.config import settings


app = FastAPI(
    title="CodeStreak API",
    description="API for the CodeStreak competitive programming practice platform.",
    version="0.1.0",
)


@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "application": "CodeStreak API",
        "environment": settings.app_env,
    }


# In production, serve the built React application from FastAPI.
static_dir = Path(__file__).parent / "static"

if static_dir.is_dir() and (static_dir / "index.html").exists():
    app.mount(
        "/",
        StaticFiles(directory=static_dir, html=True),
        name="frontend",
    )
