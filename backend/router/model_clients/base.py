from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ModelResponse:
    content: Any
    provider: str
    model: str
    latency_ms: float
    raw: Optional[dict] = None


class ModelUnavailableError(Exception):
    """Raised when a provider errors out, is rate-limited, or times out.

    The task router catches this and falls through to the next provider
    in the chain, so a single overloaded/free-tier-limited model never
    takes the whole system down.
    """


class BaseClient(ABC):
    provider_name: str

    @abstractmethod
    async def chat(self, messages: list[dict], model: Optional[str] = None, **kwargs) -> ModelResponse:
        ...
