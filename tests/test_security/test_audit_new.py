"""Tests for AuditTrail — hash-chain integrity, level filtering, retention."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta

import pytest

from ai_multicolony.security.audit import (
    AuditTrail,
    MemoryAuditStorage,
)
from ai_multicolony.types import AuditEntry, AuditEvent, AuditEventType, AuditLevel, AuditQuery


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def audit():
    """Create a memory-backed AuditTrail at FULL level."""
    return AuditTrail(level=AuditLevel.FULL, storage="memory")


@pytest.fixture
def audit_minimal():
    """Create an audit trail at MINIMAL level."""
    return AuditTrail(level=AuditLevel.MINIMAL, storage="memory")


@pytest.fixture
def audit_summary():
    """Create an audit trail at SUMMARY level."""
    return AuditTrail(level=AuditLevel.SUMMARY, storage="memory")


# ── Recording ────────────────────────────────────────────────────────────

class TestRecording:
    """Test record method."""

    def test_record_returns_entry(self, audit):
        entry = audit.record(
            agent_id="agent-1",
            tool_name="shell.execute",
            action="executed",
            event_type=AuditEventType.TOOL_CALL,
        )
        assert entry is not None
        assert entry.agent_id == "agent-1"
        assert entry.tool_name == "shell.execute"

    def test_record_increments_count(self, audit):
        assert audit.entry_count == 0
        audit.record(agent_id="a1", tool_name="t1", action="a1")
        assert audit.entry_count == 1

    def test_record_multiple(self, audit):
        for i in range(5):
            audit.record(agent_id=f"agent-{i}", tool_name="test", action="run")
        assert audit.entry_count == 5


# ── Level Filtering ──────────────────────────────────────────────────────

class TestLevelFiltering:
    """Test audit level filtering."""

    def test_minimal_filters_tool_call(self, audit_minimal):
        result = audit_minimal.record(
            agent_id="a1",
            tool_name="test",
            action="call",
            event_type=AuditEventType.TOOL_CALL,
        )
        assert result is None  # Filtered out at MINIMAL

    def test_minimal_keeps_escalation(self, audit_minimal):
        result = audit_minimal.record(
            agent_id="a1",
            tool_name="test",
            action="escalate",
            event_type=AuditEventType.ESCALATION,
        )
        assert result is not None

    def test_summary_keeps_tool_call(self, audit_summary):
        result = audit_summary.record(
            agent_id="a1",
            tool_name="test",
            action="call",
            event_type=AuditEventType.TOOL_CALL,
        )
        assert result is not None

    def test_full_keeps_everything(self, audit):
        for et in AuditEventType:
            result = audit.record(
                agent_id="a1",
                tool_name="test",
                action=et.value,
                event_type=et,
            )
            assert result is not None


# ── Hash Chain Integrity ────────────────────────────────────────────────

class TestHashChainIntegrity:
    """Test hash chain verification."""

    def test_verify_chain_intact(self, audit):
        audit.record(agent_id="a1", tool_name="t1", action="run", event_type=AuditEventType.TOOL_CALL)
        audit.record(agent_id="a2", tool_name="t2", action="run", event_type=AuditEventType.AUTH)
        audit.record(agent_id="a3", tool_name="t3", action="run", event_type=AuditEventType.TOOL_CALL)
        assert audit.verify_chain() is True

    def test_verify_chain_empty(self, audit):
        assert audit.verify_chain() is True  # Empty chain is valid

    def test_chain_hashes_differ(self, audit):
        e1 = audit.record(agent_id="a1", tool_name="t1", action="run", event_type=AuditEventType.TOOL_CALL)
        e2 = audit.record(agent_id="a2", tool_name="t2", action="run", event_type=AuditEventType.TOOL_CALL)
        h1 = audit._storage._hash_chain[0]
        h2 = audit._storage._hash_chain[1]
        assert h1 != h2


# ── Query ────────────────────────────────────────────────────────────────

class TestQuery:
    """Test query and filter methods."""

    def test_get_entries(self, audit):
        audit.record(agent_id="a1", tool_name="t1", action="run", event_type=AuditEventType.TOOL_CALL)
        audit.record(agent_id="a2", tool_name="t2", action="run", event_type=AuditEventType.TOOL_CALL)
        entries = audit.get_entries()
        assert len(entries) == 2

    def test_get_entries_by_agent(self, audit):
        audit.record(agent_id="a1", tool_name="t1", action="run", event_type=AuditEventType.TOOL_CALL)
        audit.record(agent_id="a2", tool_name="t2", action="run", event_type=AuditEventType.TOOL_CALL)
        entries = audit.get_entries(agent_id="a1")
        assert len(entries) == 1
        assert entries[0].agent_id == "a1"

    def test_get_entries_by_colony(self, audit):
        audit.record(agent_id="a1", tool_name="t1", action="run", colony_id="colony-1", event_type=AuditEventType.TOOL_CALL)
        audit.record(agent_id="a2", tool_name="t2", action="run", colony_id="colony-2", event_type=AuditEventType.TOOL_CALL)
        entries = audit.get_entries_by_colony("colony-1")
        assert len(entries) == 1

    def test_query_with_time_range(self, audit):
        audit.record(agent_id="a1", tool_name="t1", action="run", event_type=AuditEventType.TOOL_CALL)
        now = datetime.now(timezone.utc)
        entries = audit.get_entries_by_time_range(
            start=now - timedelta(hours=1),
            end=now + timedelta(hours=1),
        )
        assert len(entries) >= 1


# ── Retention ────────────────────────────────────────────────────────────

class TestRetention:
    """Test retention policy enforcement."""

    def test_enforce_retention_nothing_removed(self, audit):
        audit.record(agent_id="a1", tool_name="t1", action="run", event_type=AuditEventType.TOOL_CALL)
        removed = audit.enforce_retention()
        assert removed == 0

    def test_enforce_retention_removes_old(self, audit):
        # Manually add an old entry
        audit.record(agent_id="a1", tool_name="t1", action="run", event_type=AuditEventType.TOOL_CALL)
        # Modify timestamp to be old
        old_time = datetime.now(timezone.utc) - timedelta(days=100)
        audit._storage._entries[0].timestamp = old_time
        removed = audit.enforce_retention()
        assert removed == 1


# ── Record Event Model ──────────────────────────────────────────────────

class TestRecordEvent:
    """Test record_event with AuditEvent model."""

    def test_record_event(self, audit):
        event = AuditEvent(
            agent_id="agent-1",
            colony_id="colony-1",
            event_type=AuditEventType.TOOL_CALL,
            description="Test event",
            metadata={"tool_name": "shell.execute", "approved": True},
        )
        entry = audit.record_event(event)
        assert entry is not None
        assert entry.agent_id == "agent-1"


# ── Flush ────────────────────────────────────────────────────────────────

class TestFlush:
    """Test flush method."""

    def test_flush_memory(self, audit):
        audit.record(agent_id="a1", tool_name="t1", action="run", event_type=AuditEventType.TOOL_CALL)
        audit.flush()  # Should not raise
        assert audit.entry_count == 1  # Data still there for memory storage
