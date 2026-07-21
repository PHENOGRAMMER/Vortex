import asyncio

from backend.core.sse import sse_event
from backend.core.stream_context import StreamContext


async def fake_stream():

    stream = StreamContext()

    yield sse_event(stream.status("Starting stream..."))

    words = [
        "Hello",
        " Aryan!",
        " Welcome",
        " to",
        " OmniGen",
        ".",
        " Streaming",
        " protocol",
        " v1",
        " is",
        " working!"
    ]

    for word in words:

        await asyncio.sleep(0.25)

        yield sse_event(stream.token(word))

    yield sse_event(stream.done())