"""Tests for EventBus — pub/sub, direct/broadcast messaging, singleton pattern."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from ai_multicolony.core.event_bus import EventBus
from ai_multicolony.exceptions import EventBusError
from ai_multicolony.types.events import Action, ActionType, Event, EventType, Observation, ObservationType
from ai_multicolony.types.messages import BusMessage, BusMessagePriority, MessageType


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_event_bus():
    """Reset the singleton before each test."""
    EventBus.reset()
    yield
    EventBus.reset()


@pytest.fixture
def bus():
    """Create a fresh EventBus instance (not from singleton)."""
    return EventBus()


# ── Singleton ───────────────────────────────────────────────────────────────

class TestEventBusSingleton:
    """Test singleton pattern."""

    def test_get_instance_returns_same_object(self):
        b1 = EventBus.get_instance()
        b2 = EventBus.get_instance()
        assert b1 is b2

    def test_reset_clears_singleton(self):
        b1 = EventBus.get_instance()
        EventBus.reset()
        b2 = EventBus.get_instance()
        assert b1 is not b2

    def test_get_instance_after_reset(self):
        b1 = EventBus.get_instance()
        EventBus.reset()
        b2 = EventBus.get_instance()
        assert isinstance(b2, EventBus)


# ── Start / Stop ───────────────────────────────────────────────────────────

class TestEventBusStartStop:
    """Test lifecycle management."""

    def test_initial_state_not_running(self, bus):
        assert not bus.is_running

    @pytest.mark.asyncio
    async def test_start_sets_running(self, bus):
        await bus.start()
        assert bus.is_running

    @pytest.mark.asyncio
    async def test_stop_clears_running(self, bus):
        await bus.start()
        await bus.stop()
        assert not bus.is_running

    @pytest.mark.asyncio
    async def test_stop_cancels_pending_observations(self, bus):
        await bus.start()
        future = asyncio.get_event_loop().create_future()
        bus._pending_observations["action-1"] = future
        await bus.stop()
        assert future.cancelled() or future.done()
        assert len(bus._pending_observations) == 0


# ── Event Publishing ───────────────────────────────────────────────────────

class TestEventPublishing:
    """Test event pub/sub."""

    @pytest.mark.asyncio
    async def test_publish_increments_event_count(self, bus):
        await bus.start()
        event = Event(event_type=EventType.CUSTOM, source="test")
        await bus.publish_event(event)
        assert bus.event_count == 1

    @pytest.mark.asyncio
    async def test_publish_not_running_does_not_deliver(self, bus):
        """When bus is not running, events are recorded but not delivered to handlers."""
        received = []
        async def handler(e):
            received.append(e)

        bus.subscribe("custom", handler)
        event = Event(event_type=EventType.CUSTOM, source="test")
        await bus.publish_event(event)
        assert len(received) == 0  # not running, no delivery

    @pytest.mark.asyncio
    async def test_subscribe_and_receive(self, bus):
        await bus.start()
        received = []
        async def handler(e):
            received.append(e)

        bus.subscribe("action", handler)
        event = Event(event_type=EventType.ACTION, source="agent-1")
        await bus.publish_event(event)
        assert len(received) == 1
        assert received[0].id == event.id

    @pytest.mark.asyncio
    async def test_wildcard_subscriber(self, bus):
        await bus.start()
        received = []
        async def handler(e):
            received.append(e)

        bus.subscribe("*", handler)
        await bus.publish_event(Event(event_type=EventType.ACTION, source="a"))
        await bus.publish_event(Event(event_type=EventType.OBSERVATION, source="b"))
        assert len(received) == 2

    @pytest.mark.asyncio
    async def test_unsubscribe(self, bus):
        await bus.start()
        received = []
        async def handler(e):
            received.append(e)

        bus.subscribe("action", handler)
        bus.unsubscribe("action", handler)
        await bus.publish_event(Event(event_type=EventType.ACTION, source="test"))
        assert len(received) == 0

    @pytest.mark.asyncio
    async def test_handler_error_does_not_break_others(self, bus):
        await bus.start()
        good_received = []
        async def bad_handler(e):
            raise RuntimeError("boom")

        async def good_handler(e):
            good_received.append(e)

        bus.subscribe("action", bad_handler)
        bus.subscribe("action", good_handler)
        await bus.publish_event(Event(event_type=EventType.ACTION, source="test"))
        assert len(good_received) == 1

    @pytest.mark.asyncio
    async def test_publish_action(self, bus):
        await bus.start()
        received = []
        async def handler(e):
            received.append(e)

        bus.subscribe("action", handler)
        action = Action(action_type=ActionType.THINK, agent_id="agent-1", thought="test")
        await bus.publish_action(action)
        assert len(received) == 1
        assert received[0].action is not None

    @pytest.mark.asyncio
    async def test_publish_observation_resolves_pending(self, bus):
        await bus.start()
        action_id = "action-123"
        # Create a pending observation future
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        bus._pending_observations[action_id] = future

        obs = Observation(
            observation_type=ObservationType.SUCCESS,
            agent_id="agent-1",
            action_id=action_id,
            content="done",
        )
        await bus.publish_observation(obs)
        assert future.done()
        assert future.result().content == "done"

    @pytest.mark.asyncio
    async def test_wait_for_observation_timeout(self, bus):
        await bus.start()
        with pytest.raises(EventBusError, match="Timeout"):
            await bus.wait_for_observation("nonexistent-action", timeout=0.1)

    @pytest.mark.asyncio
    async def test_wait_for_observation_duplicate_raises(self, bus):
        await bus.start()
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        bus._pending_observations["action-1"] = future
        with pytest.raises(EventBusError, match="Already waiting"):
            await bus.wait_for_observation("action-1", timeout=1.0)


# ── History & Query ────────────────────────────────────────────────────────

class TestEventHistory:
    """Test event history."""

    @pytest.mark.asyncio
    async def test_history_appended(self, bus):
        await bus.start()
        e1 = Event(event_type=EventType.ACTION, source="a")
        e2 = Event(event_type=EventType.OBSERVATION, source="b")
        await bus.publish_event(e1)
        await bus.publish_event(e2)
        assert len(bus.get_event_history()) == 2

    @pytest.mark.asyncio
    async def test_history_filter_by_type(self, bus):
        await bus.start()
        await bus.publish_event(Event(event_type=EventType.ACTION, source="a"))
        await bus.publish_event(Event(event_type=EventType.OBSERVATION, source="b"))
        result = bus.get_event_history(event_type="action")
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_history_filter_by_source(self, bus):
        await bus.start()
        await bus.publish_event(Event(event_type=EventType.ACTION, source="agent-1"))
        await bus.publish_event(Event(event_type=EventType.ACTION, source="agent-2"))
        result = bus.get_event_history(source="agent-1")
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_history_limit(self, bus):
        await bus.start()
        for i in range(20):
            await bus.publish_event(Event(event_type=EventType.CUSTOM, source="test"))
        result = bus.get_event_history(limit=5)
        assert len(result) == 5

    @pytest.mark.asyncio
    async def test_max_history_enforced(self, bus):
        bus_small = EventBus(max_history=5)
        await bus_small.start()
        for i in range(10):
            await bus_small.publish_event(Event(event_type=EventType.CUSTOM, source="test"))
        assert len(bus_small._history) <= 5
        await bus_small.stop()


# ── Message Bus ────────────────────────────────────────────────────────────

class TestMessageBus:
    """Test message bus (direct/broadcast)."""

    @pytest.mark.asyncio
    async def test_send_message_increments_count(self, bus):
        await bus.start()
        msg = BusMessage(sender="a", channel="test", message_type=MessageType.REQUEST, content={"x": 1})
        await bus.send_message(msg)
        assert bus.message_count == 1

    @pytest.mark.asyncio
    async def test_channel_subscribe(self, bus):
        await bus.start()
        received = []
        async def handler(m):
            received.append(m)

        bus.subscribe_channel("trading", handler)
        msg = BusMessage(sender="a", channel="trading", message_type=MessageType.REQUEST, content={"x": 1})
        await bus.send_message(msg)
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_channel_unsubscribe(self, bus):
        await bus.start()
        received = []
        async def handler(m):
            received.append(m)

        bus.subscribe_channel("trading", handler)
        bus.unsubscribe_channel("trading", handler)
        msg = BusMessage(sender="a", channel="trading", message_type=MessageType.REQUEST, content={"x": 1})
        await bus.send_message(msg)
        assert len(received) == 0

    @pytest.mark.asyncio
    async def test_broadcast(self, bus):
        await bus.start()
        received = []
        async def handler(m):
            received.append(m)

        bus.subscribe_channel("announcements", handler)
        msg = await bus.broadcast(sender="system", channel="announcements", content={"msg": "hello"})
        assert len(received) == 1
        assert msg.recipient is None  # broadcast

    @pytest.mark.asyncio
    async def test_direct_message(self, bus):
        await bus.start()
        received = []
        async def handler(m):
            received.append(m)

        bus.subscribe_channel("dm", handler)
        msg = await bus.send_direct(
            sender="agent-1", recipient="agent-2",
            channel="dm", content={"text": "hello"},
        )
        assert msg.recipient == "agent-2"
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_message_type_subscribe(self, bus):
        await bus.start()
        received = []
        async def handler(m):
            received.append(m)

        bus.subscribe_messages("request", handler)
        msg = BusMessage(sender="a", channel="test", message_type=MessageType.REQUEST, content={})
        await bus.send_message(msg)
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_message_not_running_not_delivered(self, bus):
        received = []
        async def handler(m):
            received.append(m)

        bus.subscribe_channel("test", handler)
        msg = BusMessage(sender="a", channel="test", message_type=MessageType.REQUEST, content={})
        await bus.send_message(msg)
        assert len(received) == 0

    @pytest.mark.asyncio
    async def test_message_history(self, bus):
        await bus.start()
        await bus.send_direct("a", "b", "ch", {"x": 1})
        await bus.broadcast("c", "ch", {"y": 2})
        history = bus.get_message_history()
        assert len(history) == 2

    @pytest.mark.asyncio
    async def test_message_history_filter_channel(self, bus):
        await bus.start()
        await bus.send_direct("a", "b", "ch1", {"x": 1})
        await bus.send_direct("a", "b", "ch2", {"y": 2})
        result = bus.get_message_history(channel="ch1")
        assert len(result) == 1


# ── Stats ──────────────────────────────────────────────────────────────────

class TestEventBusStats:
    """Test statistics reporting."""

    @pytest.mark.asyncio
    async def test_stats(self, bus):
        await bus.start()
        await bus.publish_event(Event(event_type=EventType.CUSTOM, source="test"))
        await bus.send_direct("a", "b", "ch", {"x": 1})
        stats = bus.get_stats()
        assert stats["total_events"] == 1
        assert stats["total_messages"] == 1
        assert stats["running"] is True

    def test_clear_history(self, bus):
        bus._history.append(Event(event_type=EventType.CUSTOM, source="test"))
        bus._message_history.append(BusMessage(sender="a", channel="test"))
        bus.clear_history()
        assert len(bus._history) == 0
        assert len(bus._message_history) == 0
