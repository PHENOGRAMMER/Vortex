from datetime import datetime
from pydantic import BaseModel, Field


class Document(BaseModel):
    id: str

    filename: str

    content: str

    metadata: dict = Field(default_factory=dict)

    uploaded_at: datetime = Field(default_factory=datetime.utcnow)