# RAG Document Ingestion Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build document upload, text extraction, token chunking, database persistence, and retrieval endpoints for `.txt` and `.pdf` documents.

**Architecture:** Keep the existing thin FastAPI structure. Add ORM models and one new router for API behavior, then put file extraction and chunking in small pure service modules so unit tests can lead the implementation.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy, Alembic, PostgreSQL, `tiktoken`, `pdfplumber`, pytest

---

### Task 1: Add failing loader and chunker tests

**Files:**
- Create: `tests/fixtures/sample_document.pdf`
- Create: `tests/test_document_loaders.py`
- Create: `tests/test_chunking.py`

**Step 1: Write the failing tests**

```python
def test_txt_loader_reads_uploaded_text() -> None:
    ...


def test_pdf_loader_extracts_non_empty_text() -> None:
    ...


def test_chunker_splits_long_text_into_multiple_chunks() -> None:
    ...


def test_chunker_preserves_overlap_between_adjacent_chunks() -> None:
    ...
```

**Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_document_loaders.py tests/test_chunking.py -q`
Expected: FAIL because the loader/chunking modules do not exist yet.

**Step 3: Write minimal implementation**

Create pure service modules for TXT loading, PDF loading, and chunk generation.

**Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_document_loaders.py tests/test_chunking.py -q`
Expected: PASS

### Task 2: Add database models and migration for document storage

**Files:**
- Create: `core/models.py`
- Modify: `core/db.py`
- Create: `migrations/versions/0002_add_documents_and_chunks.py`

**Step 1: Write the failing tests**

Extend chunk/API tests to require stored document and chunk rows.

**Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_documents_api.py -q`
Expected: FAIL because the tables and session dependency are missing.

**Step 3: Write minimal implementation**

Add `Document` and `Chunk` models, a request-scoped DB session dependency, and a migration that creates both tables.

**Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_documents_api.py -q`
Expected: PASS for the storage-related assertions that are now implemented.

### Task 3: Add failing API tests for upload and retrieval

**Files:**
- Create: `tests/test_documents_api.py`

**Step 1: Write the failing tests**

Cover:
- successful TXT upload
- successful PDF upload
- unsupported type rejection
- empty file rejection
- missing document `404`
- zero-chunk document returns empty array

**Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_documents_api.py -q`
Expected: FAIL because `/documents` routes do not exist yet.

**Step 3: Write minimal implementation**

Add the documents router, request validation, loader/chunker orchestration, and persistence/retrieval behavior.

**Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_documents_api.py -q`
Expected: PASS

### Task 4: Finish validation and documentation

**Files:**
- Modify: `README.md`
- Modify: `requirements.txt`

**Step 1: Write the failing validation**

Check that docs and dependencies do not yet mention ingestion-related requirements.

**Step 2: Write minimal implementation**

Add missing dependency and usage documentation for document ingestion.

**Step 3: Run validation to verify it passes**

Run:
- `python -m pytest tests -q`
- `python -c "from app.main import app"`
- `alembic upgrade head`

Expected: PASS

Plan complete and saved to `docs/plans/2026-03-22-rag-document-ingestion-implementation.md`. For this unattended session, execution will continue in the current branch with the plan above as the source of truth.
