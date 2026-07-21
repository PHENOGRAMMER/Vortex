from backend.services.text_chunker import TextChunker


def test_chunker_splits_long_unpunctuated_pdf_text_without_looping():
    text = "table-cell " * 500

    chunks = TextChunker.chunk(text, chunk_size=80, overlap_sentences=2)

    assert chunks
    assert all(chunk.text.strip() for chunk in chunks)
    assert all(len(chunk.text) <= 80 for chunk in chunks)


def test_chunker_splits_single_unbroken_token_without_looping():
    chunks = TextChunker.chunk("x" * 250, chunk_size=80, overlap_sentences=2)

    assert [len(chunk.text) for chunk in chunks] == [80, 80, 80, 10]
