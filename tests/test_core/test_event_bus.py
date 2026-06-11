"""Comprehensive tests for EventBus.

Tests cover:
- Start / stop lifecycle
- Subscribe / unsubscribe (events)
- Publish events, actions, observations
- Wildcard subscriber
- Action/Observation pairing with wait_for_observation
- Channel-based messaging
- Direct messaging
- Broadcast messaging
- Message type handlers
- History and filtering
- Statistics
- Error handling in handlers
- Singleton pattern
- Not-running behavior
"""

from __future__ import annotations

import asyncio

import pytest

from ai_multicolony.core.event_bus import EventBus
from ai_multicolony.exceptions import EventBusError
from ai_multicolony.types.events import Action, ActionType, Event, EventType, Observation, ObservationType
from ai_multicolony.types.messages import BusMessage, BusMessagePriority, MessageType


# ══════════════════════════════════════════════════════════════════════
# 1. Start / Stop Lifecycle
# ══════════════════════════════════════════════════════════════════════


class TestEventBusLifecycle:
    """Test EventBus start, stop, and running state."""

    @pytest.mark.asyncio
    async def test_start_sets_running(self, event_bus):
        await event_bus.start()
        assert event_bus.is_running

    @pytest.mark.asyncio
    async def test_stop_clears_running(self, event_bus):
        await event_bus.start()
        await event_bus.stop()
        assert not event_bus.is_running

    @pytest.mark.asyncio
    async def test_initial_not_running(self, event_bus):
        assert not event_bus.is_running

    @pytest.mark.asyncio
    async def test_stop_cancels_pending_observations(self, event_bus):
        await event_bus.start()
        # Create a pending observation future manually
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        event_bus._pending_observations["act-1"] = future
        await event_bus.stop()
        assert future.cancelled() or future.done()
        assert len(event_bus._pending_observations) == 0

    @pytest.mark.asyncio
    async def test_stop_logs_counts(self, event_bus):
        await event_bus.start()
        # Publish some events first
        action = Action(action_type=ActionType.THINK, agent_id="test")
        await event_bus.publish_action(action)
        await event_bus.stop()
        assert event_bus._event_count == 1


# ══════════════════════════════════════════════════════════════════════
# 2. Event Subscribe / Unsubscribe
# ══════════════════════════════════════════════════════════════════════


class TestEventSubscribe:
    """Test subscribing and unsubscribing to event types."""

    def test_subscribe_adds_handler(self, event_bus):
        handler = lambda e: None
        event_bus.subscribe("action", handler)
        assert handler in event_bus._subscribers["action"]

    def test_subscribe_multiple_handlers(self, event_bus):
        h1 = lambda e: None
        h2 = lambda e: None
        event_bus.subscribe("action", h1)
        event_bus.subscribe("action", h2)
        assert len(event_bus._subscribers["action"]) == 2

    def test_subscribe_wildcard(self, event_bus):
        handler = lambda e: None
        event_bus.subscribe("*", handler)
        assert handler in event_bus._subscribers["*"]

    def test_unsubscribe_removes_handler(self, event_bus):
        handler = lambda e: None
        event_bus.subscribe("action", handler)
        event_bus.unsubscribe("action", handler)
        assert handler not in event_bus._subscribers["action"]

    def test_unsubscribe_nonexistent_type_noop(self, event_bus):
        handler = lambda e: None
        event_bus.unsubscribe("nonexistent", handler)  # Should not raise

    def test_unsubscribe_different_handler_keeps_others(self, event_bus):
        h1 = lambda e: None
        h2 = lambda e: None
        event_bus.subscribe("action", h1)
        event_bus.subscribe("action", h2)
        event_bus.unsubscribe("action", h1)
        assert h2 in event_bus._subscribers["action"]


# ══════════════════════════════════════════════════════════════════════
# 3. Publish Events
# ══════════════════════════════════════════════════════════════════════


