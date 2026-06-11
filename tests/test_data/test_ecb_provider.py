"""Tests for ECB data provider.

All tests mock HTTP responses to avoid real API calls.
No ECB API key required (ECB is a free government API).
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from quant_nanggroe.data.providers.ecb_provider import (
    ECBError,
    ECBProvider,
    ECB_CURRENCIES,
    _parse_symbol,
)
from quant_nanggroe.types.market import TimeFrame


# ─── Sample ECB SDW XML response ────────────────────────────────────────

SAMPLE_ECB_XML = """<?xml version="1.0" encoding="UTF-8"?>
<message:GenericData xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message"
                     xmlns:generic="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic"
                     xmlns:common="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common">
  <message:DataSet>
    <generic:Series>
      <generic:Obs>
        <generic:ObsKey>
          <generic:Value id="TIME_PERIOD" value="2023-01-02"/>
          <generic:Value id="CURRENCY" value="USD"/>
        </generic:ObsKey>
        <generic:ObsValue value="1.0660"/>
      </generic:Obs>
      <generic:Obs>
        <generic:ObsKey>
          <generic:Value id="TIME_PERIOD" value="2023-01-03"/>
          <generic:Value id="CURRENCY" value="USD"/>
        </generic:ObsKey>
        <generic:ObsValue value="1.0680"/>
      </generic:Obs>
      <generic:Obs>
        <generic:ObsKey>
          <generic:Value id="TIME_PERIOD" value="2023-01-04"/>
          <generic:Value id="CURRENCY" value="USD"/>
        </generic:ObsKey>
        <generic:ObsValue value="1.0700"/>
      </generic:Obs>
    </generic:Series>
  </message:DataSet>
</message:GenericData>"""

SAMPLE_ECB_EMPTY_XML = """<?xml version="1.0" encoding="UTF-8"?>
<message:GenericData xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message"
                     xmlns:generic="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic"
                     xmlns:common="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common">
  <message:DataSet>
    <generic:Series>
    </generic:Series>
  </message:DataSet>
