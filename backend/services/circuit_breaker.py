from datetime import datetime, UTC, timedelta

from backend.models.circuit_state import CircuitState


class CircuitBreaker:
    """
    Simple in-memory circuit breaker.

    Future versions can persist this to Redis or a database.
    """

    FAILURE_THRESHOLD = 3

    RECOVERY_TIMEOUT = timedelta(seconds=120)

    _states: dict[str, CircuitState] = {}

    @classmethod
    def _get_state(
        cls,
        provider: str,
    ) -> CircuitState:

        if provider not in cls._states:

            cls._states[provider] = CircuitState(
                provider=provider
            )

        return cls._states[provider]

    @classmethod
    def can_execute(
        cls,
        provider: str,
    ) -> bool:

        state = cls._get_state(provider)

        now = datetime.now(UTC)

        if state.state == "CLOSED":
            return True

        if state.state == "OPEN":

            if (
                state.retry_after
                and now >= state.retry_after
            ):

                state.state = "HALF_OPEN"

                return True

            return False

        if state.state == "HALF_OPEN":
            return True

        return True

    @classmethod
    def record_success(
        cls,
        provider: str,
    ):

        state = cls._get_state(provider)

        state.state = "CLOSED"

        state.consecutive_failures = 0

        state.last_failure = None

        state.opened_at = None

        state.retry_after = None

    @classmethod
    def record_failure(
        cls,
        provider: str,
    ):

        state = cls._get_state(provider)

        now = datetime.now(UTC)

        state.consecutive_failures += 1

        state.last_failure = now

        if (
            state.consecutive_failures
            >= cls.FAILURE_THRESHOLD
        ):

            state.state = "OPEN"

            state.opened_at = now

            state.retry_after = (
                now + cls.RECOVERY_TIMEOUT
            )

    @classmethod
    def get_state(
        cls,
        provider: str,
    ) -> CircuitState:

        return cls._get_state(provider)

    @classmethod
    def reset(cls):

        cls._states.clear()