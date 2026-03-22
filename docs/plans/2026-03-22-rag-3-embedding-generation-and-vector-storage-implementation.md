# RAG-3 Embedding Generation and Vector Storage Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an internal batch embedding pipeline that reads unembedded chunks, requests `text-embedding-3-small` vectors from OpenAI, and stores them in PostgreSQL `pgvector`.

**Architecture:** Keep the implementation split into three layers: schema metadata and migrations for `chunks`/`embeddings`, a pure Python batch processor that owns retries and dimension validation, and a CLI script that wires the processor to OpenAI and the database. Use repository abstractions so the critical behavior is testable without a live database or API dependency.

**Tech Stack:** Python 3.11, SQLAlchemy, Alembic, PostgreSQL 16, pgvector, OpenAI Python SDK, pytest

---

### Task 1: Add failing processor tests

**Files:**
- Create: `tests/test_embed_chunks.py`

**Step 1: Write the failing tests**

Add tests for:
- `embedding_dimensions_match`
- idempotent reruns with already-embedded chunks
- retry after a rate-limit response

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_embed_chunks.py -v`
Expected: FAIL because the embedding processor module does not exist yet.

**Step 3: Write minimal implementation**

Create the processor contracts and enough code for the tests to exercise batching, retries, and dimension checks.

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_embed_chunks.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/test_embed_chunks.py core
git commit -m "feat: add embedding processor"
```

### Task 2: Add chunk and embedding schema support

**Files:**
- Create: `core/models.py`
- Create: `migrations/versions/0002_add_chunks_and_embeddings.py`
- Modify: `migrations/env.py`

**Step 1: Write the failing validation**

Run: `alembic upgrade head`
Expected: FAIL until the new migration exists and imports stay valid.

**Step 2: Write minimal implementation**

Add metadata for `chunks` and `embeddings`, then create the corresponding migration with `vector(1536)`.

**Step 3: Run validation to verify it passes**

Run: `alembic upgrade head`
Expected: PASS

**Step 4: Commit**

```bash
git add core/models.py migrations
git commit -m "feat: add chunk and embedding schema"
```

### Task 3: Wire the PostgreSQL repository and OpenAI client

**Files:**
- Create: `core/embeddings.py`
- Modify: `core/db.py`

**Step 1: Extend tests or add focused failures**

Add assertions that repository-facing batch results preserve chunk IDs, dimensions, and idempotent insert counts.

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_embed_chunks.py -v`
Expected: FAIL until the repository/client wiring exists.

**Step 3: Write minimal implementation**

Add:
- a PostgreSQL repository that fetches only unembedded chunks with a `LEFT JOIN`
- batched vector insertion with `ON CONFLICT DO NOTHING`
- an OpenAI client wrapper for `text-embedding-3-small`

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_embed_chunks.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add core/embeddings.py core/db.py tests/test_embed_chunks.py
git commit -m "feat: wire embedding repository and client"
```

### Task 4: Add the CLI script and complete validation

**Files:**
- Create: `scripts/__init__.py`
- Create: `scripts/embed_chunks.py`
- Modify: `README.md`
- Modify: `docs/demand/overview.md`

**Step 1: Write the failing validation**

Run: `python -m scripts.embed_chunks --batch-size 100`
Expected: FAIL until the script package and entrypoint exist.

**Step 2: Write minimal implementation**

Add the CLI script, logging setup, API key validation, and usage docs.

**Step 3: Run validation to verify it passes**

Run:
- `pytest tests/test_embed_chunks.py -v`
- `pytest -q`
- `python -m scripts.embed_chunks --batch-size 100`

Expected:
- tests PASS
- script starts correctly and either processes chunks or fails only on missing runtime secrets/database state with a clear message

**Step 4: Commit**

```bash
git add scripts README.md docs/demand/overview.md
git commit -m "feat: add embedding batch script"
```
