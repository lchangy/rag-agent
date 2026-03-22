import codecs
from functools import lru_cache
from typing import TypedDict

import tiktoken

TOKEN_ENCODING_NAME = "cl100k_base"


class ChunkSpec(TypedDict):
    chunk_index: int
    content: str
    start_char: int
    end_char: int
    token_count: int


@lru_cache
def get_token_encoder() -> tiktoken.Encoding:
    return tiktoken.get_encoding(TOKEN_ENCODING_NAME)


def _build_token_char_offsets(token_ids: list[int]) -> list[int]:
    encoder = get_token_encoder()
    decoder = codecs.getincrementaldecoder("utf-8")()
    offsets = [0]
    total_chars = 0

    for token_id in token_ids:
        total_chars += len(decoder.decode(encoder.decode_single_token_bytes(token_id), final=False))
        offsets.append(total_chars)

    remaining = decoder.decode(b"", final=True)
    if remaining:
        offsets[-1] += len(remaining)

    return offsets


def chunk_text(text: str, chunk_size: int = 512, overlap_tokens: int = 50) -> list[ChunkSpec]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap_tokens < 0 or overlap_tokens >= chunk_size:
        raise ValueError("overlap_tokens must be between 0 and chunk_size - 1")

    encoder = get_token_encoder()
    token_ids = encoder.encode(text)
    if not token_ids:
        return []

    offsets = _build_token_char_offsets(token_ids)
    step = chunk_size - overlap_tokens
    chunks: list[ChunkSpec] = []

    for chunk_index, start_token in enumerate(range(0, len(token_ids), step)):
        end_token = min(start_token + chunk_size, len(token_ids))
        start_char = min(offsets[start_token], len(text))
        end_char = min(offsets[end_token], len(text))
        if end_char < start_char:
            raise ValueError("invalid token offsets")
        chunks.append(
            {
                "chunk_index": chunk_index,
                "content": text[start_char:end_char],
                "start_char": start_char,
                "end_char": end_char,
                "token_count": end_token - start_token,
            }
        )
        if end_token == len(token_ids):
            break

    return chunks
