"""Shared test fixtures and configuration for all test modules."""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai_multicolony.core.event_bus import EventBus
from ai_multicolony.core.llm_provider import CostTracker, LLMProvider, LLMResponse, LLMUsage
from ai_multicolony.core.memory_manager import MemoryManager
from ai_multicolony.core.tool_base import BaseTool
from ai_multicolony.core.tool_registry import ToolRegistry
from ai_multicolony.types.agent import AgentCapabilities, AgentConfig, AgentRole, AgentState
from ai_multicolony.types.events import Action, ActionType, Event, EventType, Observation, ObservationType
from ai_multicolony.types.memory import CondenserType, MemoryQuery, MemoryType
from ai_multicolony.types.messages import BusMessage, BusMessagePriority, Message, MessageRole, MessageType
from ai_multicolony.types.tools import ToolCall, ToolDefinition, ToolParameter, ToolResult, ToolType


# ─── Pytest configuration ────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _reset_singletons():
    """Reset all singleton instances before each test to avoid state leakage."""
    EventBus.reset()
    ToolRegistry.reset()
    yield
    EventBus.reset()
    ToolRegistry.reset()


# ─── EventBus fixtures ───────────────────────────────────────────────


@pytest.fixture
def event_bus() -> EventBus:
    """Create a fresh EventBus instance (not started)."""
    return EventBus()


@pytest.fixture
async def running_bus() -> EventBus:
    """Create and start an EventBus."""
    bus = EventBus()
    await bus.start()
    yield bus
    await bus.stop()


# ─── ToolRegistry / tool fixtures ────────────────────────────────────


class SimpleTestTool(BaseTool):
    """A simple tool for testing."""

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="simple_tool",
            description="A simple test tool",
            tool_type=ToolType.SHELL,
            parameters=[
                ToolParameter(name="input", type="string", description="Test input", required=True),
            ],
            tags=["test", "simple"],
        )

    async def execute(self, tool_call: ToolCall) -> ToolResult:
        return ToolResult(
            tool_call_id=tool_call.id,
            tool_name=tool_call.tool_name,
            success=True,
            output=f"Echo: {tool_call.arguments.get('input', '')}",
        )


class FileTestTool(BaseTool):
    """A file-type tool for testing."""

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="file_tool",
            description="A file test tool",
            tool_type=ToolType.FILE,
            parameters=[
                ToolParameter(name="path", type="string", description="File path", required=True),
                ToolParameter(name="content", type="string", description="File content", required=False),
            ],
            tags=["test", "file"],
        )

    async def execute(self, tool_call: ToolCall) -> ToolResult:
        path = tool_call.arguments.get("path", "")
        return ToolResult(
            tool_call_id=tool_call.id,
            tool_name=tool_call.tool_name,
            success=True,
            output=f"Read file: {path}",
        )


class ErrorTestTool(BaseTool):
    """A tool that always raises an error."""

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="error_tool",
            description="Always raises an error",
            tool_type=ToolType.SHELL,
            tags=["test"],
        )

    async def execute(self, tool_call: ToolCall) -> ToolResult:
        raise ValueError("Intentional test error")


class EnumTestTool(BaseTool):
    """A tool with enum parameters for validation testing."""

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="enum_tool",
            description="Tool with enum parameter",
            tool_type=ToolType.CODE,
            parameters=[
                ToolParameter(
                    name="mode",
                    type="string",
                    description="Execution mode",
                    required=True,
                    enum=["fast", "slow", "balanced"],
                ),
            ],
            tags=["test", "enum"],
        )

    async def execute(self, tool_call: ToolCall) -> ToolResult:
        return ToolResult(
            tool_call_id=tool_call.id,
            tool_name=tool_call.tool_name,
            success=True,
            output=f"Mode: {tool_call.arguments.get('mode', '')}",
        )


@pytest.fixture
def tool_registry() -> ToolRegistry:
    """Create a fresh ToolRegistry instance."""
    return ToolRegistry()


@pytest.fixture
def simple_tool() -> SimpleTestTool:
    """Create a SimpleTestTool instance."""
    return SimpleTestTool()


@pytest.fixture
def file_tool() -> FileTestTool:
    """Create a FileTestTool instance."""
    return FileTestTool()


@pytest.fixture
def error_tool() -> ErrorTestTool:
    """Create an ErrorTestTool instance."""
    return ErrorTestTool()


# ─── LLM Provider fixtures ──────────────────────────────────────────


