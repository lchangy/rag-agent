from services.chunking import chunk_text, get_token_encoder


def test_chunker_splits_long_text_into_multiple_chunks() -> None:
    text = " ".join(["lorem"] * 4000)

    chunks = chunk_text(text)

    assert len(chunks) > 1
    assert chunks[0]["chunk_index"] == 0
    assert all(chunk["token_count"] <= 512 for chunk in chunks)
    assert all(chunk["start_char"] < chunk["end_char"] for chunk in chunks)


def test_chunker_preserves_overlap_between_adjacent_chunks() -> None:
    text = " ".join(["lorem"] * 4000)
    encoder = get_token_encoder()

    chunks = chunk_text(text)

    first_chunk_tokens = encoder.encode(chunks[0]["content"])
    second_chunk_tokens = encoder.encode(chunks[1]["content"])

    assert first_chunk_tokens[-50:] == second_chunk_tokens[:50]
