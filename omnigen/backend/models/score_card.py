from dataclasses import dataclass


@dataclass
class ScoreCard:

    provider: str

    model: str

    score: int

    reasons: list[str]