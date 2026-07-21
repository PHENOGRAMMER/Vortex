from dataclasses import dataclass


@dataclass
class OriginalSelection:

    provider: str

    model: str

    score: int