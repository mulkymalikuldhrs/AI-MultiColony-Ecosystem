"""MCP protocol type definitions.

Defines the JSON-RPC 2.0 based protocol types for the Model Context Protocol,
including ToolDefinition, ResourceDefinition, PromptDefinition, and Permission levels.
"""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class MCPMethod(str, Enum):
    """MCP JSON-RPC methods."""

    INITIALIZE = "initialize"
    INITIALIZED = "notifications/initialized"
    LIST_TOOLS = "tools/list"
    CALL_TOOL = "tools/call"
    LIST_RESOURCES = "resources/list"
    READ_RESOURCE = "resources/read"
    SUBSCRIBE_RESOURCE = "resources/subscribe"
    UNSUBSCRIBE_RESOURCE = "resources/unsubscribe"
    LIST_PROMPTS = "prompts/list"
    GET_PROMPT = "prompts/get"
    NOTIFICATION = "notifications/progress"
    CANCELLED = "notifications/cancelled"
    LOGGING = "notifications/message"
    COMPLETION = "completion/complete"
    SAMPLING = "sampling/createMessage"


class MCPErrorCode(int, Enum):
    """JSON-RPC 2.0 error codes with MCP-specific extensions."""

    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    # MCP-specific errors
    SERVER_NOT_INITIALIZED = -32002
    UNKNOWN_TOOL = -32001
    UNKNOWN_RESOURCE = -32003
    UNKNOWN_PROMPT = -32004
    PERMISSION_DENIED = -32010
    RATE_LIMITED = -32011
    CIRCUIT_OPEN = -32012


class PermissionLevel(str, Enum):
    """Permission levels for MCP tool/resource access."""

    NONE = "none"
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"

    @property
    def level(self) -> int:
        """Numeric level for comparison."""
        order = {PermissionLevel.NONE: 0, PermissionLevel.READ: 1, PermissionLevel.WRITE: 2,
                 PermissionLevel.EXECUTE: 3, PermissionLevel.ADMIN: 4}
        return order[self]

    def gte(self, other: PermissionLevel) -> bool:
        """Check if this permission level is >= another."""
        return self.level >= other.level


class MCPRequest(BaseModel):
    """MCP JSON-RPC 2.0 request."""

    jsonrpc: str = "2.0"
    id: int | str = Field(default_factory=lambda: str(uuid.uuid4()))
    method: str
    params: dict[str, Any] = Field(default_factory=dict)

    model_config = {"arbitrary_types_allowed": True}


class MCPResponse(BaseModel):
    """MCP JSON-RPC 2.0 response."""

    jsonrpc: str = "2.0"
    id: int | str
    result: Optional[dict[str, Any]] = None
    error: Optional[dict[str, Any]] = None

    model_config = {"arbitrary_types_allowed": True}

    @property
    def is_error(self) -> bool:
        """Check if this response is an error."""
        return self.error is not None

    @classmethod
    def from_error(cls, request_id: int | str, code: MCPErrorCode, message: str, data: Any = None) -> MCPResponse:
        """Create an error response from a code and message."""
        error: dict[str, Any] = {"code": code.value, "message": message}
        if data is not None:
            error["data"] = data
        return cls(id=request_id, error=error)


class ToolDefinition(BaseModel):
    """Definition of a tool exposed via MCP.

    Provides comprehensive metadata about an MCP tool including
    input schema, permission requirements, and rate limits.
    """

    name: str
    description: str = ""
    input_schema: dict[str, Any] = Field(default_factory=dict)
    required_permission: PermissionLevel = PermissionLevel.EXECUTE
    rate_limit: Optional[int] = None  # requests per minute
    timeout: int = 30  # seconds
    category: str = "general"
    deprecated: bool = False

    model_config = {"arbitrary_types_allowed": True}


class ResourceDefinition(BaseModel):
    """Definition of a resource exposed via MCP.

    Resources are addressable data sources that can be read,
    subscribed to, and listed by MCP clients.
    """

    uri: str
    name: str
    description: str = ""
    mime_type: str = "text/plain"
    required_permission: PermissionLevel = PermissionLevel.READ
    subscribable: bool = False
    size_bytes: Optional[int] = None

    model_config = {"arbitrary_types_allowed": True}


class PromptDefinition(BaseModel):
    """Definition of a prompt template exposed via MCP.

    Prompt templates allow servers to define reusable prompt
    patterns with parameterized arguments.
    """

    name: str
    description: str = ""
    arguments: list[dict[str, Any]] = Field(default_factory=list)
    required_permission: PermissionLevel = PermissionLevel.READ
    category: str = "general"

    model_config = {"arbitrary_types_allowed": True}


# Backward-compatible aliases
MCPToolDef = ToolDefinition
MCPResource = ResourceDefinition
MCPPrompt = PromptDefinition


class MCPServerInfo(BaseModel):
    """Server information returned during initialization."""

    name: str = "ai-multicolony-mcp"
    version: str = "0.1.0"
    protocol_version: str = "2024-11-05"
    capabilities: dict[str, Any] = Field(default_factory=lambda: {
        "tools": {"listChanged": True},
        "resources": {"subscribe": True, "listChanged": True},
        "prompts": {"listChanged": True},
        "logging": {},
        "sampling": {},
    })

    model_config = {"arbitrary_types_allowed": True}


class MCPNotification(BaseModel):
    """MCP notification (no response expected)."""

    jsonrpc: str = "2.0"
    method: str
    params: dict[str, Any] = Field(default_factory=dict)

    model_config = {"arbitrary_types_allowed": True}


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class RateLimitEntry(BaseModel):
    """Rate limit tracking entry."""

    agent_id: str
    tool_name: str
    request_count: int = 0
    window_start: float = 0.0
    window_seconds: int = 60

    model_config = {"arbitrary_types_allowed": True}
