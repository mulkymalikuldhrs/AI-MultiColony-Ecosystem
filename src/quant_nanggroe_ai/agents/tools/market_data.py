"""Market data tool for agents — fetches OHLCV and latest prices."""

from __future__ import annotations

from typing import Any


async def fetch_market_data(symbol: str, timeframe: str = "1d", limit: int = 100) -> dict[str, Any]:
    """Fetch market data for a symbol."""
    # TODO: Integrate with data sources
    return {"symbol": symbol, "timeframe": timeframe, "data": []}


async def fetch_latest_price(symbol: str) -> float | None:
    """Fetch the latest price for a symbol."""
    # TODO: Integrate with data sources
    return None
