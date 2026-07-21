from datetime import datetime

from backend.models.provider_score import ProviderScore
from backend.models.router_decision import RouterDecision
from backend.services.decision_manager import DecisionManager


decision = RouterDecision(

    timestamp=datetime.now(),

    task="code",

    selected_provider="Ollama",

    selected_model="qwen2.5-coder:7b",

    selected_score=188,

    alternatives=[

        ProviderScore(

            provider="Ollama",

            model="qwen2.5-coder:7b",

            score=188,

            reasons=["Local"],

        ),

        ProviderScore(

            provider="Gemini",

            model="gemini-2.5-flash",

            score=163,

            reasons=["Cloud"],

        ),

    ],

    fallback_used=False,

    latency_ms=845,

)

DecisionManager.save(decision)

print()

print("=" * 70)
print("LAST DECISION")
print("=" * 70)

print(
    DecisionManager.last()
)

print()

print("=" * 70)
print("HISTORY")
print("=" * 70)

print(
    len(
        DecisionManager.history()
    )
)