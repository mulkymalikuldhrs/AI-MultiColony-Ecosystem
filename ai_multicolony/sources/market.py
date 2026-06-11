"""Market data feeds for the AI-MultiColony ecosystem.

Provides the :class:`MarketSource` that fetches real-time and historical
market data across equities, cryptocurrencies, and foreign exchange.

Each market segment has its own data model and normalisation logic,
ensuring consistent interfaces for downstream agents.
"""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict

from .base import (
    SourceCategory,
    SourceConfig,
    SourceItem,
    SourceProvider,
    SourceReliability,
    SourceResult,
)

logger = logging.getLogger(__name__)


# ── Data models ──────────────────────────────────────────────────────────────


class EquityQuote(BaseModel):
    """Stock/equity price quote."""
    symbol: str = ""
    name: str = ""
    price: float = 0.0
    change: float = 0.0
    change_pct: float = 0.0
    volume: int = 0
    market_cap_bn: float = 0.0
    pe_ratio: float = 0.0
    high_52w: float = 0.0
    low_52w: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CryptoQuote(BaseModel):
    """Cryptocurrency price quote."""
    symbol: str = ""
    name: str = ""
    price_usd: float = 0.0
    change_24h_pct: float = 0.0
    volume_24h_bn: float = 0.0
    market_cap_bn: float = 0.0
    dominance_pct: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ForexQuote(BaseModel):
    """Foreign exchange rate quote."""
    pair: str = ""
    rate: float = 0.0
    change: float = 0.0
    change_pct: float = 0.0
    bid: float = 0.0
    ask: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ── Market data ──────────────────────────────────────────────────────────────

EQUITY_DATA: Dict[str, Dict[str, Any]] = {
    "AAPL": {"name": "Apple Inc.", "price": 189.84, "change": 2.45, "change_pct": 1.31, "volume": 54_200_000, "market_cap_bn": 2940, "pe_ratio": 29.8, "high_52w": 199.62, "low_52w": 124.17},
    "MSFT": {"name": "Microsoft Corp.", "price": 425.52, "change": -1.23, "change_pct": -0.29, "volume": 22_100_000, "market_cap_bn": 3160, "pe_ratio": 36.2, "high_52w": 430.82, "low_52w": 309.45},
    "GOOGL": {"name": "Alphabet Inc.", "price": 175.98, "change": 3.12, "change_pct": 1.80, "volume": 28_500_000, "market_cap_bn": 2180, "pe_ratio": 25.1, "high_52w": 180.40, "low_52w": 115.35},
    "AMZN": {"name": "Amazon.com Inc.", "price": 185.07, "change": 1.89, "change_pct": 1.03, "volume": 48_300_000, "market_cap_bn": 1920, "pe_ratio": 58.7, "high_52w": 189.77, "low_52w": 118.35},
    "NVDA": {"name": "NVIDIA Corp.", "price": 878.36, "change": 15.67, "change_pct": 1.82, "volume": 41_700_000, "market_cap_bn": 2170, "pe_ratio": 72.3, "high_52w": 974.00, "low_52w": 373.56},
    "META": {"name": "Meta Platforms", "price": 502.30, "change": -3.45, "change_pct": -0.68, "volume": 18_200_000, "market_cap_bn": 1280, "pe_ratio": 26.4, "high_52w": 531.49, "low_52w": 274.38},
    "TSLA": {"name": "Tesla Inc.", "price": 175.21, "change": -5.82, "change_pct": -3.22, "volume": 112_500_000, "market_cap_bn": 558, "pe_ratio": 42.1, "high_52w": 299.29, "low_52w": 138.80},
    "BRK.B": {"name": "Berkshire Hathaway", "price": 415.80, "change": 0.95, "change_pct": 0.23, "volume": 3_400_000, "market_cap_bn": 895, "pe_ratio": 9.2, "high_52w": 425.30, "low_52w": 317.30},
}

