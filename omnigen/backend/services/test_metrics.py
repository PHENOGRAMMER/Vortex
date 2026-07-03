from datetime import datetime
from uuid import uuid4

from backend.models.router_metrics import RouterMetrics
from backend.services.metrics_manager import MetricsManager


def create_metric(
    provider: str,
    model: str,
    latency: float,
    success: bool,
):

    return RouterMetrics(

        request_id=str(uuid4()),

        timestamp=datetime.utcnow(),

        provider=provider,

        model=model,

        task="code",

        capability="code",

        latency_ms=latency,

        success=success,

        score=190 if provider == "Ollama" else 165,

        fallback_used=False,

    )


def main():

    MetricsManager.clear()

    MetricsManager.add(

        create_metric(

            "Ollama",

            "qwen2.5-coder:7b",

            1250,

            True,

        )

    )

    MetricsManager.add(

        create_metric(

            "Google Gemini",

            "gemini-2.5-flash",

            820,

            True,

        )

    )

    MetricsManager.add(

        create_metric(

            "Ollama",

            "qwen2.5-coder:7b",

            0,

            False,

        )

    )

    MetricsManager.add(

        create_metric(

            "Google Gemini",

            "gemini-2.5-pro",

            1400,

            True,

        )

    )

    print()

    print("=" * 70)

    print("GLOBAL STATS")

    print("=" * 70)

    print("Total Requests :", MetricsManager.total_requests())

    print("Successful     :", MetricsManager.successful_requests())

    print("Failed         :", MetricsManager.failed_requests())

    print("Avg Latency    :", MetricsManager.average_latency(), "ms")

    print()

    print("=" * 70)

    print("OLLAMA")

    print("=" * 70)

    print(

        MetricsManager.provider_stats(

            "Ollama"

        )

    )

    print()

    print("=" * 70)

    print("GEMINI")

    print("=" * 70)

    print(

        MetricsManager.provider_stats(

            "Google Gemini"

        )

    )

    print()

    print("=" * 70)

    print("HISTORY")

    print("=" * 70)

    for metric in MetricsManager.history():

        print(

            metric.provider,

            metric.model,

            metric.latency_ms,

            metric.success,

        )


if __name__ == "__main__":

    main()