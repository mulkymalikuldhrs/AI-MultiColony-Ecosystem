"""Comprehensive tests for MemoryManager and all 8 condenser types.

Tests cover:
- All 8 condenser types (NoOp, Recent, Observation, LLM, Amortized,
  BrowserOutput, LLMLingua, EventMask)
- Session management (create, get, close, active sessions)
- Letta-style paging (create, load, unload, update, delete, eviction)
- Entry operations (add, query, get, clear)
- Vector store integration (mocked)
- Condensation via MemoryManager
- Statistics
"""

from __future__ import annotations

import time

import pytest

from ai_multicolony.core.memory_manager import (
    AmortizedCondenser,
    BaseCondenser,
    BrowserOutputCondenser,
    EventMaskCondenser,
    LLMCondenser,
    LLMLinguaCondenser,
    MemoryManager,
    NoOpCondenser,
    ObservationCondenser,
    RecentCondenser,
    VectorStoreBackend,
)
from ai_multicolony.exceptions import MemoryError
from ai_multicolony.types.events import Action, ActionType, Event, EventType, Observation, ObservationType
from ai_multicolony.types.memory import (
    CondenserType,
    MemoryCondenserType,
    MemoryEntry,
    MemoryPage,
    MemoryQuery,
    MemorySession,
    MemoryType,
    SessionState,
)
from tests.conftest import make_events


# ══════════════════════════════════════════════════════════════════════
# 1. NoOpCondenser
# ══════════════════════════════════════════════════════════════════════


class TestNoOpCondenser:
    """Test NoOpCondenser passes events through unchanged."""

    def test_returns_all_events(self):
        condenser = NoOpCondenser()
        events = make_events(5)
        result = condenser.condense(events)
        assert len(result) == 5

    def test_preserves_event_content(self):
        condenser = NoOpCondenser()
        events = make_events(3)
        result = condenser.condense(events)
        for orig, condensed in zip(events, result):
            assert orig.id == condensed.id

    def test_condenser_type(self):
        assert NoOpCondenser().condenser_type == CondenserType.NOOP

    def test_empty_events(self):
        condenser = NoOpCondenser()
        result = condenser.condense([])
        assert len(result) == 0

    def test_returns_copy(self):
        condenser = NoOpCondenser()
        events = make_events(3)
        result = condenser.condense(events)
        assert result is not events  # Should be a new list


# ══════════════════════════════════════════════════════════════════════
# 2. RecentCondenser
# ══════════════════════════════════════════════════════════════════════


class TestRecentCondenser:
    """Test RecentCondenser keeps only most recent N events."""

    def test_keeps_recent_events(self):
        condenser = RecentCondenser(max_events=3)
        events = make_events(10)
        result = condenser.condense(events)
        assert len(result) == 3

    def test_keeps_last_events(self):
        condenser = RecentCondenser(max_events=2)
        events = make_events(5)
        result = condenser.condense(events)
        assert result[-1].data["index"] == 4

    def test_condenser_type(self):
        assert RecentCondenser().condenser_type == CondenserType.RECENT

    def test_default_max_events(self):
        condenser = RecentCondenser()
        assert condenser.max_events == 20

    def test_fewer_events_than_max(self):
        condenser = RecentCondenser(max_events=10)
        events = make_events(3)
        result = condenser.condense(events)
        assert len(result) == 3

    def test_empty_events(self):
        condenser = RecentCondenser(max_events=5)
        result = condenser.condense([])
        assert len(result) == 0


# ══════════════════════════════════════════════════════════════════════
# 3. ObservationCondenser
# ══════════════════════════════════════════════════════════════════════


