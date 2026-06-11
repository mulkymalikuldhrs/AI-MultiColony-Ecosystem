"""AI MultiColony Ecosystem - Consolidated colony-based agent operating system.

Merges 21 repos into a unified platform providing:
- Colony-based multi-agent coordination
- LLM provider abstraction via LiteLLM
- Tool registry with decorator-based registration
- Letta-style memory paging with OpenHands condensers
- Multi-channel communication (Telegram, Discord, Slack, WhatsApp)
- Event bus with Action/Observation pattern
- Browser automation, sandbox execution, and more
"""

__version__ = "0.1.0"
__author__ = "AI MultiColony Team"

# Core exports
from ai_multicolony.config.settings import Settings, get_settings
from ai_multicolony.config.logging_config import setup_logging, get_logger

# Type exports
from ai_multicolony.types.agent import AgentState, AgentRole, AgentConfig, AgentCapabilities, AgentOutput
from ai_multicolony.types.events import EventType, Action, Observation, Event, EventStream
from ai_multicolony.types.messages import Message, InboundMessage, OutboundMessage, MessageType
from ai_multicolony.types.tools import ToolType, ToolDefinition, ToolResult, ToolParameter
from ai_multicolony.types.memory import MemoryPage, MemoryType, CondenserType, SessionState
from ai_multicolony.types.colony import ColonyState, HandType, ColonyConfig, TaskAssignment

# Core exports
from ai_multicolony.core.base_agent import BaseAgent
from ai_multicolony.core.agent_loop import AgentLoop
from ai_multicolony.core.tool_registry import ToolRegistry, tool
from ai_multicolony.core.tool_base import BaseTool
from ai_multicolony.core.event_bus import EventBus
from ai_multicolony.core.llm_provider import LLMProvider
from ai_multicolony.core.memory_manager import MemoryManager
from ai_multicolony.core.channel import BaseChannel

# Exception exports
from ai_multicolony.exceptions import (
    MultiColonyError,
    AgentError,
    AgentStateError,
    AgentTimeoutError,
    ToolError,
    ToolExecutionError,
    ToolTimeoutError,
    ToolPermissionError,
    LLMError,
    LLMRateLimitError,
    LLMTokensExceededError,
    ColonyError,
    ColonyHandError,
    MemoryError,
    EventBusError,
    ChannelError,
    SecurityError,
    PermissionDeniedError,
    SandboxError,
    MCPError,
    ConfigurationError,
)

__all__ = [
    # Version
    "__version__",
    # Config
    "Settings", "get_settings", "setup_logging", "get_logger",
    # Types - Agent
    "AgentState", "AgentRole", "AgentConfig", "AgentCapabilities", "AgentOutput",
    # Types - Events
    "EventType", "Action", "Observation", "Event", "EventStream",
    # Types - Messages
    "Message", "InboundMessage", "OutboundMessage", "MessageType",
    # Types - Tools
    "ToolType", "ToolDefinition", "ToolResult", "ToolParameter",
    # Types - Memory
    "MemoryPage", "MemoryType", "CondenserType", "SessionState",
    # Types - Colony
    "ColonyState", "HandType", "ColonyConfig", "TaskAssignment",
    # Core
    "BaseAgent", "AgentLoop", "ToolRegistry", "tool", "BaseTool",
    "EventBus", "LLMProvider", "MemoryManager", "BaseChannel",
    # Exceptions
    "MultiColonyError", "AgentError", "AgentStateError", "AgentTimeoutError",
    "ToolError", "ToolExecutionError", "ToolTimeoutError", "ToolPermissionError",
    "LLMError", "LLMRateLimitError", "LLMTokensExceededError",
    "ColonyError", "ColonyHandError", "MemoryError", "EventBusError",
    "ChannelError", "SecurityError", "PermissionDeniedError",
    "SandboxError", "MCPError", "ConfigurationError",
]
