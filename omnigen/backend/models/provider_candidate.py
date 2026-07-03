from dataclasses import dataclass


@dataclass
class ProviderCandidate:

    provider: object

    model: object

    score: int = 0

    reasons: list[str] | None = None