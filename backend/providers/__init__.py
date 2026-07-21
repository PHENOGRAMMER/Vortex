from backend.providers.registry import registry

from backend.providers.implementations.mock import MockProvider
from backend.providers.implementations.ollama import OllamaProvider
from backend.providers.implementations.gemini import GeminiProvider
from backend.providers.implementations.openai import OpenAIProvider

registry.register(MockProvider())
registry.register(OllamaProvider())
registry.register(GeminiProvider())
registry.register(OpenAIProvider())

print("Registered Providers: ", registry.list())