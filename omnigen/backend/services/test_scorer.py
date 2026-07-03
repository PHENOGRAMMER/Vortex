import asyncio
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

from backend.models.chat_request import ChatMessage, ChatRequest
from backend.models.provider_candidate import ProviderCandidate
from backend.models.router_metrics import RouterMetrics
from backend.services.metrics_manager import MetricsManager
from backend.services.model_scorer import ModelScorer


def create_metric(provider, latency, success):

    return RouterMetrics(
        request_id=str(uuid4()),
        timestamp=datetime.now(UTC),
        provider=provider,
        model="demo-model",
        task="code",
        capability="code",
        latency_ms=latency,
        success=success,
    )


def build_candidate(provider_name):

    provider = SimpleNamespace(
        id=provider_name.lower().replace(" ", "_"),
        name=provider_name,
    )

    model = SimpleNamespace(
        id="demo-model",
        capabilities=["code"],
        local=True,
        speed="fast",
        cost=0,
    )

    return ProviderCandidate(
        provider=provider,
        model=model,
    )


def build_request():

    return ChatRequest(
        messages=[
            ChatMessage(
                role="user",
                content="Write a FastAPI login API",
            )
        ]
    )


async def main():

    MetricsManager.clear()

    # Simulate runtime history

    for _ in range(18):

        MetricsManager.add(
            create_metric(
                "Test Provider",
                850,
                True,
            )
        )

    for _ in range(2):

        MetricsManager.add(
            create_metric(
                "Test Provider",
                0,
                False,
            )
        )

    candidate = build_candidate(
        "Test Provider"
    )

    score = await ModelScorer.score(
        candidate,
        build_request(),
    )

    print()
    print("=" * 70)
    print("MODEL SCORE")
    print("=" * 70)

    print("Provider :", score.provider)
    print("Model    :", score.model)
    print("Score    :", score.score)

    print()

    print("Reasons")

    for reason in score.reasons:

        print(" •", reason)


if __name__ == "__main__":

    asyncio.run(main())