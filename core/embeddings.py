from __future__ import annotations

import logging
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from time import sleep as default_sleep
from typing import Protocol

from sqlalchemy import text
from sqlalchemy.orm import sessionmaker


EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536


@dataclass(frozen=True)
class ChunkRecord:
    id: str
    content: str


@dataclass(frozen=True)
class EmbeddingRecord:
    chunk_id: str
    embedding: list[float]


class ChunkEmbeddingRepository(Protocol):
    def count_pending_chunks(self) -> int:
        ...

    def fetch_pending_chunks(self, limit: int) -> list[ChunkRecord]:
        ...

    def store_embeddings(self, rows: Sequence[EmbeddingRecord], model: str) -> int:
        ...


class EmbeddingClient(Protocol):
    def create_embeddings(self, texts: Sequence[str], model: str) -> list[list[float]]:
        ...


class PostgresChunkEmbeddingRepository:
    def __init__(self, session_factory: sessionmaker) -> None:
        self.session_factory = session_factory

    def count_pending_chunks(self) -> int:
        with self.session_factory() as session:
            result = session.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM chunks
                    LEFT JOIN embeddings ON embeddings.chunk_id = chunks.id
                    WHERE embeddings.chunk_id IS NULL
                    """
                )
            )
            return int(result.scalar_one())

    def fetch_pending_chunks(self, limit: int) -> list[ChunkRecord]:
        with self.session_factory() as session:
            result = session.execute(
                text(
                    """
                    SELECT chunks.id, chunks.content
                    FROM chunks
                    LEFT JOIN embeddings ON embeddings.chunk_id = chunks.id
                    WHERE embeddings.chunk_id IS NULL
                    ORDER BY chunks.created_at, chunks.id
                    LIMIT :limit
                    """
                ),
                {"limit": limit},
            )
            return [
                ChunkRecord(id=str(row.id), content=row.content)
                for row in result.mappings()
            ]

    def store_embeddings(self, rows: Sequence[EmbeddingRecord], model: str) -> int:
        inserted = 0
        with self.session_factory() as session:
            for row in rows:
                result = session.execute(
                    text(
                        """
                        INSERT INTO embeddings (chunk_id, embedding, model)
                        VALUES (CAST(:chunk_id AS uuid), CAST(:embedding AS vector), :model)
                        ON CONFLICT (chunk_id) DO NOTHING
                        """
                    ),
                    {
                        "chunk_id": row.chunk_id,
                        "embedding": _to_vector_literal(row.embedding),
                        "model": model,
                    },
                )
                inserted += max(result.rowcount or 0, 0)
            session.commit()
        return inserted


class OpenAIEmbeddingClient:
    def __init__(self, api_key: str) -> None:
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key)

    def create_embeddings(self, texts: Sequence[str], model: str) -> list[list[float]]:
        response = self._client.embeddings.create(input=list(texts), model=model)
        ordered_data = sorted(response.data, key=lambda item: item.index)
        return [list(item.embedding) for item in ordered_data]


class EmbeddingBatchProcessor:
    def __init__(
        self,
        repository: ChunkEmbeddingRepository,
        client: EmbeddingClient,
        model: str = EMBEDDING_MODEL,
        dimensions: int = EMBEDDING_DIMENSIONS,
        logger: logging.Logger | None = None,
        sleep: Callable[[float], None] = default_sleep,
        base_delay_seconds: float = 1.0,
        max_retries: int = 5,
    ) -> None:
        self.repository = repository
        self.client = client
        self.model = model
        self.dimensions = dimensions
        self.logger = logger or logging.getLogger(__name__)
        self.sleep = sleep
        self.base_delay_seconds = base_delay_seconds
        self.max_retries = max_retries

    def run(self, batch_size: int) -> int:
        total_pending = self.repository.count_pending_chunks()
        if total_pending == 0:
            self.logger.info("Embedded 0/0 chunks")
            return 0

        processed = 0
        while True:
            chunks = self.repository.fetch_pending_chunks(batch_size)
            if not chunks:
                break

            embeddings = self._create_embeddings_with_retry([chunk.content for chunk in chunks])
            rows = self._build_embedding_records(chunks, embeddings)
            processed += self.repository.store_embeddings(rows, self.model)
            self.logger.info("Embedded %s/%s chunks", processed, total_pending)

        return processed

    def _create_embeddings_with_retry(self, texts: Sequence[str]) -> list[list[float]]:
        attempt = 0
        while True:
            try:
                return self.client.create_embeddings(texts, self.model)
            except Exception as exc:  # noqa: BLE001
                if not _is_rate_limit_error(exc) or attempt >= self.max_retries - 1:
                    raise
                delay_seconds = self.base_delay_seconds * (2**attempt)
                self.sleep(delay_seconds)
                attempt += 1

    def _build_embedding_records(
        self,
        chunks: Sequence[ChunkRecord],
        embeddings: Sequence[Sequence[float]],
    ) -> list[EmbeddingRecord]:
        if len(chunks) != len(embeddings):
            raise ValueError("Embedding response size did not match the requested chunk batch.")

        records: list[EmbeddingRecord] = []
        for chunk, embedding in zip(chunks, embeddings):
            if len(embedding) != self.dimensions:
                raise ValueError(
                    f"Expected embedding dimension {self.dimensions}, received {len(embedding)}."
                )
            records.append(EmbeddingRecord(chunk_id=chunk.id, embedding=[float(value) for value in embedding]))
        return records


def _is_rate_limit_error(exc: Exception) -> bool:
    status_code = getattr(exc, "status_code", None)
    return status_code == 429 or exc.__class__.__name__ == "RateLimitError"


def _to_vector_literal(values: Sequence[float]) -> str:
    return "[" + ",".join(str(float(value)) for value in values) + "]"
