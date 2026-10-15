# CodeStreak

CodeStreak is an AI-enabled competitive programming practice platform.

## Planned Technology Stack

- Frontend: React and Vite
- Backend: Python and FastAPI
- Database: MySQL 8
- ORM and migrations: SQLAlchemy and Alembic
- API documentation: OpenAPI and Swagger UI
- Testing: pytest, pytest-cov, and Playwright
- Containerization: Docker and Docker Compose
- AI assistance: Google Gemini API (proposed)

## Project Structure

- `frontend/` — React application
- `backend/` — FastAPI application, business logic, and tests
- `database/` — Database-related assets and seed data
- `Dockerfile` — Application image build
- `docker-compose.yml` — Local application and database services
- `.env.example` — Example environment configuration

## Planned Features

- Curated programming problem library
- Topic and difficulty filters
- Problem attempt and solved-status tracking
- Daily streaks and practice goals
- Progress analytics
- AI-generated contextual hints and explanations

## Scope

The initial release will focus on practice management and learning support. It will not execute arbitrary submitted code or implement a full-scale online judge.

## Development Status

Initial project setup is in progress.
