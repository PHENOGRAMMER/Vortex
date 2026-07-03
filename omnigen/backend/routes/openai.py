from fastapi import APIRouter
from uuid import uuid4
import time

from backend.models.chat_request import ChatRequest
from backend.models.chat_request import ChatMessage

from backend.models.openai_models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    OpenAIChoice,
    OpenAIMessage,
    OpenAIUsage,
)

from backend.services.chat_service import ChatService
from backend.providers.factory import ProviderFactory

router = APIRouter()

chat_service = ChatService()


@router.get("/models")
async def list_models():

    models = []

    for provider in ProviderFactory.list():

        try:

            provider_models = await provider.list_models()

            for model in provider_models:

                models.append(
                    {
                        "id": model.id,
                        "object": "model",
                        "created": 0,
                        "owned_by": provider.id,
                    }
                )

        except Exception as ex:

            print(
                f"Failed to load models from {provider.name}"
            )

            print(ex)

            continue

    return {
        "object": "list",
        "data": models,
    }


@router.post("/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
):

    chat_request = ChatRequest(

        provider=None,

        model=None,

        temperature=request.temperature,

        max_tokens=request.max_tokens,

        messages=[

            ChatMessage(

                role=message.role,

                content=message.content,

            )

            for message in request.messages

        ],

    )

    # Streaming support will be added in the next step.
    if request.stream:

        return await chat_service.stream_chat(
            chat_request
        )

    content, model = await chat_service.chat(
        chat_request
    )

    return ChatCompletionResponse(

        id=str(uuid4()),

        created=int(time.time()),

        model=model or "auto",

        choices=[

            OpenAIChoice(

                index=0,

                message=OpenAIMessage(

                    role="assistant",

                    content=content,

                ),

            )

        ],

        usage=OpenAIUsage(

            prompt_tokens=0,

            completion_tokens=0,

            total_tokens=0,

        ),

    )