"""Tests for MemoryManager — memory operations, condensers, paging."""

from __future__ import annotations

import pytest

from ai_multicolony.core.event_bus import EventBus
from ai_multicolony.core.memory_manager import (
    BaseCondenser,
    MemoryManager,
    NoOpCondenser,
    RecentCondenser,
    ObservationCondenser,
)
from ai_multicolony.types.events import Action, ActionType, Event, EventType, Observation, ObservationType
from ai_multicolony.types.memory import MemoryEntry, MemoryType, MemoryQuery


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_event_bus():
    EventBus.reset()
    yield
    EventBus.reset()


@pytest.fixture
def manager():
    return MemoryManager()


@pytest.fixture
def sample_events():
    return [
        Event(event_type=EventType.ACTION, source="agent-1",
              action=Action(action_type=ActionType.THINK, agent_id="agent-1", thought="thinking")),
        Event(event_type=EventType.OBSERVATION, source="agent-1",
              observation=Observation(observation_type=ObservationType.SUCCESS, agent_id="agent-1", content="done")),
        Event(event_type=EventType.CUSTOM, source="agent-1", data={"key": "value"}),
    ]


# ── MemoryManager Core ────────────────────────────────────────────────────

class TestMemoryManagerCore:
    """Test basic memory operations."""

    def test_add_entry(self, manager):
        entry = manager.add_entry(
            agent_id="agent-1",
            content="Test memory",
            memory_type=MemoryType.WORKING,
            importance=0.5,
            tags=[],  # Must be list
            source="test",
        )
        assert isinstance(entry, MemoryEntry)
        assert entry.content == "Test memory"
        assert entry.memory_type == MemoryType.WORKING

    def test_query_by_agent(self, manager):
        manager.add_entry("agent-1", "Memory 1", MemoryType.WORKING, 0.5, [], "test")
        manager.add_entry("agent-2", "Memory 2", MemoryType.WORKING, 0.5, [], "test")
        manager.add_entry("agent-1", "Memory 3", MemoryType.EPISODIC, 0.5, [], "test")

        results = manager.query(MemoryQuery(query="", agent_id="agent-1"))
        assert len(results.entries) >= 2

    def test_query_by_type(self, manager):
        manager.add_entry("agent-1", "Working", MemoryType.WORKING, 0.5, [], "test")
        manager.add_entry("agent-1", "Episodic", MemoryType.EPISODIC, 0.5, [], "test")

        results = manager.query(MemoryQuery(query="", memory_types=[MemoryType.WORKING]))
        assert all(e.memory_type == MemoryType.WORKING for e in results.entries)

    def test_query_by_importance(self, manager):
        manager.add_entry("agent-1", "Low", MemoryType.WORKING, 0.2, [], "test")
        manager.add_entry("agent-1", "High", MemoryType.WORKING, 0.9, [], "test")

        results = manager.query(MemoryQuery(query="", min_importance=0.5))
        assert all(e.importance >= 0.5 for e in results.entries)

    def test_clear_entries(self, manager):
        manager.add_entry("agent-1", "Memory", MemoryType.WORKING, 0.5, [], "test")
        manager.clear_entries(agent_id="agent-1")
        results = manager.query(MemoryQuery(query="", agent_id="agent-1"))
        assert len(results.entries) == 0


# ── Condensers ────────────────────────────────────────────────────────────

class TestNoOpCondenser:
    """Test NoOpCondenser."""

    def test_returns_all_events(self, sample_events):
        condenser = NoOpCondenser()
        result = condenser.condense(sample_events)
        assert len(result) == len(sample_events)

    def test_condenser_type(self):
        assert NoOpCondenser().condenser_type.value == "noop"


class TestRecentCondenser:
    """Test RecentCondenser."""

    def test_keeps_only_recent(self):
        events = [Event(event_type=EventType.CUSTOM, source=f"src-{i}") for i in range(10)]
        condenser = RecentCondenser(max_events=3)
        result = condenser.condense(events)
        assert len(result) == 3
        # Should keep the last 3
        assert result[-1].source == "src-9"

    def test_condenser_type(self):
        assert RecentCondenser().condenser_type.value == "recent"


class TestObservationCondenser:
    """Test ObservationCondenser."""

    def test_keeps_observations(self):
        events = [
            Event(event_type=EventType.OBSERVATION, source="agent",
                  observation=Observation(observation_type=ObservationType.SUCCESS, agent_id="agent", content="ok")),
            Event(event_type=EventType.ACTION, source="agent",
                  action=Action(action_type=ActionType.THINK, agent_id="agent")),
            Event(event_type=EventType.OBSERVATION, source="agent",
                  observation=Observation(observation_type=ObservationType.ERROR, agent_id="agent", content="err")),
        ]
        condenser = ObservationCondenser(keep_recent_actions=1)
        result = condenser.condense(events)
        # Should keep 2 observations + 1 recent action
        assert len(result) >= 2


# ── Memory Paging ─────────────────────────────────────────────────────────

class TestMemoryPaging:
    """Test Letta-style memory paging."""

    def test_create_session(self, manager):
        session = manager.create_session(agent_id="agent-1")
        assert session is not None
        assert session.agent_id == "agent-1"

    def test_get_session(self, manager):
        created = manager.create_session(agent_id="agent-1")
        retrieved = manager.get_session(created.id)  # Use .id, not .session_id
        assert retrieved is not None
        assert retrieved.id == created.id

    def test_get_nonexistent_session(self, manager):
        result = manager.get_session("nonexistent")
        assert result is None


# ── Memory Types ──────────────────────────────────────────────────────────

class TestMemoryTypes:
    """Test memory type enum values."""

    def test_memory_types_exist(self):
        assert MemoryType.WORKING.value == "working"
        assert MemoryType.EPISODIC.value == "episodic"
        assert MemoryType.TOOL_HISTORY.value == "tool_history"
        assert MemoryType.SEMANTIC.value == "semantic"
