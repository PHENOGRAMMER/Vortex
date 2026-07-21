import asyncio

from backend.providers.factory import ProviderFactory

from backend.services.health_manager import HealthManager


async def main():

    for provider_name in [

        "mock",

        "ollama",

        "gemini",

    ]:

        provider = ProviderFactory.get(provider_name)

        healthy = await HealthManager.is_healthy(provider)

        print()

        print(provider.name)

        print("Healthy:", healthy)

    print()

    print(HealthManager.get_status())


asyncio.run(main())