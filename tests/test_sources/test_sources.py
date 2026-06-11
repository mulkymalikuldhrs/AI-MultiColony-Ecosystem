"""Tests for Intelligence Data Sources."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from ai_multicolony_ecosystem.sources.base import (
    BaseSource,
    SourceHealth,
    SourceRegistry,
    SourceResult,
    SourceTier,
)
from ai_multicolony_ecosystem.sources.economic import (
    FREDSource,
    BLSSource,
    EIASource,
    TreasurySource,
)
from ai_multicolony_ecosystem.sources.osint import (
    GDELTSource,
    ACLEDSource,
    WHOSource,
    OFACSource,
    YFinanceSource,
    RedditSource,
)


# ======================================================================
# Base Source Tests
# ======================================================================

class TestSourceTier:
    def test_values(self):
        assert SourceTier.OSINT == "osint"
        assert SourceTier.ECONOMIC == "economic"
        assert SourceTier.MARKET == "market"
        assert SourceTier.WEATHER == "weather"
        assert SourceTier.SPACE == "space"
        assert SourceTier.CYBER == "cyber"


class TestSourceHealth:
    def test_values(self):
        assert SourceHealth.HEALTHY == "healthy"
        assert SourceHealth.DEGRADED == "degraded"
        assert SourceHealth.DOWN == "down"
        assert SourceHealth.UNKNOWN == "unknown"


class TestSourceResult:
    def test_defaults(self):
        result = SourceResult(source="test")
        assert result.source == "test"
        assert result.data is None
        assert result.error is None
        assert result.latency_ms == 0.0

    def test_with_data(self):
        result = SourceResult(source="test", data={"key": "value"}, tier=SourceTier.ECONOMIC)
        assert result.data == {"key": "value"}
        assert result.tier == SourceTier.ECONOMIC


class TestSourceRegistry:
    def test_list_sources(self):
        sources = SourceRegistry.list_sources()
        assert "fred" in sources
        assert "gdelt" in sources
        assert "yfinance" in sources
        assert len(sources) >= 9

    def test_create_source(self):
        source = SourceRegistry.create("fred", config={"api_key": "test"})
        assert source is not None
        assert source.name == "fred"
        assert source.tier == SourceTier.ECONOMIC

    def test_create_nonexistent(self):
        source = SourceRegistry.create("nonexistent_source")
        assert source is None

    def test_count(self):
        assert SourceRegistry.count() >= 9

    def test_create_all(self):
        sources = SourceRegistry.create_all()
        assert len(sources) >= 9


# ======================================================================
# Concrete Source Tests
# ======================================================================

class TestFREDSource:
    def test_construction(self):
        source = FREDSource(config={"api_key": "test_key"})
        assert source.name == "fred"
        assert source.tier == SourceTier.ECONOMIC

    def test_no_key(self):
        source = FREDSource()
        assert source._api_key == ""

    @pytest.mark.asyncio
    async def test_sweep_no_key(self):
        source = FREDSource()
        result = await source.safe_sweep()
        assert result.error is not None


class TestBLSSource:
    def test_construction(self):
        source = BLSSource(config={"api_key": "test"})
        assert source.name == "bls"

    @pytest.mark.asyncio
    async def test_sweep_no_key(self):
        source = BLSSource()
        result = await source.safe_sweep()
        assert result.error is not None


class TestEIASource:
    def test_construction(self):
        source = EIASource(config={"api_key": "test"})
        assert source.name == "eia"

    @pytest.mark.asyncio
    async def test_sweep_no_key(self):
        source = EIASource()
        result = await source.safe_sweep()
        assert result.error is not None


class TestTreasurySource:
    def test_construction(self):
        source = TreasurySource()
        assert source.name == "treasury"
        assert source.tier == SourceTier.ECONOMIC


class TestGDELTSource:
    def test_construction(self):
        source = GDELTSource()
        assert source.name == "gdelt"
        assert source.tier == SourceTier.OSINT


class TestACLEDSource:
    def test_construction(self):
        source = ACLEDSource(config={"api_key": "k", "email": "e"})
        assert source.name == "acled"

    @pytest.mark.asyncio
    async def test_no_credentials(self):
        source = ACLEDSource()
        result = await source.safe_sweep()
        assert result.error is not None


class TestYFinanceSource:
    def test_construction(self):
        source = YFinanceSource()
        assert source.name == "yfinance"
        assert source.tier == SourceTier.MARKET


class TestRedditSource:
    def test_construction(self):
        source = RedditSource()
        assert source.name == "reddit"
        assert source.tier == SourceTier.OSINT
