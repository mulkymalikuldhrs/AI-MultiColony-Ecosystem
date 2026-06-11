"""API request/response schemas."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


# === Agent Schemas ===

class AgentCreateRequest(BaseModel):
    """Request to create an agent."""

    agent_type: str = Field(description="Type of agent to create")
    name: Optional[str] = None
    model: str = Field(default="gpt-4o")
    tools: list[str] = Field(default_factory=list)
    system_prompt: Optional[str] = None
    autonomy_level: str = Field(default="L2")
    config: dict[str, Any] = Field(default_factory=dict)


class AgentRunRequest(BaseModel):
    """Request to run an agent."""

    task: str = Field(description="Task description")
    max_iterations: Optional[int] = None
    timeout: Optional[int] = None


class AgentResponse(BaseModel):
    """Agent information response."""

    agent_id: str
    name: str
    agent_type: str
    state: str
    current_task: Optional[str] = None
    autonomy_level: str = "L2"


# === Colony Schemas ===

class ColonyCreateRequest(BaseModel):
    """Request to create a colony."""

    name: str
    model: str = Field(default="gpt-4o")
    max_agents: int = Field(default=10)
    config: dict[str, Any] = Field(default_factory=dict)


class ColonyConfigureRequest(BaseModel):
    """Request to configure a colony."""

    max_agents: Optional[int] = None
    timeout: Optional[int] = None
    scheduling_strategy: Optional[str] = None


class ColonyScaleRequest(BaseModel):
    """Request to scale a colony."""

    target_agents: int = Field(ge=1, le=100)


class ColonyResponse(BaseModel):
    """Colony information response."""

    colony_id: str
    name: str
    state: str
    agent_count: int = 0


# === Tool Schemas ===

class ToolCallRequest(BaseModel):
    """Request to call a tool."""

    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolCallResponse(BaseModel):
    """Tool call response."""

    success: bool
    output: str = ""
    error: Optional[str] = None


# === Memory Schemas ===

class MemoryStoreRequest(BaseModel):
    """Request to store a memory."""

    content: str
    memory_type: str = Field(default="episodic")
    importance: float = Field(default=0.5)
    tags: list[str] = Field(default_factory=list)


class MemoryQueryRequest(BaseModel):
    """Request to query memories."""

    query: str
    memory_types: list[str] = Field(default_factory=list)
    limit: int = Field(default=10)


# === Session Schemas ===

class SessionCreateRequest(BaseModel):
    """Request to create a session."""

    agent_id: Optional[str] = None
    colony_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SessionResponse(BaseModel):
    """Session information response."""

    session_id: str
    agent_id: Optional[str] = None
    is_active: bool = True
    message_count: int = 0


# === Knowledge Schemas ===

class KnowledgeAddRequest(BaseModel):
    """Request to add knowledge."""

    title: str
    content: str
    category: str = Field(default="general")
    tags: list[str] = Field(default_factory=list)
    source: str = ""
    confidence: float = Field(default=1.0)


class KnowledgeSearchRequest(BaseModel):
    """Request to search knowledge base."""

    query: str
    category: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    min_confidence: float = Field(default=0.0)
    limit: int = Field(default=10)
    search_type: str = Field(default="keyword")


# === Generic ===

class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
    success: bool = True
    data: Optional[dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Error response."""

    error: str
    code: str = "UNKNOWN"
    details: Optional[dict[str, Any]] = None


class PaginatedResponse(BaseModel):
    """Paginated response."""

    items: list[dict[str, Any]] = Field(default_factory=list)
    total: int = 0
    limit: int = 10
    offset: int = 0