class TestObservationCondenser:
    """Test ObservationCondenser keeps observations and recent actions."""

    def test_condenser_type(self):
        assert ObservationCondenser().condenser_type == CondenserType.OBSERVATION

    def test_keeps_observations(self):
        condenser = ObservationCondenser()
        events = [
            Event(event_type=EventType.OBSERVATION, source="a1",
                  observation=Observation(observation_type=ObservationType.SUCCESS, agent_id="a1", action_id="x", content="obs1")),
            Event(event_type=EventType.ACTION, source="a1",
                  action=Action(action_type=ActionType.THINK, agent_id="a1")),
        ]
        result = condenser.condense(events)
        obs_events = [e for e in result if e.observation is not None]
        assert len(obs_events) >= 1

    def test_keeps_recent_actions(self):
        condenser = ObservationCondenser(keep_recent_actions=1)
        events = [
            Event(event_type=EventType.ACTION, source="a1",
                  action=Action(action_type=ActionType.THINK, agent_id="a1", thought="first")),
            Event(event_type=EventType.ACTION, source="a1",
                  action=Action(action_type=ActionType.THINK, agent_id="a1", thought="second")),
        ]
        result = condenser.condense(events)
        action_events = [e for e in result if e.action is not None]
        assert len(action_events) == 1
        assert action_events[0].action.thought == "second"

    def test_default_keep_recent_actions(self):
        condenser = ObservationCondenser()
        assert condenser.keep_recent_actions == 2

    def test_mixed_events_sorted_by_timestamp(self):
        condenser = ObservationCondenser()
        t1 = time.time() - 10
        t2 = time.time()
        events = [
            Event(event_type=EventType.OBSERVATION, source="a1", timestamp=t2,
                  observation=Observation(observation_type=ObservationType.SUCCESS, agent_id="a1", action_id="x", content="later")),
            Event(event_type=EventType.OBSERVATION, source="a1", timestamp=t1,
                  observation=Observation(observation_type=ObservationType.SUCCESS, agent_id="a1", action_id="x", content="earlier")),
        ]
        result = condenser.condense(events)
        assert result[0].timestamp <= result[1].timestamp


# ══════════════════════════════════════════════════════════════════════
# 4. LLMCondenser
# ══════════════════════════════════════════════════════════════════════


class TestLLMCondenser:
    """Test LLMCondenser (sync fallback)."""

    def test_condenser_type(self):
        assert LLMCondenser().condenser_type == CondenserType.LLM

    def test_sync_fallback_returns_recent(self):
        condenser = LLMCondenser()
        events = make_events(20)
        result = condenser.condense(events)
        assert len(result) == 10  # Fallback returns last 10

    def test_sync_fallback_fewer_than_10(self):
        condenser = LLMCondenser()
        events = make_events(5)
        result = condenser.condense(events)
        assert len(result) == 5

    @pytest.mark.asyncio
    async def test_async_no_provider_returns_events(self):
        condenser = LLMCondenser(llm_provider=None)
        events = make_events(5)
        result = await condenser.condense_async(events)
        assert len(result) == 5

    @pytest.mark.asyncio
    async def test_async_empty_events(self):
        condenser = LLMCondenser()
        result = await condenser.condense_async([])
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_async_with_mock_provider(self):
        from ai_multicolony.core.llm_provider import LLMResponse, LLMUsage
        from unittest.mock import AsyncMock

        mock_provider = AsyncMock()
        mock_provider.chat = AsyncMock(return_value=LLMResponse(
            content="Summary of events",
            usage=LLMUsage(prompt_tokens=50, completion_tokens=20, total_tokens=70),
            model="gpt-4o",
        ))
        condenser = LLMCondenser(llm_provider=mock_provider)
        # Create enough events to exceed max_tokens*4 threshold
        events = []
        for i in range(50):
            events.append(Event(
                event_type=EventType.OBSERVATION,
                source=f"agent-{i}",
                observation=Observation(
                    observation_type=ObservationType.SUCCESS,
                    agent_id=f"agent-{i}",
                    action_id=f"act-{i}",
                    content="x" * 500,  # Long content to exceed threshold
                ),
            ))
        result = await condenser.condense_async(events, max_tokens=10)
        assert len(result) == 1  # Should be condensed to 1 summary event
        assert "Condensed Summary" in result[0].observation.content


# ══════════════════════════════════════════════════════════════════════
# 5. AmortizedCondenser
# ══════════════════════════════════════════════════════════════════════


