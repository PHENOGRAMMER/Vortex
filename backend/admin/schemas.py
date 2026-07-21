from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class StatsOut(BaseModel):
    total_requests: int
    error_count: int
    error_rate: float
    avg_latency_ms: Optional[float]
    total_users: int
    requests_by_provider: dict[str, int]
    requests_by_task_type: dict[str, int]
    requests_by_status: dict[str, int]


class LogOut(BaseModel):
    id: int
    user_id: Optional[int]
    task_type: str
    provider: Optional[str]
    model: Optional[str]
    status: str
    latency_ms: Optional[float]
    error_detail: Optional[str]
    prompt_preview: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedLogs(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[LogOut]