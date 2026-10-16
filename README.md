# CodeStreak

CodeStreak is a competitive programming practice platform.

## Requirements

- Docker Desktop or Docker Engine with the Docker Compose plugin.
- An internet connection for the initial image and dependency downloads.

Python, Node.js, npm, and MySQL do not need to be installed on the host.

## Start the application

From the repository root, run:

```bash
docker compose up
```

Compose builds the application image when necessary, starts MySQL,
waits for the database health check, and starts the application.

The React frontend is built into the application image and served by FastAPI.
The database is accessible internally to the application as `db:3306`;
it is not published on a host port.

Docker automatically allocates an available host port for the web application.
To find the port, open the running app container in Docker Desktop and inspect
its published ports. The host port forwards to container port 8000.

## Stop the application

Press Ctrl+C in the terminal running Compose.

## Database persistence

MySQL data is stored in the named Docker volume `mysql_data`.
Stopping or recreating containers does not normally delete this data.

Do not use `docker compose down -v` unless you intentionally want to delete
the database volume.

## Configuration

The project can start without a local `.env` file, using development defaults.
Optional settings such as `GEMINI_API_KEY` can be supplied through environment
configuration when needed.

The built-in database credentials are for local development and demonstrations,
not production deployment.

## Technology stack

- React and Vite
- Python and FastAPI
- MySQL 8
- SQLAlchemy and Alembic
- Docker Compose
- Pytest