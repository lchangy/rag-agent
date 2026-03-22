from collections.abc import Sequence
from typing import cast
from uuid import uuid4

import pytest

from core.embeddings import ChunkRecord, EmbeddingBatchProcessor
from scripts import embed_chunks


class FakeRepository:
    def __init__(self, chunks: Sequence[ChunkRecord]) -> None:
        self._chunks = list(chunks)
        self.embeddings: dict[str, list[float]] = {}

    def count_pending_chunks(self) -> int:
        return sum(1 for chunk in self._chunks if chunk.id not in self.embeddings)

    def fetch_pending_chunks(self, limit: int) -> list[ChunkRecord]:
        pending = [chunk for chunk in self._chunks if chunk.id not in self.embeddings]
        return pending[:limit]

    def store_embeddings(self, rows, model: str) -> int:
        inserted = 0
        for row in rows:
            if row.chunk_id not in self.embeddings:
                self.embeddings[row.chunk_id] = list(row.embedding)
                inserted += 1
        return inserted


class FakeEmbeddingClient:
    def __init__(self, dimensions: int = 1536) -> None:
        self.dimensions = dimensions
        self.calls = 0

    def create_embeddings(self, texts: Sequence[str], model: str) -> list[list[float]]:
        self.calls += 1
        return [[float(index + 1)] * self.dimensions for index, _ in enumerate(texts)]


class FakeRateLimitError(Exception):
    status_code = 429


class RateLimitThenSuccessClient(FakeEmbeddingClient):
    def __init__(self) -> None:
        super().__init__()
        self.failures_remaining = 1

    def create_embeddings(self, texts: Sequence[str], model: str) -> list[list[float]]:
        self.calls += 1
        if self.failures_remaining > 0:
            self.failures_remaining -= 1
            raise FakeRateLimitError("slow down")
        return [[1.0] * self.dimensions for _ in texts]


def _make_chunks(count: int) -> list[ChunkRecord]:
    return [
        ChunkRecord(id=str(uuid4()), content=f"Chunk {index} content")
        for index in range(count)
    ]


def test_embedding_dimensions_match(caplog: pytest.LogCaptureFixture) -> None:
    repository = FakeRepository(_make_chunks(3))
    client = FakeEmbeddingClient(dimensions=1536)
    processor = EmbeddingBatchProcessor(repository=repository, client=client)

    with caplog.at_level("INFO"):
        embedded = processor.run(batch_size=2)

    assert embedded == 3
    assert len(repository.embeddings) == 3
    assert all(len(embedding) == 1536 for embedding in repository.embeddings.values())
    assert "Embedded 2/3 chunks" in caplog.text
    assert "Embedded 3/3 chunks" in caplog.text


def test_embedding_processor_is_idempotent_on_rerun() -> None:
    repository = FakeRepository(_make_chunks(2))
    client = FakeEmbeddingClient(dimensions=1536)
    processor = EmbeddingBatchProcessor(repository=repository, client=client)

    first_run = processor.run(batch_size=100)
    second_run = processor.run(batch_size=100)

    assert first_run == 2
    assert second_run == 0
    assert len(repository.embeddings) == 2
    assert client.calls == 1


def test_embedding_processor_retries_after_rate_limit() -> None:
    repository = FakeRepository(_make_chunks(1))
    client = RateLimitThenSuccessClient()
    sleeps: list[float] = []
    processor = EmbeddingBatchProcessor(
        repository=repository,
        client=client,
        sleep=sleeps.append,
        base_delay_seconds=0.25,
        max_retries=3,
    )

    embedded = processor.run(batch_size=1)

    assert embedded == 1
    assert len(repository.embeddings) == 1
    assert client.calls == 2
    assert cast(list[float], sleeps) == [0.25]


def test_embed_chunks_main_raises_clear_error_for_invalid_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    AuthenticationError = type("AuthenticationError", (Exception,), {})

    class FakeProcessor:
        def run(self, batch_size: int) -> int:
            raise AuthenticationError("invalid key")

    monkeypatch.setattr(embed_chunks, "parse_args", lambda: type("Args", (), {
        "batch_size": 2,
        "max_retries": 5,
        "base_delay_seconds": 1.0,
    })())
    monkeypatch.setattr(embed_chunks, "get_settings", lambda: type("Settings", (), {"openai_api_key": "sk-test"})())
    monkeypatch.setattr(embed_chunks, "EmbeddingBatchProcessor", lambda **kwargs: FakeProcessor())
    monkeypatch.setattr(embed_chunks, "PostgresChunkEmbeddingRepository", lambda session_factory: object())
    monkeypatch.setattr(embed_chunks, "get_session_factory", lambda: object())
    monkeypatch.setattr(embed_chunks, "OpenAIEmbeddingClient", lambda api_key: object())

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY is invalid"):
        embed_chunks.main()


def test_embed_chunks_main_raises_clear_error_for_openai_connectivity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    APIConnectionError = type("APIConnectionError", (Exception,), {})

    class FakeProcessor:
        def run(self, batch_size: int) -> int:
            raise APIConnectionError("network down")

    monkeypatch.setattr(embed_chunks, "parse_args", lambda: type("Args", (), {
        "batch_size": 2,
        "max_retries": 5,
        "base_delay_seconds": 1.0,
    })())
    monkeypatch.setattr(embed_chunks, "get_settings", lambda: type("Settings", (), {"openai_api_key": "sk-test"})())
    monkeypatch.setattr(embed_chunks, "EmbeddingBatchProcessor", lambda **kwargs: FakeProcessor())
    monkeypatch.setattr(embed_chunks, "PostgresChunkEmbeddingRepository", lambda session_factory: object())
    monkeypatch.setattr(embed_chunks, "get_session_factory", lambda: object())
    monkeypatch.setattr(embed_chunks, "OpenAIEmbeddingClient", lambda api_key: object())

    with pytest.raises(RuntimeError, match="OpenAI API connection failed"):
        embed_chunks.main()