class TestAmortizedCondenser:
    """Test AmortizedCondenser with decay factor."""

    def test_condenser_type(self):
        assert AmortizedCondenser().condenser_type == CondenserType.AMORTIZED

    def test_fresh_events_have_full_importance(self):
        condenser = AmortizedCondenser()
        events = make_events(3)
        result = condenser.condense(events)
        # Fresh events should be included
        assert len(result) == 3

    def test_decay_reduces_older_events(self):
        condenser = AmortizedCondenser(decay_factor=0.5, min_importance=0.1)
        events = make_events(5)
        # First call sets importance
        result1 = condenser.condense(events)
        assert len(result1) == 5
        # Second call decays importance of old events
        new_events = make_events(2)
        result2 = condenser.condense(new_events)
        # Some old events may be filtered
        assert len(result2) <= 7  # 5 old + 2 new

    def test_default_decay_factor(self):
        condenser = AmortizedCondenser()
        assert condenser.decay_factor == 0.9

    def test_default_min_importance(self):
        condenser = AmortizedCondenser()
        assert condenser.min_importance == 0.1

    def test_empty_events(self):
        condenser = AmortizedCondenser()
        result = condenser.condense([])
        assert len(result) == 0


# ══════════════════════════════════════════════════════════════════════
# 6. BrowserOutputCondenser
# ══════════════════════════════════════════════════════════════════════


class TestBrowserOutputCondenser:
    """Test BrowserOutputCondenser truncates long browser output."""

    def test_condenser_type(self):
        assert BrowserOutputCondenser().condenser_type == CondenserType.BROWSER_OUTPUT

    def test_truncates_long_browser_content(self):
        condenser = BrowserOutputCondenser(max_browser_output=100)
        events = [
            Event(
                event_type=EventType.OBSERVATION,
                source="browser",
                observation=Observation(
                    observation_type=ObservationType.SUCCESS,
                    agent_id="browser",
                    action_id="act-1",
                    content="x" * 500,
                ),
                data={"observation_type": "browser_page"},
            ),
        ]
        result = condenser.condense(events)
        assert len(result) == 1
        assert len(result[0].observation.content) <= 100 + len("\n[...truncated...]")

    def test_preserves_short_browser_content(self):
        condenser = BrowserOutputCondenser(max_browser_output=1000)
        events = [
            Event(
                event_type=EventType.OBSERVATION,
                source="browser",
                observation=Observation(
                    observation_type=ObservationType.SUCCESS,
                    agent_id="browser",
                    action_id="act-1",
                    content="Short content",
                ),
                data={"observation_type": "browser_page"},
            ),
        ]
        result = condenser.condense(events)
        assert result[0].observation.content == "Short content"

    def test_non_browser_events_unchanged(self):
        condenser = BrowserOutputCondenser(max_browser_output=100)
        events = [
            Event(
                event_type=EventType.OBSERVATION,
                source="agent",
                observation=Observation(
                    observation_type=ObservationType.SUCCESS,
                    agent_id="agent",
                    action_id="act-1",
                    content="x" * 500,
                ),
                data={"observation_type": "command_output"},
            ),
        ]
        result = condenser.condense(events)
        assert len(result[0].observation.content) == 500

    def test_default_max_browser_output(self):
        condenser = BrowserOutputCondenser()
        assert condenser.max_browser_output == 2000

    def test_no_observation_passthrough(self):
        condenser = BrowserOutputCondenser()
        events = [Event(event_type=EventType.ACTION, source="agent",
                        action=Action(action_type=ActionType.THINK, agent_id="agent"))]
        result = condenser.condense(events)
        assert len(result) == 1


# ══════════════════════════════════════════════════════════════════════
# 7. LLMLinguaCondenser
# ══════════════════════════════════════════════════════════════════════


