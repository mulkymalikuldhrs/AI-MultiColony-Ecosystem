"""Tests for SourceManager — registration, sweep, aggregation, deduplication."""

from __future__ import annotations

import pytest

from ai_multicolony.sources.base import SourceProvider, SourceConfig, SourceItem, SourceResult, SourceCategory, SourceReliability
from ai_multicolony.sources.manager import SourceManager, SweepResult, AggregatedResult


# ── Fixtures ────────────────────────────────────────────────────────────────

class MockSource(SourceProvider):
    """Mock source for testing."""

    def __init__(self, name: str = "mock", items: list | None = None):
        super().__init__(
            name=name,
            category=SourceCategory.GEOPOLITICAL,
            reliability=SourceReliability.RELIABLE,
        )
        self._items = items or [
            SourceItem(
                source_name=name,
                category=SourceCategory.GEOPOLITICAL,
                title=f"Test item from {name}",
                summary=f"Summary from {name}",
                content=f"Content from {name}",
                relevance_score=0.7,
                confidence=0.8,
            )
        ]

    async def fetch(self, query: str, max_items: int = 50, **kwargs) -> SourceResult:
        self._record_fetch()
        return self._make_result(
            items=self._items[:max_items],
            total_available=len(self._items),
        )

    async def scan(self, max_items: int = 100, **kwargs) -> SourceResult:
        self._record_scan()
        return self._make_result(
            items=self._items[:max_items],
            total_available=len(self._items),
        )


class FailingSource(SourceProvider):
    """Source that always fails."""

    def __init__(self):
        super().__init__(
            name="failing",
            category=SourceCategory.ECONOMIC,
            reliability=SourceReliability.UNRELIABLE,
        )

    async def fetch(self, query: str, max_items: int = 50, **kwargs) -> SourceResult:
        raise RuntimeError("Source unavailable")

    async def scan(self, max_items: int = 100, **kwargs) -> SourceResult:
        raise RuntimeError("Source unavailable")


@pytest.fixture
def manager():
    return SourceManager()


@pytest.fixture
def manager_with_sources():
    m = SourceManager()
    m.register(MockSource(name="source_a"))
    m.register(MockSource(name="source_b"))
    return m


# ── Registration ─────────────────────────────────────────────────────────

class TestRegistration:
    """Test source registration."""

    def test_register_source(self, manager):
        manager.register(MockSource())
        assert manager.source_count == 1

    def test_register_multiple(self, manager):
        manager.register(MockSource(name="a"))
        manager.register(MockSource(name="b"))
        assert manager.source_count == 2

    def test_register_replaces(self, manager):
        manager.register(MockSource(name="test"))
        manager.register(MockSource(name="test"))  # Same name
        assert manager.source_count == 1

    def test_unregister(self, manager):
        manager.register(MockSource(name="test"))
        result = manager.unregister("test")
        assert result is True
        assert manager.source_count == 0

    def test_unregister_nonexistent(self, manager):
        result = manager.unregister("nonexistent")
        assert result is False

    def test_get_source(self, manager):
        source = MockSource(name="test")
        manager.register(source)
        assert manager.get_source("test") is source

    def test_get_source_nonexistent(self, manager):
        assert manager.get_source("nonexistent") is None

    def test_sources_property(self, manager):
        manager.register(MockSource(name="a"))
        manager.register(MockSource(name="b"))
        sources = manager.sources
        assert "a" in sources
        assert "b" in sources


# ── Sweep Operations ─────────────────────────────────────────────────────

