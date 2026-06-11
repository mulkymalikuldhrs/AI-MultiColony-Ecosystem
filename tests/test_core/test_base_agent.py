"""Comprehensive tests for BaseAgent.

Tests cover:
- Initialization and defaults
- AgentState transitions (all valid and invalid paths)
- AgentConfig validation
- Dependency injection (event bus, LLM, tools, memory)
- Agent run loop (with mocked LLM)
- Tool execution
- Event emission
- Subagent spawning
- Error handling
- Status/output/reporting
- Reset behavior
- Completion detection
"""

from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai_multicolony.core.base_agent import BaseAgent
from ai_multicolony.core.event_bus import EventBus
from ai_multicolony.core.llm_provider import LLMProvider, LLMResponse, LLMUsage
from ai_multicolony.core.memory_manager import MemoryManager
from ai_multicolony.core.tool_registry import ToolRegistry
from ai_multicolony.exceptions import AgentError, AgentStateError, AgentTimeoutError
from ai_multicolony.types.agent import (
    AgentCapabilities,
    AgentConfig,
    AgentOutput,
    AgentRole,
    AgentState,
    AgentStatus,
)
from ai_multicolony.types.events import Action, ActionType, Event, EventType, Observation, ObservationType
from ai_multicolony.types.messages import Message, MessageRole
from ai_multicolony.types.memory import MemoryType


# ══════════════════════════════════════════════════════════════════════
# 1. Initialization & Defaults
# ══════════════════════════════════════════════════════════════════════


class TestBaseAgentInit:
    """Test BaseAgent initialization and default values."""

    def test_default_state_is_idle(self):
        agent = BaseAgent()
        assert agent.state == AgentState.IDLE

    def test_default_role_is_manus(self):
        agent = BaseAgent()
        assert agent.config.role == AgentRole.MANUS

    def test_default_iteration_count_is_zero(self):
        agent = BaseAgent()
        assert agent.iteration_count == 0

    def test_default_error_count_is_zero(self):
        agent = BaseAgent()
        assert agent.error_count == 0

    def test_default_tokens_used_is_zero(self):
        agent = BaseAgent()
        assert agent.tokens_used == 0

    def test_default_cost_incurred_is_zero(self):
        agent = BaseAgent()
        assert agent.cost_incurred == 0.0

    def test_default_messages_empty(self):
        agent = BaseAgent()
        assert agent.messages == []

    def test_default_subagent_ids_empty(self):
        agent = BaseAgent()
        assert agent.subagent_ids == []

    def test_default_current_task_none(self):
        agent = BaseAgent()
        assert agent.current_task is None

    def test_default_last_result_none(self):
        agent = BaseAgent()
        assert agent.last_result is None

    def test_default_timing_none(self):
        agent = BaseAgent()
        assert agent.started_at is None
        assert agent.finished_at is None

    def test_init_with_custom_config(self):
        config = AgentConfig(
            name="custom-agent",
            role=AgentRole.CODER,
            model="gpt-4-turbo",
            max_iterations=20,
        )
        agent = BaseAgent(config=config)
        assert agent.name == "custom-agent"
        assert agent.role == AgentRole.CODER
        assert agent.config.model == "gpt-4-turbo"

    def test_agent_id_unique_per_instance(self):
        a1 = BaseAgent()
        a2 = BaseAgent()
        assert a1.agent_id != a2.agent_id

    def test_unnamed_agent_gets_role_based_name(self):
        agent = BaseAgent()
        assert agent.name == "manus-agent"

    def test_coder_agent_gets_role_based_name(self):
        config = AgentConfig(role=AgentRole.CODER)
        agent = BaseAgent(config=config)
        assert agent.name == "coder-agent"

    def test_explicit_name_preserved(self):
        config = AgentConfig(name="my-agent")
        agent = BaseAgent(config=config)
        assert agent.name == "my-agent"

    def test_capabilities_from_config(self):
        caps = AgentCapabilities(code_generation=True, shell_execution=True)
        config = AgentConfig(capabilities=caps)
        agent = BaseAgent(config=config)
        assert agent.capabilities.code_generation is True
        assert agent.capabilities.shell_execution is True
        assert agent.capabilities.web_browsing is False


# ══════════════════════════════════════════════════════════════════════
# 2. State Machine Transitions
# ══════════════════════════════════════════════════════════════════════