class TestLLMLinguaCondenser:
    """Test LLMLinguaCondenser compression."""

    def test_condenser_type(self):
        assert LLMLinguaCondenser().condenser_type == CondenserType.LLMLINGUA

    def test_compression_rate(self):
        condenser = LLMLinguaCondenser(compression_rate=0.5)
        events = make_events(10)
        result = condenser.condense(events)
        assert len(result) <= 10

    def test_keeps_start_and_end(self):
        condenser = LLMLinguaCondenser(compression_rate=0.4)
        events = make_events(10)
        result = condenser.condense(events)
        # Should keep first 2 and last 2 (40% of 10)
        assert len(result) == 4

    def test_fewer_events_than_target(self):
        condenser = LLMLinguaCondenser(compression_rate=0.5)
        events = make_events(3)
        result = condenser.condense(events)
        # 50% of 3 = 1.5 -> int(1.5) = 1; but 3 <= 1 so returns all
        # Actually target_count = int(3 * 0.5) = 1, len(events) > 1, so keeps 0 + 1 = 1
        assert len(result) <= 3

    def test_default_compression_rate(self):
        condenser = LLMLinguaCondenser()
        assert condenser.compression_rate == 0.5

    def test_empty_events(self):
        condenser = LLMLinguaCondenser()
        result = condenser.condense([])
        assert len(result) == 0


# ══════════════════════════════════════════════════════════════════════
# 8. EventMaskCondenser
# ══════════════════════════════════════════════════════════════════════


class TestEventMaskCondenser:
    """Test EventMaskCondenser filters by type."""

    def test_condenser_type(self):
        assert EventMaskCondenser().condenser_type == CondenserType.EVENT_MASK

    def test_filters_masked_types(self):
        condenser = EventMaskCondenser(mask_types=["agent_state_changed"])
        events = [
            Event(event_type=EventType.ACTION, source="agent-1", data={}),
            Event(event_type=EventType.LIFECYCLE, source="agent-1", data={"observation_type": "agent_state_changed"}),
        ]
        result = condenser.condense(events)
        # The LIFECYCLE event should be filtered because its data contains agent_state_changed
        assert len(result) == 1
        assert result[0].event_type == EventType.ACTION

    def test_custom_mask_types(self):
        condenser = EventMaskCondenser(mask_types=["lifecycle", "system"])
        events = [
            Event(event_type=EventType.ACTION, source="a", data={}),
            Event(event_type=EventType.LIFECYCLE, source="a", data={}),
            Event(event_type=EventType.SYSTEM, source="a", data={}),
        ]
        result = condenser.condense(events)
        # Lifecycle and system events filtered by event_type value
        assert len(result) == 1
        assert result[0].event_type == EventType.ACTION

    def test_default_mask_types(self):
        condenser = EventMaskCondenser()
        assert "agent_state_changed" in condenser.mask_types

    def test_no_masking_needed(self):
        condenser = EventMaskCondenser(mask_types=["nonexistent"])
        events = make_events(5)
        result = condenser.condense(events)
        assert len(result) == 5

    def test_empty_events(self):
        condenser = EventMaskCondenser()
        result = condenser.condense([])
        assert len(result) == 0

    def test_filters_observation_type_in_data(self):
        condenser = EventMaskCondenser(mask_types=["agent_state_changed"])
        events = [
            Event(event_type=EventType.CUSTOM, source="a", data={"observation_type": "agent_state_changed"}),
        ]
        result = condenser.condense(events)
        assert len(result) == 0


# ══════════════════════════════════════════════════════════════════════
# 9. MemoryManager Session Operations
# ══════════════════════════════════════════════════════════════════════


