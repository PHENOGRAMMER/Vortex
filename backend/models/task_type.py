from enum import Enum


class TaskType(str, Enum):

    CHAT = "chat"

    CODE = "code"

    REASONING = "reasoning"

    VISION = "vision"

    RAG = "rag"

    AGENT = "agent"

    EMBEDDING = "embedding"