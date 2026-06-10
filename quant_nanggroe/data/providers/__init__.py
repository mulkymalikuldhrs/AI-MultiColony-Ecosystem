"""Data provider implementations.

Provider priority order (lower = higher priority):
1. Binance (priority=0) — Free crypto data (highest priority for crypto)
2. Alpaca (priority=10) — Free US equity real-time data
3. TwelveData (priority=15) — Global equity, forex, crypto data
4. Polygon (priority=20) — Production historical data with 99.9% SLA
5. FRED (priority=30) — Macro-economic data (GDP, CPI, unemployment, etc.)
6. SEC EDGAR (priority=35) — US public company filings and financials
7. Yahoo Finance (priority=50) — Development/testing only
"""

from quant_nanggroe.data.providers.yahoo import YahooFinanceProvider
from quant_nanggroe.data.providers.binance import BinanceProvider
from quant_nanggroe.data.providers.alpaca import AlpacaProvider
from quant_nanggroe.data.providers.polygon import PolygonProvider
from quant_nanggroe.data.providers.fred import FREDProvider
from quant_nanggroe.data.providers.sec_edgar import SECEdgarProvider
from quant_nanggroe.data.providers.twelvedata import TwelveDataProvider

__all__ = [
    "YahooFinanceProvider",
    "BinanceProvider",
    "AlpacaProvider",
    "PolygonProvider",
    "FREDProvider",
    "SECEdgarProvider",
    "TwelveDataProvider",
]
