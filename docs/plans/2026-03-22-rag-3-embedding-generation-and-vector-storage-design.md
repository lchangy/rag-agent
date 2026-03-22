# RAG-3 Embedding Generation and Vector Storage Design

## Goal

Add the smallest production-shaped embedding pipeline that can read chunk rows, request `text-embedding-3-small` vectors from OpenAI in batches, and persist them in PostgreSQL `pgvector` storage.

## Approaches Considered

### 1. Thin service plus PostgreSQL repository

- Keep the batch orchestration, retry policy, and dimension checks in pure Python service code.
- Use a repository layer for the `LEFT JOIN` pending-chunk query and `embeddings` inserts.
- Recommended because it keeps the OpenAI and retry behavior easy to unit test without requiring a live database or API key.

### 2. Script-only implementation with inline SQL and inline OpenAI calls

- Fastest to write.
- Couples retry logic, storage logic, and CLI parsing into one module.
- Rejected because it makes idempotency, retry, and logging behavior harder to test directly.

### 3. Add a background job framework now

- Could fit a future ingestion pipeline.
- Adds queueing and worker complexity that is not required by the ticket contract.
- Rejected because the ticket only requires a batch script that runs after chunking.

## Selected Design

- Add minimal SQLAlchemy metadata for `chunks` and `embeddings` so the schema is visible to Alembic and future tickets.
- Create one Alembic migration that adds a minimal `chunks` table and the ticket-specified `embeddings` table using `vector(1536)`.
- Implement an `EmbeddingBatchProcessor` service that:
  - counts pending chunks,
  - fetches only rows where no embedding exists,
  - requests embeddings in batches,
  - validates that every vector has 1536 dimensions,
  - retries OpenAI rate-limit failures with backoff,
  - logs `Embedded X/Y chunks` after each successful batch.
- Wire the service into `python -m scripts.embed_chunks --batch-size 100`.

## Assumptions

- The repository does not yet contain the RAG-2 chunk schema, so this ticket will create the minimum `chunks(id, content, created_at)` table needed for the embedding contract and tests.
- The embedding pipeline can remain internal-only for now; no HTTP endpoint or queue integration is required.
- Performance validation can be demonstrated with a synthetic 1000-chunk batch processor run when a live OpenAI benchmark is not possible in-session.

## Error Handling

- Missing `OPENAI_API_KEY` should fail fast with a clear runtime error in the CLI entrypoint.
- Rate-limit errors should back off and retry without inserting partial duplicate rows.
- A vector with the wrong dimension should raise immediately and abort the batch so invalid data does not reach storage.

## Testing Strategy

- Write tests first against the pure batch processor using fake repositories and fake embedding clients.
- Cover dimension enforcement, idempotent reruns, and retry-on-rate-limit behavior.
- Validate the CLI and migration path locally after implementation.
