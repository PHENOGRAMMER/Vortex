import re
from dataclasses import dataclass


@dataclass
class TextChunk:
    index: int
    text: str
    start: int
    end: int


class TextChunker:

    ####################################################################
    # Heading Detection
    ####################################################################

    @staticmethod
    def is_heading(text: str) -> bool:

        text = text.strip()

        if not text:
            return False

        # Very short line
        if len(text) <= 80:

            # No period at end
            if not text.endswith("."):

                # Mostly title case
                words = text.split()

                if len(words) <= 10:
                    return True

        # Numbered heading

        if re.match(r"^\d+(\.\d+)*", text):
            return True

        # A. Introduction

        if re.match(r"^[A-Z]\.", text):
            return True

        # Roman numerals

        if re.match(r"^[IVX]+\.", text):
            return True

        return False

    ####################################################################
    # Paragraph Split
    ####################################################################

    @staticmethod
    def split_paragraphs(text):

        paragraphs = []

        current = []

        for line in text.splitlines():

            line = line.strip()

            if not line:

                if current:
                    paragraphs.append(" ".join(current))
                    current = []

                continue

            current.append(line)

        if current:
            paragraphs.append(" ".join(current))

        return paragraphs

    ####################################################################
    # Sentence Split
    ####################################################################

    @staticmethod
    def split_sentences(text):

        return [

            s.strip()

            for s in re.split(
                r'(?<=[.!?])\s+',
                text
            )

            if s.strip()

        ]

    ####################################################################
    # Build Semantic Sections
    ####################################################################

    @staticmethod
    def build_sections(paragraphs):

        sections = []

        current = ""

        for para in paragraphs:

            if TextChunker.is_heading(para):

                if current:

                    sections.append(current.strip())

                current = para

            else:

                if current:

                    current += "\n\n" + para

                else:

                    current = para

        if current:

            sections.append(current.strip())

        return sections

    ####################################################################
    # Split Large Section
    ####################################################################

    @staticmethod
    def split_large_section(
        section,
        chunk_size,
        overlap_sentences,
    ):

        sentences = TextChunker.split_sentences(section)

        # PDF/DOCX extraction can produce a "sentence" with no punctuation
        # (for example a whole page of table data).  The old loop never
        # advanced when the first sentence was larger than ``chunk_size``.
        # Split oversized input up front so every iteration makes progress.
        normalized_sentences = []
        for sentence in sentences:
            if len(sentence) <= chunk_size:
                normalized_sentences.append(sentence)
                continue

            words = sentence.split()
            if not words:
                continue
            piece = ""
            for word in words:
                # A single unbroken token (such as an URL) still needs a hard
                # split; otherwise it could recreate the non-progress case.
                if len(word) > chunk_size:
                    if piece:
                        normalized_sentences.append(piece)
                        piece = ""
                    normalized_sentences.extend(
                        word[offset:offset + chunk_size]
                        for offset in range(0, len(word), chunk_size)
                    )
                elif not piece:
                    piece = word
                elif len(piece) + 1 + len(word) <= chunk_size:
                    piece += " " + word
                else:
                    normalized_sentences.append(piece)
                    piece = word
            if piece:
                normalized_sentences.append(piece)

        sentences = normalized_sentences

        chunks = []

        current = []

        current_size = 0

        i = 0

        while i < len(sentences):

            sentence = sentences[i]

            length = len(sentence)

            if current_size + length <= chunk_size:

                current.append(sentence)

                current_size += length + 1

                i += 1

                continue

            # ``current`` is guaranteed to be non-empty after normalizing
            # oversized sentences above.
            chunks.append(" ".join(current))

            overlap = current[-overlap_sentences:]
            overlap_size = sum(len(item) for item in overlap) + max(0, len(overlap) - 1)

            # Do not retain an overlap that leaves no room for the sentence
            # currently being considered.  Without this guard, two adjacent
            # near-limit fragments repeatedly emit the same overlap.
            if overlap_size + (1 if overlap else 0) + length > chunk_size:
                current = []
                current_size = 0
            else:
                current = overlap.copy()
                current_size = overlap_size

        if current:

            chunks.append(" ".join(current))

        return chunks

    ####################################################################
    # Main Chunk Function
    ####################################################################

    @staticmethod
    def chunk(
        text,
        chunk_size=800,
        overlap_sentences=2,
    ):

        paragraphs = TextChunker.split_paragraphs(text)

        sections = TextChunker.build_sections(paragraphs)

        chunks = []

        cursor = 0

        index = 0

        for section in sections:

            if len(section) <= chunk_size:

                chunks.append(

                    TextChunk(

                        index=index,

                        text=section,

                        start=cursor,

                        end=cursor + len(section),

                    )

                )

                cursor += len(section)

                index += 1

                continue

            pieces = TextChunker.split_large_section(

                section,

                chunk_size,

                overlap_sentences,

            )

            for piece in pieces:

                chunks.append(

                    TextChunk(

                        index=index,

                        text=piece,

                        start=cursor,

                        end=cursor + len(piece),

                    )

                )

                cursor += len(piece)

                index += 1

        return chunks
