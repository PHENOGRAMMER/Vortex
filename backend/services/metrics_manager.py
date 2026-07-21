from collections import deque
from statistics import mean
from typing import Optional

from backend.models.router_metrics import RouterMetrics


class MetricsManager:
    """
    Stores router metrics in memory.

    Later this can be swapped with SQLite,
    PostgreSQL, Redis, etc.
    """

    MAX_HISTORY = 1000

    _history = deque(maxlen=MAX_HISTORY)

    @classmethod
    def add(
        cls,
        metric: RouterMetrics,
    ):

        cls._history.append(metric)

    @classmethod
    def history(cls):

        return list(cls._history)

    @classmethod
    def clear(cls):

        cls._history.clear()

    @classmethod
    def total_requests(cls):

        return len(cls._history)

    @classmethod
    def successful_requests(cls):

        return sum(
            1
            for m in cls._history
            if m.success
        )

    @classmethod
    def failed_requests(cls):

        return sum(
            1
            for m in cls._history
            if not m.success
        )

    @classmethod
    def average_latency(cls):

        values = [
            m.latency_ms
            for m in cls._history
            if m.success
        ]

        if not values:
            return 0

        return round(
            mean(values),
            2,
        )

    @classmethod
    def provider_stats(
        cls,
        provider: str,
    ):

        metrics = [

            m

            for m in cls._history

            if m.provider == provider

        ]

        if not metrics:

            return {

                "requests": 0,

                "success": 0,

                "failures": 0,

                "avg_latency": 0,

            }

        success = sum(
            1
            for m in metrics
            if m.success
        )

        failures = len(metrics) - success

        latency = [

            m.latency_ms

            for m in metrics

            if m.success

        ]

        return {

            "requests": len(metrics),

            "success": success,

            "failures": failures,

            "avg_latency": round(
                mean(latency),
                2,
            ) if latency else 0,

        }