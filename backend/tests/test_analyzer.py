from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from backend.services.request_analyzer import RequestAnalyzer
from backend.models.chat_request import ChatRequest
from backend.models.chat_request import ChatMessage


tests = [

    "Write Python code",

    "Explain quantum mechanics",

    "Summarize this PDF",

    "Hello there",

    "Debug this FastAPI project",

]

for text in tests:

    request = ChatRequest(

        provider="",

        model="",

        messages=[

            ChatMessage(

                role="user",

                content=text,
            )
        ],
    )

    print(text)

    print(RequestAnalyzer.analyze(request))

    print("-" * 50)