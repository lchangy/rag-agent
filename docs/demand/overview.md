# RAG Agent Demand Overview

## Scope v1

- Bootstrap a FastAPI service that imports cleanly and exposes `GET /health`.
- Add PostgreSQL 16 with the `pgvector` extension available in local development.
- Add Docker Compose so the API and database start together for local work.
- Add Alembic so schema and extension setup can be managed through migrations.
- Document local setup, environment variables, and migration commands.
- Add synchronous document ingestion for `.txt` and `.pdf` uploads via `POST /documents`.
- Persist uploaded document metadata and token-overlapping chunks in PostgreSQL.
- Expose `GET /documents/{id}` to return stored document metadata and chunk content.

## Not Doing

- No retrieval, embedding, chat, or document-ingestion endpoints yet.
- No authentication, authorization, or background job system.
- No production deployment configuration beyond local Docker development.
- No application data models beyond what is required to bootstrap migrations.
- No background job queue for document processing in this phase.
- No raw file persistence beyond extracting text and storing document/chunk rows.
- No stemming, normalization, or semantic preprocessing beyond text extraction and chunking.

## Key Flows

1. A developer copies `.env.example`, then starts the stack with Docker Compose.
2. The API boots, can import `app.main`, and answers `GET /health` with `{"status": "ok"}`.
3. Alembic runs the initial migration and ensures the `vector` extension exists.
4. A developer can connect to PostgreSQL locally and confirm `pgvector` is installed.
5. A client uploads a `.txt` or `.pdf` file to `POST /documents`, receives a document UUID, and gets the chunk count in the response.
6. The service extracts text, splits it into 512-token chunks with 50-token overlap, and stores chunk metadata plus content in PostgreSQL.
7. A client fetches `GET /documents/{id}` and receives document metadata plus the stored chunks in order.

## Data and Boundaries

- FastAPI app owns HTTP routing and lightweight health behavior.
- SQLAlchemy owns engine/session setup and provides the Alembic metadata target.
- PostgreSQL stores future RAG data; the initial migration only guarantees extension readiness.
- OpenAI configuration is accepted through environment variables but not exercised yet.
- The document ingestion layer owns file validation, text extraction, chunking, and persistence.
- Character offsets are defined against the extracted text string, not PDF byte offsets.
- Token boundaries are derived from a fixed tokenizer configuration so overlap and counts are deterministic.

## Integrations

- OpenAI API via environment configuration placeholders for future embedding/chat usage.
- PostgreSQL 16 via Docker Compose, using an image with `pgvector` available.
- Alembic for schema and extension lifecycle management.
- `tiktoken` for deterministic token counting and chunk boundaries.
- `pdfplumber` for PDF text extraction.

## Assumptions

- The repository root is the application root, even though the Linear description labels it `rag-agent/`.
- A minimal bootstrap is sufficient for this ticket; future tickets will add domain models and routes.
- Docker is available in the execution environment for validation.
- Synchronous ingestion inside the request/response cycle is acceptable for files up to 50MB in this ticket.
- UUIDs can be generated in application code if DB-side `gen_random_uuid()` defaults are undesirable.
- Offset metadata should reflect extracted UTF-8 text positions, which is the only stable boundary for PDFs.

## Risks

- Local validation depends on container image and Python package downloads succeeding.
- Health checks must avoid requiring external secrets so the stack can boot unattended.
- PDF text extraction can introduce whitespace/newline variance, which can shift chunk boundaries if fixture expectations are too exact.
- Token-to-character offset mapping can become quadratic if implemented by repeatedly decoding token prefixes.
- Upload validation needs to short-circuit oversized files before expensive parsing where possible.

## Validation Notes

- Import proof: `python -c "from app.main import app"`
- API proof: `curl http://localhost:8000/health`
- Migration proof: `alembic upgrade head`
- Extension proof: `docker compose exec db psql -U postgres -d rag_agent -c "\dx"`
- Ingestion proof: `POST /documents` with TXT and PDF fixtures returns a UUID and chunk count.
- Retrieval proof: `GET /documents/{id}` returns chunk metadata/content and `404` for missing IDs.
- Chunk proof: tests assert ~50-token overlap and recorded `token_count` values.
