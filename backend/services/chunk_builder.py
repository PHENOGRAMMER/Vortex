from typing import List


class ChunkBuilder:

    def __init__(
        self,
        chunk_size: int,
        overlap_sentences: int = 1,
    ):
        self.chunk_size = chunk_size
        self.overlap_sentences = overlap_sentences

    def build(
        self,
        sentences: List[str],
    ) -> List[str]:

        if not sentences:
            return []

        chunks = []

        start = 0

        while start < len(sentences):

            current = []
            current_length = 0

            end = start

            while end < len(sentences):

                sentence = sentences[end].strip()

                if not sentence:
                    end += 1
                    continue

                sentence_length = len(sentence)

                # Extremely long sentence -> own chunk
                if sentence_length > self.chunk_size:

                    if current:
                        break

                    chunks.append(sentence)

                    end += 1

                    start = end

                    break

                additional = sentence_length

                if current:
                    additional += 1  # space

                if current_length + additional > self.chunk_size:
                    break

                current.append(sentence)

                current_length += additional

                end += 1

            if current:
                chunks.append(" ".join(current))

                # Avoid infinite loop
                if end <= start:
                    start += 1
                else:
                    start = max(
                        end - self.overlap_sentences,
                        start + 1,
                    )

        return chunks