class TestEventPublish:
    """Test publishing events."""

    @pytest.mark.asyncio
    async def test_publish_action(self, event_bus):
        await event_bus.start()
        received = []
        event_bus.subscribe("action", lambda e: received.append(e))
        action = Action(action_type=ActionType.THINK, agent_id="test")
        await event_bus.publish_action(action)
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_publish_observation(self, event_bus):
        await event_bus.start()
        received = []
        event_bus.subscribe("observation", lambda e: received.append(e))
        obs = Observation(
            observation_type=ObservationType.SUCCESS,
            agent_id="test",
            action_id="act-1",
            content="Done",
        )
        await event_bus.publish_observation(obs)
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_publish_generic_event(self, event_bus):
        await event_bus.start()
        received = []
        event_bus.subscribe("custom", lambda e: received.append(e))
        event = Event(event_type=EventType.CUSTOM, source="test", data={"key": "val"})
        await event_bus.publish_event(event)
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_publish_increments_event_count(self, event_bus):
        await event_bus.start()
        action = Action(action_type=ActionType.THINK, agent_id="test")
        await event_bus.publish_action(action)
        assert event_bus.event_count == 1

    @pytest.mark.asyncio
    async def test_publish_multiple_increments_count(self, event_bus):
        await event_bus.start()
        for i in range(5):
            action = Action(action_type=ActionType.THINK, agent_id=f"agent-{i}")
            await event_bus.publish_action(action)
        assert event_bus.event_count == 5

    @pytest.mark.asyncio
    async def test_not_running_does_not_deliver_events(self, event_bus):
        received = []
        event_bus.subscribe("action", lambda e: received.append(e))
        action = Action(action_type=ActionType.THINK, agent_id="test")
        await event_bus.publish_action(action)
        assert len(received) == 0

    @pytest.mark.asyncio
    async def test_not_running_still_increments_count(self, event_bus):
        action = Action(action_type=ActionType.THINK, agent_id="test")
        await event_bus.publish_action(action)
        assert event_bus.event_count == 1  # Counter still increments


# ══════════════════════════════════════════════════════════════════════
# 4. Wildcard Subscriber
# ══════════════════════════════════════════════════════════════════════


class TestWildcardSubscriber:
    """Test wildcard (*) subscriber receiving all events."""

    @pytest.mark.asyncio
    async def test_wildcard_receives_actions(self, event_bus):
        await event_bus.start()
        received = []
        event_bus.subscribe("*", lambda e: received.append(e))
        action = Action(action_type=ActionType.THINK, agent_id="test")
        await event_bus.publish_action(action)
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_wildcard_receives_observations(self, event_bus):
        await event_bus.start()
        received = []
        event_bus.subscribe("*", lambda e: received.append(e))
        obs = Observation(
            observation_type=ObservationType.SUCCESS,
            agent_id="test",
            action_id="a1",
            content="ok",
        )
        await event_bus.publish_observation(obs)
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_wildcard_receives_custom_events(self, event_bus):
        await event_bus.start()
        received = []
        event_bus.subscribe("*", lambda e: received.append(e))
        event = Event(event_type=EventType.SYSTEM, source="sys")
        await event_bus.publish_event(event)
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_wildcard_and_specific_both_receive(self, event_bus):
        await event_bus.start()
        all_received = []
        action_received = []
        event_bus.subscribe("*", lambda e: all_received.append(e))
        event_bus.subscribe("action", lambda e: action_received.append(e))
        action = Action(action_type=ActionType.THINK, agent_id="test")
        await event_bus.publish_action(action)
        assert len(all_received) == 1
        assert len(action_received) == 1


# ══════════════════════════════════════════════════════════════════════
# 5. Action/Observation Pairing
# ══════════════════════════════════════════════════════════════════════


