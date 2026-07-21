from dataclasses import dataclass
from datetime import datetime, timezone
import uuid


@dataclass
class StreamEvent:

    stream_id: str

    sequence: int

    type: str

    data: dict

    event_id: str | None = None

    timestamp: str | None = None

    def to_dict(self):

        return {

            "stream_id": self.stream_id,

            "event_id": self.event_id or str(uuid.uuid4()),

            "sequence": self.sequence,

            "timestamp": self.timestamp
            or datetime.now(timezone.utc).isoformat(),

            "type": self.type,

            "data": self.data,

        }

    @classmethod
    def status(

        cls,

        stream_id: str,

        sequence: int,

        message: str,

    ):

        return cls(

            stream_id=stream_id,

            sequence=sequence,

            type="status",

            data={

                "message": message,

            },

        )

    @classmethod
    def token(

        cls,

        stream_id: str,

        sequence: int,

        content: str,

    ):

        return cls(

            stream_id=stream_id,

            sequence=sequence,

            type="token",

            data={

                "content": content,

            },

        )

    @classmethod
    def error(

        cls,

        stream_id: str,

        sequence: int,

        message: str,

    ):

        return cls(

            stream_id=stream_id,

            sequence=sequence,

            type="error",

            data={

                "message": message,

            },

        )

    @classmethod
    def done(

        cls,

        stream_id: str,

        sequence: int,

    ):

        return cls(

            stream_id=stream_id,

            sequence=sequence,

            type="done",

            data={},

        )