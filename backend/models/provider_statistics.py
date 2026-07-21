from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ProviderStatistics:

    provider: str

    requests: int = 0

    successes: int = 0

    failures: int = 0

    average_latency: float = 0.0

    success_rate: float = 0.0

    last_failure: Optional[datetime] = None

    consecutive_failures: int = 0