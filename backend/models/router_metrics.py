from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class RouterMetrics:
    """
    Stores the result of a single routing decision.

    One instance = One model invocation.
    """

    # Request Info

    request_id: str

    timestamp: datetime = field(
        default_factory=datetime.utcnow
    )

    # Selected Provider

    provider: str = ""

    model: str = ""

    # Request Analysis

    task: str = ""

    capability: str = ""

    # Timing

    latency_ms: float = 0.0

    # Result

    success: bool = False

    error: Optional[str] = None

    # Token Usage (future)

    prompt_tokens: int = 0

    completion_tokens: int = 0

    total_tokens: int = 0

    # Cost (future)

    estimated_cost: float = 0.0

    # Router

    score: int = 0

    fallback_used: bool = False