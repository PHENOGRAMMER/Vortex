import itertools
import logging
from enum import Enum

from .model_clients.base import ModelUnavailableError
from .model_clients.groq_client import groq_client
from .model_clients.ollama_client import ollama_client
from .model_clients.gemini_client import gemini_client
from .model_clients.hf_client import hf_client

from backend.config import get_settings

logger = logging.getLogger("omnigen.router")
settings = get_settings()


class TaskType(str, Enum):
    CHAT = "chat"
    CODE = "code"
    IMAGE = "image"
    RAG = "rag"


CODE_KEYWORDS = (
    "code", "function", "bug", "debug", "script", "class ", "def ",
    "error", "stack trace", "compile", "refactor", "algorithm", "regex",
    "react", "frontend", "component", "tailwind", "css", "html", "javascript",
    "typescript", "website", "landing page", "ui ", "ux ", "vite",
)
IMAGE_KEYWORDS = (
    "draw", "generate an image", "picture of", "illustration", "logo",
    "photo of", "image of", "render a", "create an image", "design a poster",
)


def classify_task(prompt: str, has_context_docs: bool = False) -> TaskType:
    """Zero-cost keyword classifier. If documents are attached to the
    request, RAG always takes priority since the user wants a grounded
    answer. Swap this for a tiny LLM-based classifier later if keyword
    matching proves too blunt for production traffic."""
    if has_context_docs:
        return TaskType.RAG
    low = prompt.lower()
    if any(k in low for k in IMAGE_KEYWORDS):
        return TaskType.IMAGE
    if any(k in low for k in CODE_KEYWORDS):
        return TaskType.CODE
    return TaskType.CHAT


# Ordered fallback chain per task type. The router rotates the starting
# point on every request (round robin) so traffic spreads across providers
# instead of one model absorbing every call -- and if the chosen provider
# fails/rate-limits, it falls through to the next one automatically.
TEXT_PROVIDERS = {
    TaskType.CHAT: [
        (groq_client, settings.groq_text_model),
        (ollama_client, settings.ollama_text_model),
        (gemini_client, settings.gemini_model),
    ],
    TaskType.CODE: [
        (groq_client, settings.groq_strong_model),
        (ollama_client, settings.ollama_code_model),
        (gemini_client, settings.gemini_model),
    ],
    TaskType.RAG: [
        (groq_client, settings.groq_strong_model),
        (gemini_client, settings.gemini_model),
        (ollama_client, settings.ollama_text_model),
    ],
}

_rr_counters = {t: itertools.cycle(range(len(p))) for t, p in TEXT_PROVIDERS.items()}


# Per-task generation params, passed through to whichever client handles the
# request. Code gets a lower temperature (favors correctness/determinism over
# variety) and a higher max_tokens ceiling (multi-file frontend code needs more
# room than a short chat reply). RAG is also kept low-temperature since
# grounded answers should stick close to retrieved context rather than improvise.
GENERATION_PARAMS = {
    TaskType.CHAT: {"temperature": 0.6, "max_tokens": 1200},
    TaskType.CODE: {"temperature": 0.25, "max_tokens": 2400},
    TaskType.RAG: {"temperature": 0.3, "max_tokens": 1600},
}


async def route_text(messages: list[dict], task_type: TaskType):
    providers = TEXT_PROVIDERS[task_type]
    start_idx = next(_rr_counters[task_type])
    order = providers[start_idx:] + providers[:start_idx]  # rotated chain
    params = GENERATION_PARAMS.get(task_type, {})

    errors: list[str] = []
    for client, model in order:
        try:
            response = await client.chat(messages, model=model, **params)
            logger.info("routed %s -> %s (%s) in %.0fms", task_type, client.provider_name, model, response.latency_ms)
            return response
        except ModelUnavailableError as e:
            logger.warning("provider failed for %s: %s (%s) -> %s", task_type, client.provider_name, model, e)
            errors.append(f"{client.provider_name}({model}): {e}")
            continue

    detail = " | ".join(errors) if errors else "no providers configured"
    raise ModelUnavailableError(f"all text providers failed for {task_type}: {detail}")


async def route_image(prompt: str, model: str | None = None):
    return await hf_client.generate_image(prompt, model=model)


async def route(
    prompt: str,
    messages: list[dict],
    has_context_docs: bool = False,
    image_model: str | None = None,
):
    """Single entrypoint used by the API layer: classify -> pick provider
    chain -> return (task_type, ModelResponse)."""
    task_type = classify_task(prompt, has_context_docs)
    if task_type == TaskType.IMAGE:
        response = await route_image(prompt, model=image_model)
    else:
        response = await route_text(messages, task_type)
    return task_type, response
