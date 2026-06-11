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

import asyncio
import logging
import os
import time
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
    "FRED:DGS30": "30-Year Treasury Rate",
    "FRED:M2SL": "M2 Money Stock",
    "FRED:M2V": "M2 Velocity of Money",
    "FRED:PAYEMS": "Total Nonfarm Payrolls",
    "FRED:UMCSENT": "Consumer Sentiment (U of Michigan)",
    "FRED:VIXCLS": "CBOE Volatility Index (VIX)",
    "FRED:BAMLH0A0HYM2": "High Yield Bond Spread",
    "FRED:SP500": "S&P 500 Index",
    "FRED:DEXUSEU": "USD/EUR Exchange Rate",
    "FRED:DEXJPUS": "JPY/USD Exchange Rate",
    "FRED:DEXCHUS": "CNY/USD Exchange Rate",
    "FRED:HOUST": "Housing Starts: Total",
    "FRED:RSAFS": "Retail Sales",
    "FRED:CIVPART": "Labor Force Participation Rate",
    "FRED:PSAVERT": "Personal Saving Rate",
    "FRED:GFDEBTN": "Federal Debt: Total Public Debt",
    "FRED:FYFDP": "Federal Deficit as Percent of GDP",
    "FRED:INDPRO": "Industrial Production Index",
    "FRED:TCU": "Capacity Utilization",
    "FRED:PPIACO": "Producer Price Index",
    "FRED:T10YIE": "10-Year Breakeven Inflation Rate",
    "FRED:DEXUSUK": "USD/GBP Exchange Rate",
    "FRED:WTISPLC": "Crude Oil WTI Price",
    "FRED:GOLDAMGBD228NLBM": "Gold Fixing Price",
}

# Reverse map: series_id -> FRED:<series_id>
_SERIES_ID_TO_SYMBOL: Dict[str, str] = {
    k.split(":")[1]: k for k in FRED_SERIES_MAP
}


def _parse_symbol(symbol: str) -> str:
    """Extract FRED series ID from symbol convention."""
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
    - Real economic indicators, Treasury yields, money supply, sentiment

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
        super().__init__(name="fred", priority=priority, **kwargs)
        self._api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None
        self._last_request_time: float = 0.0
        self._rate_limit_interval: float = 0.5  # 500ms = 120 req/min

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
        """Make a rate-limited request to the FRED API.

        Enforces 120 req/min rate limit.
        """
        # Rate limiting
        elapsed = time.monotonic() - self._last_request_time
        if elapsed < self._rate_limit_interval:
            await asyncio.sleep(self._rate_limit_interval - elapsed)

        params["api_key"] = self._get_api_key()
        params["file_type"] = "json"

        client = self._get_client()
        url = f"{self.BASE_URL}/{endpoint}"
        self._last_request_time = time.monotonic()

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
        with volume set to 0.
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
                    continue

                try:
                    value = float(value_str)
                except (ValueError, TypeError):
                    continue

                date_str = obs.get("date", "")
                try:
                    ts = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    continue

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
        """Fetch the latest observation for a FRED series as a ticker."""
        try:
            series_id = _parse_symbol(symbol)

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
        """FRED does not support order book data."""
        logger.debug("FRED does not support order book data")
        return None

    async def get_series_info(self, symbol: str) -> Dict[str, Any]:
        """Fetch metadata for a FRED series.

        Returns title, frequency, units, seasonality, etc.
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

    async def get_economic_indicators(
        self,
        category: str = "all",
    ) -> Dict[str, Any]:
        """Fetch key economic indicators grouped by category.

        Args:
            category: One of 'all', 'gdp', 'inflation', 'employment',
                      'interest_rates', 'money_supply', 'sentiment'.

        Returns:
            Dict mapping indicator name to latest value.
        """
        category_series = {
            "gdp": ["GDP", "GDPC1"],
            "inflation": ["CPIAUCSL", "CPILFESL", "PPIACO", "T10YIE"],
            "employment": ["UNRATE", "PAYEMS", "CIVPART"],
            "interest_rates": ["FEDFUNDS", "DFF", "DGS10", "DGS2", "DGS30", "T10Y2Y"],
            "money_supply": ["M2SL", "M2V"],
            "sentiment": ["UMCSENT", "PSAVERT"],
            "markets": ["SP500", "VIXCLS", "BAMLH0A0HYM2"],
            "commodities": ["WTISPLC", "GOLDAMGBD228NLBM"],
        }

        if category != "all":
            series_ids = category_series.get(category, [])
        else:
            all_ids = []
            for ids in category_series.values():
                all_ids.extend(ids)
            series_ids = all_ids

        result = {}
        for series_id in series_ids:
            try:
                ticker = await self.get_ticker(f"FRED:{series_id}")
                if ticker:
                    result[series_id] = {
                        "value": ticker.last_price,
                        "date": ticker.timestamp.isoformat(),
                        "description": FRED_SERIES_MAP.get(f"FRED:{series_id}", series_id),
                    }
            except Exception:
                continue

        return result

    async def get_treasury_yields(self) -> Dict[str, Any]:
        """Fetch current Treasury yield curve data.

        Returns yields for 2Y, 5Y, 7Y, 10Y, 20Y, 30Y maturities
        plus the 10Y-2Y spread (yield curve inversion indicator).
        """
        yield_series = {
            "DGS1": "1-Year",
            "DGS2": "2-Year",
            "DGS5": "5-Year",
            "DGS7": "7-Year",
            "DGS10": "10-Year",
            "DGS20": "20-Year",
            "DGS30": "30-Year",
            "T10Y2Y": "10Y-2Y Spread",
        }

        result = {}
        for series_id, label in yield_series.items():
            try:
                ticker = await self.get_ticker(f"FRED:{series_id}")
                if ticker:
                    result[label] = {
                        "value": ticker.last_price,
                        "date": ticker.timestamp.isoformat(),
                    }
            except Exception:
                continue

        return result

    async def health_check(self) -> bool:
        """Check if the FRED API is accessible."""
        try:
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
