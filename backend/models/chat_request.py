from typing import Any

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):

    # Optional now - router will fill these
    provider: str | None = None

    model: str | None = None

    messages: list[ChatMessage]

    temperature: float = 0.7

    max_tokens: int | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)