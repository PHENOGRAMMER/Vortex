from backend.providers.factory import ProviderFactory

from backend.services.request_analyzer import RequestAnalyzer
from backend.services.routing_rules import RoutingRules
from backend.services.model_scorer import ModelScorer

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

        for provider_id in providers:

            provider = ProviderFactory.get(provider_id)

            if provider is None:
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

        scored_candidates = []

        for candidate in candidates:

            scorecard = await ModelScorer.score(

                candidate,

                request,

            )

            scored_candidates.append(

                (

                    candidate,

                    scorecard,

                )

            )

        scored_candidates.sort(

            key=lambda item: item[1].score,

            reverse=True,

        )

        print()

        print("=" * 80)
        print("MODEL SCORES")
        print("=" * 80)

        for _, score in scored_candidates:

            print(

                f"{score.provider:<20}"

                f"{score.model:<30}"

                f"{score.score}"

            )

            for reason in score.reasons:

                print(f"   • {reason}")

            print()

        print("=" * 80)

        return [

            candidate

            for candidate, _ in scored_candidates

        ]