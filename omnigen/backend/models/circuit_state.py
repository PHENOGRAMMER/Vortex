from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CircuitState:

    provider: str

    # CLOSED | OPEN | HALF_OPEN
    state: str = "CLOSED"

    consecutive_failures: int = 0

    last_failure: Optional[datetime] = None

    opened_at: Optional[datetime] = None

    retry_after: Optional[datetime] = None