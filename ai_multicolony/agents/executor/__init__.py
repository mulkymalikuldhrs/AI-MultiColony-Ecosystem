"""Executor agent module."""

from ai_multicolony.agents.executor.agent import ExecutorAgent

# Re-export from the flat executor.py for backward compatibility
try:
    from ai_multicolony.agents.executor import executor as _executor_flat

    SandboxConfig = getattr(_executor_flat, "SandboxConfig", None)
    SandboxHandle = getattr(_executor_flat, "SandboxHandle", None)
except (ImportError, AttributeError):
    SandboxConfig = None  # type: ignore[misc,assignment]
    SandboxHandle = None  # type: ignore[misc,assignment]

__all__ = ["ExecutorAgent"]