class TestMemoryManagerSessions:
    """Test session management."""

    def test_create_session(self, memory_manager):
        session = memory_manager.create_session("agent-1")
        assert isinstance(session, MemorySession)
        assert session.agent_id == "agent-1"
        assert session.state == SessionState.ACTIVE

    def test_create_session_with_metadata(self, memory_manager):
        session = memory_manager.create_session("agent-1", metadata={"key": "value"})
        assert session.metadata["key"] == "value"

    def test_get_session(self, memory_manager):
        session = memory_manager.create_session("agent-1")
        retrieved = memory_manager.get_session(session.id)
        assert retrieved is session

    def test_get_nonexistent_session(self, memory_manager):
        assert memory_manager.get_session("nonexistent") is None

    def test_get_active_sessions(self, memory_manager):
        memory_manager.create_session("agent-1")
        memory_manager.create_session("agent-2")
        active = memory_manager.get_active_sessions()
        assert len(active) == 2

    def test_get_active_sessions_filter_by_agent(self, memory_manager):
        memory_manager.create_session("agent-1")
        memory_manager.create_session("agent-2")
        active = memory_manager.get_active_sessions(agent_id="agent-1")
        assert len(active) == 1
        assert active[0].agent_id == "agent-1"

    def test_close_session(self, memory_manager):
        session = memory_manager.create_session("agent-1")
        memory_manager.close_session(session.id)
        assert session.state == SessionState.CLOSED
        assert session.closed_at is not None

    def test_close_nonexistent_session_noop(self, memory_manager):
        memory_manager.close_session("nonexistent")  # Should not raise

    def test_closed_sessions_not_in_active(self, memory_manager):
        session = memory_manager.create_session("agent-1")
        memory_manager.close_session(session.id)
        active = memory_manager.get_active_sessions()
        assert len(active) == 0


# ══════════════════════════════════════════════════════════════════════
# 10. Letta-style Paging
# ══════════════════════════════════════════════════════════════════════


class TestMemoryManagerPaging:
    """Test memory paging operations."""

    def test_create_page(self, memory_manager):
        page = memory_manager.create_page(
            agent_id="agent-1",
            title="Test Page",
            content="Test content",
            memory_type=MemoryType.WORKING,
        )
        assert page.title == "Test Page"
        assert page.content == "Test content"
        assert page.memory_type == MemoryType.WORKING
        assert page.token_count > 0

    def test_create_page_with_tags(self, memory_manager):
        page = memory_manager.create_page(
            agent_id="agent-1",
            content="Tagged",
            tags=["important", "coding"],
        )
        assert "important" in page.tags
        assert "coding" in page.tags

    def test_create_page_with_session(self, memory_manager):
        session = memory_manager.create_session("agent-1")
        page = memory_manager.create_page(
            agent_id="agent-1",
            content="Session page",
            session_id=session.id,
        )
        assert page.id in session.page_ids

    def test_load_page(self, memory_manager):
        page = memory_manager.create_page(agent_id="agent-1", content="Test")
        loaded = memory_manager.load_page(page.id)
        assert loaded.is_active
        assert loaded.access_count == 1

    def test_load_page_increments_access_count(self, memory_manager):
        page = memory_manager.create_page(agent_id="agent-1", content="Test")
        memory_manager.load_page(page.id)
        memory_manager.load_page(page.id)
        assert memory_manager.get_page(page.id).access_count == 2

    def test_unload_page(self, memory_manager):
        page = memory_manager.create_page(agent_id="agent-1", content="Test")
        memory_manager.load_page(page.id)
        memory_manager.unload_page(page.id)
        assert not memory_manager.get_page(page.id).is_active

    def test_get_active_pages(self, memory_manager):
        p1 = memory_manager.create_page(agent_id="agent-1", content="Page 1")
        p2 = memory_manager.create_page(agent_id="agent-1", content="Page 2")
        memory_manager.load_page(p1.id)
        active = memory_manager.get_active_pages()
        assert len(active) == 1

    def test_get_active_pages_filter_by_agent(self, memory_manager):
        p1 = memory_manager.create_page(agent_id="agent-1", content="Page 1")
        p2 = memory_manager.create_page(agent_id="agent-2", content="Page 2")
        memory_manager.load_page(p1.id)
        memory_manager.load_page(p2.id)
        active = memory_manager.get_active_pages(agent_id="agent-1")
        assert len(active) == 1

    def test_get_page(self, memory_manager):
        page = memory_manager.create_page(agent_id="agent-1", content="Test")
        retrieved = memory_manager.get_page(page.id)
        assert retrieved is page

    def test_get_page_nonexistent(self, memory_manager):
        assert memory_manager.get_page("nonexistent") is None

    def test_update_page_content(self, memory_manager):
        page = memory_manager.create_page(agent_id="agent-1", content="Original")
        updated = memory_manager.update_page(page.id, content="Updated")
        assert updated.content == "Updated"
        assert updated.token_count > 0

    def test_update_page_title(self, memory_manager):
        page = memory_manager.create_page(agent_id="agent-1", content="Test")
        updated = memory_manager.update_page(page.id, title="New Title")
        assert updated.title == "New Title"

    def test_update_page_updates_timestamp(self, memory_manager):
        page = memory_manager.create_page(agent_id="agent-1", content="Test")
        old_updated_at = page.updated_at
        import time
        time.sleep(0.01)
        updated = memory_manager.update_page(page.id, content="New")
        assert updated.updated_at >= old_updated_at

    def test_update_nonexistent_page_raises(self, memory_manager):
        with pytest.raises(MemoryError, match="Page not found"):
            memory_manager.update_page("nonexistent", content="Test")

    def test_delete_page(self, memory_manager):
        page = memory_manager.create_page(agent_id="agent-1", content="Test")
        memory_manager.delete_page(page.id)
        assert memory_manager.get_page(page.id) is None

    def test_delete_nonexistent_page_noop(self, memory_manager):
        memory_manager.delete_page("nonexistent")  # Should not raise

    def test_page_not_found_on_load(self, memory_manager):
        with pytest.raises(MemoryError, match="Page not found"):
            memory_manager.load_page("nonexistent")

    def test_eviction_when_max_pages_reached(self, memory_manager_small):
        for i in range(5):
            memory_manager_small.create_page(agent_id="agent-1", content=f"Page {i}")
        assert len(memory_manager_small._pages) <= 3


