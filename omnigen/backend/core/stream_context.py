import uuid

from backend.core.events import StreamEvent
from backend.core.event_types import EventType


class StreamContext:

    def __init__(self):

        self.stream_id = str(uuid.uuid4())

        self.sequence = 0

    def _event(self, event_type: EventType, data: dict):

        self.sequence += 1

        return StreamEvent(
            stream_id=self.stream_id,
            sequence=self.sequence,
            type=event_type.value,
            data=data,
        )

    def token(self, text: str):

        return self._event(
            EventType.TOKEN,
            {
                "content": text
            }
        )

    def done(self):

        return self._event(
            EventType.DONE,
            {}
        )

    def error(self, message: str):

        return self._event(
            EventType.ERROR,
            {
                "message": message
            }
        )

    def status(self, message: str):

        return self._event(
            EventType.STATUS,
            {
                "message": message
            }
        )

    def heartbeat(self):

        return self._event(
            EventType.HEARTBEAT,
            {}
        )