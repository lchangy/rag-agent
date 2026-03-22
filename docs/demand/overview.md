# RAG Agent Demand Overview

## Scope v1

- Bootstrap a FastAPI service that imports cleanly and exposes `GET /health`.
- Add PostgreSQL 16 with the `pgvector` extension available in local development.
- Add Docker Compose so the API and database start together for local work.
- Add Alembic so schema and extension setup can be managed through migrations.
- Document local setup, environment variables, and migration commands.

## Not Doing

- No retrieval, embedding, chat, or document-ingestion endpoints yet.
- No authentication, authorization, or background job system.
- No production deployment configuration beyond local Docker development.
- No application data models beyond what is required to bootstrap migrations.

## Key Flows

1. A developer copies `.env.example`, then starts the stack with Docker Compose.
2. The API boots, can import `app.main`, and answers `GET /health` with `{"status": "ok"}`.
3. Alembic runs the initial migration and ensures the `vector` extension exists.
4. A developer can connect to PostgreSQL locally and confirm `pgvector` is installed.

## Data and Boundaries

- FastAPI app owns HTTP routing and lightweight health behavior.
- SQLAlchemy owns engine/session setup and provides the Alembic metadata target.
- PostgreSQL stores future RAG data; the initial migration only guarantees extension readiness.
- OpenAI configuration is accepted through environment variables but not exercised yet.

## Integrations

- OpenAI API via environment configuration placeholders for future embedding/chat usage.
- PostgreSQL 16 via Docker Compose, using an image with `pgvector` available.
- Alembic for schema and extension lifecycle management.

## Assumptions

- The repository root is the application root, even though the Linear description labels it `rag-agent/`.
- A minimal bootstrap is sufficient for this ticket; future tickets will add domain models and routes.
- Docker is available in the execution environment for validation.

## Risks

- Local validation depends on container image and Python package downloads succeeding.
- Health checks must avoid requiring external secrets so the stack can boot unattended.

## Validation Notes

- Import proof: `python -c "from app.main import app"`
- API proof: `curl http://localhost:8000/health`
- Migration proof: `alembic upgrade head`
- Extension proof: `docker compose exec db psql -U postgres -d rag_agent -c "\dx"`