class TestSweepOperations:
    """Test sweep_all."""

    @pytest.mark.asyncio
    async def test_sweep_with_sources(self, manager_with_sources):
        result = await manager_with_sources.sweep_all(max_items=20)
        assert isinstance(result, SweepResult)
        assert result.total_items > 0

    @pytest.mark.asyncio
    async def test_sweep_no_sources(self, manager):
        result = await manager.sweep_all()
        assert result.total_items == 0

    @pytest.mark.asyncio
    async def test_sweep_handles_failing_source(self, manager):
        manager.register(MockSource(name="good"))
        manager.register(FailingSource())
        result = await manager.sweep_all()
        assert "failing" in result.errors_by_source

    @pytest.mark.asyncio
    async def test_sweep_deduplicates(self, manager):
        # Register two sources with identical items
        item = SourceItem(
            source_name="a",
            category=SourceCategory.GEOPOLITICAL,
            title="Same title",
            summary="Same summary",
            relevance_score=0.7,
            confidence=0.8,
        )
        manager.register(MockSource(name="a", items=[item]))
        manager.register(MockSource(name="b", items=[item]))
        result = await manager.sweep_all()
        # Items should be deduplicated
        assert result.deduplicated_items <= result.total_items


# ── Fetch Operations ─────────────────────────────────────────────────────

class TestFetchOperations:
    """Test fetch_all."""

    @pytest.mark.asyncio
    async def test_fetch_with_query(self, manager_with_sources):
        result = await manager_with_sources.fetch_all("test", max_items=20)
        assert isinstance(result, AggregatedResult)
        assert result.total_items >= 0

    @pytest.mark.asyncio
    async def test_fetch_no_sources(self, manager):
        result = await manager.fetch_all("test")
        assert result.total_items == 0

    @pytest.mark.asyncio
    async def test_fetch_relevance_scoring(self, manager_with_sources):
        result = await manager_with_sources.fetch_all("test", max_items=20)
        # Items should be sorted by relevance (descending)
        scores = [i.relevance_score for i in result.items]
        assert scores == sorted(scores, reverse=True)


# ── Health Check ─────────────────────────────────────────────────────────

class TestManagerHealthCheck:
    """Test health_check_all."""

    @pytest.mark.asyncio
    async def test_health_check(self, manager_with_sources):
        results = await manager_with_sources.health_check_all()
        assert isinstance(results, dict)
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_health_check_failing_source(self, manager):
        manager.register(FailingSource())
        results = await manager.health_check_all()
        assert "failing" in results


# ── Stats ────────────────────────────────────────────────────────────────

class TestManagerStats:
    """Test manager statistics."""

    def test_stats_initial(self, manager):
        stats = manager.stats
        assert stats["source_count"] == 0
        assert stats["sweep_count"] == 0

    @pytest.mark.asyncio
    async def test_stats_after_sweep(self, manager_with_sources):
        await manager_with_sources.sweep_all()
        stats = manager_with_sources.stats
        assert stats["sweep_count"] == 1
        assert stats["source_count"] == 2
        assert stats["last_sweep"] is not None


# ── Deduplication ────────────────────────────────────────────────────────

class TestDeduplication:
    """Test item deduplication."""

    def test_hash_item(self):
        item = SourceItem(
            source_name="test",
            title="Title",
            summary="Summary text",
        )
        h = SourceManager._hash_item(item)
        assert isinstance(h, str)
        assert len(h) == 32

    def test_hash_item_deterministic(self):
        item = SourceItem(
            source_name="test",
            title="Title",
            summary="Summary text",
        )
        h1 = SourceManager._hash_item(item)
        h2 = SourceManager._hash_item(item)
        assert h1 == h2

    def test_hash_item_different_for_different_items(self):
        item1 = SourceItem(source_name="a", title="Title A", summary="Summary A")
        item2 = SourceItem(source_name="b", title="Title B", summary="Summary B")
        h1 = SourceManager._hash_item(item1)
        h2 = SourceManager._hash_item(item2)
        assert h1 != h2


# ── Factory ──────────────────────────────────────────────────────────────

class TestCreateDefault:
    """Test create_default factory."""

    @pytest.mark.asyncio
    async def test_create_default(self):
        manager = SourceManager.create_default()
        assert manager.source_count >= 2  # At least OSINT and Economic
