from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text

from backend.db.database import Base


class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    task_type = Column(String, index=True)          # chat | code | image | rag
    provider = Column(String, nullable=True, index=True)   # groq | ollama | gemini | huggingface
    model = Column(String, nullable=True)

    status = Column(String, index=True)              # "success" | "error"
    latency_ms = Column(Float, nullable=True)
    error_detail = Column(Text, nullable=True)

    # Only a short preview is stored, never the full prompt/response --
    # keeps the log table light and avoids hoarding sensitive user content.
    prompt_preview = Column(String, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)