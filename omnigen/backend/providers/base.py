from abc import ABC, abstractmethod
from typing import AsyncIterator

from backend.models.chat_request import ChatRequest
from backend.models.model_info import ModelInfo
from backend.core.events import StreamEvent


class BaseProvider(ABC):

    id: str
    name: str
    capabilities: dict

    @abstractmethod
    async def stream_chat(
        self,
        request: ChatRequest,
    ) -> AsyncIterator[StreamEvent]:
        pass

    @abstractmethod
    async def complete(
        self,
        request: ChatRequest,
    ):
        pass

    @abstractmethod
    async def list_models(
        self,
    ) -> list[ModelInfo]:
        pass

    @abstractmethod
    async def health(self) -> bool:
        pass