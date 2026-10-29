# ASDL backend

FastAPI service with SQLAlchemy 2 and Alembic migrations for MySQL. FastAPI serves interactive API docs at `/docs` and `/redoc`, and its generated OpenAPI JSON at `/openapi.json`. A checked-in OpenAPI YAML starter is in `openapi.yaml`.

## Local setup

From this directory, create and activate a virtual environment, then install dependencies:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `DATABASE_URL` in `.env` for your MySQL instance. The configured driver is PyMySQL; create the database and user in MySQL before starting the API.

## Run

```powershell
uvicorn app.main:app --reload
```

The initial liveness endpoint is `GET /api/v1/health`. It confirms the API process responds and does not query MySQL.

## Migrations

Add SQLAlchemy models under `app/`, import their modules in `alembic/env.py`, and generate/apply migrations:

```powershell
alembic revision --autogenerate -m "describe schema change"
alembic upgrade head
```

Alembic reads `DATABASE_URL` from the environment (or `.env` through app settings). Review generated migration scripts before applying them.