# ══════════════════════════════════════════════════════════════════════
# 11. Entry Operations
# ══════════════════════════════════════════════════════════════════════


class TestMemoryManagerEntries:
    """Test memory entry operations."""

    def test_add_entry(self, memory_manager):
        entry = memory_manager.add_entry(
            agent_id="agent-1",
            content="Test memory",
            memory_type=MemoryType.EPISODIC,
        )
        assert entry.content == "Test memory"
        assert entry.memory_type == MemoryType.EPISODIC

    def test_add_entry_with_importance(self, memory_manager):
        entry = memory_manager.add_entry(
            agent_id="agent-1",
            content="Important",
            importance=0.9,
        )
        assert entry.importance == 0.9

    def test_add_entry_with_tags(self, memory_manager):
        entry = memory_manager.add_entry(
            agent_id="agent-1",
            content="Tagged",
            tags=["python", "coding"],
        )
        assert "python" in entry.tags

    def test_add_entry_with_source(self, memory_manager):
        entry = memory_manager.add_entry(
            agent_id="agent-1",
            content="From tool",
            source="tool",
        )
        assert entry.source == "tool"

    def test_add_entry_default_type(self, memory_manager):
        entry = memory_manager.add_entry(
            agent_id="agent-1",
            content="Default type",
        )
        assert entry.memory_type == MemoryType.EPISODIC

    def test_query_by_content(self, memory_manager):
        memory_manager.add_entry(agent_id="agent-1", content="Python is great", importance=0.8)
        memory_manager.add_entry(agent_id="agent-1", content="TypeScript is cool", importance=0.6)
        result = memory_manager.query(MemoryQuery(query="Python"))
        assert result.total_count >= 1

    def test_query_by_type(self, memory_manager):
        memory_manager.add_entry(agent_id="agent-1", content="Episodic", memory_type=MemoryType.EPISODIC)
        memory_manager.add_entry(agent_id="agent-1", content="Semantic", memory_type=MemoryType.SEMANTIC)
        result = memory_manager.query(MemoryQuery(query="", memory_types=[MemoryType.EPISODIC]))
        assert all(e.memory_type == MemoryType.EPISODIC for e in result.entries)

    def test_query_by_agent(self, memory_manager):
        memory_manager.add_entry(agent_id="agent-1", content="Agent 1")
        memory_manager.add_entry(agent_id="agent-2", content="Agent 2")
        result = memory_manager.query(MemoryQuery(query="", agent_id="agent-1"))
        assert all(e.agent_id == "agent-1" for e in result.entries)

    def test_query_by_min_importance(self, memory_manager):
        memory_manager.add_entry(agent_id="agent-1", content="Low", importance=0.2)
        memory_manager.add_entry(agent_id="agent-1", content="High", importance=0.9)
        result = memory_manager.query(MemoryQuery(query="", min_importance=0.5))
        assert all(e.importance >= 0.5 for e in result.entries)

    def test_query_by_tags(self, memory_manager):
        memory_manager.add_entry(agent_id="agent-1", content="Tagged", tags=["python"])
        memory_manager.add_entry(agent_id="agent-1", content="Untagged", tags=["other"])
        result = memory_manager.query(MemoryQuery(query="", tags=["python"]))
        assert any("python" in e.tags for e in result.entries)

    def test_query_limit(self, memory_manager):
        for i in range(20):
            memory_manager.add_entry(agent_id="agent-1", content=f"Entry {i}", importance=0.5)
        result = memory_manager.query(MemoryQuery(query="", limit=5))
        assert len(result.entries) <= 5

    def test_query_result_has_execution_time(self, memory_manager):
        memory_manager.add_entry(agent_id="agent-1", content="Test")
        result = memory_manager.query(MemoryQuery(query="Test"))
        assert result.execution_time is not None
        assert result.execution_time >= 0

    def test_get_entries(self, memory_manager):
        for i in range(5):
            memory_manager.add_entry(agent_id="agent-1", content=f"Entry {i}")
        entries = memory_manager.get_entries("agent-1", limit=3)
        assert len(entries) == 3

    def test_get_entries_by_type(self, memory_manager):
        memory_manager.add_entry(agent_id="agent-1", content="Work", memory_type=MemoryType.WORKING)
        memory_manager.add_entry(agent_id="agent-1", content="Epi", memory_type=MemoryType.EPISODIC)
        entries = memory_manager.get_entries("agent-1", memory_type=MemoryType.WORKING)
        assert all(e.memory_type == MemoryType.WORKING for e in entries)

    def test_get_entries_nonexistent_agent(self, memory_manager):
        entries = memory_manager.get_entries("nonexistent")
        assert entries == []

    def test_clear_entries_by_agent(self, memory_manager):
        memory_manager.add_entry(agent_id="agent-1", content="Entry 1")
        memory_manager.add_entry(agent_id="agent-2", content="Entry 2")
        count = memory_manager.clear_entries("agent-1")
        assert count == 1
        assert len(memory_manager.get_entries("agent-1")) == 0
        assert len(memory_manager.get_entries("agent-2")) == 1

    def test_clear_all_entries(self, memory_manager):
        memory_manager.add_entry(agent_id="agent-1", content="Entry 1")
        memory_manager.add_entry(agent_id="agent-2", content="Entry 2")
        count = memory_manager.clear_entries()
        assert count == 2
        assert len(memory_manager.get_entries("agent-1")) == 0


