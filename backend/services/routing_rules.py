from backend.models.task_type import TaskType


class RoutingRules:

    RULES = {

    TaskType.CODE: {
        "providers": [
            "ollama",
            "gemini",
        ],
        "capability": "code",
    },

    TaskType.CHAT: {
        "providers": [
            "gemini",
            "ollama",
        ],
        "capability": "chat",
    },

    TaskType.REASONING: {
        "providers": [
            "gemini",
            "ollama",
        ],
        "capability": "reasoning",
    },

    TaskType.VISION: {
        "providers": [
            "gemini",
        ],
        "capability": "vision",
    },

    TaskType.RAG: {
        "providers": [
            "ollama",
            "gemini",
        ],
        "capability": "chat",
    },

    TaskType.AGENT: {
        "providers": [
            "gemini",
        ],
        "capability": "reasoning",
    },

    TaskType.EMBEDDING: {
        "providers": [
            "ollama",
        ],
        "capability": "embedding",
    },
}
    @classmethod
    def get(cls, task: TaskType):

        return cls.RULES[task]