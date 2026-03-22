# RAG Agent

Bootstrap for the RAG Agent backend using FastAPI, PostgreSQL 16 with `pgvector`, Docker Compose, and Alembic.

## Prerequisites

- Python 3.11 for local development
- Docker and Docker Compose

## Project Layout

- `app/`: FastAPI entry point and environment-backed settings
- `api/routes/`: HTTP route modules
- `core/`: SQLAlchemy metadata and database helpers
- `scripts/`: internal maintenance commands such as batch embedding generation
- `migrations/`: Alembic environment and migration scripts
- `tests/`: pytest coverage for the bootstrap surface

## Environment Variables

Copy `.env.example` to `.env` when you want to override defaults:

```bash
cp .env.example .env
```

Supported variables:

- `APP_NAME`: FastAPI application name shown in docs metadata
- `DATABASE_HOST`: PostgreSQL host for local commands, default `localhost`
- `DATABASE_PORT`: PostgreSQL host port for local commands, default `5433`
- `DATABASE_USER`: PostgreSQL username, default `postgres`
- `DATABASE_PASSWORD`: PostgreSQL password, default `postgres`
- `DATABASE_NAME`: PostgreSQL database name, default `rag_agent`
- `OPENAI_API_KEY`: required for live runs of `python -m scripts.embed_chunks`

## Local Python Workflow

Install dependencies into any Python 3.11 environment, then run the import, tests, and migrations:

```bash
pip install -r requirements.txt
python -m pytest
python -c "from app.main import app"
alembic upgrade head
```

Generate embeddings for chunks that do not yet have rows in `embeddings` with:

```bash
python -m scripts.embed_chunks --batch-size 100
```

The batch command is idempotent: it only selects chunks missing embeddings, stores vectors as `vector(1536)`, and logs progress as `Embedded X/Y chunks`.

## Docker Workflow

Start the API and database stack:

```bash
docker compose up -d --build
docker compose ps
curl http://localhost:8000/health
```

Expected health response:

```json
{"status": "ok"}
```

To rerun migrations inside the API container:

```bash
docker compose exec api alembic upgrade head
```

To verify `pgvector` is installed:

```bash
docker compose exec db psql -U postgres -d rag_agent -c "\dx"
```

Stop the stack with:

```bash
docker compose down
```
