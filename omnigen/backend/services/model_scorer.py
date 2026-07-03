from backend.models.chat_request import ChatRequest
from backend.models.provider_candidate import ProviderCandidate
from backend.models.score_card import ScoreCard

from backend.services.provider_statistics import ProviderStatisticsService
from backend.services.request_analyzer import RequestAnalyzer
from backend.services.routing_rules import RoutingRules


class ModelScorer:

    @staticmethod
    def _success_rate_bonus(success_rate: float) -> int:
        if success_rate >= 100:
            return 20
        if success_rate >= 95:
            return 18
        if success_rate >= 90:
            return 16
        if success_rate >= 80:
            return 12
        if success_rate >= 70:
            return 8
        return 3

    @staticmethod
    def _latency_bonus(latency_ms: float) -> int:
        if latency_ms < 500:
            return 20
        if latency_ms < 1000:
            return 18
        if latency_ms < 2000:
            return 15
        if latency_ms < 3000:
            return 10
        return 5

    @staticmethod
    def _reliability_bonus(consecutive_failures: int) -> int:
        if consecutive_failures <= 0:
            return 15
        if consecutive_failures == 1:
            return 10
        if consecutive_failures == 2:
            return 5
        return -30

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

        stats = ProviderStatisticsService.get(
            candidate.provider.name
        )

        success_bonus = ModelScorer._success_rate_bonus(
            stats.success_rate
        )
        score += success_bonus
        reasons.append(
            f"Success Rate ({stats.success_rate}%) +{success_bonus}"
        )

        latency_bonus = ModelScorer._latency_bonus(
            stats.average_latency
        )
        score += latency_bonus
        reasons.append(
            f"Latency ({stats.average_latency}ms) +{latency_bonus}"
        )

        reliability_bonus = ModelScorer._reliability_bonus(
            stats.consecutive_failures
        )
        score += reliability_bonus
        reasons.append(
            f"Reliability ({stats.consecutive_failures} consecutive failures) {reliability_bonus:+d}"
        )

        if candidate.model.local:

            score += 20

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