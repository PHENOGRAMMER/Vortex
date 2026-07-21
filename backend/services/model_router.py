from backend.providers.factory import ProviderFactory


class ModelRouter:

    @staticmethod
    def get_provider(provider_name: str):

        return ProviderFactory.get(provider_name)