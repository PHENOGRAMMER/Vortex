from dataclasses import dataclass

from backend.models.chat_request import ChatRequest
from backend.models.model_info import ModelInfo

from backend.services.provider_resolver import ProviderResolver
from backend.services.health_manager import HealthManager


@dataclass
class ModelSelection:

    provider: object

    model: ModelInfo


class ModelSelector:

    @classmethod
    async def select(
        cls,
        request: ChatRequest,
    ) -> ModelSelection:

        # ---------------------------------------
        # Resolve candidate providers
        # ---------------------------------------

        candidates = await ProviderResolver.resolve(
            request
        )

        # ---------------------------------------
        # Try providers in priority order
        # ---------------------------------------

        for candidate in candidates:

            provider = candidate.provider
            model = candidate.model

            healthy = await HealthManager.is_healthy(
                provider
            )

            if not healthy:

                print(
                    f"Skipping {provider.name} (offline)"
                )

                continue

            return ModelSelection(

                provider=provider,

                model=model,

            )

        raise RuntimeError(

            "No healthy provider with a compatible model found."

        )