"""Data access layer for Quant Nanggroe AI.

Provides unified access to market data across multiple providers
with automatic failover, caching, and data normalization.

Includes:
- Data providers (Yahoo, Alpaca, Binance, etc.)
- Fallback chains with circuit breakers (from AI-Trader)
"""

from quant_nanggroe.data.providers.base import DataProvider
from quant_nanggroe.data.manager import DataProviderManager
from quant_nanggroe.data.providers import (
    AlphaVantageProvider,
    AlpacaProvider,
    BinanceProvider,
    CoinGeckoProvider,
    FREDProvider,
    PolygonProvider,
    SECEdgarProvider,
    TwelveDataProvider,
    YahooFinanceProvider,
)
from quant_nanggroe.data.fallback import FallbackChain, ProviderHealth as FallbackProviderHealth

__all__ = [
    "DataProvider",
    "DataProviderManager",
    "AlphaVantageProvider",
    "AlpacaProvider",
    "BinanceProvider",
    "CoinGeckoProvider",
    "FREDProvider",
    "PolygonProvider",
    "SECEdgarProvider",
    "TwelveDataProvider",
    "YahooFinanceProvider",
    "FallbackChain",
    "FallbackProviderHealth",
]
