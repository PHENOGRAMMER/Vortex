from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query

from backend.admin.models import RequestLog
from backend.admin.schemas import LogOut, PaginatedLogs, StatsOut
from backend.auth.dependencies import get_current_admin
from backend.auth.models import User
from backend.auth.schemas import UserOut
from backend.db.database import get_db

router = APIRouter()


@router.get("/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    total = db.query(RequestLog).count()
    errors = db.query(RequestLog).filter(RequestLog.status == "error").count()

    by_provider = dict(
        db.query(RequestLog.provider, func.count())
        .filter(RequestLog.provider.isnot(None))
        .group_by(RequestLog.provider)
        .all()
    )
    by_task = dict(
        db.query(RequestLog.task_type, func.count()).group_by(RequestLog.task_type).all()
    )
    by_status = dict(
        db.query(RequestLog.status, func.count()).group_by(RequestLog.status).all()
    )
    avg_latency = (
        db.query(func.avg(RequestLog.latency_ms)).filter(RequestLog.status == "success").scalar()
    )

    return StatsOut(
        total_requests=total,
        error_count=errors,
        error_rate=round(errors / total, 3) if total else 0.0,
        avg_latency_ms=round(avg_latency, 1) if avg_latency else None,
        total_users=db.query(User).count(),
        requests_by_provider=by_provider,
        requests_by_task_type=by_task,
        requests_by_status=by_status,
    )


@router.get("/logs", response_model=PaginatedLogs)
def logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status_filter: str | None = Query(None, alias="status"),
    provider: str | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    q = db.query(RequestLog)
    if status_filter:
        q = q.filter(RequestLog.status == status_filter)
    if provider:
        q = q.filter(RequestLog.provider == provider)

    total = q.count()
    rows = q.order_by(RequestLog.created_at.desc()).offset(offset).limit(limit).all()

    return PaginatedLogs(
        total=total,
        limit=limit,
        offset=offset,
        items=[LogOut.model_validate(r) for r in rows],
    )


@router.get("/users", response_model=list[UserOut])
def users(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    return db.query(User).order_by(User.created_at.asc()).all()