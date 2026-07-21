import time
from uuid import uuid4
from datetime import datetime, UTC
from typing import AsyncIterator

from backend.models.chat_request import ChatRequest
from backend.models.router_metrics import RouterMetrics
from backend.models.provider_score import ProviderScore
from backend.models.router_decision import RouterDecision
from backend.models.original_selection import OriginalSelection

from backend.core.events import StreamEvent

from backend.services.circuit_breaker import CircuitBreaker
from backend.services.provider_resolver import ProviderResolver
from backend.services.metrics_manager import MetricsManager
from backend.services.decision_manager import DecisionManager
from backend.services.request_analyzer import RequestAnalyzer


class ChatService:

    async def stream_chat(
        self,
        request: ChatRequest,
    ) -> AsyncIterator[StreamEvent]:

        task = RequestAnalyzer.analyze(request)

        candidates = await ProviderResolver.resolve(
            request
        )

        original_selection = None

        if candidates:

            best = candidates[0]

            original_selection = OriginalSelection(
                provider=best.provider.name,
                model=best.model.id,
                score=best.score,
            )

        provider_scores = []

        for candidate in candidates:

            provider_scores.append(

                ProviderScore(

                    provider=candidate.provider.name,

                    model=candidate.model.id,

                    score=candidate.score,

                    reasons=candidate.reasons or [],

                )

            )

        request_id = str(uuid4())

        if request.metadata is None:
            request.metadata = {}

        request.metadata["stream_id"] = request_id

        fallback_used = False

        for index, candidate in enumerate(candidates):

            request.provider = candidate.provider.id
            request.model = candidate.model.id

            print()
            print("=" * 70)
            print("TRYING PROVIDER")
            print("Provider :", candidate.provider.name)
            print("Model    :", candidate.model.id)
            print("=" * 70)

            # Notify clients which provider is being used.
            yield StreamEvent.status(

                stream_id=request_id,

                sequence=index,

                message=f"Using {candidate.provider.name} ({candidate.model.id})",

            )

            start = time.perf_counter()

            try:

                async for event in candidate.provider.stream_chat(
                    request
                ):
                    yield event

                latency = (
                    time.perf_counter() - start
                ) * 1000

                MetricsManager.add(

                    RouterMetrics(

                        request_id=request_id,

                        timestamp=datetime.now(UTC),

                        provider=candidate.provider.name,

                        model=candidate.model.id,

                        task=task.value,

                        capability="",

                        latency_ms=latency,

                        success=True,

                        score=0,

                        fallback_used=fallback_used,

                    )

                )

                CircuitBreaker.record_success(
                    candidate.provider.name,
                )

                DecisionManager.save(

                    RouterDecision(

                        timestamp=datetime.now(UTC),

                        task=task.value,

                        selected_provider=candidate.provider.name,

                        selected_model=candidate.model.id,

                        selected_score=candidate.score,

                        original_selection=original_selection,

                        alternatives=provider_scores,

                        fallback_used=fallback_used,

                        latency_ms=latency,

                    )

                )

                return

            except Exception as ex:

                latency = (
                    time.perf_counter() - start
                ) * 1000

                MetricsManager.add(

                    RouterMetrics(

                        request_id=request_id,

                        timestamp=datetime.now(UTC),

                        provider=candidate.provider.name,

                        model=candidate.model.id,

                        task=task.value,

                        capability="",

                        latency_ms=latency,

                        success=False,

                        error=str(ex),

                        score=0,

                        fallback_used=fallback_used,

                    )

                )

                CircuitBreaker.record_failure(
                    candidate.provider.name,
                )

                print()
                print("=" * 70)
                print("FAILED")
                print("Provider :", candidate.provider.name)
                print("Model    :", candidate.model.id)
                print("Reason   :", ex)
                print("=" * 70)

                if index < len(candidates) - 1:

                    fallback_used = True

                    yield StreamEvent.status(

                        stream_id=request_id,

                        sequence=index + 1,

                        message=f"Provider {candidate.provider.name} failed. Trying next provider...",

                    )

                    continue

                raise RuntimeError(
                    "No providers available."
                )

    async def chat(
        self,
        request: ChatRequest,
    ) -> tuple[str, str]:

        content = ""

        async for event in self.stream_chat(request):

            if event.type == "token":

                content += event.data["content"]

        decision = DecisionManager.last()

        model = "auto"

        if decision is not None:

            model = decision.selected_model

        return content, model