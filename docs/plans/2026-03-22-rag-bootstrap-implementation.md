# RAG Bootstrap Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the initial FastAPI, PostgreSQL + pgvector, Docker Compose, and Alembic foundation for the RAG Agent repository.

**Architecture:** Keep the application intentionally thin: one FastAPI app, one health router, one SQLAlchemy setup module, and one Alembic migration that enables `pgvector`. Use Docker Compose to orchestrate the API and Postgres services for local development.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy, Alembic, PostgreSQL 16, pgvector, Docker Compose, pytest

---

### Task 1: Establish failing tests for the missing app surface

**Files:**
- Create: `tests/test_health.py`

**Step 1: Write the failing test**

```python
from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_returns_ok() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_health.py -v`
Expected: FAIL because `app.main` does not exist yet.

**Step 3: Write minimal implementation**

Create the app package, register a health router, and return the expected payload.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_health.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/test_health.py app api
git commit -m "feat: add fastapi health endpoint"
```

### Task 2: Add configuration and database bootstrap

**Files:**
- Create: `app/config.py`
- Create: `core/db.py`

**Step 1: Write the failing test**

Extend `tests/test_health.py` with an import-level assertion that `app` is a FastAPI instance and the settings/database modules import cleanly.

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_health.py -v`
Expected: FAIL until the modules exist.

**Step 3: Write minimal implementation**

Add settings and SQLAlchemy engine/session helpers using environment-backed configuration.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_health.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/config.py core/db.py tests/test_health.py
git commit -m "feat: add config and database bootstrap"
```

### Task 3: Add container and migration scaffolding

**Files:**
- Create: `Dockerfile`
- Create: `docker-compose.yml`
- Create: `alembic.ini`
- Create: `migrations/env.py`
- Create: `migrations/script.py.mako`
- Create: `migrations/versions/0001_enable_pgvector.py`
- Create: `requirements.txt`
- Create: `.env.example`

**Step 1: Write the failing validation**

Run: `docker compose config`
Expected: FAIL until the compose and Docker files exist.

**Step 2: Run migration command to verify it fails**

Run: `alembic upgrade head`
Expected: FAIL until Alembic is configured.

**Step 3: Write minimal implementation**

Add Compose, Docker, dependency, and Alembic files so the stack builds and the migration creates the `vector` extension.

**Step 4: Run validations to verify they pass**

Run: `docker compose config`
Run: `alembic upgrade head`

**Step 5: Commit**

```bash
git add Dockerfile docker-compose.yml alembic.ini migrations requirements.txt .env.example
git commit -m "feat: add docker and migration bootstrap"
```

### Task 4: Finish documentation and full validation

**Files:**
- Modify: `README.md`

**Step 1: Write the failing validation**

Check the README against ticket requirements and confirm run/env/migration instructions are missing.

**Step 2: Write minimal implementation**

Document setup, environment variables, Docker Compose usage, and migration commands.

**Step 3: Run validation to verify it passes**

Run:
- `pytest`
- `python -c "from app.main import app"`
- `docker compose up -d`
- `docker compose ps`
- `curl http://localhost:8000/health`
- `docker compose exec db psql -U postgres -d rag_agent -c "\dx"`
- `alembic upgrade head`

**Step 4: Commit**

```bash
git add README.md
git commit -m "docs: add local development guide"
```
