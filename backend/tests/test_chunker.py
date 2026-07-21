from backend.services.text_chunker import TextChunker


text = """

Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet.
Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet.
Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet.
Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet.
Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet.

""" * 25


chunks = TextChunker.chunk(
    text,
    chunk_size=200,
)

print()

print("=" * 70)

print(f"Chunks: {len(chunks)}")

for chunk in chunks:

    print()

    print("=" * 70)

    print(chunk.index)

    print(len(chunk.text))

    print(chunk.text[:150])