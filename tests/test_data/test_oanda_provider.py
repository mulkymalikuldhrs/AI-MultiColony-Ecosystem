"""Tests for OANDA data provider.

All tests mock HTTP responses to avoid real API calls.
No OANDA API token required to run these tests.
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from quant_nanggroe.data.providers.oanda_provider import (
    OANDAError,
    OANDAProvider,
    _parse_symbol,
)
from quant_nanggroe.types.market import TimeFrame


# ─── Sample OANDA API responses ────────────────────────────────────────

SAMPLE_CANDLES_RESPONSE = {
    "instrument": "EUR_USD",
    "granularity": "D",
    "candles": [
        {
            "complete": True,
            "volume": 12500,
            "time": "1672531200.000000000",
            "mid": {"o": "1.0650", "h": "1.0700", "l": "1.0600", "c": "1.0680"},
        },
        {
            "complete": True,
            "volume": 13200,
            "time": "1672444800.000000000",
            "mid": {"o": "1.0600", "h": "1.0660", "l": "1.0580", "c": "1.0650"},
        },
        {
            "complete": True,
            "volume": 11800,
            "time": "1672358400.000000000",
            "mid": {"o": "1.0580", "h": "1.0620", "l": "1.0550", "c": "1.0600"},
        },
    ],
}

SAMPLE_PRICING_CANDLES = {
    "instrument": "EUR_USD",
    "granularity": "M1",
    "candles": [
        {
            "complete": True,
            "volume": 500,
            "time": "1672531200.000000000",
            "bid": {"o": "1.0649", "h": "1.0699", "l": "1.0599", "c": "1.0679"},
            "ask": {"o": "1.0651", "h": "1.0701", "l": "1.0601", "c": "1.0681"},
        }
    ],
}


# ─── Unit tests ──────────────────────────────────────────────────────────


class TestParseSymbol:
    """Tests for the _parse_symbol helper function."""

    def test_parse_with_prefix(self):
        assert _parse_symbol("OANDA:EUR_USD") == "EUR_USD"

    def test_parse_without_prefix(self):
        assert _parse_symbol("EUR_USD") == "EUR_USD"

    def test_parse_cfd(self):
        assert _parse_symbol("OANDA:US30_USD") == "US30_USD"

    def test_parse_jpy_pair(self):
        assert _parse_symbol("OANDA:GBP_JPY") == "GBP_JPY"


class TestOANDAProviderInit:
    """Tests for OANDAProvider initialization."""

    def test_init_defaults(self):
        provider = OANDAProvider(api_token="test-token")
        assert provider.name == "oanda"
        assert provider.priority == 12
        assert provider._live is False

    def test_init_custom_priority(self):
        provider = OANDAProvider(api_token="test-token", priority=20)
        assert provider.priority == 20

    def test_init_live_mode(self):
        provider = OANDAProvider(api_token="test-token", live=True)
        assert provider._live is True

    def test_repr(self):
        provider = OANDAProvider(api_token="test-token")
        assert "oanda" in repr(provider)


class TestOANDAGetApiKey:
    """Tests for API key resolution."""

    def test_get_api_key_from_param(self):
        provider = OANDAProvider(api_token="my-token")
        assert provider._get_token() == "my-token"

    def test_get_api_key_from_env(self):
        with patch.dict("os.environ", {"QNAI_OANDA_API_TOKEN": "env-token"}):
            provider = OANDAProvider()
            assert provider._get_token() == "env-token"

    def test_get_api_key_missing_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            import os
            os.environ.pop("QNAI_OANDA_API_TOKEN", None)
            provider = OANDAProvider()
            with pytest.raises(OANDAError, match="OANDA API token not configured"):
                provider._get_token()


class TestOANDAGetOHLCV:
    """Tests for get_ohlcv method with mocked API."""

    @pytest.mark.asyncio
    async def test_get_ohlcv_success(self):
        provider = OANDAProvider(api_token="test-token")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_CANDLES_RESPONSE

            result = await provider.get_ohlcv("OANDA:EUR_USD", TimeFrame.D1)

        assert len(result) == 3
        assert result[0].symbol == "OANDA:EUR_USD"
        assert result[0].open == 1.058
        assert result[0].close == 1.06
        assert result[2].open == 1.065
        assert result[2].close == 1.068
        assert result[2].volume == 12500.0

    @pytest.mark.asyncio
    async def test_get_ohlcv_raw_symbol(self):
        provider = OANDAProvider(api_token="test-token")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_CANDLES_RESPONSE

            result = await provider.get_ohlcv("EUR_USD", TimeFrame.H1)

        call_args = mock_req.call_args
        assert "EUR_USD" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_get_ohlcv_empty_response(self):
        provider = OANDAProvider(api_token="test-token")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = {"candles": []}

            result = await provider.get_ohlcv("OANDA:EUR_USD", TimeFrame.D1)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_ohlcv_api_error(self):
        provider = OANDAProvider(api_token="test-token")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.side_effect = OANDAError("API error")

            result = await provider.get_ohlcv("OANDA:EUR_USD", TimeFrame.D1)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_ohlcv_with_date_range(self):
        provider = OANDAProvider(api_token="test-token")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_CANDLES_RESPONSE

            await provider.get_ohlcv(
                "OANDA:EUR_USD",
                start=datetime(2023, 1, 1),
                end=datetime(2023, 12, 31),
            )

        call_params = mock_req.call_args[0][1]
        assert "from" in call_params
        assert "to" in call_params


class TestOANDAGetTicker:
    """Tests for get_ticker method with mocked API."""

    @pytest.mark.asyncio
    async def test_get_ticker_success(self):
        provider = OANDAProvider(api_token="test-token")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_PRICING_CANDLES

            ticker = await provider.get_ticker("OANDA:EUR_USD")

        assert ticker is not None
        assert ticker.symbol == "OANDA:EUR_USD"
        assert ticker.last_price > 0
        assert ticker.bid is not None
        assert ticker.ask is not None

    @pytest.mark.asyncio
    async def test_get_ticker_empty_response(self):
        provider = OANDAProvider(api_token="test-token")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = {"candles": []}

            ticker = await provider.get_ticker("OANDA:EUR_USD")

        assert ticker is None

    @pytest.mark.asyncio
    async def test_get_ticker_api_error(self):
        provider = OANDAProvider(api_token="test-token")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.side_effect = OANDAError("API error")

            ticker = await provider.get_ticker("OANDA:EUR_USD")

        assert ticker is None


class TestOANDAGetOrderbook:
    """Tests for get_orderbook method."""

    @pytest.mark.asyncio
    async def test_get_orderbook_success(self):
        provider = OANDAProvider(api_token="test-token")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_PRICING_CANDLES

            ob = await provider.get_orderbook("OANDA:EUR_USD")

        assert ob is not None
        assert ob.symbol == "OANDA:EUR_USD"
        assert len(ob.bids) == 1
        assert len(ob.asks) == 1
        assert ob.spread is not None
        assert ob.mid_price is not None

    @pytest.mark.asyncio
    async def test_get_orderbook_api_error(self):
        provider = OANDAProvider(api_token="test-token")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.side_effect = OANDAError("API error")

            ob = await provider.get_orderbook("OANDA:EUR_USD")

        assert ob is None


class TestOANDAHealthCheck:
    """Tests for health_check method."""

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        provider = OANDAProvider(api_token="test-token")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_CANDLES_RESPONSE

            result = await provider.health_check()

        assert result is True
        assert provider.is_available is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        provider = OANDAProvider(api_token="test-token")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.side_effect = OANDAError("Connection failed")

            result = await provider.health_check()

        assert result is False
        assert provider.is_available is False


class TestOANDAHealthScore:
    """Tests for health score tracking."""

    def test_initial_health_score(self):
        provider = OANDAProvider(api_token="test-token")
        assert provider.health_score == 1.0

    def test_health_score_after_errors(self):
        provider = OANDAProvider(api_token="test-token")
        provider.mark_error("test error")
        assert provider.health_score < 1.0

    def test_unavailable_after_many_errors(self):
        provider = OANDAProvider(api_token="test-token")
        for _ in range(10):
            provider.mark_error("error")
        assert not provider.is_available