CRYPTO_DATA: Dict[str, Dict[str, Any]] = {
    "BTC": {"name": "Bitcoin", "price_usd": 67250.00, "change_24h_pct": 1.45, "volume_24h_bn": 32.5, "market_cap_bn": 1320, "dominance_pct": 52.3},
    "ETH": {"name": "Ethereum", "price_usd": 3520.00, "change_24h_pct": 2.12, "volume_24h_bn": 18.7, "market_cap_bn": 423, "dominance_pct": 16.8},
    "BNB": {"name": "BNB", "price_usd": 595.00, "change_24h_pct": -0.85, "volume_24h_bn": 2.1, "market_cap_bn": 92, "dominance_pct": 3.6},
    "SOL": {"name": "Solana", "price_usd": 148.50, "change_24h_pct": 3.45, "volume_24h_bn": 4.2, "market_cap_bn": 65, "dominance_pct": 2.6},
    "XRP": {"name": "XRP", "price_usd": 0.62, "change_24h_pct": -1.23, "volume_24h_bn": 1.8, "market_cap_bn": 34, "dominance_pct": 1.3},
    "ADA": {"name": "Cardano", "price_usd": 0.48, "change_24h_pct": 0.78, "volume_24h_bn": 0.6, "market_cap_bn": 17, "dominance_pct": 0.7},
    "AVAX": {"name": "Avalanche", "price_usd": 38.20, "change_24h_pct": 4.12, "volume_24h_bn": 1.2, "market_cap_bn": 15, "dominance_pct": 0.6},
    "DOT": {"name": "Polkadot", "price_usd": 7.35, "change_24h_pct": 1.98, "volume_24h_bn": 0.5, "market_cap_bn": 10, "dominance_pct": 0.4},
}

FOREX_DATA: Dict[str, Dict[str, Any]] = {
    "EUR/USD": {"rate": 1.0845, "change": 0.0023, "change_pct": 0.21, "bid": 1.0844, "ask": 1.0846},
    "GBP/USD": {"rate": 1.2715, "change": -0.0015, "change_pct": -0.12, "bid": 1.2714, "ask": 1.2716},
    "USD/JPY": {"rate": 154.82, "change": 0.45, "change_pct": 0.29, "bid": 154.81, "ask": 154.83},
    "USD/CHF": {"rate": 0.8912, "change": 0.0018, "change_pct": 0.20, "bid": 0.8911, "ask": 0.8913},
    "AUD/USD": {"rate": 0.6623, "change": -0.0032, "change_pct": -0.48, "bid": 0.6622, "ask": 0.6624},
    "USD/CAD": {"rate": 1.3645, "change": 0.0025, "change_pct": 0.18, "bid": 1.3644, "ask": 1.3646},
    "NZD/USD": {"rate": 0.6098, "change": -0.0018, "change_pct": -0.29, "bid": 0.6097, "ask": 0.6099},
    "EUR/GBP": {"rate": 0.8528, "change": 0.0012, "change_pct": 0.14, "bid": 0.8527, "ask": 0.8529},
}


STALE_DATA_WARNING = (
    "MarketSource is returning STATIC/HARDCODED data. "
    "This is a development-mode stub and does NOT reflect live market prices. "
    "Do NOT use this data for production trading decisions."
)


