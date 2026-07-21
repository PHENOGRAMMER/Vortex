from fastapi import APIRouter

from backend.services.metrics_manager import MetricsManager
from backend.services.decision_manager import DecisionManager

router = APIRouter(
    prefix="/api/router",
    tags=["Router"],
)


@router.get("/stats")
def router_stats():

    return MetricsManager.get_stats()


@router.get("/last")
def last_decision():

    decision = DecisionManager.last()

    if decision is None:

        return {

            "message": "No routing decisions yet."

        }

    return decision


@router.get("/history")
def decision_history():

    return DecisionManager.history()