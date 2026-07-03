from backend.models.provider_statistics import ProviderStatistics
from backend.services.metrics_manager import MetricsManager


class ProviderStatisticsService:

    @classmethod
    def get(
        cls,
        provider: str,
    ) -> ProviderStatistics:

        history = [

            metric

            for metric in MetricsManager.history()

            if metric.provider == provider

        ]

        stats = ProviderStatistics(
            provider=provider
        )

        if not history:
            return stats

        stats.requests = len(history)

        total_latency = 0

        successful_latency = 0

        last_failure = None

        consecutive_failures = 0

        for metric in history:

            if metric.success:

                stats.successes += 1

                total_latency += metric.latency_ms

                successful_latency += 1

                consecutive_failures = 0

            else:

                stats.failures += 1

                last_failure = metric.timestamp

                consecutive_failures += 1

        if successful_latency:

            stats.average_latency = round(

                total_latency /

                successful_latency,

                2,

            )

        stats.success_rate = round(

            (

                stats.successes /

                stats.requests

            ) * 100,

            2,

        )

        stats.last_failure = last_failure

        stats.consecutive_failures = consecutive_failures

        return stats