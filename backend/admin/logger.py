from typing import Optional

from sqlalchemy.orm import Session

from backend.admin.models import RequestLog

PREVIEW_LEN = 120
ERROR_DETAIL_MAX_LEN = 2000


def log_request(
    db: Session,
    *,
    user_id: Optional[int],
    task_type: str,
    status: str,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    latency_ms: Optional[float] = None,
    error_detail: Optional[str] = None,
    prompt: Optional[str] = None,
) -> None:
    entry = RequestLog(
        user_id=user_id,
        task_type=task_type,
        provider=provider,
        model=model,
        status=status,
        latency_ms=latency_ms,
        error_detail=error_detail[:ERROR_DETAIL_MAX_LEN] if error_detail else None,
        prompt_preview=prompt[:PREVIEW_LEN] if prompt else None,
    )
    db.add(entry)
    db.commit()