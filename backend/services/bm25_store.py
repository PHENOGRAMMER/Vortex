from collections import Counter

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    BM25Okapi = None


class BM25Store:

    def __init__(self):

        self.metadata = []

        self.documents = []

        self.tokenized = []

        self.index = None

    ####################################################################
    # Build
    ####################################################################

    def build(
        self,
        metadata: list[dict],
    ):

        self.metadata = metadata

        self.documents = [

            item["text"]

            for item in metadata

        ]

        self.tokenized = [

            text.lower().split()

            for text in self.documents

        ]

        if self.tokenized and BM25Okapi is not None:

            self.index = BM25Okapi(
                self.tokenized
            )

        else:

            self.index = None

    ####################################################################
    # Search
    ####################################################################

    def search(
        self,
        query: str,
        top_k: int = 20,
    ) -> list[dict]:

        if not self.tokenized:
            return []

        query_terms = query.lower().split()

        if self.index is None:
            query_counts = Counter(query_terms)
            scores = [
                sum(Counter(tokens)[term] * weight for term, weight in query_counts.items())
                for tokens in self.tokenized
            ]
        else:
            scores = self.index.get_scores(query_terms)

        ranked = sorted(

            zip(
                self.metadata,
                scores,
            ),

            key=lambda x: x[1],

            reverse=True,

        )

        results = []

        for item, score in ranked[:top_k]:

            results.append(
                {
                    "score": float(score),
                    **item,
                }
            )

        return results

    ####################################################################
    # Reset
    ####################################################################

    def reset(self):

        self.metadata = []

        self.documents = []

        self.tokenized = []

        self.index = None
