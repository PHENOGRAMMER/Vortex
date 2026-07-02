from typing import Dict

from backend.providers.base import BaseProvider


class ProviderRegistry:

    def __init__(self):
        self.providers: Dict[str, BaseProvider] = {}

    def register(self, provider: BaseProvider):

        if provider.id in self.providers:
            raise ValueError(
                f"Provider '{provider.id}' already registered."
            )

        self.providers[provider.id] = provider

    def get(self, provider_id: str) -> BaseProvider:

        try:
            return self.providers[provider_id]

        except KeyError:
            raise ValueError(
                f"Provider '{provider_id}' not registered."
            )

    def list(self):

        return list(self.providers.values())


registry = ProviderRegistry()