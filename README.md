# RAG Agent

Bootstrap for the RAG Agent backend using FastAPI, PostgreSQL 16 with `pgvector`, Docker Compose, and Alembic.

The repository now also includes a React + Vite frontend for document upload and question answering against the local API.

## Prerequisites

- Python 3.11 for local development
- Docker and Docker Compose
- Node.js 22 and npm 10 for the frontend

## Project Layout

- `app/`: FastAPI entry point and environment-backed settings
- `api/routes/`: HTTP route modules
- `core/`: SQLAlchemy metadata and database helpers
- `src/`: React frontend entry point, API client, and page UI
- `migrations/`: Alembic environment and migration scripts
- `tests/`: pytest coverage for the bootstrap surface
- `tests-ui/`: Vitest coverage for the frontend upload and Q&A flows

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

## Frontend Workflow

Install the frontend dependencies and run the UI locally:

```bash
npm install
npm run dev
```

The Vite app defaults to calling the backend at `http://localhost:8000`. Override that base URL when needed with:

```bash
VITE_API_BASE_URL=http://localhost:8000 npm run dev
```

Run the frontend checks with:

```bash
npm run test -- --run
npm run build
```

The page provides:

- document upload for `.pdf` and `.txt`
- success and error banners for uploads
- question submission with a loading state
- answer rendering with expandable source previews and relevance scores

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
