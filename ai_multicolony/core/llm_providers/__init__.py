"""LLM provider infrastructure for the AI MultiColony Ecosystem.

Exports
-------
NIMProvider
    NVIDIA NIM (Inference Microservice) provider.
ProviderRegistry
    Multi-provider registry with automatic failover.
CircuitBreaker
    Async circuit-breaker for provider health.
ProviderHealth
    Dataclass snapshot of a provider's health.
CircuitState
    Enum for circuit-breaker states (CLOSED / OPEN / HALF_OPEN).
"""

from ai_multicolony.core.llm_providers.circuit_breaker import CircuitBreaker, CircuitState
from ai_multicolony.core.llm_providers.nim_provider import NIMProvider
from ai_multicolony.core.llm_providers.provider_registry import ProviderHealth, ProviderRegistry

__all__ = [
    "NIMProvider",
    "ProviderRegistry",
    "CircuitBreaker",
    "CircuitState",
    "ProviderHealth",
]
