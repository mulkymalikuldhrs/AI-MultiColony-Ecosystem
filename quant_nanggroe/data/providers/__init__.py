"""Data provider implementations.

Provider priority order (lower = higher priority):
1. Alpaca (priority=10) — Free US equity real-time data
2. Polygon (priority=20) — Production historical data with 99.9% SLA
3. Binance (priority=0) — Free crypto data (highest priority for crypto)
4. Yahoo Finance (priority=50) — Development/testing only
"""

from quant_nanggroe.data.providers.yahoo import YahooFinanceProvider
from quant_nanggroe.data.providers.binance import BinanceProvider
from quant_nanggroe.data.providers.alpaca import AlpacaProvider
from quant_nanggroe.data.providers.polygon import PolygonProvider

__all__ = [
    "YahooFinanceProvider",
    "BinanceProvider",
    "AlpacaProvider",
    "PolygonProvider",
]
