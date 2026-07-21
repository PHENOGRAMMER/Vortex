import json
import time
from uuid import uuid4

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.models.chat_request import ChatRequest
from backend.models.chat_request import ChatMessage

from backend.models.openai_models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    OpenAIChoice,
    OpenAIMessage,
    OpenAIUsage,
)

from backend.models.embedding_models import (
    EmbeddingRequest,
    EmbeddingResponse,
    EmbeddingData,
    EmbeddingUsage,
)

from backend.providers.factory import ProviderFactory
from backend.services.chat_service import ChatService

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


def openai_sse(data: dict):

    return f"data: {json.dumps(data)}\n\n"


@router.post("/embeddings")
async def embeddings(
    request: EmbeddingRequest,
):
    provider = ProviderFactory.get("ollama")
    model = request.model 

    if model == "auto":
        model = "text-embedding-004"

    vectors = await provider.embeddings(
        request.input,
        model,
    )
    return EmbeddingResponse(
        model=model,
        data=[
            EmbeddingData(
                embedding=vector,
                index=index,
            )

            for index,vector in enumerate(vectors)
        ],
        usage=EmbeddingUsage(
            prompt_tokens=0,
            total_tokens=0,
        ),
    )


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

    # ============================================================
    # STREAMING
    # ============================================================

    if request.stream:

        async def event_generator():

            chunk_id = str(uuid4())

            created = int(time.time())

            selected_model = "auto"

            async for event in chat_service.stream_chat(
                chat_request
            ):

                # --------------------------------------------
                # Internal status events
                # --------------------------------------------

                if event.type == "status":

                    message = event.data.get(
                        "message",
                        "",
                    )

                    if message.startswith("Using "):

                        # Example:
                        # Using Ollama (qwen2.5-coder:7b)

                        selected_model = (
                            message
                            .replace("Using ", "")
                            .replace(")", "")
                            .split("(")[-1]
                        )

                    # Status events are NOT forwarded
                    # to OpenAI clients.
                    continue

                # --------------------------------------------
                # Token
                # --------------------------------------------

                if event.type == "token":

                    yield openai_sse(
                        {
                            "id": chunk_id,
                            "object": "chat.completion.chunk",
                            "created": created,
                            "model": selected_model,
                            "choices": [
                                {
                                    "index": 0,
                                    "delta": {
                                        "content": event.data["content"],
                                    },
                                    "finish_reason": None,
                                }
                            ],
                        }
                    )

                    continue

                # --------------------------------------------
                # Done
                # --------------------------------------------

                if event.type == "done":

                    yield openai_sse(
                        {
                            "id": chunk_id,
                            "object": "chat.completion.chunk",
                            "created": created,
                            "model": selected_model,
                            "choices": [
                                {
                                    "index": 0,
                                    "delta": {},
                                    "finish_reason": "stop",
                                }
                            ],
                        }
                    )

                    yield "data: [DONE]\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
        )

    # ============================================================
    # NON-STREAMING
    # ============================================================

    content, model = await chat_service.chat(
        chat_request
    )

    return ChatCompletionResponse(

        id=str(uuid4()),

        created=int(time.time()),

        model=model,

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