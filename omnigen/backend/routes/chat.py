from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.models.chat_request import ChatRequest
from backend.services.chat_service import ChatService
from backend.core.sse import sse_event

router = APIRouter(tags=["Chat"])

service = ChatService()


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
async def stream_chat(request: ChatRequest):

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