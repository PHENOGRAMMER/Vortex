import asyncio

from backend.models.chat_request import ChatMessage
from backend.models.chat_request import ChatRequest

from omnigen.backend.services.model_selector import ModelSelector


async def main():

    request = ChatRequest(

        provider="",

        model="",

        messages=[

            ChatMessage(

                role="user",

                content="What is a Black hole",

            )

        ],

    )

    selection = await ModelSelector.select(
        request
    )

    print()

    print("Provider")

    print(selection.provider.name)

    print()

    print("Model")

    print(selection.model.name)


asyncio.run(main())