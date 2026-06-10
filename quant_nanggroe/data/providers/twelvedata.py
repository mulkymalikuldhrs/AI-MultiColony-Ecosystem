"""TwelveData market data provider.

Implements the DataProvider interface for the TwelveData REST API.
Provides global equity, forex, and crypto market data with a generous
free tier (800 API credits/day).

TwelveData API key required: https://twelvedata.com/pricing

Features:
- Global equity data (US, EU, Asia markets)
- Forex pairs with real-time rates
- Crypto data from major exchanges
- Technical indicators built-in
- WebSocket real-time streaming
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

from quant_nanggroe.data.providers.base import DataProvider
from quant_nanggroe.types.market import OHLCV, OrderBook, OrderBookLevel, Ticker, TimeFrame

logger = logging.getLogger(__name__)

# Timeframe mapping from our TimeFrame to TwelveData interval strings
_TIMEFRAME_MAP: Dict[TimeFrame, str] = {
    TimeFrame.M1: "1min",
    TimeFrame.M5: "5min",
    TimeFrame.M15: "15min",
    TimeFrame.M30: "30min",
    TimeFrame.H1: "1h",
    TimeFrame.H4: "4h",
    TimeFrame.D1: "1day",
    TimeFrame.W1: "1week",
    TimeFrame.MO1: "1month",
}


class TwelveDataError(Exception):
    """TwelveData API error."""


class TwelveDataProvider(DataProvider):
    """TwelveData market data provider.

    Provides global equity, forex, and crypto market data via the
    TwelveData REST API. Requires QNAI_TWELVEDATA_API_KEY environment variable.

    Features:
    - Global equity data across 50+ exchanges
    - Forex pairs with real-time rates
    - Crypto data from major exchanges
    - Free tier: 800 API credits/day, 8 credits/minute
    - OHLCV, ticker, and forex rate endpoints

    Example:
        >>> provider = TwelveDataProvider(api_key="your-key")
        >>> candles = await provider.get_ohlcv("AAPL", TimeFrame.D1)
        >>> ticker = await provider.get_ticker("EUR/USD")
        >>> rate = await provider.get_forex_rate("EUR/USD")
    """

    BASE_URL = "https://api.twelvedata.com"

    def __init__(
        self,
        api_key: Optional[str] = None,
        priority: int = 15,
        **kwargs,
    ):
        """Initialize TwelveData provider.

        Args:
            api_key: TwelveData API key. Falls back to QNAI_TWELVEDATA_API_KEY env var.
            priority: Failover priority (lower = higher priority). Default 15
                      (between Alpaca=10 and Polygon=20 for equity data).
        """
        super().__init__(name="twelvedata", priority=priority, **kwargs)
        self._api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None

    def _get_api_key(self) -> str:
        """Get TwelveData API key from config or environment."""
        key = self._api_key
        if not key:
            key = os.environ.get("QNAI_TWELVEDATA_API_KEY", "")
        if not key:
            raise TwelveDataError(
                "TwelveData API key not configured. Set QNAI_TWELVEDATA_API_KEY "
                "environment variable or pass api_key parameter."
            )
        return key

    def _get_client(self) -> httpx.AsyncClient:
        """Lazy-initialize the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def _request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the TwelveData API.

        Args:
            endpoint: API endpoint (e.g., 'time_series').
            params: Query parameters (apikey will be added automatically).

        Returns:
            Parsed JSON response.

        Raises:
            TwelveDataError: On API errors.
        """
        params["apikey"] = self._get_api_key()

        client = self._get_client()
        url = f"{self.BASE_URL}/{endpoint}"

        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # TwelveData returns errors with a 'status' field
            if data.get("status") == "error":
                error_msg = data.get("message", "Unknown error")
                self.mark_error(f"TwelveData API error: {error_msg}")
                raise TwelveDataError(f"TwelveData API error: {error_msg}")

            return data

        except httpx.HTTPStatusError as e:
            self.mark_error(f"TwelveData HTTP error: {e.response.status_code}")
            raise TwelveDataError(
                f"TwelveData returned {e.response.status_code}"
            ) from e
        except httpx.RequestError as e:
            self.mark_error(f"TwelveData request error: {e}")
            raise TwelveDataError(f"TwelveData request failed: {e}") from e

    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: TimeFrame = TimeFrame.D1,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 500,
    ) -> List[OHLCV]:
        """Fetch OHLCV candlestick data from TwelveData.

        Args:
            symbol: Symbol (e.g., 'AAPL', 'EUR/USD', 'BTC/USD').
            timeframe: Candle timeframe.
            start: Start datetime.
            end: End datetime.
            limit: Maximum number of candles.

        Returns:
            List of OHLCV candles sorted by timestamp ascending.
        """
        try:
            interval = _TIMEFRAME_MAP.get(timeframe, "1day")

            params: Dict[str, Any] = {
                "symbol": symbol,
                "interval": interval,
                "outputsize": min(limit, 5000),
            }

            if start:
                params["start_date"] = start.strftime("%Y-%m-%d")
            if end:
                params["end_date"] = end.strftime("%Y-%m-%d")

            data = await self._request("time_series", params)

            values = data.get("values", [])
            if not values:
                self.mark_error(f"No OHLCV data returned for {symbol}")
                return []

            result = []
            for val in values:
                try:
                    # TwelveData returns string values
                    open_price = float(val.get("open", 0))
                    high_price = float(val.get("high", 0))
                    low_price = float(val.get("low", 0))
                    close_price = float(val.get("close", 0))
                    volume = float(val.get("volume", 0) or 0)

                    if open_price <= 0 or close_price <= 0:
                        continue

                    # Parse timestamp
                    datetime_str = val.get("datetime", "")
                    try:
                        # Try ISO format first
                        ts = datetime.fromisoformat(datetime_str)
                    except (ValueError, TypeError):
                        try:
                            ts = datetime.strptime(datetime_str, "%Y-%m-%d")
                        except (ValueError, TypeError):
                            continue

                    candle = OHLCV(
                        symbol=symbol,
                        timestamp=ts,
                        open=open_price,
                        high=high_price,
                        low=low_price,
                        close=close_price,
                        volume=volume,
                    )
                    result.append(candle)

                except (ValueError, TypeError, KeyError):
                    continue

            self.mark_success()
            # Data comes in reverse order from TwelveData, reverse to ascending
            result.reverse()
            return result[-limit:]

        except TwelveDataError:
            return []
        except Exception as e:
            self.mark_error(str(e))
            logger.warning(f"TwelveData OHLCV error for {symbol}: {e}")
            return []

    async def get_ticker(self, symbol: str) -> Optional[Ticker]:
        """Fetch current ticker/quote data from TwelveData.

        Args:
            symbol: Symbol (e.g., 'AAPL', 'EUR/USD', 'BTC/USD').

        Returns:
            Current ticker data or None if unavailable.
        """
        try:
            params: Dict[str, Any] = {
                "symbol": symbol,
            }

            data = await self._request("quote", params)

            if not data or "close" not in data:
                self.mark_error(f"No quote data for {symbol}")
                return None

            close_price = float(data.get("close", 0) or 0)
            if close_price <= 0:
                self.mark_error(f"Invalid close price for {symbol}")
                return None

            ticker = Ticker(
                symbol=symbol,
                timestamp=datetime.now(),
                last_price=close_price,
                bid=float(data.get("bid", 0) or 0) or None,
                ask=float(data.get("ask", 0) or 0) or None,
                high_24h=float(data.get("high", 0) or 0) or None,
                low_24h=float(data.get("low", 0) or 0) or None,
                volume_24h=float(data.get("volume", 0) or 0) or None,
                change_pct_24h=float(data.get("percent_change", 0) or 0) or None,
            )

            self.mark_success()
            return ticker

        except TwelveDataError:
            return None
        except Exception as e:
            self.mark_error(str(e))
            logger.warning(f"TwelveData ticker error for {symbol}: {e}")
            return None

    async def get_forex_rate(
        self,
        pair: str,
    ) -> Optional[Dict[str, Any]]:
        """Fetch real-time forex exchange rate.

        Args:
            pair: Forex pair (e.g., 'EUR/USD', 'GBP/JPY').

        Returns:
            Dict with rate info: {'pair', 'rate', 'timestamp'} or None.
        """
        try:
            params: Dict[str, Any] = {
                "symbol": pair,
                "interval": "1min",
                "outputsize": 1,
            }

            data = await self._request("time_series", params)

            values = data.get("values", [])
            if not values:
                self.mark_error(f"No forex rate data for {pair}")
                return None

            latest = values[0]
            close_price = float(latest.get("close", 0) or 0)
            if close_price <= 0:
                self.mark_error(f"Invalid forex rate for {pair}")
                return None

            datetime_str = latest.get("datetime", "")
            try:
                ts = datetime.fromisoformat(datetime_str)
            except (ValueError, TypeError):
                ts = datetime.now()

            self.mark_success()
            return {
                "pair": pair,
                "rate": close_price,
                "timestamp": ts.isoformat(),
            }

        except TwelveDataError:
            return None
        except Exception as e:
            self.mark_error(str(e))
            logger.warning(f"TwelveData forex rate error for {pair}: {e}")
            return None

    async def get_orderbook(self, symbol: str, limit: int = 20) -> Optional[OrderBook]:
        """TwelveData does not provide Level 2 order book data.

        Returns:
            None — Level 2 data not available through TwelveData.
        """
        logger.debug("TwelveData does not provide order book data")
        return None

    async def health_check(self) -> bool:
        """Check if the TwelveData API is accessible.

        Returns:
            True if the API responds successfully.
        """
        try:
            params: Dict[str, Any] = {
                "symbol": "AAPL",
                "interval": "1day",
                "outputsize": 1,
            }
            await self._request("time_series", params)
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
