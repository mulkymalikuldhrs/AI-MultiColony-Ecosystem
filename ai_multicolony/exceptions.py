"""Custom exceptions for the AI MultiColony Ecosystem.

Provides a comprehensive hierarchy of exceptions covering all subsystems:
agents, tools, LLM, colony, memory, events, channels, security, sandbox,
MCP, configuration, resources, and vector stores.
"""

from __future__ import annotations


class MultiColonyError(Exception):
    """Base exception for all MultiColony errors."""

    def __init__(self, message: str, code: str = "UNKNOWN", details: dict | None = None) -> None:
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

    def __str__(self) -> str:
        base = f"[{self.code}] {self.message}"
        if self.details:
            detail_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            base += f" ({detail_str})"
        return base


# === Agent Exceptions ===


class AgentError(MultiColonyError):
    """Errors related to agent operations."""

    def __init__(self, message: str, agent_id: str | None = None, **kwargs: object) -> None:
        details: dict = kwargs.pop("details", {}) if "details" in kwargs else {}  # type: ignore[assignment]
        if agent_id:
            details["agent_id"] = agent_id
        super().__init__(message, code="AGENT_ERROR", details=details)


class AgentStateError(AgentError):
    """Agent is in an invalid state for the requested operation."""

    def __init__(self, message: str, agent_id: str | None = None, current_state: str | None = None) -> None:
        details: dict = {}
        if current_state:
            details["current_state"] = current_state
        super().__init__(message, agent_id=agent_id, details=details)
        self.code = "AGENT_STATE_ERROR"


class AgentTimeoutError(AgentError):
    """Agent operation timed out."""

    def __init__(self, message: str, agent_id: str | None = None, timeout: float | None = None) -> None:
        details: dict = {}
        if timeout is not None:
            details["timeout"] = timeout
        super().__init__(message, agent_id=agent_id, details=details)
        self.code = "AGENT_TIMEOUT"


class AgentNotFoundError(AgentError):
    """Requested agent was not found."""

    def __init__(self, message: str, agent_id: str | None = None) -> None:
        super().__init__(message, agent_id=agent_id)
        self.code = "AGENT_NOT_FOUND"


# === Tool Exceptions ===


class ToolError(MultiColonyError):
    """Errors related to tool operations."""

    def __init__(self, message: str, tool_name: str | None = None, **kwargs: object) -> None:
        details: dict = kwargs.pop("details", {}) if "details" in kwargs else {}  # type: ignore[assignment]
        if tool_name:
            details["tool_name"] = tool_name
        super().__init__(message, code="TOOL_ERROR", details=details)


class ToolExecutionError(ToolError):
    """Tool execution failed."""

    def __init__(self, message: str, tool_name: str | None = None, exit_code: int | None = None) -> None:
        details: dict = {}
        if exit_code is not None:
            details["exit_code"] = exit_code
        super().__init__(message, tool_name=tool_name, details=details)
        self.code = "TOOL_EXECUTION_ERROR"


class ToolTimeoutError(ToolError):
    """Tool execution timed out."""

    def __init__(self, message: str, tool_name: str | None = None, timeout: float | None = None) -> None:
        details: dict = {}
        if timeout is not None:
            details["timeout"] = timeout
        super().__init__(message, tool_name=tool_name, details=details)
        self.code = "TOOL_TIMEOUT"


class ToolPermissionError(ToolError):
    """Tool execution denied due to permission restrictions."""

    def __init__(self, message: str, tool_name: str | None = None, required_permission: str | None = None) -> None:
        details: dict = {}
        if required_permission:
            details["required_permission"] = required_permission
        super().__init__(message, tool_name=tool_name, details=details)
        self.code = "TOOL_PERMISSION_ERROR"


class ToolNotFoundError(ToolError):
    """Requested tool was not found in the registry."""

    def __init__(self, message: str, tool_name: str | None = None) -> None:
        super().__init__(message, tool_name=tool_name)
        self.code = "TOOL_NOT_FOUND"


# === LLM Exceptions ===


class LLMError(MultiColonyError):
    """Errors related to LLM operations."""

    def __init__(self, message: str, provider: str | None = None, model: str | None = None, **kwargs: object) -> None:
        details: dict = kwargs.pop("details", {}) if "details" in kwargs else {}  # type: ignore[assignment]
        if provider:
            details["provider"] = provider
        if model:
            details["model"] = model
        super().__init__(message, code="LLM_ERROR", details=details)


class LLMRateLimitError(LLMError):
    """LLM rate limit exceeded."""

    def __init__(self, message: str, provider: str | None = None, retry_after: float | None = None) -> None:
        details: dict = {}
        if retry_after is not None:
            details["retry_after"] = retry_after
        super().__init__(message, provider=provider, details=details)
        self.code = "LLM_RATE_LIMIT"


class LLMTokensExceededError(LLMError):
    """Token limit exceeded for the LLM request."""

    def __init__(self, message: str, tokens_used: int | None = None, token_limit: int | None = None) -> None:
        details: dict = {}
        if tokens_used is not None:
            details["tokens_used"] = tokens_used
        if token_limit is not None:
            details["token_limit"] = token_limit
        super().__init__(message, details=details)
        self.code = "LLM_TOKENS_EXCEEDED"