class TestActionObservationPairing:
    """Test wait_for_observation and action/observation pairing."""

    @pytest.mark.asyncio
    async def test_wait_and_resolve(self, event_bus):
        await event_bus.start()

        async def publish_later():
            await asyncio.sleep(0.05)
            obs = Observation(
                observation_type=ObservationType.SUCCESS,
                agent_id="test",
                action_id="act-1",
                content="Resolved!",
            )
            await event_bus.publish_observation(obs)

        asyncio.create_task(publish_later())
        result = await event_bus.wait_for_observation("act-1", timeout=2.0)
        assert result.content == "Resolved!"

    @pytest.mark.asyncio
    async def test_wait_timeout_raises(self, event_bus):
        await event_bus.start()
        with pytest.raises(EventBusError, match="Timeout"):
            await event_bus.wait_for_observation("nonexistent", timeout=0.1)

    @pytest.mark.asyncio
    async def test_double_wait_raises(self, event_bus):
        await event_bus.start()
        asyncio.create_task(event_bus.wait_for_observation("act-1", timeout=2.0))
        await asyncio.sleep(0.01)
        with pytest.raises(EventBusError, match="Already waiting"):
            await event_bus.wait_for_observation("act-1")

    @pytest.mark.asyncio
    async def test_resolve_clears_pending(self, event_bus):
        await event_bus.start()

        async def publish_later():
            await asyncio.sleep(0.05)
            obs = Observation(
                observation_type=ObservationType.SUCCESS,
                agent_id="test",
                action_id="act-1",
                content="Done",
            )
            await event_bus.publish_observation(obs)

        asyncio.create_task(publish_later())
        await event_bus.wait_for_observation("act-1", timeout=2.0)
        assert "act-1" not in event_bus._pending_observations

    @pytest.mark.asyncio
    async def test_unresolved_removed_after_timeout(self, event_bus):
        await event_bus.start()
        try:
            await event_bus.wait_for_observation("act-x", timeout=0.1)
        except EventBusError:
            pass
        assert "act-x" not in event_bus._pending_observations


# ══════════════════════════════════════════════════════════════════════
# 6. Channel Messaging
# ══════════════════════════════════════════════════════════════════════


class TestChannelMessaging:
    """Test channel-based message routing."""

    @pytest.mark.asyncio
    async def test_subscribe_channel(self, event_bus):
        handler = lambda m: None
        event_bus.subscribe_channel("test", handler)
        assert handler in event_bus._channel_subscribers["test"]

    @pytest.mark.asyncio
    async def test_unsubscribe_channel(self, event_bus):
        handler = lambda m: None
        event_bus.subscribe_channel("test", handler)
        event_bus.unsubscribe_channel("test", handler)
        assert handler not in event_bus._channel_subscribers.get("test", [])

    @pytest.mark.asyncio
    async def test_send_message_to_channel(self, event_bus):
        await event_bus.start()
        received = []
        event_bus.subscribe_channel("test", lambda m: received.append(m))
        msg = BusMessage(sender="agent-1", channel="test", content={"text": "hello"})
        await event_bus.send_message(msg)
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_channel_wildcard_receives_all(self, event_bus):
        await event_bus.start()
        received = []
        event_bus.subscribe_channel("*", lambda m: received.append(m))
        msg = BusMessage(sender="agent-1", channel="any", content={"text": "hello"})
        await event_bus.send_message(msg)
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_channel_message_not_delivered_to_other_channel(self, event_bus):
        await event_bus.start()
        received_a = []
        received_b = []
        event_bus.subscribe_channel("channel-a", lambda m: received_a.append(m))
        event_bus.subscribe_channel("channel-b", lambda m: received_b.append(m))
        msg = BusMessage(sender="agent-1", channel="channel-a", content={"text": "hello"})
        await event_bus.send_message(msg)
        assert len(received_a) == 1
        assert len(received_b) == 0

    @pytest.mark.asyncio
    async def test_send_message_increments_message_count(self, event_bus):
        await event_bus.start()
        msg = BusMessage(sender="agent-1", channel="test", content={})
        await event_bus.send_message(msg)
        assert event_bus.message_count == 1

    @pytest.mark.asyncio
    async def test_not_running_does_not_deliver_messages(self, event_bus):
        received = []
        event_bus.subscribe_channel("test", lambda m: received.append(m))
        msg = BusMessage(sender="agent-1", channel="test", content={})
        await event_bus.send_message(msg)
        assert len(received) == 0


