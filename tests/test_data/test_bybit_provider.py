"""Tests for Bybit data provider.

All tests mock HTTP responses to avoid real API calls.
No Bybit API key required to run these tests.
"""

from __future__ import annotations

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from quant_nanggroe.data.providers.bybit_provider import (
    BybitError,
    BybitProvider,
    _parse_symbol,
)
from quant_nanggroe.types.market import TimeFrame


# ─── Sample Bybit API responses ────────────────────────────────────────

SAMPLE_KLINE_RESPONSE = {
    "retCode": 0,
    "retMsg": "OK",
    "result": {
        "symbol": "BTCUSDT",
        "category": "linear",
        "list": [
            ["1672531200000", "16500.00", "16600.00", "16400.00", "16550.00", "1250.5", "20625775.0"],
            ["1672444800000", "16400.00", "16550.00", "16300.00", "16500.00", "1180.3", "19378990.0"],
            ["1672358400000", "16300.00", "16450.00", "16200.00", "16400.00", "1320.1", "21612300.0"],
        ],
    },
}

SAMPLE_TICKERS_RESPONSE = {
    "retCode": 0,
    "retMsg": "OK",
    "result": {
        "category": "linear",
        "list": [
            {
                "symbol": "BTCUSDT",
                "lastPrice": "43000.00",
                "bid1Price": "42999.50",
                "ask1Price": "43000.50",
                "bid1Size": "1.5",
                "ask1Size": "2.0",
                "highPrice24h": "43500.00",
                "lowPrice24h": "42500.00",
                "volume24h": "25000.5",
                "price24hPcnt": "0.0235",
                "markPrice": "43001.00",
            }
        ],
    },
}

SAMPLE_ORDERBOOK_RESPONSE = {
    "retCode": 0,
    "retMsg": "OK",
    "result": {
        "s": "BTCUSDT",
        "b": [
            ["42999.00", "1.5"],
            ["42998.00", "2.0"],
            ["42997.00", "0.5"],
        ],
        "a": [
            ["43001.00", "1.0"],
            ["43002.00", "3.0"],
            ["43003.00", "1.5"],
        ],
    },
}

SAMPLE_TIME_RESPONSE = {
    "retCode": 0,
    "retMsg": "OK",
    "result": {
        "timeSecond": "1672531200",
        "timeNano": "1672531200000000000",
    },
}

SAMPLE_ERROR_RESPONSE = {
    "retCode": 10001,
    "retMsg": "Params error",
    "result": {},
}

SAMPLE_RATE_LIMIT_RESPONSE = {
    "retCode": 10016,
    "retMsg": "Rate limit exceeded",
    "result": {},
}


# ─── Unit tests ──────────────────────────────────────────────────────────


class TestParseSymbol:
    """Tests for the _parse_symbol helper function."""

    def test_parse_with_prefix(self):
        sym, cat = _parse_symbol("BYBIT:BTCUSDT")
        assert sym == "BTCUSDT"
        assert cat == "linear"

    def test_parse_without_prefix(self):
        sym, cat = _parse_symbol("BTCUSDT")
        assert sym == "BTCUSDT"
        assert cat == "linear"

    def test_parse_with_category(self):
        sym, cat = _parse_symbol("BYBIT:ETHUSDT:spot")
        assert sym == "ETHUSDT"
        assert cat == "spot"

    def test_parse_with_inverse_category(self):
        sym, cat = _parse_symbol("BYBIT:BTCUSD:inverse")
        assert sym == "BTCUSD"
        assert cat == "inverse"

    def test_parse_unknown_category_defaults_linear(self):
        sym, cat = _parse_symbol("BYBIT:BTCUSDT:unknown")
        assert sym == "BTCUSDT"
        assert cat == "linear"


class TestBybitProviderInit:
    """Tests for BybitProvider initialization."""

    def test_init_defaults(self):
        provider = BybitProvider()
        assert provider.name == "bybit"
        assert provider.priority == 2
        assert provider._default_category == "linear"

    def test_init_custom_priority(self):
        provider = BybitProvider(priority=5)
        assert provider.priority == 5

    def test_init_with_api_key(self):
        provider = BybitProvider(api_key="test-key", api_secret="test-secret")
        assert provider._api_key == "test-key"
        assert provider._api_secret == "test-secret"

    def test_init_with_category(self):
        provider = BybitProvider(category="spot")
        assert provider._default_category == "spot"

    def test_repr(self):
        provider = BybitProvider()
        assert "bybit" in repr(provider)


