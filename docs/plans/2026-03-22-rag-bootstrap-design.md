# RAG Bootstrap Design

## Goal

Set up a thin but production-shaped backend foundation for the RAG Agent project so local development can start from a working FastAPI service, a Dockerized PostgreSQL instance with `pgvector`, and an Alembic migration path.

## Approaches Considered

### 1. Minimal bootstrap with extension-only migration

- Fastest path to the ticket goals.
- Keeps the first migration focused on enabling `vector` rather than inventing premature tables.
- Recommended because the acceptance criteria are infrastructure-oriented, not feature-oriented.

### 2. Bootstrap plus placeholder domain tables

- Could make later tickets start faster.
- Adds assumptions about chunk/document schemas before retrieval requirements are defined.
- Rejected for this ticket because it broadens scope without acceptance coverage.

### 3. Docker-only validation with no local Python test path

- Simplifies host setup.
- Makes fast iteration and import-level verification weaker.
- Rejected because the ticket explicitly requires `python -c "from app.main import app"` and benefits from a local test cycle.

## Selected Design

- Use `FastAPI` with a small app factory-free setup in `app/main.py`.
- Keep configuration in `app/config.py` using `pydantic-settings`.
- Put SQLAlchemy engine/session helpers in `core/db.py`.
- Expose one router in `api/routes/health.py` returning `{"status": "ok"}`.
- Configure Alembic to target the project metadata and run an initial migration that executes `CREATE EXTENSION IF NOT EXISTS vector`.
- Use Docker Compose with two services:
  - `db`: `pgvector/pgvector:pg16` with a PostgreSQL health check.
  - `api`: Python 3.11 image built from the local `Dockerfile`, running Uvicorn with an HTTP health check.

## Error Handling

- Health endpoint remains lightweight and does not require a DB round-trip, so the API can become healthy as soon as the process is serving.
- Database connectivity is still validated through Alembic and explicit PostgreSQL checks during validation.

## Testing Strategy

- Start with failing tests for import and the health endpoint.
- Add the minimal code required to make those tests pass.
- Use CLI validation for import, migrations, Docker health, and extension presence.