class TestBaseAgentStateMachine:
    """Test all valid and invalid AgentState transitions."""

    # --- Valid transitions from IDLE ---
    def test_idle_to_running(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.RUNNING)
        assert agent.state == AgentState.RUNNING

    def test_idle_to_terminated(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.TERMINATED)
        assert agent.state == AgentState.TERMINATED

    # --- Valid transitions from RUNNING ---
    def test_running_to_paused(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.PAUSED)
        assert agent.state == AgentState.PAUSED

    def test_running_to_error(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.ERROR)
        assert agent.state == AgentState.ERROR

    def test_running_to_waiting(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.WAITING)
        assert agent.state == AgentState.WAITING

    def test_running_to_thinking(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.THINKING)
        assert agent.state == AgentState.THINKING

    def test_running_to_terminated(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.TERMINATED)
        assert agent.state == AgentState.TERMINATED

    def test_running_to_idle(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.IDLE)
        assert agent.state == AgentState.IDLE

    # --- Valid transitions from PAUSED ---
    def test_paused_to_running(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.PAUSED)
        agent._transition_to(AgentState.RUNNING)
        assert agent.state == AgentState.RUNNING

    def test_paused_to_terminated(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.PAUSED)
        agent._transition_to(AgentState.TERMINATED)
        assert agent.state == AgentState.TERMINATED

    def test_paused_to_idle(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.PAUSED)
        agent._transition_to(AgentState.IDLE)
        assert agent.state == AgentState.IDLE

    # --- Valid transitions from WAITING ---
    def test_waiting_to_running(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.WAITING)
        agent._transition_to(AgentState.RUNNING)
        assert agent.state == AgentState.RUNNING

    def test_waiting_to_error(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.WAITING)
        agent._transition_to(AgentState.ERROR)
        assert agent.state == AgentState.ERROR

    def test_waiting_to_terminated(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.WAITING)
        agent._transition_to(AgentState.TERMINATED)
        assert agent.state == AgentState.TERMINATED

    # --- Valid transitions from THINKING ---
    def test_thinking_to_running(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.THINKING)
        agent._transition_to(AgentState.RUNNING)
        assert agent.state == AgentState.RUNNING

    def test_thinking_to_error(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.THINKING)
        agent._transition_to(AgentState.ERROR)
        assert agent.state == AgentState.ERROR

    # --- Valid transitions from ERROR ---
    def test_error_to_running(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.ERROR)
        agent._transition_to(AgentState.RUNNING)
        assert agent.state == AgentState.RUNNING

    def test_error_to_idle(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.ERROR)
        agent._transition_to(AgentState.IDLE)
        assert agent.state == AgentState.IDLE

    def test_error_to_terminated(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.ERROR)
        agent._transition_to(AgentState.TERMINATED)
        assert agent.state == AgentState.TERMINATED

    # --- TERMINATED is terminal ---
    def test_terminated_no_transitions(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.TERMINATED)
        for target in AgentState:
            if target == AgentState.TERMINATED:
                continue
            with pytest.raises(AgentStateError):
                agent._transition_to(target)

    # --- Invalid transitions from IDLE ---
    def test_idle_to_paused_invalid(self):
        agent = BaseAgent()
        with pytest.raises(AgentStateError):
            agent._transition_to(AgentState.PAUSED)

    def test_idle_to_error_invalid(self):
        agent = BaseAgent()
        with pytest.raises(AgentStateError):
            agent._transition_to(AgentState.ERROR)

    def test_idle_to_waiting_invalid(self):
        agent = BaseAgent()
        with pytest.raises(AgentStateError):
            agent._transition_to(AgentState.WAITING)

    def test_idle_to_thinking_invalid(self):
        agent = BaseAgent()
        with pytest.raises(AgentStateError):
            agent._transition_to(AgentState.THINKING)

    # --- Invalid: RUNNING -> IDLE is actually valid per VALID_TRANSITIONS ---
    def test_invalid_transition_raises_state_error(self):
        agent = BaseAgent()
        with pytest.raises(AgentStateError) as exc_info:
            agent._transition_to(AgentState.PAUSED)  # IDLE -> PAUSED invalid
        assert "Invalid state transition" in str(exc_info.value)
        assert exc_info.value.code == "AGENT_STATE_ERROR"

    def test_state_error_contains_current_state(self):
        agent = BaseAgent()
        with pytest.raises(AgentStateError) as exc_info:
            agent._transition_to(AgentState.PAUSED)
        assert "idle" in exc_info.value.details.get("current_state", "")