# ══════════════════════════════════════════════════════════════════════
# 7. Direct and Broadcast Messaging
# ══════════════════════════════════════════════════════════════════════


class TestDirectBroadcastMessaging:
    """Test direct and broadcast message methods."""

    @pytest.mark.asyncio
    async def test_broadcast_message(self, event_bus):
        await event_bus.start()
        received = []
        event_bus.subscribe_channel("general", lambda m: received.append(m))
        msg = await event_bus.broadcast(
            sender="agent-1",
            channel="general",
            content={"msg": "hi"},
        )
        assert msg.recipient is None
        assert msg.message_type == MessageType.BROADCAST
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_direct_message(self, event_bus):
        await event_bus.start()
        received = []
        event_bus.subscribe_channel("dm", lambda m: received.append(m))
        msg = await event_bus.send_direct(
            sender="agent-1",
            recipient="agent-2",
            channel="dm",
            content={"text": "direct"},
        )
        assert msg.recipient == "agent-2"
        assert msg.message_type == MessageType.REQUEST
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_direct_with_correlation_id(self, event_bus):
        await event_bus.start()
        msg = await event_bus.send_direct(
            sender="agent-1",
            recipient="agent-2",
            channel="dm",
            content={},
            correlation_id="corr-123",
        )
        assert msg.correlation_id == "corr-123"

    @pytest.mark.asyncio
    async def test_broadcast_has_normal_priority(self, event_bus):
        await event_bus.start()
        msg = await event_bus.broadcast(
            sender="agent-1",
            channel="general",
            content={},
        )
        assert msg.priority == BusMessagePriority.NORMAL


# ══════════════════════════════════════════════════════════════════════
# 8. Message Type Handlers
# ══════════════════════════════════════════════════════════════════════


class TestMessageTypeHandlers:
    """Test message type-based handlers."""

    @pytest.mark.asyncio
    async def test_subscribe_messages(self, event_bus):
        handler = lambda m: None
        event_bus.subscribe_messages("request", handler)
        assert handler in event_bus._message_handlers["request"]

    @pytest.mark.asyncio
    async def test_message_type_handler_receives(self, event_bus):
        await event_bus.start()
        received = []
        event_bus.subscribe_messages("request", lambda m: received.append(m))
        msg = BusMessage(
            sender="agent-1",
            channel="test",
            message_type=MessageType.REQUEST,
            content={},
        )
        await event_bus.send_message(msg)
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_message_type_handler_not_called_for_other_type(self, event_bus):
        await event_bus.start()
        received = []
        event_bus.subscribe_messages("request", lambda m: received.append(m))
        msg = BusMessage(
            sender="agent-1",
            channel="test",
            message_type=MessageType.NOTIFICATION,
            content={},
        )
        await event_bus.send_message(msg)
        assert len(received) == 0


# ══════════════════════════════════════════════════════════════════════
# 9. History
# ══════════════════════════════════════════════════════════════════════


