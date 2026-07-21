from typing import Optional

from pydantic import BaseModel

from dataclasses import dataclass

@dataclass
class ModelInfo:

    id: str

    name: str

    provider: str

    capabilities: list[str]

    context_length: int

    vision: bool

    tool_calling: bool

    embeddings: bool

    local: bool

    speed: str

    priority: int

    cost: float