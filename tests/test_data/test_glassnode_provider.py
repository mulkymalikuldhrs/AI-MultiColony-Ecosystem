"""Tests for Glassnode data provider.

All tests mock HTTP responses to avoid real API calls.
No Glassnode API key required to run these tests.
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from quant_nanggroe.data.providers.glassnode_provider import (
    FREE_METRICS,
    GlassnodeError,
    GlassnodeProvider,
    _parse_symbol,
)
from quant_nanggroe.types.market import TimeFrame


# ─── Sample Glassnode API responses ────────────────────────────────────────

SAMPLE_PRICE_RESPONSE = [
    {"t": 1672531200, "v": 16550.0},
    {"t": 1672444800, "v": 16500.0},
    {"t": 1672358400, "v": 16400.0},
]

SAMPLE_METRIC_RESPONSE = [
    {"t": 1672531200, "v": 850000},
    {"t": 1672444800, "v": 820000},
    {"t": 1672358400, "v": 780000},
]

SAMPLE_EMPTY_RESPONSE = []


# ─── Unit tests ──────────────────────────────────────────────────────────


class TestParseSymbol:
    """Tests for the _parse_symbol helper function."""

    def test_parse_with_prefix(self):
        asset, metric = _parse_symbol("GN:BTC")
        assert asset == "BTC"
        assert metric == "price"

    def test_parse_without_prefix(self):
        asset, metric = _parse_symbol("ETH")
        assert asset == "ETH"
        assert metric == "price"

    def test_parse_with_metric(self):
        asset, metric = _parse_symbol("GN:BTC:active_addresses")
        assert asset == "BTC"
        assert metric == "active_addresses"

    def test_parse_eth_with_metric(self):
        asset, metric = _parse_symbol("GN:ETH:marketcap")
        assert asset == "ETH"
        assert metric == "marketcap"


class TestFreeMetrics:
    """Tests for the FREE_METRICS constant."""

    def test_has_basic_metrics(self):
        assert "price" in FREE_METRICS
        assert "marketcap" in FREE_METRICS
        assert "active_addresses" in FREE_METRICS
        assert "hash_rate" in FREE_METRICS

    def test_count(self):
        assert len(FREE_METRICS) >= 10


class TestGlassnodeProviderInit:
    """Tests for GlassnodeProvider initialization."""

    def test_init_defaults(self):
        provider = GlassnodeProvider(api_key="test-key")
        assert provider.name == "glassnode"
        assert provider.priority == 28

    def test_init_custom_priority(self):
        provider = GlassnodeProvider(api_key="test-key", priority=35)
        assert provider.priority == 35

    def test_repr(self):
        provider = GlassnodeProvider(api_key="test-key")
        assert "glassnode" in repr(provider)


class TestGlassnodeGetApiKey:
    """Tests for API key resolution."""

    def test_get_api_key_from_param(self):
        provider = GlassnodeProvider(api_key="my-key")
        assert provider._get_api_key() == "my-key"

    def test_get_api_key_from_env(self):
        with patch.dict("os.environ", {"QNAI_GLASSNODE_API_KEY": "env-key"}):
            provider = GlassnodeProvider()
            assert provider._get_api_key() == "env-key"

    def test_get_api_key_missing_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            import os
            os.environ.pop("QNAI_GLASSNODE_API_KEY", None)
            provider = GlassnodeProvider()
            with pytest.raises(GlassnodeError, match="Glassnode API key not configured"):
                provider._get_api_key()


class TestGlassnodeGetOHLCV:
    """Tests for get_ohlcv method with mocked API."""

    @pytest.mark.asyncio
    async def test_get_ohlcv_success(self):
        provider = GlassnodeProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_PRICE_RESPONSE

            result = await provider.get_ohlcv("GN:BTC", TimeFrame.D1)

        assert len(result) == 3
        assert result[0].symbol == "GN:BTC"
        assert result[0].close == 16400.0
        assert result[2].close == 16550.0

    @pytest.mark.asyncio
    async def test_get_ohlcv_raw_symbol(self):
        provider = GlassnodeProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_PRICE_RESPONSE

            result = await provider.get_ohlcv("BTC", TimeFrame.D1)

        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_get_ohlcv_empty_response(self):
        provider = GlassnodeProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_EMPTY_RESPONSE

            result = await provider.get_ohlcv("GN:BTC", TimeFrame.D1)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_ohlcv_api_error(self):
        provider = GlassnodeProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.side_effect = GlassnodeError("API error")

            result = await provider.get_ohlcv("GN:BTC", TimeFrame.D1)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_ohlcv_with_date_range(self):
        provider = GlassnodeProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_PRICE_RESPONSE

            await provider.get_ohlcv(
                "GN:BTC",
                start=datetime(2023, 1, 1),
                end=datetime(2023, 12, 31),
            )

        call_params = mock_req.call_args[0][1]
        assert "s" in call_params
        assert "u" in call_params


class TestGlassnodeGetTicker:
    """Tests for get_ticker method with mocked API."""

    @pytest.mark.asyncio
    async def test_get_ticker_success(self):
        provider = GlassnodeProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_PRICE_RESPONSE

            ticker = await provider.get_ticker("GN:BTC")

        assert ticker is not None
        assert ticker.symbol == "GN:BTC"
        assert ticker.last_price == 16550.0

    @pytest.mark.asyncio
    async def test_get_ticker_empty_response(self):
        provider = GlassnodeProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_EMPTY_RESPONSE

            ticker = await provider.get_ticker("GN:BTC")

        assert ticker is None

    @pytest.mark.asyncio
    async def test_get_ticker_api_error(self):
        provider = GlassnodeProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.side_effect = GlassnodeError("API error")

            ticker = await provider.get_ticker("GN:BTC")

        assert ticker is None


class TestGlassnodeGetOrderbook:
    """Tests for get_orderbook method."""

    @pytest.mark.asyncio
    async def test_get_orderbook_returns_none(self):
        provider = GlassnodeProvider(api_key="test-key")
        result = await provider.get_orderbook("GN:BTC")
        assert result is None


class TestGlassnodeGetMetric:
    """Tests for get_metric method."""

    @pytest.mark.asyncio
    async def test_get_metric_success(self):
        provider = GlassnodeProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_METRIC_RESPONSE

            result = await provider.get_metric("GN:BTC:active_addresses")

        assert len(result) == 3
        assert result[0]["v"] == 850000  # Data returned as-is from API

    @pytest.mark.asyncio
    async def test_get_metric_with_explicit_name(self):
        provider = GlassnodeProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_METRIC_RESPONSE

            result = await provider.get_metric("GN:BTC", metric="sopr")

        call_args = mock_req.call_args
        assert "indicators/sopr" in call_args[0][0]


class TestGlassnodeHealthCheck:
    """Tests for health_check method."""

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        provider = GlassnodeProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_PRICE_RESPONSE

            result = await provider.health_check()

        assert result is True
        assert provider.is_available is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        provider = GlassnodeProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.side_effect = GlassnodeError("Connection failed")

            result = await provider.health_check()

        assert result is False
        assert provider.is_available is False


class TestGlassnodeHealthScore:
    """Tests for health score tracking."""

    def test_initial_health_score(self):
        provider = GlassnodeProvider(api_key="test-key")
        assert provider.health_score == 1.0

    def test_health_score_after_errors(self):
        provider = GlassnodeProvider(api_key="test-key")
        provider.mark_error("test error")
        assert provider.health_score < 1.0

    def test_unavailable_after_many_errors(self):
        provider = GlassnodeProvider(api_key="test-key")
        for _ in range(10):
            provider.mark_error("error")
        assert not provider.is_available
