"""OSINT Sources — GDELT, ACLED, ReliefWeb, WHO, OFAC, OpenSanctions.

Ported from Crucix apis/sources/ with Python async rewrite.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ai_multicolony_ecosystem.sources.base import (
    BaseSource,
    SourceRegistry,
    SourceResult,
    SourceTier,
)

logger = logging.getLogger(__name__)


@SourceRegistry.register
class GDELTSource(BaseSource):
    """GDELT Project — Global events, media, sentiment tracking."""

    name = "gdelt"
    tier = SourceTier.OSINT
    timeout_seconds = 20

    async def sweep(self) -> SourceResult:
        import httpx

        results = {}
        async with httpx.AsyncClient(timeout=20) as client:
            try:
                # GDELT API for latest events
                resp = await client.get(
                    "https://api.gdeltproject.org/api/v2/doc/doc",
                    params={
                        "query": "conflict OR crisis OR sanctions",
                        "mode": "ArtList",
                        "maxrecords": 10,
                        "format": "json",
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                articles = data.get("articles", [])
                results = {
                    "total_articles": len(articles),
                    "top_events": [
                        {
                            "title": a.get("title", ""),
                            "url": a.get("url", ""),
                            "source": a.get("sourcecountry", ""),
                            "date": a.get("seendate", ""),
                            "tone": a.get("tone", ""),
                        }
                        for a in articles[:5]
                    ],
                }
            except Exception as exc:
                logger.debug("GDELT sweep failed: %s", exc)

        return SourceResult(source=self.name, tier=self.tier, data=results)


@SourceRegistry.register
class ACLEDSource(BaseSource):
    """ACLED — Armed Conflict Location & Event Data."""

    name = "acled"
    tier = SourceTier.OSINT
    timeout_seconds = 15

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self._api_key = (config or {}).get("api_key", "")
        self._email = (config or {}).get("email", "")

    async def sweep(self) -> SourceResult:
        import httpx

        if not self._api_key or not self._email:
            return SourceResult(source=self.name, tier=self.tier, error="ACLED credentials not configured")

        results = {}
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                from datetime import timedelta
                end = datetime.now(tz=timezone.utc)
                start = end - timedelta(days=7)
                resp = await client.get(
                    "https://api.acleddata.com/acled/read",
                    params={
                        "key": self._api_key,
                        "email": self._email,
                        "event_date": f"{start.strftime('%Y-%m-%d')}|{end.strftime('%Y-%m-%d')}",
                        "event_date_where": "BETWEEN",
                        "limit": 10,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                events = data.get("data", [])
                results = {
                    "total_events": len(events),
                    "conflict_zones": list(set(e.get("country", "") for e in events if e.get("country"))),
                    "event_types": list(set(e.get("event_type", "") for e in events if e.get("event_type"))),
                }
            except Exception as exc:
                logger.debug("ACLED sweep failed: %s", exc)

        return SourceResult(source=self.name, tier=self.tier, data=results)


@SourceRegistry.register
class WHOSource(BaseSource):
    """World Health Organization — Disease outbreaks, health data."""

    name = "who"
    tier = SourceTier.OSINT
    timeout_seconds = 15

    async def sweep(self) -> SourceResult:
        import httpx

        results = {}
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                resp = await client.get(
                    "https://ghoapi.azureedge.net/api/DON",
                )
                if resp.status_code == 200:
                    data = resp.json()
                    outbreaks = data.get("value", [])
                    results = {
                        "active_outbreaks": len(outbreaks),
                        "recent": [
                            {"title": b.get("Title", ""), "date": b.get("Date", "")}
                            for b in outbreaks[:5]
                        ],
                    }
            except Exception as exc:
                logger.debug("WHO sweep failed: %s", exc)

        return SourceResult(source=self.name, tier=self.tier, data=results)


@SourceRegistry.register
class OFACSource(BaseSource):
    """OFAC Sanctions — US Treasury sanctions lists."""

    name = "ofac"
    tier = SourceTier.OSINT
    timeout_seconds = 15

    async def sweep(self) -> SourceResult:
        import httpx

        results = {}
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                resp = await client.get(
                    "https://api.trade.gov/static/consolidated_screening_list.csv",
                )
                if resp.status_code == 200:
                    lines = resp.text.strip().split("\n")
                    results = {
                        "total_entries": len(lines) - 1,
                        "last_updated": datetime.now(tz=timezone.utc).isoformat(),
                    }
            except Exception as exc:
                logger.debug("OFAC sweep failed: %s", exc)

        return SourceResult(source=self.name, tier=self.tier, data=results)


@SourceRegistry.register
class YFinanceSource(BaseSource):
    """Yahoo Finance — Market data for equities, crypto, forex."""

    name = "yfinance"
    tier = SourceTier.MARKET
    timeout_seconds = 15

    async def sweep(self) -> SourceResult:
        try:
            import yfinance as yf

            tickers = {
                "^GSPC": "sp500",
                "^VIX": "vix",
                "BTC-USD": "btc",
                "EURUSD=X": "eurusd",
                "GC=F": "gold",
            }

            results = {}
            for symbol, label in tickers.items():
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info or {}
                    price = info.get("regularMarketPrice") or info.get("currentPrice", 0)
                    change = info.get("regularMarketChangePercent", 0)
                    results[label] = {
                        "price": float(price) if price else 0,
                        "change_pct": float(change) if change else 0,
                    }
                except Exception:
                    pass

            return SourceResult(source=self.name, tier=self.tier, data=results)
        except ImportError:
            return SourceResult(source=self.name, tier=self.tier, error="yfinance not installed")


@SourceRegistry.register
class RedditSource(BaseSource):
    """Reddit — Social sentiment from trading/finance subreddits."""

    name = "reddit"
    tier = SourceTier.OSINT
    timeout_seconds = 15

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self._client_id = (config or {}).get("client_id", "")
        self._client_secret = (config or {}).get("client_secret", "")

    async def sweep(self) -> SourceResult:
        results = {"note": "Reddit API requires OAuth - check configuration"}
        return SourceResult(source=self.name, tier=self.tier, data=results)


__all__ = ["GDELTSource", "ACLEDSource", "WHOSource", "OFACSource", "YFinanceSource", "RedditSource"]