@pytest.fixture
def llm_provider() -> LLMProvider:
    """Create a mock LLM provider with a generous cost limit."""
    return LLMProvider(default_model="gpt-4o", cost_limit_daily=1000.0)


@pytest.fixture
def mock_llm_response() -> LLMResponse:
    """Create a sample LLMResponse."""
    return LLMResponse(
        content="Task complete",
        tool_calls=[],
        usage=LLMUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
        model="gpt-4o",
        finish_reason="stop",
        cost=0.001,
        latency=0.5,
    )


@pytest.fixture
def mock_llm_response_with_tools() -> LLMResponse:
    """Create a sample LLMResponse that includes tool calls."""
    return LLMResponse(
        content="",
        tool_calls=[
            {
                "id": "call-1",
                "type": "function",
                "function": {
                    "name": "simple_tool",
                    "arguments": '{"input": "hello"}',
                },
            }
        ],
        usage=LLMUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30),
        model="gpt-4o",
        finish_reason="tool_calls",
        cost=0.002,
        latency=0.8,
    )


# ─── MemoryManager fixtures ─────────────────────────────────────────


@pytest.fixture
def memory_manager() -> MemoryManager:
    """Create a fresh MemoryManager instance."""
    return MemoryManager()


@pytest.fixture
def memory_manager_small() -> MemoryManager:
    """Create a MemoryManager with small limits for eviction testing."""
    return MemoryManager(max_pages=3, page_size=100)


# ─── Agent fixtures ──────────────────────────────────────────────────


@pytest.fixture
def agent_config() -> AgentConfig:
    """Create a test agent configuration."""
    return AgentConfig(
        name="test-agent",
        role=AgentRole.MANUS,
        model="gpt-4o",
        max_iterations=3,
        tools=[],
    )


@pytest.fixture
def coder_config() -> AgentConfig:
    """Create a coder agent configuration."""
    return AgentConfig(
        name="coder-agent",
        role=AgentRole.CODER,
        model="gpt-4o",
        capabilities=AgentCapabilities(
            code_generation=True,
            code_execution=True,
            file_operations=True,
        ),
        tools=["simple_tool"],
        max_iterations=5,
    )


# ─── Event / Message fixtures ────────────────────────────────────────


@pytest.fixture
def sample_action() -> Action:
    """Create a sample action."""
    return Action(
        action_type=ActionType.THINK,
        agent_id="test-agent",
        thought="Testing",
    )


@pytest.fixture
def sample_observation() -> Observation:
    """Create a sample observation."""
    return Observation(
        observation_type=ObservationType.SUCCESS,
        agent_id="test-agent",
        action_id="action-123",
        content="Test output",
    )


@pytest.fixture
def sample_event() -> Event:
    """Create a sample event."""
    return Event(
        event_type=EventType.CUSTOM,
        source="test-agent",
        data={"key": "value"},
    )


@pytest.fixture
def sample_message() -> Message:
    """Create a sample message."""
    return Message(role=MessageRole.USER, content="Hello, test!")


@pytest.fixture
def sample_bus_message() -> BusMessage:
    """Create a sample bus message."""
    return BusMessage(
        sender="agent-1",
        channel="test",
        message_type=MessageType.NOTIFICATION,
        content={"text": "hello"},
    )


@pytest.fixture
def sample_tool_call() -> ToolCall:
    """Create a sample tool call."""
    return ToolCall(
        tool_name="simple_tool",
        arguments={"input": "value1"},
        agent_id="test-agent",
    )


@pytest.fixture
def sample_tool_result() -> ToolResult:
    """Create a sample tool result."""
    return ToolResult(
        tool_call_id="call-123",
        tool_name="simple_tool",
        success=True,
        output="Test output",
    )


# ─── Helper to create events for condenser tests ────────────────────


def make_events(count: int = 5) -> list[Event]:
    """Create a list of test events with alternating actions and observations."""
    events = []
    for i in range(count):
        if i % 2 == 0:
            events.append(Event(
                event_type=EventType.ACTION,
                source=f"agent-{i}",
                action=Action(
                    action_type=ActionType.THINK,
                    agent_id=f"agent-{i}",
                    thought=f"Step {i}",
                ),
                data={"index": i},
            ))
        else:
            events.append(Event(
                event_type=EventType.OBSERVATION,
                source=f"agent-{i}",
                observation=Observation(
                    observation_type=ObservationType.SUCCESS,
                    agent_id=f"agent-{i}",
                    action_id=f"act-{i}",
                    content=f"Result {i}",
                ),
                data={"index": i},
            ))
    return events