class TestEventBusHistory:
    """Test event and message history."""

    @pytest.mark.asyncio
    async def test_event_history_basic(self, event_bus):
        await event_bus.start()
        action = Action(action_type=ActionType.THINK, agent_id="test")
        await event_bus.publish_action(action)
        history = event_bus.get_event_history()
        assert len(history) == 1

    @pytest.mark.asyncio
    async def test_event_history_filter_by_type(self, event_bus):
        await event_bus.start()
        action = Action(action_type=ActionType.THINK, agent_id="test")
        await event_bus.publish_action(action)
        obs = Observation(
            observation_type=ObservationType.SUCCESS,
            agent_id="test",
            action_id="a1",
            content="ok",
        )
        await event_bus.publish_observation(obs)
        action_history = event_bus.get_event_history(event_type="action")
        assert len(action_history) == 1
        obs_history = event_bus.get_event_history(event_type="observation")
        assert len(obs_history) == 1

    @pytest.mark.asyncio
    async def test_event_history_filter_by_source(self, event_bus):
        await event_bus.start()
        action1 = Action(action_type=ActionType.THINK, agent_id="agent-1")
        action2 = Action(action_type=ActionType.THINK, agent_id="agent-2")
        await event_bus.publish_action(action1)
        await event_bus.publish_action(action2)
        history = event_bus.get_event_history(source="agent-1")
        assert len(history) == 1

    @pytest.mark.asyncio
    async def test_event_history_limit(self, event_bus):
        await event_bus.start()
        for i in range(10):
            action = Action(action_type=ActionType.THINK, agent_id=f"agent-{i}")
            await event_bus.publish_action(action)
        history = event_bus.get_event_history(limit=5)
        assert len(history) == 5

    @pytest.mark.asyncio
    async def test_message_history_basic(self, event_bus):
        await event_bus.start()
        await event_bus.broadcast(sender="test", channel="test", content={})
        history = event_bus.get_message_history()
        assert len(history) == 1

    @pytest.mark.asyncio
    async def test_message_history_filter_by_channel(self, event_bus):
        await event_bus.start()
        await event_bus.broadcast(sender="test", channel="chan-a", content={})
        await event_bus.broadcast(sender="test", channel="chan-b", content={})
        history = event_bus.get_message_history(channel="chan-a")
        assert len(history) == 1

    @pytest.mark.asyncio
    async def test_message_history_filter_by_sender(self, event_bus):
        await event_bus.start()
        await event_bus.broadcast(sender="agent-1", channel="test", content={})
        await event_bus.broadcast(sender="agent-2", channel="test", content={})
        history = event_bus.get_message_history(sender="agent-1")
        assert len(history) == 1

    @pytest.mark.asyncio
    async def test_message_history_limit(self, event_bus):
        await event_bus.start()
        for i in range(10):
            await event_bus.broadcast(sender=f"agent-{i}", channel="test", content={})
        history = event_bus.get_message_history(limit=5)
        assert len(history) == 5

    @pytest.mark.asyncio
    async def test_clear_history(self, event_bus):
        await event_bus.start()
        action = Action(action_type=ActionType.THINK, agent_id="test")
        await event_bus.publish_action(action)
        await event_bus.broadcast(sender="test", channel="test", content={})
        event_bus.clear_history()
        assert len(event_bus.get_event_history()) == 0
        assert len(event_bus.get_message_history()) == 0

    @pytest.mark.asyncio
    async def test_history_respects_max_history(self):
        bus = EventBus(max_history=5)
        await bus.start()
        for i in range(10):
            event = Event(event_type=EventType.CUSTOM, source=f"src-{i}")
            await bus.publish_event(event)
        assert len(bus._history) <= 5


# ══════════════════════════════════════════════════════════════════════
# 10. Error Handling
# ══════════════════════════════════════════════════════════════════════


class TestEventBusErrorHandling:
    """Test error handling in event/message handlers."""

    @pytest.mark.asyncio
    async def test_handler_error_doesnt_crash_event_publish(self, event_bus):
        await event_bus.start()

        async def bad_handler(e):
            raise ValueError("Handler error")

        event_bus.subscribe("action", bad_handler)
        action = Action(action_type=ActionType.THINK, agent_id="test")
        await event_bus.publish_action(action)  # Should not raise

    @pytest.mark.asyncio
    async def test_handler_error_doesnt_crash_message(self, event_bus):
        await event_bus.start()

        async def bad_handler(m):
            raise ValueError("Handler error")

        event_bus.subscribe_channel("test", bad_handler)
        msg = BusMessage(sender="agent-1", channel="test", content={})
        await event_bus.send_message(msg)  # Should not raise

    @pytest.mark.asyncio
    async def test_bad_handler_doesnt_prevent_good_handler(self, event_bus):
        await event_bus.start()
        received = []

        async def bad_handler(e):
            raise ValueError("fail")

        event_bus.subscribe("action", bad_handler)
        event_bus.subscribe("action", lambda e: received.append(e))
        action = Action(action_type=ActionType.THINK, agent_id="test")
        await event_bus.publish_action(action)
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_message_type_handler_error_doesnt_crash(self, event_bus):
        await event_bus.start()

        async def bad_handler(m):
            raise ValueError("fail")

        event_bus.subscribe_messages("request", bad_handler)
        msg = BusMessage(
            sender="agent-1",
            channel="test",
            message_type=MessageType.REQUEST,
            content={},
        )
        await event_bus.send_message(msg)  # Should not raise


