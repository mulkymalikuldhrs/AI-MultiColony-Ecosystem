"""FRED (Federal Reserve Economic Data) provider.

Implements the DataProvider interface for the Federal Reserve Bank of St. Louis
FRED API. Provides macro-economic time series data including GDP, CPI,
unemployment rates, interest rates, and hundreds of other economic indicators.

Symbol convention: ``FRED:<series_id>`` (e.g., ``FRED:GDP``, ``FRED:CPIAUCSL``,
``FRED:UNRATE``, ``FRED:FEDFUNDS``).

FRED API is free but requires an API key:
https://fred.stlouisfed.org/docs/api/api_key.html

Rate limits: 120 requests per minute (free tier).
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

from quant_nanggroe.data.providers.base import DataProvider
from quant_nanggroe.types.market import OHLCV, OrderBook, Ticker, TimeFrame

logger = logging.getLogger(__name__)

# Well-known FRED series mapping
FRED_SERIES_MAP: Dict[str, str] = {
    "FRED:GDP": "Gross Domestic Product",
    "FRED:GDPC1": "Real Gross Domestic Product",
    "FRED:CPIAUCSL": "Consumer Price Index for All Urban Consumers: All Items",
    "FRED:CPILFESL": "Core CPI (Less Food & Energy)",
    "FRED:UNRATE": "Unemployment Rate",
    "FRED:FEDFUNDS": "Federal Funds Effective Rate",
    "FRED:DFF": "Daily Federal Funds Effective Rate",
    "FRED:T10Y2Y": "10-Year Treasury Minus 2-Year Treasury",
    "FRED:DGS10": "10-Year Treasury Rate",
    "FRED:DGS2": "2-Year Treasury Rate",
    "FRED:M2SL": "M2 Money Stock",
    "FRED:PAYEMS": "Total Nonfarm Payrolls",
    "FRED:UMCSENT": "Consumer Sentiment (U of Michigan)",
    "FRED:VIXCLS": "CBOE Volatility Index (VIX)",
    "FRED:BAMLH0A0HYM2": "High Yield Bond Spread",
    "FRED:SP500": "S&P 500 Index",
    "FRED:DEXUSEU": "USD/EUR Exchange Rate",
    "FRED:DEXJPUS": "JPY/USD Exchange Rate",
    "FRED:HOUST": "Housing Starts: Total",
    "FRED:RSAFS": "Retail Sales",
}

# Reverse map: series_id -> FRED:<series_id>
_SERIES_ID_TO_SYMBOL: Dict[str, str] = {
    k.split(":")[1]: k for k in FRED_SERIES_MAP
}


def _parse_symbol(symbol: str) -> str:
    """Extract FRED series ID from symbol convention.

    Args:
        symbol: Symbol in FRED:<series_id> format or raw series ID.

    Returns:
        The FRED series ID.
    """
    if symbol.startswith("FRED:"):
        return symbol[5:]
    return symbol


class FREDError(Exception):
    """FRED API error."""


class FREDProvider(DataProvider):
    """FRED (Federal Reserve Economic Data) provider.

    Provides macro-economic time series data from the Federal Reserve Bank
    of St. Louis. Requires QNAI_FRED_API_KEY environment variable.

    Features:
    - 800,000+ US and international economic time series
    - Daily, weekly, monthly, quarterly, annual frequencies
    - Free API with 120 req/min rate limit
    - Symbol convention: FRED:<series_id> (e.g. FRED:GDP)

    Example:
        >>> provider = FREDProvider(api_key="your-key")
        >>> candles = await provider.get_ohlcv("FRED:GDP", TimeFrame.MO1)
        >>> ticker = await provider.get_ticker("FRED:UNRATE")
    """

    BASE_URL = "https://api.stlouisfed.org/fred"

    def __init__(
        self,
        api_key: Optional[str] = None,
        priority: int = 30,
        **kwargs,
    ):
        """Initialize FRED provider.

        Args:
            api_key: FRED API key. Falls back to QNAI_FRED_API_KEY env var.
            priority: Failover priority (lower = higher priority). Default 30
                      (macro data, lower priority than real-time market data).
        """
        super().__init__(name="fred", priority=priority, **kwargs)
        self._api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None

    def _get_api_key(self) -> str:
        """Get FRED API key from config or environment."""
        key = self._api_key
        if not key:
            key = os.environ.get("QNAI_FRED_API_KEY", "")
        if not key:
            raise FREDError(
                "FRED API key not configured. Set QNAI_FRED_API_KEY environment "
                "variable or pass api_key parameter."
            )
        return key

    def _get_client(self) -> httpx.AsyncClient:
        """Lazy-initialize the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def _request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the FRED API.

        Args:
            endpoint: API endpoint (e.g., 'series/observations').
            params: Query parameters (api_key will be added automatically).

        Returns:
            Parsed JSON response.

        Raises:
            FREDError: On API errors.
        """
        params["api_key"] = self._get_api_key()
        params["file_type"] = "json"

        client = self._get_client()
        url = f"{self.BASE_URL}/{endpoint}"

        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            self.mark_error(f"FRED API error: {e.response.status_code}")
            raise FREDError(f"FRED API returned {e.response.status_code}") from e
        except httpx.RequestError as e:
            self.mark_error(f"FRED request error: {e}")
            raise FREDError(f"FRED request failed: {e}") from e

    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: TimeFrame = TimeFrame.D1,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 500,
    ) -> List[OHLCV]:
        """Fetch FRED time series as OHLCV candles.

        FRED series are typically single-valued (close = open = high = low),
        with volume set to 0. The timestamp is mapped from the observation date.

        Args:
            symbol: FRED series symbol (e.g., 'FRED:GDP', 'FRED:UNRATE').
            timeframe: Candle timeframe (FRED data has its own frequency; this
                       parameter is used for filtering).
            start: Start datetime.
            end: End datetime.
            limit: Maximum number of observations.

        Returns:
            List of OHLCV candles with single-valued prices.
        """
        try:
            series_id = _parse_symbol(symbol)

            params: Dict[str, Any] = {
                "series_id": series_id,
                "sort_order": "asc",
                "limit": limit,
            }

            if start:
                params["observation_start"] = start.strftime("%Y-%m-%d")
            if end:
                params["observation_end"] = end.strftime("%Y-%m-%d")

            data = await self._request("series/observations", params)

            observations = data.get("observations", [])
            if not observations:
                self.mark_error(f"No observations returned for {symbol}")
                return []

            result = []
            for obs in observations:
                value_str = obs.get("value", ".")
                if value_str == "." or value_str == "":
                    continue  # Skip missing values

                try:
                    value = float(value_str)
                except (ValueError, TypeError):
                    continue

                date_str = obs.get("date", "")
                try:
                    ts = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    continue

                # FRED data is single-valued: O=H=L=C=value, volume=0
                candle = OHLCV(
                    symbol=symbol,
                    timestamp=ts,
                    open=value,
                    high=value,
                    low=value,
                    close=value,
                    volume=0.0,
                )
                result.append(candle)

            self.mark_success()
            return result[-limit:]

        except FREDError:
            return []
        except Exception as e:
            self.mark_error(str(e))
            logger.warning(f"FRED OHLCV error for {symbol}: {e}")
            return []

    async def get_ticker(self, symbol: str) -> Optional[Ticker]:
        """Fetch the latest observation for a FRED series as a ticker.

        Args:
            symbol: FRED series symbol (e.g., 'FRED:GDP', 'FRED:UNRATE').

        Returns:
            Ticker with the latest value as last_price.
        """
        try:
            series_id = _parse_symbol(symbol)

            # Fetch the latest observation
            params: Dict[str, Any] = {
                "series_id": series_id,
                "sort_order": "desc",
                "limit": 1,
            }

            data = await self._request("series/observations", params)

            observations = data.get("observations", [])
            if not observations:
                self.mark_error(f"No observations for {symbol}")
                return None

            latest = observations[0]
            value_str = latest.get("value", ".")
            if value_str == "." or value_str == "":
                self.mark_error(f"Latest observation missing for {symbol}")
                return None

            try:
                value = float(value_str)
            except (ValueError, TypeError):
                self.mark_error(f"Invalid value for {symbol}: {value_str}")
                return None

            date_str = latest.get("date", "")
            try:
                ts = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                ts = datetime.now()

            ticker = Ticker(
                symbol=symbol,
                timestamp=ts,
                last_price=value,
                high_24h=None,
                low_24h=None,
                volume_24h=None,
                change_24h=None,
            )

            self.mark_success()
            return ticker

        except FREDError:
            return None
        except Exception as e:
            self.mark_error(str(e))
            logger.warning(f"FRED ticker error for {symbol}: {e}")
            return None

    async def get_orderbook(self, symbol: str, limit: int = 20) -> Optional[OrderBook]:
        """FRED does not support order book data.

        Returns:
            None — FRED provides macro-economic data, not market microstructure.
        """
        logger.debug("FRED does not support order book data")
        return None

    async def get_series_info(self, symbol: str) -> Dict[str, Any]:
        """Fetch metadata for a FRED series.

        Args:
            symbol: FRED series symbol (e.g., 'FRED:GDP').

        Returns:
            Dict with series metadata (title, frequency, units, etc.).
        """
        try:
            series_id = _parse_symbol(symbol)
            data = await self._request("series", {"series_id": series_id})
            self.mark_success()
            return data.get("seriess", [{}])[0]
        except Exception as e:
            self.mark_error(str(e))
            logger.warning(f"FRED series info error for {symbol}: {e}")
            return {}

    async def health_check(self) -> bool:
        """Check if the FRED API is accessible.

        Returns:
            True if the API responds successfully.
        """
        try:
            # Try fetching info for a well-known series
            params: Dict[str, Any] = {
                "series_id": "GDP",
                "limit": 1,
            }
            await self._request("series/observations", params)
            self._is_available = True
            return True
        except Exception as e:
            self._is_available = False
            self._last_error = str(e)
            return False

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