class MarketSource(SourceProvider):
    """Market data feed provider.

    .. warning::
        This provider currently returns **hardcoded static data** for
        development and testing.  It is NOT suitable for production use.
        Check ``source.is_live`` before relying on any data.

    Fetches equity quotes, cryptocurrency prices, and forex rates.

    Usage::

        source = MarketSource()
        result = await source.fetch("AAPL", max_items=5)
        result = await source.scan(max_items=50)
    """

    def __init__(
        self,
        config: Optional[SourceConfig] = None,
        segments: Optional[List[str]] = None,
    ):
        super().__init__(
            name="market",
            category=SourceCategory.MARKET,
            reliability=SourceReliability.RELIABLE,
            config=config,
        )
        self._segments = segments or ["equities", "crypto", "forex"]

    @property
    def is_live(self) -> bool:
        """Whether this source returns live market data.

        Returns ``False`` because all data is hardcoded / static.
        """
        return False

    async def fetch(self, query: str, max_items: int = 50, **kwargs: Any) -> SourceResult:
        """Fetch market data matching a query.

        Parameters
        ----------
        query:
            Search query (symbol, name, or segment).
        max_items:
            Maximum items to return.

        Returns
        -------
        SourceResult
            Matched market data items.
        """
        start = time.monotonic()
        self._record_fetch()
        logger.warning(STALE_DATA_WARNING)
        items: List[SourceItem] = []
        errors: List[str] = []
        query_lower = query.lower()

        try:
            if "equities" in self._segments:
                items.extend(self._fetch_equities(query_lower, max_items))
            if "crypto" in self._segments and len(items) < max_items:
                items.extend(self._fetch_crypto(query_lower, max_items - len(items)))
            if "forex" in self._segments and len(items) < max_items:
                items.extend(self._fetch_forex(query_lower, max_items - len(items)))
        except Exception as exc:
            errors.append(str(exc))
            self._record_error()

        items = items[:max_items]
        elapsed = (time.monotonic() - start) * 1000
        return self._make_result(
            items=items,
            total_available=len(items),
            errors=errors,
            elapsed_ms=elapsed,
        )

    async def scan(self, max_items: int = 100, **kwargs: Any) -> SourceResult:
        """Scan all market data across segments.

        Parameters
        ----------
        max_items:
            Maximum items to return.

        Returns
        -------
        SourceResult
            Latest market data from all segments.
        """
        start = time.monotonic()
        self._record_scan()
        logger.warning(STALE_DATA_WARNING)
        items: List[SourceItem] = []
        errors: List[str] = []

        try:
            if "equities" in self._segments:
                items.extend(self._fetch_equities("", max_items))
            if "crypto" in self._segments and len(items) < max_items:
                items.extend(self._fetch_crypto("", max_items - len(items)))
            if "forex" in self._segments and len(items) < max_items:
                items.extend(self._fetch_forex("", max_items - len(items)))
        except Exception as exc:
            errors.append(str(exc))
            self._record_error()

        items = items[:max_items]
        elapsed = (time.monotonic() - start) * 1000
        return self._make_result(
            items=items,
            total_available=len(items),
            errors=errors,
            elapsed_ms=elapsed,
        )

    # ── Segment-specific fetch ──────────────────────────────────────────

    def _fetch_equities(self, query: str, max_items: int) -> List[SourceItem]:
        """Fetch equity quotes matching query."""
        items: List[SourceItem] = []
        for symbol, data in EQUITY_DATA.items():
            text = f"{symbol} {data['name']}".lower()
            if not query or query in text:
                quote = EquityQuote(symbol=symbol, **data)
                items.append(self._equity_to_item(quote))
                if len(items) >= max_items:
                    break
        return items

    def _fetch_crypto(self, query: str, max_items: int) -> List[SourceItem]:
        """Fetch crypto quotes matching query."""
        items: List[SourceItem] = []
        for symbol, data in CRYPTO_DATA.items():
            text = f"{symbol} {data['name']}".lower()
            if not query or query in text:
                quote = CryptoQuote(symbol=symbol, **data)
                items.append(self._crypto_to_item(quote))
                if len(items) >= max_items:
                    break
        return items

    def _fetch_forex(self, query: str, max_items: int) -> List[SourceItem]:
        """Fetch forex quotes matching query."""
        items: List[SourceItem] = []
        for pair, data in FOREX_DATA.items():
            text = pair.lower()
            if not query or query in text:
                quote = ForexQuote(pair=pair, **data)
                items.append(self._forex_to_item(quote))
                if len(items) >= max_items:
                    break
        return items

    # ── Converters ──────────────────────────────────────────────────────

    def _equity_to_item(self, quote: EquityQuote) -> SourceItem:
        """Convert equity quote to SourceItem."""
        return self._make_item(
            title=f"{quote.symbol} – {quote.name}: ${quote.price:.2f}",
            summary=f"{quote.name} trading at ${quote.price:.2f} ({quote.change_pct:+.2f}%)",
            content=(
                f"{quote.name} ({quote.symbol})\n"
                f"Price: ${quote.price:.2f} | Change: {quote.change:+.2f} ({quote.change_pct:+.2f}%)\n"
                f"Volume: {quote.volume:,} | Market Cap: ${quote.market_cap_bn:.0f}B\n"
                f"P/E: {quote.pe_ratio:.1f} | 52w Range: ${quote.low_52w:.2f} - ${quote.high_52w:.2f}"
            ),
            category=SourceCategory.MARKET,
            reliability=SourceReliability.RELIABLE,
            relevance_score=0.8,
            confidence=0.95,
            tags=["equity", quote.symbol.lower()],
        )

    def _crypto_to_item(self, quote: CryptoQuote) -> SourceItem:
        """Convert crypto quote to SourceItem."""
        return self._make_item(
            title=f"{quote.symbol} – {quote.name}: ${quote.price_usd:,.2f}",
            summary=f"{quote.name} at ${quote.price_usd:,.2f} ({quote.change_24h_pct:+.2f}% 24h)",
            content=(
                f"{quote.name} ({quote.symbol})\n"
                f"Price: ${quote.price_usd:,.2f} | 24h Change: {quote.change_24h_pct:+.2f}%\n"
                f"Volume (24h): ${quote.volume_24h_bn:.1f}B | Market Cap: ${quote.market_cap_bn:.0f}B\n"
                f"Dominance: {quote.dominance_pct:.1f}%"
            ),
            category=SourceCategory.MARKET,
            reliability=SourceReliability.USUALLY_RELIABLE,
            relevance_score=0.7,
            confidence=0.90,
            tags=["crypto", quote.symbol.lower()],
        )

    def _forex_to_item(self, quote: ForexQuote) -> SourceItem:
        """Convert forex quote to SourceItem."""
        return self._make_item(
            title=f"{quote.pair}: {quote.rate:.4f}",
            summary=f"{quote.pair} at {quote.rate:.4f} ({quote.change_pct:+.2f}%)",
            content=(
                f"{quote.pair}\n"
                f"Rate: {quote.rate:.4f} | Change: {quote.change:+.4f} ({quote.change_pct:+.2f}%)\n"
                f"Bid: {quote.bid:.4f} | Ask: {quote.ask:.4f} | Spread: {quote.ask - quote.bid:.4f}"
            ),
            category=SourceCategory.MARKET,
            reliability=SourceReliability.RELIABLE,
            relevance_score=0.6,
            confidence=0.95,
            tags=["forex", quote.pair.lower().replace("/", "")],
        )

    # ── Direct access methods ───────────────────────────────────────────

    def get_equity_quote(self, symbol: str) -> Optional[EquityQuote]:
        """Get a quote for a specific equity symbol."""
        data = EQUITY_DATA.get(symbol.upper())
        if data is None:
            return None
        return EquityQuote(symbol=symbol.upper(), **data)

    def get_crypto_quote(self, symbol: str) -> Optional[CryptoQuote]:
        """Get a quote for a specific crypto symbol."""
        data = CRYPTO_DATA.get(symbol.upper())
        if data is None:
            return None
        return CryptoQuote(symbol=symbol.upper(), **data)

    def get_forex_quote(self, pair: str) -> Optional[ForexQuote]:
        """Get a quote for a specific forex pair."""
        data = FOREX_DATA.get(pair.upper())
        if data is None:
            return None
        return ForexQuote(pair=pair.upper(), **data)

    @property
    def available_symbols(self) -> Dict[str, List[str]]:
        """Available symbols by segment."""
        return {
            "equities": list(EQUITY_DATA.keys()),
            "crypto": list(CRYPTO_DATA.keys()),
            "forex": list(FOREX_DATA.keys()),
        }
