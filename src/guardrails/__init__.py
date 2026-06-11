"""Pre-tool-call authorization middleware.

Consolidated from deer-flow guardrails system.
"""

from src.guardrails.builtin import AllowlistProvider
from src.guardrails.provider import GuardrailDecision, GuardrailProvider, GuardrailReason, GuardrailRequest

try:
    from src.guardrails.middleware import GuardrailMiddleware
except ImportError:
    # langchain not available — GuardrailMiddleware requires langchain/langgraph
    GuardrailMiddleware = None  # type: ignore[assignment,misc]

__all__ = [
    "AllowlistProvider",
    "GuardrailDecision",
    "GuardrailMiddleware",
    "GuardrailProvider",
    "GuardrailReason",
    "GuardrailRequest",
]