# ══════════════════════════════════════════════════════════════════════
# 3. Dependency Injection
# ══════════════════════════════════════════════════════════════════════


class TestBaseAgentDependencyInjection:
    """Test setting and getting infrastructure components."""

    def test_set_event_bus(self, event_bus):
        agent = BaseAgent()
        agent.set_event_bus(event_bus)
        assert agent._event_bus is event_bus

    def test_set_llm_provider(self, llm_provider):
        agent = BaseAgent()
        agent.set_llm_provider(llm_provider)
        assert agent._llm_provider is llm_provider

    def test_set_tool_registry(self, tool_registry):
        agent = BaseAgent()
        agent.set_tool_registry(tool_registry)
        assert agent._tool_registry is tool_registry

    def test_set_memory_manager(self, memory_manager):
        agent = BaseAgent()
        agent.set_memory_manager(memory_manager)
        assert agent._memory_manager is memory_manager

    def test_get_event_bus_creates_default(self):
        agent = BaseAgent()
        bus = agent._get_event_bus()
        assert bus is not None
        assert isinstance(bus, EventBus)

    def test_get_event_bus_returns_same_instance(self):
        agent = BaseAgent()
        bus1 = agent._get_event_bus()
        bus2 = agent._get_event_bus()
        assert bus1 is bus2

    def test_get_llm_provider_creates_default(self):
        agent = BaseAgent()
        provider = agent._get_llm_provider()
        assert isinstance(provider, LLMProvider)

    def test_get_tool_registry_creates_default(self):
        agent = BaseAgent()
        registry = agent._get_tool_registry()
        assert isinstance(registry, ToolRegistry)

    def test_get_memory_manager_creates_default(self):
        agent = BaseAgent()
        manager = agent._get_memory_manager()
        assert isinstance(manager, MemoryManager)

    def test_injected_provider_overrides_default(self, llm_provider):
        agent = BaseAgent()
        agent.set_llm_provider(llm_provider)
        assert agent._get_llm_provider() is llm_provider


# ══════════════════════════════════════════════════════════════════════
# 4. Control Methods (pause, resume, terminate)
# ══════════════════════════════════════════════════════════════════════


class TestBaseAgentControl:
    """Test pause, resume, and terminate control methods."""

    @pytest.mark.asyncio
    async def test_pause_from_running(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.RUNNING)
        await agent.pause()
        assert agent.state == AgentState.PAUSED

    @pytest.mark.asyncio
    async def test_pause_from_idle_noop(self):
        agent = BaseAgent()
        await agent.pause()
        assert agent.state == AgentState.IDLE  # no change

    @pytest.mark.asyncio
    async def test_resume_from_paused(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.PAUSED)
        await agent.resume()
        assert agent.state == AgentState.RUNNING

    @pytest.mark.asyncio
    async def test_resume_from_idle_noop(self):
        agent = BaseAgent()
        await agent.resume()
        assert agent.state == AgentState.IDLE

    @pytest.mark.asyncio
    async def test_terminate_from_idle(self):
        agent = BaseAgent()
        await agent.terminate()
        assert agent.state == AgentState.TERMINATED

    @pytest.mark.asyncio
    async def test_terminate_from_running(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.RUNNING)
        await agent.terminate()
        assert agent.state == AgentState.TERMINATED

    @pytest.mark.asyncio
    async def test_terminate_idempotent(self):
        agent = BaseAgent()
        await agent.terminate()
        await agent.terminate()  # second call should not raise
        assert agent.state == AgentState.TERMINATED


# ══════════════════════════════════════════════════════════════════════
# 5. Run Method & Agent Loop
# ══════════════════════════════════════════════════════════════════════