class TestBybitGetOHLCV:
    """Tests for get_ohlcv method with mocked API."""

    @pytest.mark.asyncio
    async def test_get_ohlcv_success(self):
        provider = BybitProvider()

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_KLINE_RESPONSE["result"]

            result = await provider.get_ohlcv("BYBIT:BTCUSDT", TimeFrame.D1)

        assert len(result) == 3
        assert result[0].symbol == "BYBIT:BTCUSDT"
        assert result[0].close == 16400.0
        assert result[2].close == 16550.0
        assert result[0].volume > 0
        assert provider._request_count > 0

    @pytest.mark.asyncio
    async def test_get_ohlcv_uses_raw_symbol(self):
        provider = BybitProvider()

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_KLINE_RESPONSE["result"]

            result = await provider.get_ohlcv("BTCUSDT", TimeFrame.H1)

        call_args = mock_req.call_args
        assert call_args[0][0] == "kline"
        params = call_args[0][1]
        assert params["symbol"] == "BTCUSDT"
        assert params["category"] == "linear"

    @pytest.mark.asyncio
    async def test_get_ohlcv_empty_response(self):
        provider = BybitProvider()

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = {"list": []}

            result = await provider.get_ohlcv("BYBIT:NONEXISTENT", TimeFrame.D1)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_ohlcv_api_error(self):
        provider = BybitProvider()

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.side_effect = BybitError("API error")

            result = await provider.get_ohlcv("BYBIT:BTCUSDT", TimeFrame.D1)

        assert result == []


class TestBybitGetTicker:
    """Tests for get_ticker method with mocked API."""

    @pytest.mark.asyncio
    async def test_get_ticker_success(self):
        provider = BybitProvider()

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_TICKERS_RESPONSE["result"]

            ticker = await provider.get_ticker("BYBIT:BTCUSDT")

        assert ticker is not None
        assert ticker.symbol == "BYBIT:BTCUSDT"
        assert ticker.last_price == 43000.0
        assert ticker.bid == 42999.5
        assert ticker.ask == 43000.5
        assert ticker.high_24h == 43500.0
        assert ticker.low_24h == 42500.0

    @pytest.mark.asyncio
    async def test_get_ticker_empty_response(self):
        provider = BybitProvider()

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = {"list": []}

            ticker = await provider.get_ticker("BYBIT:NONEXISTENT")

        assert ticker is None

    @pytest.mark.asyncio
    async def test_get_ticker_api_error(self):
        provider = BybitProvider()

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.side_effect = BybitError("API error")

            ticker = await provider.get_ticker("BYBIT:BTCUSDT")

        assert ticker is None


class TestBybitGetOrderbook:
    """Tests for get_orderbook method with mocked API."""

    @pytest.mark.asyncio
    async def test_get_orderbook_success(self):
        provider = BybitProvider()

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_ORDERBOOK_RESPONSE["result"]

            ob = await provider.get_orderbook("BYBIT:BTCUSDT")

        assert ob is not None
        assert ob.symbol == "BYBIT:BTCUSDT"
        assert len(ob.bids) == 3
        assert len(ob.asks) == 3
        assert ob.bids[0].price == 42999.0
        assert ob.asks[0].price == 43001.0
        assert ob.spread is not None
        assert ob.mid_price is not None

    @pytest.mark.asyncio
    async def test_get_orderbook_api_error(self):
        provider = BybitProvider()

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.side_effect = BybitError("API error")

            ob = await provider.get_orderbook("BYBIT:BTCUSDT")

        assert ob is None


class TestBybitHealthCheck:
    """Tests for health_check method."""

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        provider = BybitProvider()

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_TIME_RESPONSE["result"]

            result = await provider.health_check()

        assert result is True
        assert provider.is_available is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        provider = BybitProvider()

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.side_effect = BybitError("Connection failed")

            result = await provider.health_check()

        assert result is False
        assert provider.is_available is False


class TestBybitHealthScore:
    """Tests for health score tracking."""

    def test_initial_health_score(self):
        provider = BybitProvider()
        assert provider.health_score == 1.0

    def test_health_score_after_errors(self):
        provider = BybitProvider()
        provider.mark_error("test error")
        assert provider.health_score < 1.0

    def test_unavailable_after_many_errors(self):
        provider = BybitProvider()
        for _ in range(10):
            provider.mark_error("error")
        assert not provider.is_available


class TestBybitExtraMethods:
    """Tests for Bybit-specific extra methods."""

    @pytest.mark.asyncio
    async def test_get_funding_rate(self):
        provider = BybitProvider()
        mock_data = {"list": [{"fundingRate": "0.0001", "symbol": "BTCUSDT"}]}

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = mock_data

            result = await provider.get_funding_rate("BYBIT:BTCUSDT")

        assert result is not None

    @pytest.mark.asyncio
    async def test_get_open_interest(self):
        provider = BybitProvider()
        mock_data = {"openInterest": "15000.5", "symbol": "BTCUSDT"}

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = mock_data

            result = await provider.get_open_interest("BYBIT:BTCUSDT")

        assert result is not None
