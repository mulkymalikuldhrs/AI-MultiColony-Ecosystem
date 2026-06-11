"""Tests for SenseEngine — signal scanning, RSS/API/Trend scanners."""

from __future__ import annotations

import pytest

from ai_multicolony.organism.sense import (
    APIScanner,
    RSSScanner,
    ScanResult,
    SenseEngine,
    Signal,
    SignalScanner,
    SignalSeverity,
    SignalSource,
    SignalType,
    TrendScanner,
)


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def engine():
    return SenseEngine()


# ── Signal Model ─────────────────────────────────────────────────────────

class TestSignalModel:
    """Test Signal Pydantic model."""

    def test_signal_defaults(self):
        s = Signal()
        assert s.signal_type == SignalType.PROBLEM
        assert s.severity == SignalSeverity.MEDIUM
        assert s.confidence == 0.5

    def test_signal_is_urgent_critical(self):
        s = Signal(severity=SignalSeverity.CRITICAL)
        assert s.is_urgent is True

    def test_signal_is_urgent_high(self):
        s = Signal(severity=SignalSeverity.HIGH)
        assert s.is_urgent is True

    def test_signal_not_urgent_medium(self):
        s = Signal(severity=SignalSeverity.MEDIUM)
        assert s.is_urgent is False

    def test_signal_with_data(self):
        s = Signal(
            signal_type=SignalType.THREAT,
            severity=SignalSeverity.HIGH,
            title="Security breach",
            data={"source": "firewall"},
            tags=["security", "breach"],
        )
        assert s.signal_type == SignalType.THREAT
        assert len(s.tags) == 2


# ── Signal Types ─────────────────────────────────────────────────────────

class TestSignalTypes:
    """Test signal type enums."""

    def test_signal_types(self):
        types = {t.value for t in SignalType}
        assert "problem" in types
        assert "opportunity" in types
        assert "threat" in types
        assert "trend" in types
        assert "anomaly" in types
        assert "event" in types

    def test_severity_levels(self):
        levels = {l.value for l in SignalSeverity}
        assert "critical" in levels
        assert "high" in levels
        assert "medium" in levels
        assert "low" in levels
        assert "info" in levels

    def test_signal_sources(self):
        sources = {s.value for s in SignalSource}
        assert "rss_feed" in sources
        assert "api" in sources
        assert "trend_detection" in sources


# ── RSS Scanner ──────────────────────────────────────────────────────────

class TestRSSScanner:
    """Test RSSScanner."""

    @pytest.mark.asyncio
    async def test_scan_with_feeds(self):
        scanner = RSSScanner(feeds=["https://example.com/feed"])
        signals = await scanner.scan()
        assert isinstance(signals, list)
        assert len(signals) > 0

    @pytest.mark.asyncio
    async def test_scan_no_feeds(self):
        scanner = RSSScanner(feeds=[])
        signals = await scanner.scan()
        assert len(signals) == 0

    @pytest.mark.asyncio
    async def test_custom_keywords(self):
        scanner = RSSScanner(
            feeds=["https://example.com/feed"],
            keywords=["custom_keyword"],
        )
        assert "custom_keyword" in scanner._keywords

    def test_scanner_stats(self):
        scanner = RSSScanner()
        stats = scanner.stats
        assert stats["name"] == "rss_scanner"
        assert stats["source"] == "rss_feed"


# ── API Scanner ──────────────────────────────────────────────────────────

class TestAPIScanner:
    """Test APIScanner."""

    @pytest.mark.asyncio
    async def test_scan_with_endpoints(self):
        scanner = APIScanner(endpoints=[
            {"url": "https://api.example.com", "thresholds": {"cpu": 90}},
        ])
        signals = await scanner.scan()
        assert len(signals) > 0
        assert any(s.title == "Threshold check: cpu" for s in signals)

    @pytest.mark.asyncio
    async def test_scan_no_endpoints(self):
        scanner = APIScanner(endpoints=[])
        signals = await scanner.scan()
        assert len(signals) == 0


# ── Trend Scanner ────────────────────────────────────────────────────────

class TestTrendScanner:
    """Test TrendScanner."""

    @pytest.mark.asyncio
    async def test_spike_detection(self):
        scanner = TrendScanner(spike_threshold=1.0, window_size=5)
        # Add data with a spike
        for i in range(10):
            scanner.add_data_point("test_series", 10.0)
        scanner.add_data_point("test_series", 100.0)  # Spike
        signals = await scanner.scan()
        spike_signals = [s for s in signals if "Spike" in s.title]
        assert len(spike_signals) > 0

    @pytest.mark.asyncio
    async def test_trend_detection(self):
        scanner = TrendScanner(trend_threshold=0.5, window_size=5)
        # Add trending data
        for i in range(25):
            scanner.add_data_point("test_series", float(i))
        signals = await scanner.scan()
        trend_signals = [s for s in signals if "trend" in s.title.lower()]
        assert len(trend_signals) > 0

    @pytest.mark.asyncio
    async def test_insufficient_data(self):
        scanner = TrendScanner()
        scanner.add_data_point("test_series", 1.0)
        signals = await scanner.scan()
        assert len(signals) == 0


# ── Sense Engine ─────────────────────────────────────────────────────────

class TestSenseEngine:
    """Test SenseEngine orchestration."""

    def test_add_scanner(self, engine):
        scanner = RSSScanner()
        engine.add_scanner(scanner)
        assert engine.scanner_count == 1

    def test_remove_scanner(self, engine):
        scanner = RSSScanner()
        engine.add_scanner(scanner)
        result = engine.remove_scanner("rss_scanner")
        assert result is True
        assert engine.scanner_count == 0

    def test_remove_nonexistent_scanner(self, engine):
        result = engine.remove_scanner("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_scan_with_scanners(self, engine):
        engine.add_scanner(RSSScanner(feeds=["https://example.com/feed"]))
        result = await engine.scan()
        assert isinstance(result, ScanResult)
        assert result.elapsed_ms >= 0

    @pytest.mark.asyncio
    async def test_scan_no_scanners(self, engine):
        result = await engine.scan()
        assert result.signals == []
        assert result.errors == []

    @pytest.mark.asyncio
    async def test_scan_deduplicates(self, engine):
        # Two identical feeds should be deduplicated
        engine.add_scanner(RSSScanner(feeds=["https://example.com/feed"]))
        result = await engine.scan()
        # Second scan with same feed should not duplicate
        result2 = await engine.scan()
        # New signals should be fewer (most already seen)
        assert result2.new_signals <= result.new_signals

    @pytest.mark.asyncio
    async def test_scan_handles_scanner_error(self, engine):
        class ErrorScanner(SignalScanner):
            def __init__(self):
                super().__init__("error_scanner", SignalSource.API)
            async def scan(self, **kwargs):
                self._scan_count += 1
                raise RuntimeError("Scanner error")

        engine.add_scanner(ErrorScanner())
        result = await engine.scan()
        assert len(result.errors) > 0

    def test_engine_stats(self, engine):
        stats = engine.stats
        assert "scanner_count" in stats
        assert "scan_count" in stats