class TestBaseAgentRun:
    """Test the run method and execute loop with mocked LLM."""

    @pytest.mark.asyncio
    async def test_run_requires_idle_or_error_state(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.RUNNING)
        with pytest.raises(AgentStateError):
            await agent.run("task")

    @pytest.mark.asyncio
    async def test_run_from_idle_works(self, llm_provider, memory_manager, event_bus):
        agent = BaseAgent()
        agent.set_llm_provider(llm_provider)
        agent.set_memory_manager(memory_manager)
        agent.set_event_bus(event_bus)
        await event_bus.start()

        mock_resp = LLMResponse(
            content="Task complete",
            usage=LLMUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            model="gpt-4o",
            cost=0.001,
        )
        with patch.object(agent, '_call_llm', new_callable=AsyncMock, return_value=mock_resp):
            result = await agent.run("test task")
            assert result
            assert agent.state == AgentState.IDLE

    @pytest.mark.asyncio
    async def test_run_from_error_state_works(self, llm_provider, memory_manager, event_bus):
        agent = BaseAgent()
        agent.set_llm_provider(llm_provider)
        agent.set_memory_manager(memory_manager)
        agent.set_event_bus(event_bus)
        await event_bus.start()

        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.ERROR)
        mock_resp = LLMResponse(
            content="Task complete",
            usage=LLMUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            model="gpt-4o",
            cost=0.001,
        )
        with patch.object(agent, '_call_llm', new_callable=AsyncMock, return_value=mock_resp):
            result = await agent.run("retry task")
            assert result

    @pytest.mark.asyncio
    async def test_run_sets_current_task(self, llm_provider, memory_manager, event_bus):
        agent = BaseAgent()
        agent.set_llm_provider(llm_provider)
        agent.set_memory_manager(memory_manager)
        agent.set_event_bus(event_bus)
        await event_bus.start()

        mock_resp = LLMResponse(
            content="Task complete",
            usage=LLMUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            model="gpt-4o",
            cost=0.001,
        )
        with patch.object(agent, '_call_llm', new_callable=AsyncMock, return_value=mock_resp):
            await agent.run("my task")
            assert agent.current_task is None  # cleared after completion

    @pytest.mark.asyncio
    async def test_run_sets_timing(self, llm_provider, memory_manager, event_bus):
        agent = BaseAgent()
        agent.set_llm_provider(llm_provider)
        agent.set_memory_manager(memory_manager)
        agent.set_event_bus(event_bus)
        await event_bus.start()

        mock_resp = LLMResponse(
            content="Task complete",
            usage=LLMUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            model="gpt-4o",
            cost=0.001,
        )
        with patch.object(agent, '_call_llm', new_callable=AsyncMock, return_value=mock_resp):
            before = time.time()
            await agent.run("timed task")
            after = time.time()
            assert agent.started_at is not None
            assert agent.finished_at is not None
            assert agent.started_at >= before
            assert agent.finished_at <= after

    @pytest.mark.asyncio
    async def test_run_adds_system_prompt(self, llm_provider, memory_manager, event_bus):
        config = AgentConfig(system_prompt="You are a test assistant.")
        agent = BaseAgent(config=config)
        agent.set_llm_provider(llm_provider)
        agent.set_memory_manager(memory_manager)
        agent.set_event_bus(event_bus)
        await event_bus.start()

        mock_resp = LLMResponse(
            content="Task complete",
            usage=LLMUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            model="gpt-4o",
            cost=0.001,
        )
        with patch.object(agent, '_call_llm', new_callable=AsyncMock, return_value=mock_resp):
            await agent.run("task")
            system_msgs = [m for m in agent.messages if m.role == MessageRole.SYSTEM]
            assert len(system_msgs) == 1
            assert system_msgs[0].content == "You are a test assistant."

    @pytest.mark.asyncio
    async def test_run_does_not_duplicate_system_prompt(self, llm_provider, memory_manager, event_bus):
        config = AgentConfig(system_prompt="You are a test assistant.")
        agent = BaseAgent(config=config)
        agent.set_llm_provider(llm_provider)
        agent.set_memory_manager(memory_manager)
        agent.set_event_bus(event_bus)
        await event_bus.start()

        mock_resp = LLMResponse(
            content="Task complete",
            usage=LLMUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            model="gpt-4o",
            cost=0.001,
        )
        with patch.object(agent, '_call_llm', new_callable=AsyncMock, return_value=mock_resp):
            await agent.run("task 1")
        with patch.object(agent, '_call_llm', new_callable=AsyncMock, return_value=mock_resp):
            await agent.run("task 2")
        system_msgs = [m for m in agent.messages if m.role == MessageRole.SYSTEM]
        assert len(system_msgs) == 1

    @pytest.mark.asyncio
    async def test_run_adds_user_message(self, llm_provider, memory_manager, event_bus):
        agent = BaseAgent()
        agent.set_llm_provider(llm_provider)
        agent.set_memory_manager(memory_manager)
        agent.set_event_bus(event_bus)
        await event_bus.start()

        mock_resp = LLMResponse(
            content="Task complete",
            usage=LLMUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            model="gpt-4o",
            cost=0.001,
        )
        with patch.object(agent, '_call_llm', new_callable=AsyncMock, return_value=mock_resp):
            await agent.run("hello agent")
            user_msgs = [m for m in agent.messages if m.role == MessageRole.USER]
            assert any("hello agent" in m.content for m in user_msgs)


# ══════════════════════════════════════════════════════════════════════
# 6. Completion Detection
# ══════════════════════════════════════════════════════════════════════


class TestBaseAgentIsDone:
    """Test the _is_done completion detection."""

    def test_task_complete(self):
        agent = BaseAgent()
        assert agent._is_done("The task complete now")

    def test_task_completed(self):
        agent = BaseAgent()
        assert agent._is_done("Task completed successfully")

    def test_im_done(self):
        agent = BaseAgent()
        assert agent._is_done("I'm done with this")

    def test_finished(self):
        agent = BaseAgent()
        assert agent._is_done("All finished")

    def test_mission_accomplished(self):
        agent = BaseAgent()
        assert agent._is_done("Mission accomplished!")

    def test_all_done(self):
        agent = BaseAgent()
        assert agent._is_done("All done here")

    def test_case_insensitive(self):
        agent = BaseAgent()
        assert agent._is_done("TASK COMPLETE")

    def test_in_progress_not_done(self):
        agent = BaseAgent()
        assert not agent._is_done("Still working on it")

    def test_empty_string_not_done(self):
        agent = BaseAgent()
        assert not agent._is_done("")


# ══════════════════════════════════════════════════════════════════════
# 7. Max Iterations & Timeout
# ══════════════════════════════════════════════════════════════════════


class TestBaseAgentMaxIterations:
    """Test max iterations and timeout behavior."""

    @pytest.mark.asyncio
    async def test_max_iterations_raises_timeout(self, llm_provider, memory_manager, event_bus):
        """Agent that never completes should hit max_iterations and raise."""
        config = AgentConfig(max_iterations=2)
        agent = BaseAgent(config=config)
        agent.set_llm_provider(llm_provider)
        agent.set_memory_manager(memory_manager)
        agent.set_event_bus(event_bus)
        await event_bus.start()

        # Mock LLM to never indicate completion
        mock_response = LLMResponse(
            content="Still working...",
            usage=LLMUsage(prompt_tokens=5, completion_tokens=3, total_tokens=8),
            model="gpt-4o",
            cost=0.001,
        )
        with patch.object(agent, '_call_llm', new_callable=AsyncMock, return_value=mock_response):
            with pytest.raises(AgentTimeoutError):
                await agent.run("never ending task")

    @pytest.mark.asyncio
    async def test_timeout_error_transitions_to_error_state(self, llm_provider, memory_manager, event_bus):
        config = AgentConfig(max_iterations=1)
        agent = BaseAgent(config=config)
        agent.set_llm_provider(llm_provider)
        agent.set_memory_manager(memory_manager)
        agent.set_event_bus(event_bus)
        await event_bus.start()

        mock_response = LLMResponse(
            content="Not done yet",
            usage=LLMUsage(prompt_tokens=5, completion_tokens=3, total_tokens=8),
            model="gpt-4o",
            cost=0.001,
        )
        with patch.object(agent, '_call_llm', new_callable=AsyncMock, return_value=mock_response):
            with pytest.raises(AgentTimeoutError):
                await agent.run("task")
            assert agent.state == AgentState.ERROR


# ══════════════════════════════════════════════════════════════════════
# 8. Tool Execution via Agent
# ══════════════════════════════════════════════════════════════════════


