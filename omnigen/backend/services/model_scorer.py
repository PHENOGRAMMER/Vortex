from backend.models.provider_candidate import ProviderCandidate
from backend.models.chat_request import ChatRequest
from backend.models.score_card import ScoreCard

from backend.services.request_analyzer import RequestAnalyzer
from backend.services.routing_rules import RoutingRules
from backend.services.health_manager import HealthManager


class ModelScorer:

    @staticmethod
    async def score(
        candidate: ProviderCandidate,
        request: ChatRequest,
    ) -> ScoreCard:

        score = 0

        reasons = []

        task = RequestAnalyzer.analyze(request)

        rule = RoutingRules.get(task)

        capability = rule["capability"]

        if capability in candidate.model.capabilities:

            score += 100

            reasons.append(
                f"Supports {capability}"
            )

        healthy = await HealthManager.is_healthy(
            candidate.provider
        )

        if healthy:

            score += 40

            reasons.append(
                "Healthy"
            )

        else:

            reasons.append(
                "Unhealthy"
            )
        
        if candidate.model.local:
            
            score+=20

            reasons.append(
                "Local model"
            )

        else:
            reasons.append(
                "Cloud model"
            )

        speed_scores = {
            "very_fast": 20,
            "fast": 15,
            "medium": 10,
            "slow": 5,
        }

        speed_bonus = speed_scores.get(
            candidate.model.speed,
            0,
        )

        score += speed_bonus

        reasons.append(
            f"Speed ({candidate.model.speed}) +{speed_bonus}"
        )

        if candidate.model.cost == 0:
            score += 15
            reasons.append(
                "Free model"
            )
        elif candidate.model.cost == 1:
            score += 10
            reasons.append(
                "Low cost"
            )
        elif candidate.model.cost == 2:
            score += 5
            reasons.append(
                "Medium cost"
            )
        else:
            reasons.append(
                "Expensive model"
            )

        return ScoreCard(
            provider=candidate.provider.name,
            model=candidate.model.id,
            score=score,
            reasons=reasons,
        )