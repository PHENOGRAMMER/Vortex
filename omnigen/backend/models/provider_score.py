from dataclasses import dataclass


@dataclass
class ProviderScore:

    provider: str

    model: str

    score: int

    reasons: list[str]