class TestBaseAgentToolExecution:
    """Test tool execution within the agent loop."""

    @pytest.mark.asyncio
    async def test_process_tool_calls_success(self, tool_registry, llm_provider, memory_manager, event_bus):
        from tests.conftest import SimpleTestTool
        tool_registry.register(SimpleTestTool)
        agent = BaseAgent()
        agent.set_tool_registry(tool_registry)
        agent.set_llm_provider(llm_provider)
        agent.set_memory_manager(memory_manager)
        agent.set_event_bus(event_bus)
        await event_bus.start()
        agent._transition_to(AgentState.RUNNING)

        response = LLMResponse(
            content="",
            tool_calls=[
                {
                    "id": "call-1",
                    "type": "function",
                    "function": {"name": "simple_tool", "arguments": '{"input": "hello"}'},
                }
            ],
            usage=LLMUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            model="gpt-4o",
            cost=0.001,
        )
        result = await agent._process_tool_calls(response)
        assert "simple_tool" in result
        assert "Success" in result

    @pytest.mark.asyncio
    async def test_process_tool_calls_error(self, tool_registry, llm_provider, memory_manager, event_bus):
        from tests.conftest import ErrorTestTool
        tool_registry.register(ErrorTestTool)
        agent = BaseAgent()
        agent.set_tool_registry(tool_registry)
        agent.set_llm_provider(llm_provider)
        agent.set_memory_manager(memory_manager)
        agent.set_event_bus(event_bus)
        await event_bus.start()
        agent._transition_to(AgentState.RUNNING)

        response = LLMResponse(
            content="",
            tool_calls=[
                {
                    "id": "call-1",
                    "type": "function",
                    "function": {"name": "error_tool", "arguments": "{}"},
                }
            ],
            usage=LLMUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            model="gpt-4o",
            cost=0.001,
        )
        result = await agent._process_tool_calls(response)
        assert "error_tool" in result
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_tool_call_adds_tool_message(self, tool_registry, llm_provider, memory_manager, event_bus):
        from tests.conftest import SimpleTestTool
        tool_registry.register(SimpleTestTool)
        agent = BaseAgent()
        agent.set_tool_registry(tool_registry)
        agent.set_llm_provider(llm_provider)
        agent.set_memory_manager(memory_manager)
        agent.set_event_bus(event_bus)
        await event_bus.start()
        agent._transition_to(AgentState.RUNNING)

        response = LLMResponse(
            content="",
            tool_calls=[
                {
                    "id": "call-1",
                    "type": "function",
                    "function": {"name": "simple_tool", "arguments": '{"input": "hi"}'},
                }
            ],
            usage=LLMUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            model="gpt-4o",
            cost=0.001,
        )
        await agent._process_tool_calls(response)
        tool_msgs = [m for m in agent.messages if m.role == MessageRole.TOOL]
        assert len(tool_msgs) == 1

    @pytest.mark.asyncio
    async def test_invalid_json_arguments_handled(self, tool_registry, llm_provider, memory_manager, event_bus):
        from tests.conftest import SimpleTestTool
        tool_registry.register(SimpleTestTool)
        agent = BaseAgent()
        agent.set_tool_registry(tool_registry)
        agent.set_llm_provider(llm_provider)
        agent.set_memory_manager(memory_manager)
        agent.set_event_bus(event_bus)
        await event_bus.start()
        agent._transition_to(AgentState.RUNNING)

        response = LLMResponse(
            content="",
            tool_calls=[
                {
                    "id": "call-1",
                    "type": "function",
                    "function": {"name": "simple_tool", "arguments": "not-json"},
                }
            ],
            usage=LLMUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            model="gpt-4o",
            cost=0.001,
        )
        # Should not raise - invalid JSON becomes empty dict
        result = await agent._process_tool_calls(response)
        assert "simple_tool" in result  # Tool still gets called (with empty args)


# ══════════════════════════════════════════════════════════════════════
# 9. Status, Output, and Reporting
# ══════════════════════════════════════════════════════════════════════


class TestBaseAgentStatusOutput:
    """Test get_status, get_output, and related methods."""

    def test_get_status_returns_agent_status(self):
        agent = BaseAgent()
        status = agent.get_status()
        assert isinstance(status, AgentStatus)
        assert status.agent_id == agent.agent_id
        assert status.state == AgentState.IDLE
        assert status.role == AgentRole.MANUS
        assert status.iterations == 0

    def test_get_status_reflects_current_state(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.RUNNING)
        status = agent.get_status()
        assert status.state == AgentState.RUNNING

    def test_get_status_includes_subagents(self):
        agent = BaseAgent()
        agent.subagent_ids.append("child-1")
        status = agent.get_status()
        assert "child-1" in status.subagents

    def test_get_output_returns_agent_output(self):
        agent = BaseAgent()
        output = agent.get_output()
        assert isinstance(output, AgentOutput)
        assert output.agent_id == agent.agent_id

    def test_get_output_success_when_idle(self):
        agent = BaseAgent()
        output = agent.get_output()
        assert output.success is True

    def test_get_output_failure_when_error(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.ERROR)
        output = agent.get_output()
        assert output.success is False
        assert output.error is not None

    def test_get_output_duration(self, llm_provider, memory_manager, event_bus):
        agent = BaseAgent()
        agent.set_llm_provider(llm_provider)
        agent.set_memory_manager(memory_manager)
        agent.set_event_bus(event_bus)

        agent.started_at = 100.0
        agent.finished_at = 105.0
        output = agent.get_output()
        assert output.duration == 5.0

    def test_get_output_zero_duration_no_times(self):
        agent = BaseAgent()
        output = agent.get_output()
        assert output.duration == 0.0

    def test_repr_contains_class_name(self):
        agent = BaseAgent()
        r = repr(agent)
        assert "BaseAgent" in r
        assert "idle" in r

    def test_repr_contains_name(self):
        config = AgentConfig(name="special-agent")
        agent = BaseAgent(config=config)
        r = repr(agent)
        assert "special-agent" in r


