"""Data provider implementations.

Provider priority order (lower = higher priority):
1. Binance (priority=1) — Free crypto data (highest priority for crypto)
2. Bybit (priority=2) — Free crypto exchange data (perpetual futures, spot, options)
3. CoinGecko (priority=15) — Comprehensive crypto data with 10K+ coins
4. Alpaca (priority=10) — Free US equity real-time data
5. OANDA (priority=12) — Free forex/CFD data (practice account)
6. Polygon (priority=20) — Production historical data with 99.9% SLA
7. Finnhub (priority=22) — Stock, forex, crypto data (60 calls/min free)
8. Alpha Vantage (priority=25) — Stock, forex, crypto data
9. Glassnode (priority=28) — On-chain crypto analytics (free tier)
10. FRED (priority=30) — Federal Reserve macro-economic data
11. ECB (priority=35) — European Central Bank reference exchange rates
12. NewsAPI (priority=40) — Financial news aggregation for sentiment analysis
13. Yahoo Finance (priority=50) — Development/testing only
14. SEC EDGAR — Filing and fundamental data
15. TwelveData — Multi-asset market data
"""

from quant_nanggroe.data.providers.alpha_vantage import AlphaVantageProvider
from quant_nanggroe.data.providers.alpaca import AlpacaProvider
from quant_nanggroe.data.providers.binance import BinanceProvider
from quant_nanggroe.data.providers.bybit_provider import BybitProvider
from quant_nanggroe.data.providers.coingecko import CoinGeckoProvider
from quant_nanggroe.data.providers.ecb_provider import ECBProvider
from quant_nanggroe.data.providers.finnhub_provider import FinnhubProvider
from quant_nanggroe.data.providers.fred import FREDProvider
from quant_nanggroe.data.providers.glassnode_provider import GlassnodeProvider
from quant_nanggroe.data.providers.newsapi_provider import NewsAPIProvider
from quant_nanggroe.data.providers.oanda_provider import OANDAProvider
from quant_nanggroe.data.providers.polygon import PolygonProvider
from quant_nanggroe.data.providers.sec_edgar import SECEdgarProvider
from quant_nanggroe.data.providers.twelvedata import TwelveDataProvider
from quant_nanggroe.data.providers.yahoo import YahooFinanceProvider

__all__ = [
    "AlphaVantageProvider",
    "AlpacaProvider",
    "BinanceProvider",
    "BybitProvider",
    "CoinGeckoProvider",
    "ECBProvider",
    "FinnhubProvider",
    "FREDProvider",
    "GlassnodeProvider",
    "NewsAPIProvider",
    "OANDAProvider",
    "PolygonProvider",
    "SECEdgarProvider",
    "TwelveDataProvider",
    "YahooFinanceProvider",
]
