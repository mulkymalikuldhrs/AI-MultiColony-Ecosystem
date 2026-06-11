"""Data provider implementations.

Provider priority order (lower = higher priority):
1. Binance (priority=1) — Free crypto data (highest priority for crypto)
2. CoinGecko (priority=15) — Comprehensive crypto data with 10K+ coins
3. Alpaca (priority=10) — Free US equity real-time data
4. Alpha Vantage (priority=25) — Stock, forex, crypto data
5. Polygon (priority=20) — Production historical data with 99.9% SLA
6. FRED (priority=30) — Federal Reserve macro-economic data
7. Yahoo Finance (priority=50) — Development/testing only
8. SEC EDGAR — Filing and fundamental data
9. TwelveData — Multi-asset market data
"""

from quant_nanggroe.data.providers.alpha_vantage import AlphaVantageProvider
from quant_nanggroe.data.providers.alpaca import AlpacaProvider
from quant_nanggroe.data.providers.binance import BinanceProvider
from quant_nanggroe.data.providers.coingecko import CoinGeckoProvider
from quant_nanggroe.data.providers.fred import FREDProvider
from quant_nanggroe.data.providers.polygon import PolygonProvider
from quant_nanggroe.data.providers.sec_edgar import SECEdgarProvider
from quant_nanggroe.data.providers.twelvedata import TwelveDataProvider
from quant_nanggroe.data.providers.yahoo import YahooFinanceProvider

__all__ = [
    "AlphaVantageProvider",
    "AlpacaProvider",
    "BinanceProvider",
    "CoinGeckoProvider",
    "FREDProvider",
    "PolygonProvider",
    "SECEdgarProvider",
    "TwelveDataProvider",
    "YahooFinanceProvider",
]
