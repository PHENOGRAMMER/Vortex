from backend.models.chat_request import ChatRequest
from backend.models.task_type import TaskType


class RequestAnalyzer:

    CODE_KEYWORDS = {
        "python",
        "java",
        "javascript",
        "typescript",
        "cpp",
        "c++",
        "c#",
        "html",
        "css",
        "sql",
        "react",
        "vue",
        "angular",
        "fastapi",
        "flask",
        "django",
        "node",
        "express",
        "api",
        "algorithm",
        "function",
        "class",
        "code",
        "bug",
        "debug",
        "fix",
        "program",
        "implement",
        "compile",
        "leetcode",
        "binary tree",
    }

    RAG_KEYWORDS = {
        "document",
        "pdf",
        "file",
        "upload",
        "knowledge base",
        "rag",
        "summarize this document",
    }

    REASONING_KEYWORDS = {
        "explain",
        "why",
        "how",
        "analyze",
        "compare",
        "reason",
        "advantages",
        "disadvantages",
        "pros",
        "cons",
    }

    @classmethod
    def analyze(
        cls,
        request: ChatRequest,
    ) -> TaskType:

        if not request.messages:
            return TaskType.CHAT

        last_message = request.messages[-1]

        text = last_message.content.lower()

        # -------- Code --------

        for keyword in cls.CODE_KEYWORDS:

            if keyword in text:
                return TaskType.CODE

        # -------- RAG --------

        for keyword in cls.RAG_KEYWORDS:

            if keyword in text:
                return TaskType.RAG

        # -------- Reasoning --------

        for keyword in cls.REASONING_KEYWORDS:

            if keyword in text:
                return TaskType.REASONING

        # -------- Vision --------

        if getattr(request, "images", None):
            return TaskType.VISION

        # -------- Default --------

        return TaskType.CHAT