# === Colony Exceptions ===


class ColonyError(MultiColonyError):
    """Errors related to colony operations."""

    def __init__(self, message: str, colony_id: str | None = None, **kwargs: object) -> None:
        details: dict = kwargs.pop("details", {}) if "details" in kwargs else {}  # type: ignore[assignment]
        if colony_id:
            details["colony_id"] = colony_id
        super().__init__(message, code="COLONY_ERROR", details=details)


class ColonyHandError(ColonyError):
    """Error in a colony hand operation."""

    def __init__(self, message: str, colony_id: str | None = None, hand_type: str | None = None) -> None:
        details: dict = {}
        if hand_type:
            details["hand_type"] = hand_type
        super().__init__(message, colony_id=colony_id, details=details)
        self.code = "COLONY_HAND_ERROR"


# === Memory Exceptions ===


class MemoryError(MultiColonyError):
    """Errors related to memory operations."""

    def __init__(self, message: str, **kwargs: object) -> None:
        super().__init__(message, code="MEMORY_ERROR", details=kwargs.pop("details", {}) if "details" in kwargs else {})


# === Event Bus Exceptions ===


class EventBusError(MultiColonyError):
    """Errors related to event bus operations."""

    def __init__(self, message: str, **kwargs: object) -> None:
        super().__init__(message, code="EVENT_BUS_ERROR", details=kwargs.pop("details", {}) if "details" in kwargs else {})


# === Channel Exceptions ===


class ChannelError(MultiColonyError):
    """Errors related to channel operations."""

    def __init__(self, message: str, channel_type: str | None = None, **kwargs: object) -> None:
        details: dict = kwargs.pop("details", {}) if "details" in kwargs else {}  # type: ignore[assignment]
        if channel_type:
            details["channel_type"] = channel_type
        super().__init__(message, code="CHANNEL_ERROR", details=details)


# === Security Exceptions ===


class SecurityError(MultiColonyError):
    """Security-related errors."""

    def __init__(self, message: str, **kwargs: object) -> None:
        super().__init__(message, code="SECURITY_ERROR", details=kwargs.pop("details", {}) if "details" in kwargs else {})


class PermissionDeniedError(SecurityError):
    """Permission denied for the requested operation."""

    def __init__(self, message: str, permission: str | None = None, subject: str | None = None) -> None:
        details: dict = {}
        if permission:
            details["permission"] = permission
        if subject:
            details["subject"] = subject
        super().__init__(message, details=details)
        self.code = "PERMISSION_DENIED"


# === Sandbox Exceptions ===


class SandboxError(MultiColonyError):
    """Errors related to sandbox operations."""

    def __init__(self, message: str, sandbox_type: str | None = None, **kwargs: object) -> None:
        details: dict = kwargs.pop("details", {}) if "details" in kwargs else {}  # type: ignore[assignment]
        if sandbox_type:
            details["sandbox_type"] = sandbox_type
        super().__init__(message, code="SANDBOX_ERROR", details=details)


# === MCP Exceptions ===


class MCPError(MultiColonyError):
    """Errors related to MCP protocol operations."""

    def __init__(self, message: str, **kwargs: object) -> None:
        super().__init__(message, code="MCP_ERROR", details=kwargs.pop("details", {}) if "details" in kwargs else {})


# === Configuration Exceptions ===


class ConfigurationError(MultiColonyError):
    """Configuration-related errors."""

    def __init__(self, message: str, **kwargs: object) -> None:
        super().__init__(message, code="CONFIGURATION_ERROR", details=kwargs.pop("details", {}) if "details" in kwargs else {})


# === Resource Exceptions ===


class ResourceError(MultiColonyError):
    """Errors related to resource allocation and limits."""

    def __init__(self, message: str, resource_type: str | None = None, **kwargs: object) -> None:
        details: dict = kwargs.pop("details", {}) if "details" in kwargs else {}  # type: ignore[assignment]
        if resource_type:
            details["resource_type"] = resource_type
        super().__init__(message, code="RESOURCE_ERROR", details=details)


class ResourceExhaustedError(ResourceError):
    """A resource has been exhausted (e.g., token budget, cost limit)."""

    def __init__(self, message: str, resource_type: str | None = None, limit: float | None = None, current: float | None = None) -> None:
        details: dict = {}
        if limit is not None:
            details["limit"] = limit
        if current is not None:
            details["current"] = current
        super().__init__(message, resource_type=resource_type, details=details)
        self.code = "RESOURCE_EXHAUSTED"


# === Vector Store Exceptions ===


class VectorStoreError(MultiColonyError):
    """Errors related to vector store operations (Qdrant, ChromaDB, etc.)."""

    def __init__(self, message: str, store_type: str | None = None, **kwargs: object) -> None:
        details: dict = kwargs.pop("details", {}) if "details" in kwargs else {}  # type: ignore[assignment]
        if store_type:
            details["store_type"] = store_type
        super().__init__(message, code="VECTOR_STORE_ERROR", details=details)
