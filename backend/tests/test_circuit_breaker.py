from datetime import UTC, datetime, timedelta

from backend.services.circuit_breaker import CircuitBreaker


provider = "Ollama"

CircuitBreaker.reset()

print()
print("=" * 70)
print("INITIAL")
print("=" * 70)

print(
    CircuitBreaker.get_state(provider)
)

print()

print("=" * 70)
print("FAILURES")
print("=" * 70)

for i in range(3):

    CircuitBreaker.record_failure(
        provider
    )

    print()

    print(

        f"Failure {i+1}"

    )

    print(

        CircuitBreaker.get_state(
            provider
        )

    )

print()

print("=" * 70)
print("CAN EXECUTE?")
print("=" * 70)

print(

    CircuitBreaker.can_execute(
        provider
    )

)

print()

print("=" * 70)
print("FORCE RECOVERY")
print("=" * 70)

state = CircuitBreaker.get_state(
    provider
)

state.retry_after = (

    datetime.now(UTC)

    - timedelta(seconds=1)

)

print(

    CircuitBreaker.can_execute(
        provider
    )

)

print(

    CircuitBreaker.get_state(
        provider
    )

)

print()

print("=" * 70)
print("SUCCESS")
print("=" * 70)

CircuitBreaker.record_success(
    provider
)

print(

    CircuitBreaker.get_state(
        provider
    )

)