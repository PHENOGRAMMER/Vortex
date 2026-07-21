from dataclasses import dataclass


@dataclass
class RetrievedChunk:

    score: float

    document_id: str

    filename: str

    chunk_id: str

    chunk_index: int

    text: str

    start: int

    end: int

    length: int

    section: str | None = None

    source_start_chunk: int | None = None

    source_end_chunk: int | None = None
