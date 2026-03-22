# RAG Document Ingestion Design

## Goal

Implement a deterministic document ingestion pipeline for `.txt` and `.pdf` uploads so the API can extract text, split it into overlapping token chunks, persist both document and chunk rows in PostgreSQL, and return the stored data via a retrieval endpoint.

## Approaches Considered

### 1. Synchronous ingestion during `POST /documents`

- Read and validate the upload in the request lifecycle.
- Extract text, generate chunks, insert the `documents` row and child `chunks`, then return the result.
- Recommended because it matches the ticket contract and keeps the bootstrap codebase small.

### 2. Background ingestion with queued processing

- Store the upload, return a pending document record immediately, and process extraction/chunking asynchronously.
- Better for very large files and retries, but it requires job orchestration, status tracking, and changed endpoint semantics.
- Rejected for this ticket because it expands scope beyond the stated contract.

### 3. Persist token boundaries only and derive chunk text at read time

- Save token spans and compute content/char offsets on demand.
- Avoids some write-time work but complicates reads and weakens the explicit chunk metadata contract.
- Rejected because the ticket expects stored chunk text and straightforward retrieval behavior.

## Selected Design

- Add ORM models for `documents` and `chunks`, plus an Alembic migration that creates both tables.
- Add a new documents router with:
  - `POST /documents` for multipart upload, validation, extraction, chunking, and persistence.
  - `GET /documents/{id}` for document metadata plus ordered chunks.
- Introduce a small service layer:
  - `services/loaders.py` for TXT and PDF text extraction.
  - `services/chunking.py` for token chunk generation and metadata calculation.
- Generate document/chunk UUIDs in application code for deterministic inserts without requiring additional DB extensions.
- Keep character offsets relative to the extracted text string. For PDFs, this is the only stable definition.

## Tokenization and Chunking

- Use `tiktoken` with an explicit encoding so chunk boundaries remain reproducible.
- Chunk size is `512` tokens with `50` tokens of overlap.
- Each chunk stores:
  - `chunk_index`
  - `content`
  - `start_char`
  - `end_char`
  - `token_count`
- Offset mapping should be derived from token positions once per document, not by repeatedly decoding prefixes, to avoid quadratic behavior on larger documents.

## Error Handling

- Reject unsupported extensions with `400` and `{"detail": "Unsupported file type. Use .pdf or .txt"}`.
- Reject empty files with `400` and `{"detail": "File is empty"}`.
- Reject files larger than `50MB` with `413`.
- Return `404` when `GET /documents/{id}` references a document that does not exist.
- Return an empty `chunks` array when extraction yields no chunks.

## Testing Strategy

- Write failing unit tests first for:
  - TXT loading
  - PDF loading
  - Chunk generation
  - Chunk overlap behavior
- Add route-level tests for:
  - successful TXT upload
  - successful PDF upload
  - unsupported file rejection
  - empty file rejection
  - `GET /documents/{id}` success and `404`
- Use a committed PDF fixture and property-style assertions for extraction/chunk metadata rather than brittle exact-string expectations.
