import asyncio

from backend.models.chat_request import ChatRequest
from backend.models.chat_request import ChatMessage

from backend.services.provider_resolver import ProviderResolver
from backend.services.model_scorer import ModelScorer


async def main():

    request = ChatRequest(

        messages=[
            ChatMessage(
                role="user",
                content="Write a FastAPI login API",
            )
        ]
    )

    providers = await ProviderResolver.resolve(
        request
    )

    for provider in providers:

        score = await ModelScorer.score(
            provider,
            request,
        )

        print()
        print(score)


asyncio.run(main())