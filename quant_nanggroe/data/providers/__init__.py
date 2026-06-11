"""Data provider implementations.

All providers use REAL API sources with no mock/dummy data.

Provider priority order (lower = higher priority):
 1. Binance (priority=1)    — Free crypto data via ccxt + direct REST API
 5. CoinGecko (priority=5)  — Free crypto prices, market cap, trending
10. Yahoo Finance (priority=10) — Free stocks/ETFs/forex/crypto via yfinance
15. Twelve Data (priority=15) — Global equity/forex/crypto (free tier 800/day)
16. Finnhub (priority=16)   — Stock quotes, news, earnings, sentiment (free tier)
18. Alpha Vantage (priority=18) — Stocks/forex/crypto + technical indicators
20. Polygon (priority=20)   — Production historical data with 99.9% SLA
30. FRED (priority=30)      — Federal Reserve economic data
32. ECB (priority=32)       — European Central Bank exchange/interest rates
33. World Bank (priority=33) — Global development indicators
35. SEC EDGAR (priority=35) — US public company filings and financials
"""

try:
    from quant_nanggroe.data.providers.binance import BinanceProvider
except ImportError:
    BinanceProvider = None
from quant_nanggroe.data.providers.coingecko import CoinGeckoProvider
from quant_nanggroe.data.providers.yahoo import YahooFinanceProvider
from quant_nanggroe.data.providers.twelvedata import TwelveDataProvider
try:
    from quant_nanggroe.data.providers.finnhub import FinnhubProvider
except ImportError:
    FinnhubProvider = None
from quant_nanggroe.data.providers.alpha_vantage import AlphaVantageProvider
from quant_nanggroe.data.providers.alpaca import AlpacaProvider
from quant_nanggroe.data.providers.polygon import PolygonProvider
from quant_nanggroe.data.providers.fred import FREDProvider
try:
    from quant_nanggroe.data.providers.ecb import ECBProvider
except ImportError:
    ECBProvider = None
try:
    from quant_nanggroe.data.providers.world_bank import WorldBankProvider
except ImportError:
    WorldBankProvider = None
from quant_nanggroe.data.providers.sec_edgar import SECEdgarProvider

# Provider registry: maps name -> provider class
PROVIDER_REGISTRY: dict[str, type] = {
    "binance": BinanceProvider,
    "coingecko": CoinGeckoProvider,
    "yahoo": YahooFinanceProvider,
    "twelvedata": TwelveDataProvider,
    "finnhub": FinnhubProvider,
    "alpha_vantage": AlphaVantageProvider,
    "alpaca": AlpacaProvider,
    "polygon": PolygonProvider,
    "fred": FREDProvider,
    "ecb": ECBProvider,
    "world_bank": WorldBankProvider,
    "sec_edgar": SECEdgarProvider,
}

__all__ = [
    "BinanceProvider",
    "CoinGeckoProvider",
    "YahooFinanceProvider",
    "TwelveDataProvider",
    "FinnhubProvider",
    "AlphaVantageProvider",
    "AlpacaProvider",
    "PolygonProvider",
    "FREDProvider",
    "ECBProvider",
    "WorldBankProvider",
    "SECEdgarProvider",
    "PROVIDER_REGISTRY",
]
