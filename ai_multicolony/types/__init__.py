"""Type definitions for the AI MultiColony Ecosystem."""

from ai_multicolony.types.agent import AgentState, AgentRole, AgentConfig, AgentCapabilities, AgentOutput, AgentStatus, SubagentSpawn
from ai_multicolony.types.events import (
    EventType,
    ActionType,
    ObservationType,
    Action,
    Observation,
    Event,
    EventStream,
)
from ai_multicolony.types.messages import (
    MessageType,
    MessageRole,
    Message,
    BusMessage,
    BusMessagePriority,
    InboundMessage,
    OutboundMessage,
)
from ai_multicolony.types.tools import ToolType, ToolCall, ToolDefinition, ToolResult, ToolParameter
from ai_multicolony.types.memory import (
    MemoryType,
    CondenserType,
    MemoryCondenserType,
    MemoryPage,
    MemoryEntry,
    SessionState,
    MemorySession,
    MemoryQuery,
    MemoryQueryResult,
)
from ai_multicolony.types.colony import (
    ColonyState,
    HandType,
    TaskPriority,
    TaskStatus,
    ColonyConfig,
    TaskAssignment,
    ColonyTask,
    ColonyStatus,
)

__all__ = [
    # Agent
    "AgentState", "AgentRole", "AgentConfig", "AgentCapabilities", "AgentOutput",
    "AgentStatus", "SubagentSpawn",
    # Events
    "EventType", "ActionType", "ObservationType", "Action", "Observation", "Event", "EventStream",
    # Messages
    "MessageType", "MessageRole", "Message", "BusMessage", "BusMessagePriority",
    "InboundMessage", "OutboundMessage",
    # Tools
    "ToolType", "ToolCall", "ToolDefinition", "ToolResult", "ToolParameter",
    # Memory
    "MemoryType", "CondenserType", "MemoryCondenserType", "MemoryPage", "MemoryEntry",
    "SessionState", "MemorySession", "MemoryQuery", "MemoryQueryResult",
    # Colony
    "ColonyState", "HandType", "TaskPriority", "TaskStatus", "ColonyConfig",
    "TaskAssignment", "ColonyTask", "ColonyStatus",
]
