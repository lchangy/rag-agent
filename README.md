# RAG Agent

Bootstrap for the RAG Agent backend using FastAPI, PostgreSQL 16 with `pgvector`, Docker Compose, and Alembic.

## Prerequisites

- Python 3.11 for local development
- Docker and Docker Compose

## Project Layout

- `app/`: FastAPI entry point and environment-backed settings
- `api/routes/`: HTTP route modules
- `core/`: SQLAlchemy metadata and database helpers
- `services/`: document loaders and token chunking helpers
- `migrations/`: Alembic environment and migration scripts
- `tests/`: pytest coverage for the bootstrap surface

## API Surface

- `GET /health`: liveness endpoint returning `{"status": "ok"}`
- `POST /documents`: multipart upload endpoint accepting `.txt` and `.pdf` files under the `file` field
- `GET /documents/{id}`: returns stored document metadata and chunk content

Document upload behavior:

- Maximum file size: `50MB`
- Supported formats: `.txt`, `.pdf`
- Chunking: `512` tokens per chunk with `50` tokens of overlap
- Stored chunk metadata: `chunk_index`, `start_char`, `end_char`, `token_count`

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
- `OPENAI_API_KEY`: reserved for future embedding/chat integrations

## Local Python Workflow

Install dependencies into any Python 3.11 environment, then run the import, tests, and migrations:

```bash
pip install -r requirements.txt
python -m pytest
python -c "from app.main import app"
alembic upgrade head
```

To exercise the document API locally without starting Docker:

```bash
python - <<'PY'
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
response = client.post(
    "/documents",
    files={"file": ("sample.txt", b"hello world " * 200, "text/plain")},
)
print(response.status_code, response.json())
PY
```

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

Example upload response:

```json
{"document_id":"<uuid>","filename":"sample.txt","chunks_created":1}
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
