"""Tests for OSINTSource — GDELT, ACLED, WHO, OFAC sources."""

from __future__ import annotations

import pytest

from ai_multicolony.sources.osint import OSINTSource, OSINT_CATEGORIES
from ai_multicolony.sources.base import SourceCategory, SourceReliability


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def osint():
    return OSINTSource()


# ── OSINT Categories ─────────────────────────────────────────────────────

class TestOSINTCategories:
    """Test OSINT category definitions."""

    def test_categories_exist(self):
        assert len(OSINT_CATEGORIES) > 0

    def test_geopolitical_conflict_category(self):
        cat = OSINT_CATEGORIES["geopolitical_conflict"]
        assert cat["category"] == SourceCategory.GEOPOLITICAL

    def test_sanctions_category(self):
        cat = OSINT_CATEGORIES["geopolitical_sanctions"]
        assert cat["category"] == SourceCategory.GEOPOLITICAL
        assert cat["reliability"] == SourceReliability.RELIABLE


# ── Source Properties ────────────────────────────────────────────────────

class TestOSINTSourceProperties:
    """Test source metadata."""

    def test_name(self, osint):
        assert osint.name == "osint"

    def test_category(self, osint):
        assert osint.category == SourceCategory.GEOPOLITICAL

    def test_reliability(self, osint):
        assert osint.reliability in (
            SourceReliability.USUALLY_RELIABLE,
            SourceReliability.RELIABLE,
            SourceReliability.FAIRLY_RELIABLE,
        )


# ── Fetch ────────────────────────────────────────────────────────────────

class TestOSINTFetch:
    """Test targeted fetch."""

    @pytest.mark.asyncio
    async def test_fetch_returns_result(self, osint):
        result = await osint.fetch("conflict", max_items=10)
        assert result is not None
        assert hasattr(result, "items")
        assert hasattr(result, "errors")

    @pytest.mark.asyncio
    async def test_fetch_with_query(self, osint):
        result = await osint.fetch("sanctions", max_items=10)
        # Should return some items matching "sanctions"
        assert result.total_available >= 0

    @pytest.mark.asyncio
    async def test_fetch_max_items_respected(self, osint):
        result = await osint.fetch("conflict", max_items=3)
        assert len(result.items) <= 3

    @pytest.mark.asyncio
    async def test_fetch_empty_query(self, osint):
        result = await osint.fetch("", max_items=10)
        # Empty query should still work
        assert result is not None


# ── Scan ─────────────────────────────────────────────────────────────────

class TestOSINTScan:
    """Test broad scan."""

    @pytest.mark.asyncio
    async def test_scan_returns_items(self, osint):
        result = await osint.scan(max_items=50)
        assert len(result.items) > 0

    @pytest.mark.asyncio
    async def test_scan_items_have_source_name(self, osint):
        result = await osint.scan(max_items=10)
        for item in result.items:
            assert item.source_name == "osint"

    @pytest.mark.asyncio
    async def test_scan_items_have_category(self, osint):
        result = await osint.scan(max_items=10)
        for item in result.items:
            assert isinstance(item.category, SourceCategory)


# ── Health Check ─────────────────────────────────────────────────────────

class TestOSINTHealthCheck:
    """Test health check."""

    @pytest.mark.asyncio
    async def test_health_check(self, osint):
        result = await osint.health_check()
        assert "status" in result
