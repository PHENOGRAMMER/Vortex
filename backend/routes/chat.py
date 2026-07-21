from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Any

from backend.models.chat_request import ChatRequest, ChatMessage
from backend.services.chat_service import ChatService
from backend.core.sse import sse_event
from backend.services.rag_service import RAGService
from backend.auth.dependencies import get_current_user
from backend.auth.models import User

router = APIRouter(tags=["Chat"])

service = ChatService()
rag_service = RAGService()


class RAGChatRequest(BaseModel):
    question: str
    top_k: int = 5
    history: list[dict] = Field(default_factory=list)
    document_ids: list[str] | None = None
    filenames: list[str] | None = None


class StreamChatRequest(BaseModel):
    """Frontend sends {prompt, history}; we build the ChatRequest here."""
    prompt: str
    history: list[dict[str, Any]] = Field(default_factory=list)
    system: str | None = None


@router.post("")
async def chat(
    request: RAGChatRequest,
    current_user: User = Depends(get_current_user),
):
    return await rag_service.answer(
        question=request.question,
        top_k=request.top_k,
        history=request.history,
        document_ids=request.document_ids,
        filenames=request.filenames,
        user_id=current_user.id,
    )


@router.post(
    "/stream",
    summary="Stream Chat Response",
    description="Streams chat responses using Server-Sent Events (SSE).",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "Server-Sent Event Stream",
            "content": {
                "text/event-stream": {}
            },
        }
    },
)
async def stream_chat(
    body: StreamChatRequest,
    current_user: User = Depends(get_current_user),
):
    # Build message list from prompt + optional history
    messages: list[ChatMessage] = []

    # Default system prompt
    system_content = body.system or (
        "You are OmniGen, a precise and helpful AI assistant. "
        "Give complete, well-structured answers. Be concise for simple "
        "questions, thorough for complex ones."
    )
    messages.append(ChatMessage(role="system", content=system_content))

    # Append conversation history (cap at last 8 turns)
    for item in body.history[-8:]:
        role = item.get("role", "user")
        content = str(item.get("content", ""))
        if role in ("user", "assistant") and content:
            messages.append(ChatMessage(role=role, content=content))

    # Current user turn
    messages.append(ChatMessage(role="user", content=body.prompt))

    request = ChatRequest(messages=messages, metadata={})

    async def event_generator():
        async for event in service.stream_chat(request):
            yield sse_event(event)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
