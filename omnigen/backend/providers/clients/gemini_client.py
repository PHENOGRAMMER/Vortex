from google import genai

from backend.config.settings import settings


class GeminiClient:

    def __init__(self):

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )