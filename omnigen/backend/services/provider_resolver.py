from backend.providers.factory import ProviderFactory

from backend.services.request_analyzer import RequestAnalyzer
from backend.services.routing_rules import RoutingRules
from backend.services.model_scorer import ModelScorer
from backend.services.circuit_breaker import CircuitBreaker

from backend.models.chat_request import ChatRequest
from backend.models.provider_candidate import ProviderCandidate


class ProviderResolver:

    @classmethod
    async def resolve(
        cls,
        request: ChatRequest,
    ):

        task = RequestAnalyzer.analyze(request)

        rule = RoutingRules.get(task)

        providers = rule["providers"]

        capability = rule["capability"]

        candidates = []

        # ---------------------------------------------
        # Collect candidate models
        # ---------------------------------------------

        for provider_id in providers:

            provider = ProviderFactory.get(provider_id)

            if provider is None:
                continue

            if not CircuitBreaker.can_execute(
                provider.name,
            ):

                print()
                print("=" * 70)
                print("CIRCUIT OPEN")
                print(provider.name)
                print("=" * 70)

                continue

            try:

                models = await provider.list_models()

            except Exception as ex:

                print(
                    f"Unable to load models from {provider.name}"
                )

                print(ex)

                continue

            for model in models:

                if capability not in model.capabilities:
                    continue

                candidates.append(

                    ProviderCandidate(

                        provider=provider,

                        model=model,

                    )

                )

        # ---------------------------------------------
        # Score every candidate
        # ---------------------------------------------

        scored_candidates = []

        for candidate in candidates:

            scorecard = await ModelScorer.score(
                candidate,
                request,
            )

            candidate.score = scorecard.score
            candidate.reasons = scorecard.reasons

            scored_candidates.append(
                (
                    candidate,
                    scorecard,
                )
            )

        # ---------------------------------------------
        # Sort by score
        # ---------------------------------------------

        scored_candidates.sort(

            key=lambda item: item[1].score,

            reverse=True,

        )

        # ---------------------------------------------
        # Print scores
        # ---------------------------------------------

        print()
        print("=" * 80)
        print("MODEL SCORES")
        print("=" * 80)

        for candidate, scorecard in scored_candidates:

            print(
                f"{candidate.provider.name:<20}"
                f"{candidate.model.id:<30}"
                f"{candidate.score}"
            )

            for reason in candidate.reasons:

                print(f"   • {reason}")

            print()

        print("=" * 80)

        # ---------------------------------------------
        # Return ordered candidates
        # ---------------------------------------------

        return [

            candidate

            for candidate, _ in scored_candidates

        ]