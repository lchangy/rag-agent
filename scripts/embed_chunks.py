from __future__ import annotations

import argparse
import logging

from app.config import get_settings
from core.db import get_session_factory
from core.embeddings import (
    EmbeddingBatchProcessor,
    OpenAIEmbeddingClient,
    PostgresChunkEmbeddingRepository,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate embeddings for unembedded chunks.")
    parser.add_argument("--batch-size", type=int, default=100, help="Number of chunks to embed per batch.")
    parser.add_argument("--max-retries", type=int, default=5, help="Maximum rate-limit retry attempts.")
    parser.add_argument(
        "--base-delay-seconds",
        type=float,
        default=1.0,
        help="Base delay used for exponential backoff on rate-limit retries.",
    )
    return parser.parse_args()


def _format_runtime_error(exc: Exception) -> RuntimeError:
    error_name = exc.__class__.__name__
    if error_name == "AuthenticationError":
        return RuntimeError(
            "OPENAI_API_KEY is invalid. Update the environment with a valid OpenAI Platform API key."
        )
    if error_name in {"APIConnectionError", "APITimeoutError"}:
        return RuntimeError(
            "OpenAI API connection failed. Check outbound network access and retry with a valid key."
        )
    return RuntimeError(str(exc))


def main() -> int:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required to generate chunk embeddings.")

    processor = EmbeddingBatchProcessor(
        repository=PostgresChunkEmbeddingRepository(get_session_factory()),
        client=OpenAIEmbeddingClient(api_key=settings.openai_api_key),
        max_retries=args.max_retries,
        base_delay_seconds=args.base_delay_seconds,
    )
    try:
        processor.run(batch_size=args.batch_size)
    except Exception as exc:  # noqa: BLE001
        raise _format_runtime_error(exc) from exc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
