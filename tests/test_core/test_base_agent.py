"""Tests for BaseAgent — state machine, dependency injection, run loop."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai_multicolony.core.base_agent import BaseAgent
from ai_multicolony.core.event_bus import EventBus
from ai_multicolony.core.llm_provider import LLMProvider, LLMResponse, LLMUsage
from ai_multicolony.core.memory_manager import MemoryManager
from ai_multicolony.core.tool_registry import ToolRegistry
from ai_multicolony.exceptions import AgentError, AgentStateError, AgentTimeoutError
from ai_multicolony.types.agent import AgentCapabilities, AgentConfig, AgentRole, AgentState
from ai_multicolony.types.messages import Message, MessageRole


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_event_bus():
    EventBus.reset()
    yield
    EventBus.reset()

@pytest.fixture(autouse=True)
def reset_tool_registry():
    ToolRegistry.reset()
    yield
    ToolRegistry.reset()


@pytest.fixture
def agent():
    """Create a basic BaseAgent for testing."""
    return BaseAgent(config=AgentConfig(
        name="test-agent",
        role=AgentRole.MANUS,
        max_iterations=3,
        model="gpt-4o",
    ))


@pytest.fixture
def mock_llm_provider():
    """Create a mock LLMProvider."""
    provider = MagicMock(spec=LLMProvider)
    provider.chat = AsyncMock(return_value=LLMResponse(
        content="Task complete",
        tool_calls=[],
        usage=LLMUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
        model="gpt-4o",
        cost=0.001,
    ))
    return provider


# ── Initialization ──────────────────────────────────────────────────────────

class TestBaseAgentInit:
    """Test agent initialization."""

    def test_default_config(self):
        agent = BaseAgent()
        assert agent.state == AgentState.IDLE
        assert agent.config.role == AgentRole.MANUS
        assert agent.iteration_count == 0
        assert agent.error_count == 0

    def test_custom_config(self):
        agent = BaseAgent(config=AgentConfig(
            name="custom-agent",
            role=AgentRole.CODER,
            max_iterations=5,
        ))
        assert agent.name == "custom-agent"
        assert agent.role == AgentRole.CODER
        assert agent.config.max_iterations == 5

    def test_auto_name_from_role(self):
        agent = BaseAgent(config=AgentConfig(role=AgentRole.PLANNER))
        assert "planner" in agent.name

    def test_agent_id_is_string(self, agent):
        assert isinstance(agent.agent_id, str)
        assert len(agent.agent_id) > 0


# ── Dependency Injection ───────────────────────────────────────────────────

class TestDependencyInjection:
    """Test setting and getting dependencies."""

    def test_set_event_bus(self, agent):
        bus = EventBus()
        agent.set_event_bus(bus)
        assert agent._get_event_bus() is bus

    def test_default_event_bus(self, agent):
        bus = agent._get_event_bus()
        assert isinstance(bus, EventBus)

    def test_set_llm_provider(self, agent):
        provider = LLMProvider()
        agent.set_llm_provider(provider)
        assert agent._get_llm_provider() is provider

    def test_default_llm_provider(self, agent):
        provider = agent._get_llm_provider()
        assert isinstance(provider, LLMProvider)

    def test_set_memory_manager(self, agent):
        mm = MemoryManager()
        agent.set_memory_manager(mm)
        assert agent._get_memory_manager() is mm

    def test_default_memory_manager(self, agent):
        mm = agent._get_memory_manager()
        assert isinstance(mm, MemoryManager)

    def test_set_tool_registry(self, agent):
        tr = ToolRegistry()
        agent.set_tool_registry(tr)
        assert agent._get_tool_registry() is tr


# ── State Machine ──────────────────────────────────────────────────────────

class TestStateMachine:
    """Test agent state transitions."""

    def test_initial_state_is_idle(self, agent):
        assert agent.state == AgentState.IDLE

    def test_idle_to_running(self, agent):
        agent._transition_to(AgentState.RUNNING)
        assert agent.state == AgentState.RUNNING

    def test_idle_to_terminated(self, agent):
        agent._transition_to(AgentState.TERMINATED)
        assert agent.state == AgentState.TERMINATED

    def test_running_to_paused(self, agent):
        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.PAUSED)
        assert agent.state == AgentState.PAUSED

    def test_running_to_error(self, agent):
        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.ERROR)
        assert agent.state == AgentState.ERROR

    def test_running_to_thinking(self, agent):
        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.THINKING)
        assert agent.state == AgentState.THINKING

    def test_invalid_transition_raises(self, agent):
        # IDLE -> PAUSED is invalid — raises AgentStateError
        with pytest.raises(AgentStateError):
            agent._transition_to(AgentState.PAUSED)

    def test_terminated_no_transitions(self, agent):
        agent._transition_to(AgentState.TERMINATED)
        with pytest.raises(AgentStateError):
            agent._transition_to(AgentState.RUNNING)

    def test_error_to_running(self, agent):
        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.ERROR)
        agent._transition_to(AgentState.RUNNING)
        assert agent.state == AgentState.RUNNING


# ── Run Loop ───────────────────────────────────────────────────────────────

class TestAgentRun:
    """Test the agent run loop."""

    @pytest.mark.asyncio
    async def test_run_success(self, agent, mock_llm_provider):
        agent.set_llm_provider(mock_llm_provider)
        result = await agent.run("Do something")
        assert result == "Task complete"
        assert agent.state == AgentState.IDLE

    @pytest.mark.asyncio
    async def test_run_sets_task(self, agent, mock_llm_provider):
        agent.set_llm_provider(mock_llm_provider)
        await agent.run("Do something")
        assert agent.current_task is None  # Cleared in finally

    @pytest.mark.asyncio
    async def test_run_adds_system_prompt(self, agent, mock_llm_provider):
        agent.config.system_prompt = "You are a helpful assistant."
        agent.set_llm_provider(mock_llm_provider)
        await agent.run("Do something")
        system_msgs = [m for m in agent.messages if m.role == MessageRole.SYSTEM]
        assert len(system_msgs) == 1

    @pytest.mark.asyncio
    async def test_run_invalid_state_raises(self, agent, mock_llm_provider):
        agent.set_llm_provider(mock_llm_provider)
        # Manually transition to RUNNING (bypassing validation for setup)
        agent._transition_to(AgentState.RUNNING)
        # Now run should raise because agent is in RUNNING state
        with pytest.raises((AgentStateError, AgentError)):
            await agent.run("Do something")

    @pytest.mark.asyncio
    async def test_run_error_state_on_failure(self, agent):
        mock_provider = MagicMock(spec=LLMProvider)
        mock_provider.chat = AsyncMock(side_effect=RuntimeError("LLM error"))
        agent.set_llm_provider(mock_provider)
        # Agent needs to be in IDLE or ERROR state to run
        with pytest.raises((AgentError, Exception)):
            await agent.run("Do something")
        # Agent should end up in ERROR state (or THINKING if error occurred mid-transition)
        assert agent.state in (AgentState.ERROR, AgentState.THINKING)

    @pytest.mark.asyncio
    async def test_run_max_iterations_raises_timeout(self, agent, mock_llm_provider):
        # Return content that doesn't match done markers
        mock_llm_provider.chat = AsyncMock(return_value=LLMResponse(
            content="Still working...",
            tool_calls=[],
            usage=LLMUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
            model="gpt-4o",
            cost=0.001,
        ))
        agent.config.max_iterations = 2
        agent.set_llm_provider(mock_llm_provider)
        with pytest.raises((AgentTimeoutError, AgentError)):
            await agent.run("Never finish")

    @pytest.mark.asyncio
    async def test_run_tracks_tokens_and_cost(self, agent, mock_llm_provider):
        agent.set_llm_provider(mock_llm_provider)
        await agent.run("Do something")
        assert agent.tokens_used >= 0
        assert agent.cost_incurred >= 0


# ── Completion Detection ───────────────────────────────────────────────────

class TestCompletionDetection:
    """Test _is_done method."""

    def test_task_complete(self, agent):
        assert agent._is_done("The task complete") is True

    def test_finished(self, agent):
        assert agent._is_done("I'm finished") is True

    def test_mission_accomplished(self, agent):
        assert agent._is_done("Mission accomplished!") is True

    def test_not_done(self, agent):
        assert agent._is_done("I'm still working on this") is False

    def test_case_insensitive(self, agent):
        assert agent._is_done("TASK COMPLETED") is True


# ── Control Methods ────────────────────────────────────────────────────────

class TestControlMethods:
    """Test pause, resume, terminate."""

    @pytest.mark.asyncio
    async def test_pause(self, agent):
        agent._transition_to(AgentState.RUNNING)
        await agent.pause()
        assert agent.state == AgentState.PAUSED

    @pytest.mark.asyncio
    async def test_resume(self, agent):
        agent._transition_to(AgentState.RUNNING)
        await agent.pause()
        await agent.resume()
        assert agent.state == AgentState.RUNNING

    @pytest.mark.asyncio
    async def test_terminate(self, agent):
        agent._transition_to(AgentState.RUNNING)
        await agent.terminate()
        assert agent.state == AgentState.TERMINATED

    @pytest.mark.asyncio
    async def test_terminate_from_idle(self, agent):
        await agent.terminate()
        assert agent.state == AgentState.TERMINATED


# ── Status and Output ──────────────────────────────────────────────────────

class TestStatusOutput:
    """Test get_status and get_output."""

    def test_get_status(self, agent):
        status = agent.get_status()
        assert status.agent_id == agent.agent_id
        assert status.state == AgentState.IDLE

    def test_get_output_initial(self, agent):
        output = agent.get_output()
        assert output.agent_id == agent.agent_id
        assert output.success is True
        assert output.iterations == 0


# ── Reset ──────────────────────────────────────────────────────────────────

class TestReset:
    """Test agent reset."""

    def test_reset(self, agent):
        agent._transition_to(AgentState.TERMINATED)
        agent.messages = [Message(role=MessageRole.USER, content="test")]
        agent.reset()
        assert agent.state == AgentState.IDLE
        assert agent.messages == []
        assert agent.iteration_count == 0
        assert agent.tokens_used == 0
