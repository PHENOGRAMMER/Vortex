import asyncio
import time

from backend.providers.registry import registry


class HealthManager:
    """
    Keeps a cached health status for every provider.

    Providers are NOT pinged on every request.
    Health is refreshed every CACHE_TTL seconds.
    """

    CACHE_TTL = 30  # seconds

    _cache = {}

    _timestamps = {}

    @classmethod
    async def is_healthy(
        cls,
        provider,
    ) -> bool:

        provider_id = provider.id

        now = time.time()

        # ------------------------
        # Cached?
        # ------------------------

        if provider_id in cls._cache:

            age = now - cls._timestamps[provider_id]

            if age < cls.CACHE_TTL:

                return cls._cache[provider_id]

        # ------------------------
        # Refresh
        # ------------------------

        try:

            healthy = await provider.health()

        except Exception:

            healthy = False

        cls._cache[provider_id] = healthy

        cls._timestamps[provider_id] = now

        return healthy

    @classmethod
    def mark_unhealthy(cls, provider):

        cls._cache[provider.id] = False

        cls._timestamps[provider.id] = time.time()

    @classmethod
    async def refresh_all(cls):

        providers = registry.providers.values()

        await asyncio.gather(

            *[

                cls.is_healthy(provider)

                for provider in providers

            ]

        )

    @classmethod
    def get_status(cls):

        return dict(cls._cache)

    @classmethod
    def clear(cls):

        cls._cache.clear()

        cls._timestamps.clear()