from dataclasses import dataclass
from datetime import datetime

from backend.models.provider_score import ProviderScore
from backend.models.original_selection import OriginalSelection


@dataclass
class RouterDecision:

    timestamp: datetime

    task: str

    selected_provider: str

    selected_model: str

    selected_score: int

    original_selection: OriginalSelection

    alternatives: list[ProviderScore]

    fallback_used: bool

    latency_ms: float