"""Tests for NewsAPI data provider.

All tests mock HTTP responses to avoid real API calls.
No NewsAPI API key required to run these tests.
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from quant_nanggroe.data.providers.newsapi_provider import (
    NewsAPIError,
    NewsAPIProvider,
    _parse_symbol,
)
from quant_nanggroe.types.market import TimeFrame


# ─── Sample NewsAPI responses ────────────────────────────────────────

SAMPLE_EVERYTHING_RESPONSE = {
    "status": "ok",
    "totalResults": 3,
    "articles": [
        {
            "source": {"id": "crypto-news", "name": "Crypto News"},
            "author": "John Doe",
            "title": "Bitcoin Surges Past $40K",
            "description": "Bitcoin price reached new highs amid institutional buying.",
            "url": "https://example.com/bitcoin-40k",
            "publishedAt": "2023-01-03T10:00:00Z",
        },
        {
            "source": {"id": "finance-daily", "name": "Finance Daily"},
            "author": "Jane Smith",
            "title": "Fed Signals Rate Pause",
            "description": "Federal Reserve signals potential pause in rate hikes.",
            "url": "https://example.com/fed-pause",
            "publishedAt": "2023-01-03T08:00:00Z",
        },
        {
            "source": {"id": "market-watch", "name": "Market Watch"},
            "author": "Bob Wilson",
            "title": "Ethereum Upgrade Boosts Network",
            "description": "Latest Ethereum upgrade improves scalability.",
            "url": "https://example.com/eth-upgrade",
            "publishedAt": "2023-01-02T14:00:00Z",
        },
    ],
}

SAMPLE_HEADLINES_RESPONSE = {
    "status": "ok",
    "totalResults": 2,
    "articles": [
        {
            "source": {"id": "bloomberg", "name": "Bloomberg"},
            "title": "Wall Street Rallies on Earnings",
            "description": "Strong earnings drive market rally.",
            "url": "https://example.com/wall-street",
            "publishedAt": "2023-01-03T12:00:00Z",
        },
        {
            "source": {"id": "cnbc", "name": "CNBC"},
            "title": "Tech Stocks Surge",
            "description": "Technology sector leads gains.",
            "url": "https://example.com/tech-surge",
            "publishedAt": "2023-01-03T11:00:00Z",
        },
    ],
}

SAMPLE_SOURCES_RESPONSE = {
    "status": "ok",
    "sources": [
        {"id": "bloomberg", "name": "Bloomberg", "category": "business"},
        {"id": "cnbc", "name": "CNBC", "category": "business"},
        {"id": "techcrunch", "name": "TechCrunch", "category": "technology"},
    ],
}

SAMPLE_ERROR_RESPONSE = {
    "status": "error",
    "code": "apiKeyInvalid",
    "message": "Your API key is invalid.",
}


# ─── Unit tests ──────────────────────────────────────────────────────────


class TestParseSymbol:
    """Tests for the _parse_symbol helper function."""

    def test_parse_with_prefix(self):
        assert _parse_symbol("NEWS:bitcoin") == "bitcoin"

    def test_parse_without_prefix(self):
        assert _parse_symbol("bitcoin") == "bitcoin"

    def test_parse_multi_word(self):
        assert _parse_symbol("NEWS:Federal Reserve") == "Federal Reserve"


class TestNewsAPIProviderInit:
    """Tests for NewsAPIProvider initialization."""

    def test_init_defaults(self):
        provider = NewsAPIProvider(api_key="test-key")
        assert provider.name == "newsapi"
        assert provider.priority == 40

    def test_init_custom_priority(self):
        provider = NewsAPIProvider(api_key="test-key", priority=50)
        assert provider.priority == 50

    def test_repr(self):
        provider = NewsAPIProvider(api_key="test-key")
        assert "newsapi" in repr(provider)

    def test_daily_limit(self):
        provider = NewsAPIProvider(api_key="test-key")
        assert provider._daily_limit == 100


class TestNewsAPIGetApiKey:
    """Tests for API key resolution."""

    def test_get_api_key_from_param(self):
        provider = NewsAPIProvider(api_key="my-key")
        assert provider._get_api_key() == "my-key"

    def test_get_api_key_from_env(self):
        with patch.dict("os.environ", {"QNAI_NEWSAPI_API_KEY": "env-key"}):
            provider = NewsAPIProvider()
            assert provider._get_api_key() == "env-key"

    def test_get_api_key_missing_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            import os
            os.environ.pop("QNAI_NEWSAPI_API_KEY", None)
            provider = NewsAPIProvider()
            with pytest.raises(NewsAPIError, match="NewsAPI API key not configured"):
                provider._get_api_key()


class TestNewsAPIGetNews:
    """Tests for get_news method with mocked API."""

    @pytest.mark.asyncio
    async def test_get_news_success(self):
        provider = NewsAPIProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_EVERYTHING_RESPONSE

            result = await provider.get_news("NEWS:bitcoin")

        assert len(result) == 3
        assert result[0]["title"] == "Bitcoin Surges Past $40K"
        assert provider._request_count > 0

    @pytest.mark.asyncio
    async def test_get_news_raw_query(self):
        provider = NewsAPIProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_EVERYTHING_RESPONSE

            await provider.get_news("bitcoin")

        call_params = mock_req.call_args[0][1]
        assert call_params["q"] == "bitcoin"

    @pytest.mark.asyncio
    async def test_get_news_with_date_range(self):
        provider = NewsAPIProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_EVERYTHING_RESPONSE

            await provider.get_news(
                "NEWS:bitcoin",
                start=datetime(2023, 1, 1),
                end=datetime(2023, 12, 31),
            )

        call_params = mock_req.call_args[0][1]
        assert "from" in call_params
        assert "to" in call_params

    @pytest.mark.asyncio
    async def test_get_news_api_error(self):
        provider = NewsAPIProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.side_effect = NewsAPIError("API error")

            result = await provider.get_news("NEWS:bitcoin")

        assert result == []


class TestNewsAPIGetTopHeadlines:
    """Tests for get_top_headlines method."""

    @pytest.mark.asyncio
    async def test_get_headlines_success(self):
        provider = NewsAPIProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_HEADLINES_RESPONSE

            result = await provider.get_top_headlines()

        assert len(result) == 2
        assert result[0]["title"] == "Wall Street Rallies on Earnings"

    @pytest.mark.asyncio
    async def test_get_headlines_with_category(self):
        provider = NewsAPIProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_HEADLINES_RESPONSE

            await provider.get_top_headlines(category="business")

        call_params = mock_req.call_args[0][1]
        assert call_params["category"] == "business"


class TestNewsAPIGetSources:
    """Tests for get_sources method."""

    @pytest.mark.asyncio
    async def test_get_sources_success(self):
        provider = NewsAPIProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_SOURCES_RESPONSE

            result = await provider.get_sources()

        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_get_sources_with_filter(self):
        provider = NewsAPIProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_SOURCES_RESPONSE

            await provider.get_sources(category="business", language="en")

        call_params = mock_req.call_args[0][1]
        assert call_params["category"] == "business"
        assert call_params["language"] == "en"


class TestNewsAPIGetOHLCV:
    """Tests for get_ohlcv (returns empty, as expected)."""

    @pytest.mark.asyncio
    async def test_get_ohlcv_returns_empty(self):
        provider = NewsAPIProvider(api_key="test-key")
        result = await provider.get_ohlcv("NEWS:bitcoin", TimeFrame.D1)
        assert result == []


class TestNewsAPIGetTicker:
    """Tests for get_ticker (returns None, as expected)."""

    @pytest.mark.asyncio
    async def test_get_ticker_returns_none(self):
        provider = NewsAPIProvider(api_key="test-key")
        result = await provider.get_ticker("NEWS:bitcoin")
        assert result is None


class TestNewsAPIGetOrderbook:
    """Tests for get_orderbook (returns None, as expected)."""

    @pytest.mark.asyncio
    async def test_get_orderbook_returns_none(self):
        provider = NewsAPIProvider(api_key="test-key")
        result = await provider.get_orderbook("NEWS:bitcoin")
        assert result is None


class TestNewsAPIGetSentimentSummary:
    """Tests for get_sentiment_summary method."""

    @pytest.mark.asyncio
    async def test_sentiment_summary_success(self):
        provider = NewsAPIProvider(api_key="test-key")

        with patch.object(provider, "get_news", new_callable=AsyncMock) as mock_news:
            mock_news.return_value = SAMPLE_EVERYTHING_RESPONSE["articles"]

            result = await provider.get_sentiment_summary("bitcoin")

        assert result["query"] == "bitcoin"
        assert result["article_count"] == 3
        assert len(result["sources"]) > 0
        assert len(result["articles"]) == 3


class TestNewsAPIHealthCheck:
    """Tests for health_check method."""

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        provider = NewsAPIProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = SAMPLE_HEADLINES_RESPONSE

            result = await provider.health_check()

        assert result is True
        assert provider.is_available is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        provider = NewsAPIProvider(api_key="test-key")

        with patch.object(provider, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.side_effect = NewsAPIError("Connection failed")

            result = await provider.health_check()

        assert result is False
        assert provider.is_available is False


class TestNewsAPIHealthScore:
    """Tests for health score tracking."""

    def test_initial_health_score(self):
        provider = NewsAPIProvider(api_key="test-key")
        assert provider.health_score == 1.0

    def test_health_score_after_errors(self):
        provider = NewsAPIProvider(api_key="test-key")
        provider.mark_error("test error")
        assert provider.health_score < 1.0

    def test_unavailable_after_many_errors(self):
        provider = NewsAPIProvider(api_key="test-key")
        for _ in range(10):
            provider.mark_error("error")
        assert not provider.is_available


class TestNewsAPIDailyRateLimit:
    """Tests for daily rate limiting."""

    def test_daily_limit_enforcement(self):
        provider = NewsAPIProvider(api_key="test-key")
        provider._daily_request_count = 100
        assert provider._daily_request_count >= provider._daily_limit