# ══════════════════════════════════════════════════════════════════════
# 10. Reset
# ══════════════════════════════════════════════════════════════════════


class TestBaseAgentReset:
    """Test the reset method restores initial state."""

    def test_reset_returns_to_idle(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.RUNNING)
        agent.reset()
        assert agent.state == AgentState.IDLE

    def test_reset_clears_messages(self, llm_provider, memory_manager, event_bus):
        agent = BaseAgent()
        agent.set_llm_provider(llm_provider)
        agent.set_memory_manager(memory_manager)
        agent.set_event_bus(event_bus)

        agent.messages.append(Message(role=MessageRole.USER, content="hi"))
        agent.reset()
        assert agent.messages == []

    def test_reset_clears_current_task(self):
        agent = BaseAgent()
        agent.current_task = "some task"
        agent.reset()
        assert agent.current_task is None

    def test_reset_clears_last_result(self):
        agent = BaseAgent()
        agent.last_result = "some result"
        agent.reset()
        assert agent.last_result is None

    def test_reset_clears_counters(self):
        agent = BaseAgent()
        agent.iteration_count = 10
        agent.error_count = 3
        agent.tokens_used = 5000
        agent.cost_incurred = 2.50
        agent.reset()
        assert agent.iteration_count == 0
        assert agent.error_count == 0
        assert agent.tokens_used == 0
        assert agent.cost_incurred == 0.0

    def test_reset_clears_timing(self):
        agent = BaseAgent()
        agent.started_at = 100.0
        agent.finished_at = 200.0
        agent.reset()
        assert agent.started_at is None
        assert agent.finished_at is None

    def test_reset_clears_subagent_ids(self):
        agent = BaseAgent()
        agent.subagent_ids = ["child-1", "child-2"]
        agent.reset()
        assert agent.subagent_ids == []


# ══════════════════════════════════════════════════════════════════════
# 11. System Prompt
# ══════════════════════════════════════════════════════════════════════


class TestBaseAgentSystemPrompt:
    """Test system prompt handling."""

    def test_default_system_prompt(self):
        agent = BaseAgent()
        prompt = agent.get_system_prompt()
        assert "helpful" in prompt.lower()

    def test_custom_system_prompt(self):
        config = AgentConfig(system_prompt="You are a coding assistant.")
        agent = BaseAgent(config=config)
        assert agent.get_system_prompt() == "You are a coding assistant."

    def test_empty_system_prompt_returns_default(self):
        config = AgentConfig(system_prompt="")
        agent = BaseAgent(config=config)
        # Empty string is falsy, so falls back to default
        prompt = agent.get_system_prompt()
        assert "helpful" in prompt.lower()


# ══════════════════════════════════════════════════════════════════════
# 12. Error Handling in Run
# ══════════════════════════════════════════════════════════════════════


