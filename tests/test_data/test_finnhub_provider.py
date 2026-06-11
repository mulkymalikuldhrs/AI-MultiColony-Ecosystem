"""Tests for Finnhub data provider.

All tests mock HTTP responses to avoid real API calls.
No Finnhub API key required to run these tests.
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from quant_nanggroe.data.providers.finnhub_provider import (
    FinnhubError,
    FinnhubProvider,
    _parse_symbol,
)
from quant_nanggroe.types.market import TimeFrame


# ─── Sample Finnhub API responses ────────────────────────────────────────

SAMPLE_STOCK_CANDLE_RESPONSE = {
    "s": "ok",
    "c": [165.50, 167.00, 168.25],
    "h": [166.00, 168.50, 169.00],
    "l": [164.00, 166.00, 167.00],
    "o": [164.50, 166.50, 167.50],
    "t": [1672531200, 1672444800, 1672358400],
    "v": [12500000, 13200000, 11800000],
}

SAMPLE_STOCK_QUOTE_RESPONSE = {
    "c": 175.50,
    "h": 176.00,
    "l": 174.00,
    "o": 174.50,
    "pc": 174.00,
    "t": 1672531200,
}

SAMPLE_FOREX_RATES_RESPONSE = {
    "base": "EUR",
    "quote": {
        "USD": 1.0680,
        "GBP": 0.8850,
        "JPY": 140.50,
    },
}

SAMPLE_CRYPTO_QUOTE_RESPONSE = {
    "currentPrice": 43000.0,
    "high": 43500.0,
    "low": 42500.0,
}

SAMPLE_EMPTY_CANDLE_RESPONSE = {
    "s": "no_data",
}


# ─── Unit tests ──────────────────────────────────────────────────────────


class TestParseSymbol:
    """Tests for the _parse_symbol helper function."""

    def test_parse_stock_with_prefix(self):
        sym, stype = _parse_symbol("FINH:AAPL")
        assert sym == "AAPL"
        assert stype == "stock"

    def test_parse_stock_without_prefix(self):
        sym, stype = _parse_symbol("TSLA")
        assert sym == "TSLA"
        assert stype == "stock"

    def test_parse_forex(self):
        sym, stype = _parse_symbol("FINH:OANDA:EUR_USD")
        assert sym == "EUR/USD"
        assert stype == "forex"

    def test_parse_crypto(self):
        sym, stype = _parse_symbol("FINH:BINANCE:BTCUSDT")
        assert sym == "BINANCE:BTCUSDT"
        assert stype == "crypto"


class TestFinnhubProviderInit:
    """Tests for FinnhubProvider initialization."""

    def test_init_defaults(self):
        provider = FinnhubProvider(api_key="test-key")
        assert provider.name == "finnhub"
        assert provider.priority == 22

    def test_init_custom_priority(self):
        provider = FinnhubProvider(api_key="test-key", priority=30)
        assert provider.priority == 30

    def test_repr(self):
        provider = FinnhubProvider(api_key="test-key")
        assert "finnhub" in repr(provider)


class TestFinnhubGetApiKey:
    """Tests for API key resolution."""

    def test_get_api_key_from_param(self):
        provider = FinnhubProvider(api_key="my-key")
        assert provider._get_api_key() == "my-key"

    def test_get_api_key_from_env(self):
        with patch.dict("os.environ", {"QNAI_FINNHUB_API_KEY": "env-key"}):
            provider = FinnhubProvider()
            assert provider._get_api_key() == "env-key"

    def test_get_api_key_missing_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            import os
            os.environ.pop("QNAI_FINNHUB_API_KEY", None)
            provider = FinnhubProvider()
            with pytest.raises(FinnhubError, match="Finnhub API key not configured"):
                provider._get_api_key()


class TestFinnhubGetOHLCV:
    """Tests for get_ohlcv method with mocked API."""

    @pytest.mark.asyncio
    async def test_get_ohlcv_stock_success(self):
        provider = FinnhubProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_STOCK_CANDLE_RESPONSE

            result = await provider.get_ohlcv("FINH:AAPL", TimeFrame.D1)

        assert len(result) == 3
        assert result[0].symbol == "FINH:AAPL"
        # Sorted by timestamp ascending: Dec 30, Dec 31, Jan 1
        assert result[0].open == 167.5
        assert result[0].close == 168.25
        assert result[2].open == 164.5
        assert result[2].close == 165.5

    @pytest.mark.asyncio
    async def test_get_ohlcv_no_data(self):
        provider = FinnhubProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_EMPTY_CANDLE_RESPONSE

            result = await provider.get_ohlcv("FINH:NONEXISTENT", TimeFrame.D1)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_ohlcv_api_error(self):
        provider = FinnhubProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.side_effect = FinnhubError("API error")

            result = await provider.get_ohlcv("FINH:AAPL", TimeFrame.D1)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_ohlcv_forex_routes_correctly(self):
        provider = FinnhubProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_STOCK_CANDLE_RESPONSE

            await provider.get_ohlcv("FINH:OANDA:EUR_USD", TimeFrame.D1)

        call_args = mock_req.call_args
        assert call_args[0][0] == "forex/candle"

    @pytest.mark.asyncio
    async def test_get_ohlcv_crypto_routes_correctly(self):
        provider = FinnhubProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_STOCK_CANDLE_RESPONSE

            await provider.get_ohlcv("FINH:BINANCE:BTCUSDT", TimeFrame.D1)

        call_args = mock_req.call_args
        assert call_args[0][0] == "crypto/candle"


class TestFinnhubGetTicker:
    """Tests for get_ticker method with mocked API."""

    @pytest.mark.asyncio
    async def test_get_ticker_stock_success(self):
        provider = FinnhubProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_STOCK_QUOTE_RESPONSE

            ticker = await provider.get_ticker("FINH:AAPL")

        assert ticker is not None
        assert ticker.symbol == "FINH:AAPL"
        assert ticker.last_price == 175.5
        assert ticker.high_24h == 176.0
        assert ticker.low_24h == 174.0
        assert ticker.change_pct_24h is not None

    @pytest.mark.asyncio
    async def test_get_ticker_forex(self):
        provider = FinnhubProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_FOREX_RATES_RESPONSE

            ticker = await provider.get_ticker("FINH:OANDA:EUR_USD")

        assert ticker is not None
        assert ticker.last_price == 1.068

    @pytest.mark.asyncio
    async def test_get_ticker_zero_price(self):
        provider = FinnhubProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = {"c": 0, "h": 0, "l": 0, "o": 0, "pc": 0}

            ticker = await provider.get_ticker("FINH:AAPL")

        assert ticker is None

    @pytest.mark.asyncio
    async def test_get_ticker_api_error(self):
        provider = FinnhubProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.side_effect = FinnhubError("API error")

            ticker = await provider.get_ticker("FINH:AAPL")

        assert ticker is None


class TestFinnhubGetOrderbook:
    """Tests for get_orderbook method."""

    @pytest.mark.asyncio
    async def test_get_orderbook_returns_none(self):
        provider = FinnhubProvider(api_key="test-key")
        result = await provider.get_orderbook("FINH:AAPL")
        assert result is None


class TestFinnhubExtraMethods:
    """Tests for Finnhub-specific extra methods."""

    @pytest.mark.asyncio
    async def test_get_news_sentiment(self):
        provider = FinnhubProvider(api_key="test-key")
        mock_data = {"buzz": {"articlesInLastWeek": 50}, "sentiment": {"bearishPercent": 0.3}}

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = mock_data

            result = await provider.get_news_sentiment("FINH:AAPL")

        assert result is not None
        assert "buzz" in result

    @pytest.mark.asyncio
    async def test_get_earnings(self):
        provider = FinnhubProvider(api_key="test-key")
        mock_data = [{"actual": 1.52, "estimate": 1.50, "period": "2023-01-01"}]

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = mock_data

            result = await provider.get_earnings("FINH:AAPL")

        assert result is not None
        assert len(result) == 1


class TestFinnhubHealthCheck:
    """Tests for health_check method."""

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        provider = FinnhubProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_STOCK_QUOTE_RESPONSE

            result = await provider.health_check()

        assert result is True
        assert provider.is_available is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        provider = FinnhubProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.side_effect = FinnhubError("Connection failed")

            result = await provider.health_check()

        assert result is False
        assert provider.is_available is False
