from backend.providers.registry import registry


class ProviderFactory:

    @staticmethod
    def get(provider_name: str):

        return registry.get(provider_name)

    @staticmethod
    def list():

        return list(registry.providers.values())