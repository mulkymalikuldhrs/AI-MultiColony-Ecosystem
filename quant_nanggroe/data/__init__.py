"""Data access layer for Quant Nanggroe AI.

Provides unified access to market data across multiple providers
with automatic failover, caching, and data normalization.
"""

from quant_nanggroe.data.providers.base import DataProvider
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
    PROVIDER_REGISTRY,
)
from quant_nanggroe.data.fallback import (
    CIRCUIT_FAILURE_THRESHOLD,
    CIRCUIT_RESET_SECONDS,
    FallbackChain,
    FallbackEvent,
    ProviderHealth,
)

__all__ = [
    "DataProvider",
    "AlphaVantageProvider",
    "AlpacaProvider",
    "BinanceProvider",
    "CoinGeckoProvider",
    "FREDProvider",
    "PolygonProvider",
    "SECEdgarProvider",
    "TwelveDataProvider",
    "YahooFinanceProvider",
    "PROVIDER_REGISTRY",
    "CIRCUIT_FAILURE_THRESHOLD",
    "CIRCUIT_RESET_SECONDS",
    "FallbackChain",
    "FallbackEvent",
    "ProviderHealth",
]
