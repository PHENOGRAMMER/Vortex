from enum import Enum


class EventType(str, Enum):
    TOKEN = "token"
    DONE = "done"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    TOOL_START = "tool_start"
    TOOL_RESULT = "tool_result"
    IMAGE = "image"
    RAG = "rag"
    STATUS = "status"