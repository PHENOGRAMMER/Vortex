from typing import AsyncIterator

from backend.models.chat_request import ChatRequest
from backend.core.events import StreamEvent
from backend.core.stream_context import StreamContext

from backend.services.health_manager import HealthManager
from backend.services.provider_resolver import ProviderResolver


class ChatService:

    async def stream_chat(
        self,
        request: ChatRequest,
    ) -> AsyncIterator[StreamEvent]:

        stream = StreamContext()

        candidates = await ProviderResolver.resolve(
            request
        )

        for candidate in candidates:

            try:

                request.provider = candidate.provider.id

                request.model = candidate.model.id

                print()

                print("=" * 70)
                print("TRYING PROVIDER")
                print("Provider :", candidate.provider.name)
                print("Model    :", candidate.model.id)
                print("=" * 70)

                async for event in candidate.provider.stream_chat(
                    request
                ):
                    yield event

                print()

                print("=" * 70)
                print("SUCCESS")
                print("Provider :", candidate.provider.name)
                print("=" * 70)

                return

            except Exception as ex:

                HealthManager.mark_unhealthy(
                    candidate.provider
                )

                yield stream.status(
                    f"{candidate.provider.name} unavailable. Trying another provider..."
                )

                print()

                print("=" * 70)
                print("FAILED")
                print("Provider :", candidate.provider.name)
                print("Model    :", candidate.model.id)
                print("Reason   :", str(ex))
                print("=" * 70)

                continue

        raise RuntimeError(
            "No providers available."
        )