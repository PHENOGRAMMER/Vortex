from backend.models.router_decision import RouterDecision


class DecisionManager:

    _last_decision: RouterDecision | None = None

    _history: list[RouterDecision] = []

    MAX_HISTORY = 100

    @classmethod
    def save(
        cls,
        decision: RouterDecision,
    ):

        cls._last_decision = decision

        cls._history.append(decision)

        if len(cls._history) > cls.MAX_HISTORY:

            cls._history.pop(0)

    @classmethod
    def last(cls):

        return cls._last_decision

    @classmethod
    def history(cls):

        return cls._history