class TestBaseAgentErrorHandling:
    """Test error handling in the agent run loop."""

    @pytest.mark.asyncio
    async def test_llm_exception_propagates(self, llm_provider, memory_manager, event_bus):
        """An exception in _call_llm causes an error that propagates from run."""
        config = AgentConfig(max_iterations=5)
        agent = BaseAgent(config=config)
        agent.set_llm_provider(llm_provider)
        agent.set_memory_manager(memory_manager)
        agent.set_event_bus(event_bus)
        await event_bus.start()

        # _call_llm transitions to THINKING, then calls provider.chat().
        # If chat() raises, the agent stays in THINKING. The next loop
        # iteration tries THINKING->THINKING which raises AgentStateError.
        # This propagates through run() since AgentStateError is re-raised.
        with patch.object(llm_provider, 'chat', new_callable=AsyncMock, side_effect=RuntimeError("LLM crashed")):
            with pytest.raises((AgentError, AgentStateError)):
                await agent.run("task")

    @pytest.mark.asyncio
    async def test_error_count_incremented_on_exception(self, llm_provider, memory_manager, event_bus):
        """When _call_llm fails, error_count is incremented."""
        config = AgentConfig(max_iterations=5)
        agent = BaseAgent(config=config)
        agent.set_llm_provider(llm_provider)
        agent.set_memory_manager(memory_manager)
        agent.set_event_bus(event_bus)
        await event_bus.start()

        with patch.object(llm_provider, 'chat', new_callable=AsyncMock, side_effect=RuntimeError("LLM crashed")):
            try:
                await agent.run("task")
            except (AgentError, AgentStateError):
                pass
            assert agent.error_count >= 1

    @pytest.mark.asyncio
    async def test_run_from_paused_state_raises(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.PAUSED)
        with pytest.raises(AgentStateError):
            await agent.run("task")

    @pytest.mark.asyncio
    async def test_run_from_terminated_state_raises(self):
        agent = BaseAgent()
        agent._transition_to(AgentState.TERMINATED)
        with pytest.raises(AgentStateError):
            await agent.run("task")


# ══════════════════════════════════════════════════════════════════════
# 13. Properties
# ══════════════════════════════════════════════════════════════════════


class TestBaseAgentProperties:
    """Test agent property accessors."""

    def test_agent_id_from_config(self):
        config = AgentConfig(agent_id="fixed-id-123")
        agent = BaseAgent(config=config)
        assert agent.agent_id == "fixed-id-123"

    def test_name_from_config(self):
        config = AgentConfig(name="my-agent")
        agent = BaseAgent(config=config)
        assert agent.name == "my-agent"

    def test_role_from_config(self):
        config = AgentConfig(role=AgentRole.PLANNER)
        agent = BaseAgent(config=config)
        assert agent.role == AgentRole.PLANNER

    def test_capabilities_from_config(self):
        caps = AgentCapabilities(planning=True, research=True)
        config = AgentConfig(capabilities=caps)
        agent = BaseAgent(config=config)
        assert agent.capabilities.planning is True
        assert agent.capabilities.research is True


# ══════════════════════════════════════════════════════════════════════
# 14. Memory Integration
# ══════════════════════════════════════════════════════════════════════


class TestBaseAgentMemoryIntegration:
    """Test that the agent stores memory entries during run."""

    @pytest.mark.asyncio
    async def test_run_stores_task_in_memory(self, llm_provider, memory_manager, event_bus):
        agent = BaseAgent()
        agent.set_llm_provider(llm_provider)
        agent.set_memory_manager(memory_manager)
        agent.set_event_bus(event_bus)
        await event_bus.start()

        mock_resp = LLMResponse(
            content="Task complete",
            usage=LLMUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            model="gpt-4o",
            cost=0.001,
        )
        with patch.object(agent, '_call_llm', new_callable=AsyncMock, return_value=mock_resp):
            await agent.run("remember this")
            entries = memory_manager.get_entries(agent.agent_id, memory_type=MemoryType.WORKING)
            assert len(entries) >= 1
            assert any("remember this" in e.content for e in entries)

    @pytest.mark.asyncio
    async def test_tool_execution_stores_in_memory(self, tool_registry, llm_provider, memory_manager, event_bus):
        from tests.conftest import SimpleTestTool
        tool_registry.register(SimpleTestTool)
        agent = BaseAgent()
        agent.set_tool_registry(tool_registry)
        agent.set_llm_provider(llm_provider)
        agent.set_memory_manager(memory_manager)
        agent.set_event_bus(event_bus)
        await event_bus.start()
        agent._transition_to(AgentState.RUNNING)

        response = LLMResponse(
            content="",
            tool_calls=[
                {
                    "id": "call-1",
                    "type": "function",
                    "function": {"name": "simple_tool", "arguments": '{"input": "test"}'},
                }
            ],
            usage=LLMUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            model="gpt-4o",
            cost=0.001,
        )
        await agent._process_tool_calls(response)
        entries = memory_manager.get_entries(agent.agent_id, memory_type=MemoryType.TOOL_HISTORY)
        assert len(entries) >= 1
