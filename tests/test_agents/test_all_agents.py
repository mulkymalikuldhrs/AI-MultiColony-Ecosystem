"""Comprehensive tests for all 9 agent types + AgentRegistry + AgentFactory.

Tests cover:
- Each agent can be instantiated with default config
- Each agent can be instantiated with custom config
- Each agent has correct required tools
- Each agent has correct default role, name, description
- Each agent has correct default capabilities
- Agent state transitions work for each agent type
- Agent-specific methods and history tracking
- AgentRegistry registration, lookup, creation, and listing
- AgentFactory creation from config, team creation, dynamic registration
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai_multicolony.agents.manus.agent import ToolCallAgent, ManusAgent
from ai_multicolony.agents.planner.agent import PlannerAgent
from ai_multicolony.agents.executor.agent import ExecutorAgent
from ai_multicolony.agents.coder.agent import CoderAgent
from ai_multicolony.agents.browser.agent import BrowserAgent
from ai_multicolony.agents.voice.agent import VoiceAgent
from ai_multicolony.agents.security.agent import SecurityAgent
from ai_multicolony.agents.researcher.agent import ResearcherAgent
from ai_multicolony.agents.colony.agent import ColonyAgent
from ai_multicolony.agents.registry import AgentRegistry, AgentFactory
from ai_multicolony.core.base_agent import BaseAgent
from ai_multicolony.core.event_bus import EventBus
from ai_multicolony.core.llm_provider import LLMProvider, LLMResponse, LLMUsage
from ai_multicolony.core.memory_manager import MemoryManager
from ai_multicolony.core.tool_registry import ToolRegistry
from ai_multicolony.exceptions import AgentNotFoundError, AgentStateError
from ai_multicolony.types.agent import AgentCapabilities, AgentConfig, AgentRole, AgentState
from ai_multicolony.types.colony import ColonyTask


# ══════════════════════════════════════════════════════════════════════
# Helper: All 9 agent classes
# ══════════════════════════════════════════════════════════════════════

ALL_AGENT_CLASSES = [
    ManusAgent,
    PlannerAgent,
    ExecutorAgent,
    CoderAgent,
    BrowserAgent,
    VoiceAgent,
    SecurityAgent,
    ResearcherAgent,
    ColonyAgent,
]

AGENT_ROLE_MAP = {
    ManusAgent: AgentRole.MANUS,
    PlannerAgent: AgentRole.PLANNER,
    ExecutorAgent: AgentRole.EXECUTOR,
    CoderAgent: AgentRole.CODER,
    BrowserAgent: AgentRole.BROWSER,
    VoiceAgent: AgentRole.VOICE,
    SecurityAgent: AgentRole.SECURITY,
    ResearcherAgent: AgentRole.RESEARCHER,
    ColonyAgent: AgentRole.COLONY,
}

AGENT_REQUIRED_TOOLS_MAP = {
    ManusAgent: ["shell", "file", "search", "code", "browser", "memory"],
    PlannerAgent: ["memory", "search"],
    ExecutorAgent: ["shell", "file", "code", "docker"],
    CoderAgent: ["code", "file", "shell", "search", "memory"],
    BrowserAgent: ["browser", "search", "file", "memory"],
    VoiceAgent: ["voice", "memory", "channel"],
    SecurityAgent: ["shell", "file", "code", "memory"],
    ResearcherAgent: ["search", "browser", "file", "memory"],
    ColonyAgent: ["memory", "channel", "search"],
}


# ══════════════════════════════════════════════════════════════════════
# 1. Instantiation & Defaults for All 9 Agents
# ══════════════════════════════════════════════════════════════════════


class TestAgentInstantiation:
    """Test that each agent can be instantiated with default config."""

    @pytest.mark.parametrize("agent_cls", ALL_AGENT_CLASSES,
                             ids=[c.__name__ for c in ALL_AGENT_CLASSES])
    def test_instantiate_default(self, agent_cls):
        agent = agent_cls()
        assert agent is not None
        assert isinstance(agent, BaseAgent)

    @pytest.mark.parametrize("agent_cls", ALL_AGENT_CLASSES,
                             ids=[c.__name__ for c in ALL_AGENT_CLASSES])
    def test_default_state_is_idle(self, agent_cls):
        agent = agent_cls()
        assert agent.state == AgentState.IDLE

    @pytest.mark.parametrize("agent_cls,expected_role", list(AGENT_ROLE_MAP.items()),
                             ids=[c.__name__ for c in AGENT_ROLE_MAP.keys()])
    def test_default_role(self, agent_cls, expected_role):
        agent = agent_cls()
        assert agent.role == expected_role

    @pytest.mark.parametrize("agent_cls", ALL_AGENT_CLASSES,
                             ids=[c.__name__ for c in ALL_AGENT_CLASSES])
    def test_has_agent_id(self, agent_cls):
        agent = agent_cls()
        assert agent.agent_id is not None
        assert len(agent.agent_id) > 0

    @pytest.mark.parametrize("agent_cls", ALL_AGENT_CLASSES,
                             ids=[c.__name__ for c in ALL_AGENT_CLASSES])
    def test_has_name(self, agent_cls):
        agent = agent_cls()
        assert agent.name is not None
        assert len(agent.name) > 0

    @pytest.mark.parametrize("agent_cls", ALL_AGENT_CLASSES,
                             ids=[c.__name__ for c in ALL_AGENT_CLASSES])
    def test_default_iteration_count_zero(self, agent_cls):
        agent = agent_cls()
        assert agent.iteration_count == 0

    @pytest.mark.parametrize("agent_cls", ALL_AGENT_CLASSES,
                             ids=[c.__name__ for c in ALL_AGENT_CLASSES])
    def test_default_error_count_zero(self, agent_cls):
        agent = agent_cls()
        assert agent.error_count == 0

    @pytest.mark.parametrize("agent_cls", ALL_AGENT_CLASSES,
                             ids=[c.__name__ for c in ALL_AGENT_CLASSES])
    def test_default_messages_empty(self, agent_cls):
        agent = agent_cls()
        assert agent.messages == []


# ══════════════════════════════════════════════════════════════════════
# 2. Required Tools
# ══════════════════════════════════════════════════════════════════════


class TestAgentRequiredTools:
    """Test that each agent returns correct required tools."""

    @pytest.mark.parametrize("agent_cls,expected_tools", list(AGENT_REQUIRED_TOOLS_MAP.items()),
                             ids=[c.__name__ for c in AGENT_REQUIRED_TOOLS_MAP.keys()])
    def test_get_required_tools(self, agent_cls, expected_tools):
        assert agent_cls.get_required_tools() == expected_tools

    @pytest.mark.parametrize("agent_cls", ALL_AGENT_CLASSES,
                             ids=[c.__name__ for c in ALL_AGENT_CLASSES])
    def test_get_required_tools_returns_list(self, agent_cls):
        tools = agent_cls.get_required_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0

    @pytest.mark.parametrize("agent_cls", ALL_AGENT_CLASSES,
                             ids=[c.__name__ for c in ALL_AGENT_CLASSES])
    def test_get_required_tools_strings(self, agent_cls):
        tools = agent_cls.get_required_tools()
        for t in tools:
            assert isinstance(t, str)

    @pytest.mark.parametrize("agent_cls", ALL_AGENT_CLASSES,
                             ids=[c.__name__ for c in ALL_AGENT_CLASSES])
    def test_config_tools_match_required(self, agent_cls):
        """Default config.tools should contain at least required tools."""
        agent = agent_cls()
        for t in agent_cls.get_required_tools():
            assert t in agent.config.tools, f"Required tool '{t}' not in config.tools"


# ══════════════════════════════════════════════════════════════════════
# 3. System Prompt
# ══════════════════════════════════════════════════════════════════════


class TestAgentSystemPrompt:
    """Test that each agent has a non-empty system prompt."""

    @pytest.mark.parametrize("agent_cls", ALL_AGENT_CLASSES,
                             ids=[c.__name__ for c in ALL_AGENT_CLASSES])
    def test_system_prompt_not_empty(self, agent_cls):
        agent = agent_cls()
        prompt = agent.get_system_prompt()
        assert prompt is not None
        assert len(prompt) > 0

    @pytest.mark.parametrize("agent_cls", ALL_AGENT_CLASSES,
                             ids=[c.__name__ for c in ALL_AGENT_CLASSES])
    def test_config_system_prompt_matches(self, agent_cls):
        agent = agent_cls()
        assert agent.config.system_prompt == agent.get_system_prompt()


# ══════════════════════════════════════════════════════════════════════
# 4. Custom Config
# ══════════════════════════════════════════════════════════════════════


class TestAgentCustomConfig:
    """Test that agents accept custom config."""

    @pytest.mark.parametrize("agent_cls", ALL_AGENT_CLASSES,
                             ids=[c.__name__ for c in ALL_AGENT_CLASSES])
    def test_custom_name(self, agent_cls):
        config = AgentConfig(name="custom-name")
        agent = agent_cls(config=config)
        assert agent.name == "custom-name"

    @pytest.mark.parametrize("agent_cls", ALL_AGENT_CLASSES,
                             ids=[c.__name__ for c in ALL_AGENT_CLASSES])
    def test_custom_model(self, agent_cls):
        config = AgentConfig(model="gpt-4-turbo")
        agent = agent_cls(config=config)
        assert agent.config.model == "gpt-4-turbo"

    @pytest.mark.parametrize("agent_cls", ALL_AGENT_CLASSES,
                             ids=[c.__name__ for c in ALL_AGENT_CLASSES])
    def test_custom_max_iterations(self, agent_cls):
        config = AgentConfig(max_iterations=42)
        agent = agent_cls(config=config)
        assert agent.config.max_iterations == 42

    @pytest.mark.parametrize("agent_cls", ALL_AGENT_CLASSES,
                             ids=[c.__name__ for c in ALL_AGENT_CLASSES])
    def test_custom_system_prompt_overrides(self, agent_cls):
        config = AgentConfig(system_prompt="Custom prompt")
        agent = agent_cls(config=config)
        # When config has a system prompt, the agent uses it
        assert agent.config.system_prompt == "Custom prompt"

    @pytest.mark.parametrize("agent_cls", ALL_AGENT_CLASSES,
                             ids=[c.__name__ for c in ALL_AGENT_CLASSES])
    def test_default_config_no_system_prompt_gets_agent_default(self, agent_cls):
        """If config has no system_prompt, the agent provides its own."""
        config = AgentConfig(system_prompt=None)
        agent = agent_cls(config=config)
        # After construction, config.system_prompt should be set by the agent
        prompt = agent.get_system_prompt()
        assert len(prompt) > 0


# ══════════════════════════════════════════════════════════════════════
# 5. Agent State Transitions
# ══════════════════════════════════════════════════════════════════════


class TestAgentStateTransitions:
    """Test state transitions work for each agent type."""

    @pytest.mark.parametrize("agent_cls", ALL_AGENT_CLASSES,
                             ids=[c.__name__ for c in ALL_AGENT_CLASSES])
    def test_idle_to_running(self, agent_cls):
        agent = agent_cls()
        agent._transition_to(AgentState.RUNNING)
        assert agent.state == AgentState.RUNNING

    @pytest.mark.parametrize("agent_cls", ALL_AGENT_CLASSES,
                             ids=[c.__name__ for c in ALL_AGENT_CLASSES])
    def test_running_to_paused(self, agent_cls):
        agent = agent_cls()
        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.PAUSED)
        assert agent.state == AgentState.PAUSED

    @pytest.mark.parametrize("agent_cls", ALL_AGENT_CLASSES,
                             ids=[c.__name__ for c in ALL_AGENT_CLASSES])
    def test_running_to_error(self, agent_cls):
        agent = agent_cls()
        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.ERROR)
        assert agent.state == AgentState.ERROR

    @pytest.mark.parametrize("agent_cls", ALL_AGENT_CLASSES,
                             ids=[c.__name__ for c in ALL_AGENT_CLASSES])
    def test_error_to_running(self, agent_cls):
        agent = agent_cls()
        agent._transition_to(AgentState.RUNNING)
        agent._transition_to(AgentState.ERROR)
        agent._transition_to(AgentState.RUNNING)
        assert agent.state == AgentState.RUNNING

    @pytest.mark.parametrize("agent_cls", ALL_AGENT_CLASSES,
                             ids=[c.__name__ for c in ALL_AGENT_CLASSES])
    def test_invalid_transition_raises(self, agent_cls):
        agent = agent_cls()
        with pytest.raises(AgentStateError):
            agent._transition_to(AgentState.PAUSED)  # IDLE -> PAUSED invalid


# ══════════════════════════════════════════════════════════════════════
# 6. Agent-Specific Methods
# ══════════════════════════════════════════════════════════════════════


class TestManusAgentSpecific:
    """Test ManusAgent/ToolCallAgent specific features."""

    def test_tool_stats_initial(self):
        agent = ManusAgent()
        stats = agent.get_tool_stats()
        assert stats["total_tool_calls"] == 0
        assert stats["successful_tool_calls"] == 0
        assert stats["failed_tool_calls"] == 0
        assert stats["consecutive_failures"] == 0
        assert stats["success_rate"] == 0.0

    def test_toolcall_agent_inherits_manus(self):
        agent = ManusAgent()
        assert isinstance(agent, ToolCallAgent)

    def test_toolcall_agent_required_tools(self):
        assert ToolCallAgent.get_required_tools() == ["shell", "file", "search", "memory"]


class TestPlannerAgentSpecific:
    """Test PlannerAgent specific features."""

    def test_plan_history_initially_empty(self):
        agent = PlannerAgent()
        assert agent.get_plan_history() == []

    def test_clear_plan_history(self):
        agent = PlannerAgent()
        agent._plan_history.append({"task": "test"})
        agent.clear_plan_history()
        assert agent.get_plan_history() == []

    def test_parse_json_plan(self):
        agent = PlannerAgent()
        plan_text = '[{"title": "Task 1", "description": "Do stuff"}, {"title": "Task 2"}]'
        tasks = agent._parse_plan(plan_text, "parent")
        assert len(tasks) == 2
        assert tasks[0].title == "Task 1"
        assert tasks[1].title == "Task 2"

    def test_parse_markdown_plan(self):
        agent = PlannerAgent()
        plan_text = "### Subtask: Write code\n- Description: Implement feature\n- Agent: code"
        tasks = agent._parse_markdown_plan(plan_text, "parent")
        assert len(tasks) >= 1
        assert any("Write code" in t.title for t in tasks)

    def test_parse_line_plan(self):
        agent = PlannerAgent()
        plan_text = "1. First step\n2. Second step\n3. Third step"
        tasks = agent._parse_line_plan(plan_text, "parent")
        assert len(tasks) == 3

    def test_parse_empty_plan_returns_single_task(self):
        agent = PlannerAgent()
        tasks = agent._parse_plan("", "parent task")
        assert len(tasks) == 1
        assert tasks[0].title == "parent task"

    def test_parse_json_array_of_strings(self):
        agent = PlannerAgent()
        plan_text = '["Step one", "Step two"]'
        tasks = agent._try_parse_json_plan(plan_text, "parent")
        assert len(tasks) == 2


class TestExecutorAgentSpecific:
    """Test ExecutorAgent specific features."""

    def test_execution_log_initially_empty(self):
        agent = ExecutorAgent()
        assert agent.get_execution_log() == []

    def test_clear_execution_log(self):
        agent = ExecutorAgent()
        agent._execution_log.append({"status": "error"})
        agent.clear_execution_log()
        assert agent.get_execution_log() == []

    def test_max_retries_default(self):
        agent = ExecutorAgent()
        assert agent._max_retries == 2


class TestCoderAgentSpecific:
    """Test CoderAgent specific features."""

    def test_code_changes_initially_empty(self):
        agent = CoderAgent()
        assert agent.get_code_changes() == []

    def test_clear_code_changes(self):
        agent = CoderAgent()
        agent._code_changes.append({"type": "write"})
        agent.clear_code_changes()
        assert agent.get_code_changes() == []
        assert agent._debug_attempts == 0

    def test_max_debug_attempts(self):
        agent = CoderAgent()
        assert agent._max_debug_attempts == 3


class TestBrowserAgentSpecific:
    """Test BrowserAgent specific features."""

    def test_browsing_history_initially_empty(self):
        agent = BrowserAgent()
        assert agent.get_browsing_history() == []

    def test_stealth_mode_default(self):
        agent = BrowserAgent()
        assert agent._stealth_mode is True

    def test_enable_disable_stealth(self):
        agent = BrowserAgent()
        agent.disable_stealth()
        assert agent._stealth_mode is False
        agent.enable_stealth()
        assert agent._stealth_mode is True

    def test_set_rate_limit_wait(self):
        agent = BrowserAgent()
        agent.set_rate_limit_wait(2.5)
        assert agent._rate_limit_wait == 2.5

    def test_rate_limit_wait_non_negative(self):
        agent = BrowserAgent()
        agent.set_rate_limit_wait(-1.0)
        assert agent._rate_limit_wait == 0.0

    def test_clear_browsing_history(self):
        agent = BrowserAgent()
        agent._browsing_history.append({"url": "http://test.com"})
        agent._pages_visited = 5
        agent.clear_browsing_history()
        assert agent.get_browsing_history() == []
        assert agent._pages_visited == 0


class TestVoiceAgentSpecific:
    """Test VoiceAgent specific features."""

    def test_conversation_history_initially_empty(self):
        agent = VoiceAgent()
        assert agent.get_conversation_history() == []

    def test_default_language_is_en(self):
        agent = VoiceAgent()
        assert agent.current_language == "en"

    def test_set_language_supported(self):
        agent = VoiceAgent()
        agent.set_language("es")
        assert agent.current_language == "es"

    def test_set_language_unsupported_still_set(self):
        agent = VoiceAgent()
        agent.set_language("xx")
        assert agent.current_language == "xx"

    def test_supported_languages_list(self):
        agent = VoiceAgent()
        assert "en" in agent._languages_supported
        assert "es" in agent._languages_supported
        assert "fr" in agent._languages_supported
        assert "de" in agent._languages_supported
        assert "zh" in agent._languages_supported
        assert "ja" in agent._languages_supported
        assert "ko" in agent._languages_supported

    def test_is_listening_default_false(self):
        agent = VoiceAgent()
        assert agent.is_listening is False

    def test_start_stop_listening(self):
        agent = VoiceAgent()
        agent.start_listening()
        assert agent.is_listening is True
        agent.stop_listening()
        assert agent.is_listening is False

    def test_clear_conversation_history(self):
        agent = VoiceAgent()
        agent._conversation_history.append({"type": "transcription"})
        agent.clear_conversation_history()
        assert agent.get_conversation_history() == []


class TestSecurityAgentSpecific:
    """Test SecurityAgent specific features."""

    def test_findings_initially_empty(self):
        agent = SecurityAgent()
        assert agent.get_findings() == []

    def test_critical_findings_empty(self):
        agent = SecurityAgent()
        assert agent.get_critical_findings() == []

    def test_high_findings_empty(self):
        agent = SecurityAgent()
        assert agent.get_high_findings() == []

    def test_audit_log_initially_empty(self):
        agent = SecurityAgent()
        assert agent.get_audit_log() == []

    def test_incidents_initially_empty(self):
        agent = SecurityAgent()
        assert agent.get_incidents() == []

    def test_parse_findings(self):
        agent = SecurityAgent()
        result = "CRITICAL: SQL injection found\nHIGH: XSS vulnerability\nNormal line"
        findings = agent._parse_findings(result)
        assert len(findings) == 2
        assert findings[0]["severity"] == "CRITICAL"
        assert findings[1]["severity"] == "HIGH"

    def test_get_findings_filtered_by_severity(self):
        agent = SecurityAgent()
        agent._findings = [
            {"severity": "CRITICAL", "description": "A"},
            {"severity": "HIGH", "description": "B"},
            {"severity": "LOW", "description": "C"},
        ]
        critical = agent.get_findings("CRITICAL")
        assert len(critical) == 1
        assert critical[0]["severity"] == "CRITICAL"

    def test_clear_findings(self):
        agent = SecurityAgent()
        agent._findings.append({"severity": "HIGH"})
        agent._audit_log.append({"action": "test"})
        agent._incidents.append({"incident": "test"})
        agent._scan_count = 5
        agent.clear_findings()
        assert agent.get_findings() == []
        assert agent.get_audit_log() == []
        assert agent.get_incidents() == []
        assert agent._scan_count == 0


class TestResearcherAgentSpecific:
    """Test ResearcherAgent specific features."""

    def test_research_log_initially_empty(self):
        agent = ResearcherAgent()
        assert agent.get_research_log() == []

    def test_stats_initial(self):
        agent = ResearcherAgent()
        stats = agent.get_stats()
        assert stats["queries_made"] == 0
        assert stats["sources_found"] == 0
        assert stats["research_tasks"] == 0

    def test_clear_research_log(self):
        agent = ResearcherAgent()
        agent._research_log.append({"type": "research"})
        agent._sources_found = 10
        agent._queries_made = 5
        agent.clear_research_log()
        assert agent.get_research_log() == []
        assert agent._sources_found == 0
        assert agent._queries_made == 0


class TestColonyAgentSpecific:
    """Test ColonyAgent specific features."""

    def test_task_queue_initially_empty(self):
        agent = ColonyAgent()
        assert agent.get_pending_tasks() == []

    def test_completed_tasks_initially_empty(self):
        agent = ColonyAgent()
        assert agent.get_completed_tasks() == []

    def test_failed_tasks_initially_empty(self):
        agent = ColonyAgent()
        assert agent.get_failed_tasks() == []

    def test_add_task(self):
        agent = ColonyAgent()
        task = ColonyTask(title="Test task", description="desc", priority=1, status="pending")
        agent.add_task(task)
        pending = agent.get_pending_tasks()
        assert len(pending) == 1
        assert pending[0].title == "Test task"

    def test_add_tasks(self):
        agent = ColonyAgent()
        tasks = [
            ColonyTask(title="T1", description="", priority=1, status="pending"),
            ColonyTask(title="T2", description="", priority=2, status="pending"),
        ]
        agent.add_tasks(tasks)
        assert len(agent.get_pending_tasks()) == 2

    def test_pop_next_task(self):
        agent = ColonyAgent()
        task = ColonyTask(title="First", description="", priority=1, status="pending")
        agent.add_task(task)
        popped = agent.pop_next_task()
        assert popped is not None
        assert popped.title == "First"
        assert agent.pop_next_task() is None

    def test_pop_next_task_empty(self):
        agent = ColonyAgent()
        assert agent.pop_next_task() is None

    def test_route_task_keyword_matching(self):
        agent = ColonyAgent()
        # Verify routing table entries for keyword matching
        assert "code" in agent._routing_table
        assert agent._routing_table["code"] == AgentRole.CODER

    def test_update_routing(self):
        agent = ColonyAgent()
        agent.update_routing("deploy", AgentRole.EXECUTOR)
        assert agent._routing_table["deploy"] == AgentRole.EXECUTOR

    def test_get_routing_table(self):
        agent = ColonyAgent()
        table = agent.get_routing_table()
        assert isinstance(table, dict)
        assert "code" in table
        assert table["code"] == "coder"

    def test_clear_history(self):
        agent = ColonyAgent()
        agent._task_queue.append(ColonyTask(title="T", description="", priority=1, status="pending"))
        agent._completed_tasks.append({"task": "done"})
        agent._failed_tasks.append({"task": "fail"})
        agent.clear_history()
        assert agent.get_pending_tasks() == []
        assert agent.get_completed_tasks() == []
        assert agent.get_failed_tasks() == []

    def test_default_routing_has_all_roles(self):
        agent = ColonyAgent()
        routing = agent._routing_table
        # Check that each expected keyword maps to a role
        assert routing.get("code") == AgentRole.CODER
        assert routing.get("browse") == AgentRole.BROWSER
        assert routing.get("search") == AgentRole.RESEARCHER
        assert routing.get("security") == AgentRole.SECURITY
        assert routing.get("voice") == AgentRole.VOICE
        assert routing.get("plan") == AgentRole.PLANNER
        assert routing.get("execute") == AgentRole.EXECUTOR


# ══════════════════════════════════════════════════════════════════════
# 7. Agent Registry
# ══════════════════════════════════════════════════════════════════════


class TestAgentRegistry:
    """Test AgentRegistry registration, lookup, and creation."""

    def setup_method(self):
        AgentRegistry.reset()

    def teardown_method(self):
        AgentRegistry.reset()

    def test_auto_discover_loads_agents(self):
        registry = AgentRegistry()
        assert registry.agent_count >= 1  # At least some agents should load

    def test_get_instance_singleton(self):
        r1 = AgentRegistry.get_instance()
        r2 = AgentRegistry.get_instance()
        assert r1 is r2

    def test_reset_clears_singleton(self):
        r1 = AgentRegistry.get_instance()
        AgentRegistry.reset()
        r2 = AgentRegistry.get_instance()
        assert r1 is not r2

    def test_register_custom_agent(self):
        registry = AgentRegistry()
        registry.register("custom", ManusAgent)
        assert "custom" in registry.agent_names

    def test_register_non_basetype_raises(self):
        registry = AgentRegistry()
        with pytest.raises(TypeError):
            registry.register("bad", str)

    def test_unregister(self):
        registry = AgentRegistry()
        registry.register("temp", ManusAgent)
        registry.unregister("temp")
        with pytest.raises(KeyError):
            registry.get("temp")

    def test_get_unknown_raises_keyerror(self):
        registry = AgentRegistry()
        with pytest.raises(KeyError) as exc_info:
            registry.get("nonexistent")
        assert "nonexistent" in str(exc_info.value)

    def test_get_known_returns_class(self):
        registry = AgentRegistry()
        registry.register("manus", ManusAgent)
        cls = registry.get("manus")
        assert cls is ManusAgent

    def test_create_returns_instance(self):
        registry = AgentRegistry()
        registry.register("manus", ManusAgent)
        agent = registry.create("manus")
        assert isinstance(agent, ManusAgent)
        assert isinstance(agent, BaseAgent)

    def test_create_unknown_raises(self):
        registry = AgentRegistry()
        with pytest.raises(KeyError):
            registry.create("nonexistent")

    def test_create_tracks_instance(self):
        registry = AgentRegistry()
        registry.register("manus", ManusAgent)
        agent = registry.create("manus")
        assert registry.instance_count >= 1

    def test_get_instance_by_id(self):
        registry = AgentRegistry()
        registry.register("manus", ManusAgent)
        agent = registry.create("manus")
        found = registry.get_instance_by_id(agent.agent_id)
        assert found is agent

    def test_get_instance_by_id_not_found(self):
        registry = AgentRegistry()
        with pytest.raises(AgentNotFoundError):
            registry.get_instance_by_id("nonexistent-id")

    def test_agent_names_property(self):
        registry = AgentRegistry()
        registry.register("manus", ManusAgent)
        registry.register("planner", PlannerAgent)
        names = registry.agent_names
        assert "manus" in names
        assert "planner" in names

    def test_list_all(self):
        registry = AgentRegistry()
        registry.register("manus", ManusAgent)
        info = registry.list_all()
        assert "manus" in info
        assert "description" in info["manus"]

    def test_list_instances(self):
        registry = AgentRegistry()
        registry.register("manus", ManusAgent)
        registry.create("manus")
        instances = registry.list_instances()
        assert len(instances) >= 1

    def test_get_state(self):
        registry = AgentRegistry()
        registry.register("manus", ManusAgent)
        agent = registry.create("manus")
        state = registry.get_state(agent.agent_id)
        assert state.state == AgentState.IDLE

    def test_get_state_not_found(self):
        registry = AgentRegistry()
        with pytest.raises(AgentNotFoundError):
            registry.get_state("missing")

    def test_create_with_model(self):
        registry = AgentRegistry()
        registry.register("manus", ManusAgent)
        agent = registry.create("manus", model="gpt-4-turbo")
        assert agent.config.model == "gpt-4-turbo"

    def test_create_with_tools(self):
        registry = AgentRegistry()
        registry.register("manus", ManusAgent)
        agent = registry.create("manus", tools=["shell", "file"])
        assert "shell" in agent.config.tools
        assert "file" in agent.config.tools

    def test_create_with_event_bus(self):
        registry = AgentRegistry()
        registry.register("manus", ManusAgent)
        bus = EventBus()
        agent = registry.create("manus", event_bus=bus)
        assert agent._event_bus is bus

    def test_create_with_memory_manager(self):
        registry = AgentRegistry()
        registry.register("manus", ManusAgent)
        mm = MemoryManager()
        agent = registry.create("manus", memory_manager=mm)
        assert agent._memory_manager is mm


# ══════════════════════════════════════════════════════════════════════
# 8. Agent Factory
# ══════════════════════════════════════════════════════════════════════


class TestAgentFactory:
    """Test AgentFactory creation from config and team creation."""

    def setup_method(self):
        AgentRegistry.reset()

    def teardown_method(self):
        AgentRegistry.reset()

    def test_create_from_config(self):
        registry = AgentRegistry()
        registry.register("manus", ManusAgent)
        factory = AgentFactory(registry=registry)
        agent = factory.create_from_config({"type": "manus"})
        assert isinstance(agent, ManusAgent)

    def test_create_from_config_missing_type_raises(self):
        registry = AgentRegistry()
        factory = AgentFactory(registry=registry)
        with pytest.raises(ValueError, match="type"):
            factory.create_from_config({})

    def test_create_from_config_with_name(self):
        registry = AgentRegistry()
        registry.register("manus", ManusAgent)
        factory = AgentFactory(registry=registry)
        agent = factory.create_from_config({"type": "manus", "name": "my-agent"})
        assert agent.name == "my-agent"

    def test_create_from_config_with_model(self):
        registry = AgentRegistry()
        registry.register("manus", ManusAgent)
        factory = AgentFactory(registry=registry)
        agent = factory.create_from_config({"type": "manus", "model": "gpt-4-turbo"})
        assert agent.config.model == "gpt-4-turbo"

    def test_create_from_config_with_tools(self):
        registry = AgentRegistry()
        registry.register("manus", ManusAgent)
        factory = AgentFactory(registry=registry)
        agent = factory.create_from_config({"type": "manus", "tools": ["shell", "code"]})
        assert "shell" in agent.config.tools
        assert "code" in agent.config.tools

    def test_create_from_config_with_capabilities(self):
        registry = AgentRegistry()
        registry.register("manus", ManusAgent)
        factory = AgentFactory(registry=registry)
        agent = factory.create_from_config({
            "type": "manus",
            "capabilities": {"code_generation": True, "web_browsing": True},
        })
        assert agent.capabilities.code_generation is True
        assert agent.capabilities.web_browsing is True

    def test_create_team(self):
        registry = AgentRegistry()
        registry.register("manus", ManusAgent)
        registry.register("coder", CoderAgent)
        factory = AgentFactory(registry=registry)
        team = factory.create_team([
            {"type": "manus", "name": "team-manus"},
            {"type": "coder", "name": "team-coder"},
        ])
        assert len(team) == 2
        assert "team-manus" in team
        assert "team-coder" in team

    def test_create_default_team(self):
        registry = AgentRegistry()
        registry.register("manus", ManusAgent)
        registry.register("coder", CoderAgent)
        factory = AgentFactory(registry=registry)
        team = factory.create_default_team()
        assert len(team) >= 2

    def test_register_agent_type(self):
        registry = AgentRegistry()
        factory = AgentFactory(registry=registry)
        factory.register_agent_type("custom", ManusAgent)
        assert "custom" in registry.agent_names

    def test_available_types(self):
        registry = AgentRegistry()
        registry.register("manus", ManusAgent)
        factory = AgentFactory(registry=registry)
        assert "manus" in factory.available_types

    def test_set_event_bus(self):
        registry = AgentRegistry()
        factory = AgentFactory(registry=registry)
        bus = EventBus()
        factory.set_event_bus(bus)
        assert factory._event_bus is bus

    def test_set_llm_provider(self):
        registry = AgentRegistry()
        factory = AgentFactory(registry=registry)
        provider = LLMProvider(default_model="gpt-4o")
        factory.set_llm_provider(provider)
        assert factory._llm_provider is provider

    def test_set_tool_registry(self):
        registry = AgentRegistry()
        factory = AgentFactory(registry=registry)
        tr = ToolRegistry()
        factory.set_tool_registry(tr)
        assert factory._tool_registry is tr

    def test_set_memory_manager(self):
        registry = AgentRegistry()
        factory = AgentFactory(registry=registry)
        mm = MemoryManager()
        factory.set_memory_manager(mm)
        assert factory._memory_manager is mm

    def test_create_from_config_with_description(self):
        registry = AgentRegistry()
        registry.register("manus", ManusAgent)
        factory = AgentFactory(registry=registry)
        agent = factory.create_from_config({"type": "manus", "description": "My custom agent"})
        assert agent.config.description == "My custom agent"

    def test_create_from_config_with_temperature(self):
        registry = AgentRegistry()
        registry.register("manus", ManusAgent)
        factory = AgentFactory(registry=registry)
        agent = factory.create_from_config({"type": "manus", "temperature": 0.5})
        assert agent.config.temperature == 0.5

    def test_create_from_config_unknown_type_raises(self):
        registry = AgentRegistry()
        factory = AgentFactory(registry=registry)
        with pytest.raises(KeyError):
            factory.create_from_config({"type": "nonexistent"})

    def test_registry_property(self):
        registry = AgentRegistry()
        factory = AgentFactory(registry=registry)
        assert factory.registry is registry
