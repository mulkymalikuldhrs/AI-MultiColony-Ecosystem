"""Subagent orchestration module."""

from .config import SubagentConfig
from .registry import get_available_subagent_names, get_subagent_config, list_subagents

try:
    from .executor import SubagentExecutor, SubagentResult
except ImportError:
    # langchain not available — subagent executor requires langchain
    SubagentExecutor = None  # type: ignore[assignment,misc]
    SubagentResult = None  # type: ignore[assignment,misc]

__all__ = [
    "SubagentConfig",
    "SubagentExecutor",
    "SubagentResult",
    "get_available_subagent_names",
    "get_subagent_config",
    "list_subagents",
]
