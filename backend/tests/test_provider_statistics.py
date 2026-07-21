from datetime import UTC, datetime
from uuid import uuid4

from backend.models.router_metrics import RouterMetrics
from backend.services.metrics_manager import MetricsManager
from backend.services.provider_statistics import (
    ProviderStatisticsService,
)


def metric(

    provider,

    latency,

    success,

):

    return RouterMetrics(

        request_id=str(uuid4()),

        timestamp=datetime.now(UTC),

        provider=provider,

        model="demo",

        task="chat",

        capability="chat",

        latency_ms=latency,

        success=success,

    )


def main():

    MetricsManager.clear()

    MetricsManager.add(

        metric(

            "Ollama",

            950,

            True,

        )

    )

    MetricsManager.add(

        metric(

            "Ollama",

            870,

            True,

        )

    )

    MetricsManager.add(

        metric(

            "Ollama",

            0,

            False,

        )

    )

    MetricsManager.add(

        metric(

            "Google Gemini",

            1320,

            True,

        )

    )

    MetricsManager.add(

        metric(

            "Google Gemini",

            1180,

            True,

        )

    )

    print()

    print("=" * 70)

    print("OLLAMA")

    print("=" * 70)

    print(

        ProviderStatisticsService.get(

            "Ollama"

        )

    )

    print()

    print("=" * 70)

    print("GEMINI")

    print("=" * 70)

    print(

        ProviderStatisticsService.get(

            "Google Gemini"

        )

    )


if __name__ == "__main__":

    main()