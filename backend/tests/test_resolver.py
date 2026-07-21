import asyncio

from backend.models.chat_request import ChatRequest
from backend.models.chat_request import ChatMessage
from backend.services.provider_resolver import ProviderResolver


async def main():

    request = ChatRequest(
        provider="",
        model="",
        messages=[
            ChatMessage(
                role="user",
                content="Write a FastAPI CRUD API"
            )
        ],
    )

    providers = await ProviderResolver.resolve(request)

    print()

    for candidate in providers:
            print("----------------------")
            print("Provider :", candidate.provider.name)
            print("Model    :", candidate.model.id)
            print("Speed    :", candidate.model.speed)
            print("Local    :", candidate.model.local)  
            print("Cost     :", candidate.model.cost)
            print()


asyncio.run(main())