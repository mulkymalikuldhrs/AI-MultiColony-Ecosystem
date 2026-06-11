"""Core module for the AI MultiColony Ecosystem."""

from ai_multicolony.core.base_agent import BaseAgent
from ai_multicolony.core.agent_loop import AgentLoop
from ai_multicolony.core.tool_registry import ToolRegistry, tool
from ai_multicolony.core.tool_base import BaseTool
from ai_multicolony.core.event_bus import EventBus
from ai_multicolony.core.llm_provider import LLMProvider, LLMResponse, LLMUsage
from ai_multicolony.core.memory_manager import MemoryManager
from ai_multicolony.core.channel import BaseChannel, TelegramChannel, DiscordChannel, SlackChannel, WhatsAppChannel, create_channel
from ai_multicolony.core.ai_selector import AISelector, AgentDescriptor, ai_selector, discover_agents, DEFAULT_FAILOVER_CHAIN

__all__ = [
    "BaseAgent", "AgentLoop", "ToolRegistry", "tool", "BaseTool",
    "EventBus", "LLMProvider", "LLMResponse", "LLMUsage",
    "MemoryManager", "BaseChannel", "TelegramChannel", "DiscordChannel",
    "SlackChannel", "WhatsAppChannel", "create_channel",
    # AI Selector (dynamic discovery)
    "AISelector", "AgentDescriptor", "ai_selector", "discover_agents",
    "DEFAULT_FAILOVER_CHAIN",
]