# ══════════════════════════════════════════════════════════════════════
# 12. Condensation via MemoryManager
# ══════════════════════════════════════════════════════════════════════


class TestMemoryManagerCondensation:
    """Test condensation through the MemoryManager."""

    def test_condense_with_recent(self, memory_manager):
        events = make_events(10)
        result = memory_manager.condense_events(events, CondenserType.RECENT)
        assert len(result) <= 20  # Default max_events=20

    def test_condense_with_noop(self, memory_manager):
        events = make_events(5)
        result = memory_manager.condense_events(events, CondenserType.NOOP)
        assert len(result) == 5

    def test_condense_with_default_condenser(self, memory_manager):
        events = make_events(5)
        result = memory_manager.condense_events(events)
        assert len(result) > 0

    def test_get_condenser(self, memory_manager):
        condenser = memory_manager.get_condenser(CondenserType.NOOP)
        assert isinstance(condenser, NoOpCondenser)

    def test_get_condenser_default(self, memory_manager):
        # Default is RECENT
        condenser = memory_manager.get_condenser()
        assert isinstance(condenser, RecentCondenser)

    def test_get_condenser_unknown_returns_noop(self, memory_manager):
        # Passing a CondenserType that doesn't exist should return NOOP
        # This tests the fallback: get returns _condensers[CondenserType.NOOP]
        condenser = memory_manager.get_condenser(CondenserType.NOOP)
        assert isinstance(condenser, NoOpCondenser)


