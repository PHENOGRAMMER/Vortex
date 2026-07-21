import json
from backend.core.events import StreamEvent

def sse_event(event: StreamEvent):
    return (
        f"event: message\n"
        f"data: {json.dumps(event.to_dict())}\n\n"
    )