# ══════════════════════════════════════════════════════════════════════
# 11. Statistics
# ══════════════════════════════════════════════════════════════════════


class TestEventBusStats:
    """Test get_stats method."""

    @pytest.mark.asyncio
    async def test_initial_stats(self, event_bus):
        stats = event_bus.get_stats()
        assert stats["running"] is False
        assert stats["total_events"] == 0
        assert stats["total_messages"] == 0
        assert stats["history_size"] == 0

    @pytest.mark.asyncio
    async def test_stats_after_events(self, event_bus):
        await event_bus.start()
        action = Action(action_type=ActionType.THINK, agent_id="test")
        await event_bus.publish_action(action)
        stats = event_bus.get_stats()
        assert stats["total_events"] == 1
        assert stats["history_size"] == 1

    @pytest.mark.asyncio
    async def test_stats_after_messages(self, event_bus):
        await event_bus.start()
        await event_bus.broadcast(sender="test", channel="test", content={})
        stats = event_bus.get_stats()
        assert stats["total_messages"] == 1

    @pytest.mark.asyncio
    async def test_stats_subscriber_count(self, event_bus):
        event_bus.subscribe("action", lambda e: None)
        event_bus.subscribe("observation", lambda e: None)
        stats = event_bus.get_stats()
        assert stats["subscriber_count"] == 2

    @pytest.mark.asyncio
    async def test_stats_pending_observations(self, event_bus):
        await event_bus.start()
        stats = event_bus.get_stats()
        assert stats["pending_observations"] == 0


# ══════════════════════════════════════════════════════════════════════
# 12. Singleton Pattern
# ══════════════════════════════════════════════════════════════════════


class TestEventBusSingleton:
    """Test EventBus singleton pattern."""

    def test_get_instance_returns_bus(self):
        EventBus.reset()
        instance = EventBus.get_instance()
        assert isinstance(instance, EventBus)

    def test_get_instance_returns_same(self):
        EventBus.reset()
        i1 = EventBus.get_instance()
        i2 = EventBus.get_instance()
        assert i1 is i2

    def test_reset_clears_singleton(self):
        i1 = EventBus.get_instance()
        EventBus.reset()
        i2 = EventBus.get_instance()
        assert i1 is not i2


# ══════════════════════════════════════════════════════════════════════
# 13. Multiple Subscribers
# ══════════════════════════════════════════════════════════════════════


class TestMultipleSubscribers:
    """Test multiple subscribers on the same event type."""

    @pytest.mark.asyncio
    async def test_all_subscribers_receive_event(self, event_bus):
        await event_bus.start()
        received_1 = []
        received_2 = []
        event_bus.subscribe("action", lambda e: received_1.append(e))
        event_bus.subscribe("action", lambda e: received_2.append(e))
        action = Action(action_type=ActionType.THINK, agent_id="test")
        await event_bus.publish_action(action)
        assert len(received_1) == 1
        assert len(received_2) == 1

    @pytest.mark.asyncio
    async def test_all_channel_subscribers_receive(self, event_bus):
        await event_bus.start()
        received_1 = []
        received_2 = []
        event_bus.subscribe_channel("test", lambda m: received_1.append(m))
        event_bus.subscribe_channel("test", lambda m: received_2.append(m))
        msg = BusMessage(sender="agent-1", channel="test", content={})
        await event_bus.send_message(msg)
        assert len(received_1) == 1
        assert len(received_2) == 1