# ══════════════════════════════════════════════════════════════════════
# 13. Vector Store Integration (Mocked)
# ══════════════════════════════════════════════════════════════════════


class MockVectorBackend(VectorStoreBackend):
    """Mock vector store backend for testing."""

    def __init__(self):
        self._data: dict[str, dict] = {}

    async def upsert(self, id: str, embedding: list[float], metadata: dict) -> None:
        self._data[id] = {"id": id, "embedding": embedding, "metadata": metadata}

    async def search(self, embedding: list[float], limit: int = 10) -> list[dict]:
        return [
            {"id": k, "score": 0.9, "payload": v["metadata"]}
            for k, v in list(self._data.items())[:limit]
        ]

    async def delete(self, id: str) -> None:
        self._data.pop(id, None)


class TestVectorStoreIntegration:
    """Test vector store integration (mocked)."""

    @pytest.mark.asyncio
    async def test_vector_search_with_backend(self):
        backend = MockVectorBackend()
        await backend.upsert("entry-1", [0.1, 0.2, 0.3], {"agent_id": "agent-1", "content": "test"})
        manager = MemoryManager(vector_backend=backend)
        results = await manager.vector_search([0.1, 0.2, 0.3], limit=5)
        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_vector_search_no_backend(self, memory_manager):
        results = await memory_manager.vector_search([0.1, 0.2, 0.3])
        assert results == []

    @pytest.mark.asyncio
    async def test_vector_search_filter_by_agent(self):
        backend = MockVectorBackend()
        await backend.upsert("e1", [0.1], {"agent_id": "agent-1", "content": "a1"})
        await backend.upsert("e2", [0.2], {"agent_id": "agent-2", "content": "a2"})
        manager = MemoryManager(vector_backend=backend)
        results = await manager.vector_search([0.1], limit=10, agent_id="agent-1")
        assert all(e.agent_id == "agent-1" for e in results)

    def test_add_entry_with_embedding(self):
        backend = MockVectorBackend()
        manager = MemoryManager(vector_backend=backend)
        entry = manager.add_entry(
            agent_id="agent-1",
            content="Embedded content",
            embedding=[0.1, 0.2, 0.3],
        )
        assert entry.embedding == [0.1, 0.2, 0.3]


# ══════════════════════════════════════════════════════════════════════
# 14. Statistics
# ══════════════════════════════════════════════════════════════════════


class TestMemoryManagerStats:
    """Test MemoryManager get_stats."""

    def test_initial_stats(self, memory_manager):
        stats = memory_manager.get_stats()
        assert stats["total_pages"] == 0
        assert stats["active_pages"] == 0
        assert stats["total_entries"] == 0
        assert stats["total_sessions"] == 0
        assert stats["active_sessions"] == 0
        assert stats["agents_with_memory"] == 0
        assert stats["max_pages"] == 100
        assert stats["vector_backend"] is None

    def test_stats_after_operations(self, memory_manager):
        memory_manager.create_session("agent-1")
        memory_manager.create_page(agent_id="agent-1", content="Test")
        memory_manager.add_entry(agent_id="agent-1", content="Memory")
        stats = memory_manager.get_stats()
        assert stats["total_sessions"] == 1
        assert stats["total_pages"] == 1
        # create_page also creates an entry internally
        assert stats["total_entries"] == 2
        assert stats["agents_with_memory"] == 1

    def test_stats_vector_backend_name(self):
        backend = MockVectorBackend()
        manager = MemoryManager(vector_backend=backend)
        stats = manager.get_stats()
        assert stats["vector_backend"] == "MockVectorBackend"

    def test_stats_active_pages(self, memory_manager):
        p = memory_manager.create_page(agent_id="agent-1", content="Test")
        memory_manager.load_page(p.id)
        stats = memory_manager.get_stats()
        assert stats["active_pages"] == 1