</message:GenericData>"""


# ─── Unit tests ──────────────────────────────────────────────────────────


class TestParseSymbol:
    """Tests for the _parse_symbol helper function."""

    def test_parse_with_prefix(self):
        assert _parse_symbol("ECB:USD") == "USD"

    def test_parse_without_prefix(self):
        assert _parse_symbol("USD") == "USD"

    def test_parse_lowercase(self):
        assert _parse_symbol("ecb:usd") == "USD"

    def test_parse_jpy(self):
        assert _parse_symbol("ECB:JPY") == "JPY"


class TestECBCurrencies:
    """Tests for the ECB_CURRENCIES constant."""

    def test_has_major_currencies(self):
        assert "USD" in ECB_CURRENCIES
        assert "JPY" in ECB_CURRENCIES
        assert "GBP" in ECB_CURRENCIES
        assert "CHF" in ECB_CURRENCIES

    def test_count(self):
        assert len(ECB_CURRENCIES) >= 30


class TestECBProviderInit:
    """Tests for ECBProvider initialization."""

    def test_init_defaults(self):
        provider = ECBProvider()
        assert provider.name == "ecb"
        assert provider.priority == 35

    def test_init_custom_priority(self):
        provider = ECBProvider(priority=50)
        assert provider.priority == 50

    def test_repr(self):
        provider = ECBProvider()
        assert "ecb" in repr(provider)


class TestECBParseXML:
    """Tests for XML parsing."""

    def test_parse_xml_success(self):
        provider = ECBProvider()
        result = provider._parse_ecb_xml(SAMPLE_ECB_XML)

        assert len(result) == 3
        assert result[0][0] == datetime(2023, 1, 2)
        assert result[0][1] == 1.066
        assert result[2][0] == datetime(2023, 1, 4)
        assert result[2][1] == 1.07

    def test_parse_xml_empty(self):
        provider = ECBProvider()
        result = provider._parse_ecb_xml(SAMPLE_ECB_EMPTY_XML)
        assert result == []

    def test_parse_xml_invalid(self):
        provider = ECBProvider()
        result = provider._parse_ecb_xml("not xml at all")
        assert result == []


class TestECBGetOHLCV:
    """Tests for get_ohlcv method with mocked API."""

    @pytest.mark.asyncio
    async def test_get_ohlcv_success(self):
        provider = ECBProvider()

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_ECB_XML

            result = await provider.get_ohlcv("ECB:USD", TimeFrame.D1)

        assert len(result) == 3
        assert result[0].symbol == "ECB:USD"
        assert result[0].open == 1.066
        assert result[0].close == 1.066
        assert result[0].volume == 0.0

    @pytest.mark.asyncio
    async def test_get_ohlcv_raw_symbol(self):
        provider = ECBProvider()

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_ECB_XML

            result = await provider.get_ohlcv("USD", TimeFrame.D1)

        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_get_ohlcv_empty_response(self):
        provider = ECBProvider()

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_ECB_EMPTY_XML

            result = await provider.get_ohlcv("ECB:USD", TimeFrame.D1)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_ohlcv_api_error(self):
        provider = ECBProvider()

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.side_effect = ECBError("API error")

            result = await provider.get_ohlcv("ECB:USD", TimeFrame.D1)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_ohlcv_with_date_range(self):
        provider = ECBProvider()

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_ECB_XML

            await provider.get_ohlcv(
                "ECB:USD",
                start=datetime(2023, 1, 1),
                end=datetime(2023, 12, 31),
            )

        call_params = mock_req.call_args[0][1]
        assert "startPeriod" in call_params
        assert "endPeriod" in call_params

    @pytest.mark.asyncio
    async def test_get_ohlcv_respects_limit(self):
        provider = ECBProvider()

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_ECB_XML

            result = await provider.get_ohlcv("ECB:USD", TimeFrame.D1, limit=2)

        assert len(result) <= 2


class TestECBGetTicker:
    """Tests for get_ticker method with mocked API."""

    @pytest.mark.asyncio
    async def test_get_ticker_success(self):
        provider = ECBProvider()

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_ECB_XML

            ticker = await provider.get_ticker("ECB:USD")

        assert ticker is not None
        assert ticker.symbol == "ECB:USD"
        assert ticker.last_price == 1.07

    @pytest.mark.asyncio
    async def test_get_ticker_empty_response(self):
        provider = ECBProvider()

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_ECB_EMPTY_XML

            ticker = await provider.get_ticker("ECB:USD")

        assert ticker is None

    @pytest.mark.asyncio
    async def test_get_ticker_api_error(self):
        provider = ECBProvider()

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.side_effect = ECBError("API error")

            ticker = await provider.get_ticker("ECB:USD")

        assert ticker is None


class TestECBGetOrderbook:
    """Tests for get_orderbook method."""

    @pytest.mark.asyncio
    async def test_get_orderbook_returns_none(self):
        provider = ECBProvider()
        result = await provider.get_orderbook("ECB:USD")
        assert result is None


class TestECBHealthCheck:
    """Tests for health_check method."""

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        provider = ECBProvider()

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_ECB_XML

            result = await provider.health_check()

        assert result is True
        assert provider.is_available is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        provider = ECBProvider()

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.side_effect = ECBError("Connection failed")

            result = await provider.health_check()

        assert result is False
        assert provider.is_available is False


class TestECBHealthScore:
    """Tests for health score tracking."""

    def test_initial_health_score(self):
        provider = ECBProvider()
        assert provider.health_score == 1.0

    def test_health_score_after_errors(self):
        provider = ECBProvider()
        provider.mark_error("test error")
        assert provider.health_score < 1.0

    def test_unavailable_after_many_errors(self):
        provider = ECBProvider()
        for _ in range(10):
            provider.mark_error("error")
        assert not provider.is_available
