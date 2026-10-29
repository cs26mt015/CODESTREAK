# CodeStreak backend

FastAPI service with SQLAlchemy 2 and Alembic migrations for MySQL. The SQLAlchemy models and migrations implement the entities in the project ERD. FastAPI serves interactive API docs at `/docs` and `/redoc`, generated OpenAPI JSON at `/openapi.json`; the reviewed API contract is in `openapi.yaml`.

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

The API includes JSON login/registration, public problem search/details, learner-owned attempts/status/plans/progress, deterministic recommendations, and administrator-only problem management. Passwords use Argon2 hashes and protected endpoints use expiring JWT bearer tokens. Registering creates a learner; an administrator must be provisioned by promoting a trusted account in the database.

The recommendation rule first looks for an unsolved published problem in the learner's least-solved topic, orders candidates by difficulty (easy, medium, hard), and falls back to the next unsolved published problem when no topic match exists.

The hint route currently returns `503` because no AI provider is configured. The request is rate-limited and minimal failure metadata is stored; the user's hint question is not persisted or sent externally.

## Migrations

Add SQLAlchemy models under `app/`, import their modules in `alembic/env.py`, and generate/apply migrations:

```powershell
alembic revision --autogenerate -m "describe schema change"
alembic upgrade head
```

Alembic reads `DATABASE_URL` from the environment (or `.env` through app settings). In Docker, the backend applies existing migrations automatically before starting the API. Review generated migration scripts before applying them.

The ERD does not mark column nullability. Optional problem content and attempt metrics are nullable in this implementation; the required/optional distinction can be adjusted if the intended data rules differ. One activity row per user-local date and one plan per user/date are enforced to support the design document's streak and goal rules.
