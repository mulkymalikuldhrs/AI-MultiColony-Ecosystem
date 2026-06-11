"""Economic Data Sources — FRED, BLS, EIA, Treasury.

Ported from Crucix apis/sources/ with Python async rewrite.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from ai_multicolony_ecosystem.sources.base import (
    BaseSource,
    SourceHealth,
    SourceRegistry,
    SourceResult,
    SourceTier,
)

logger = logging.getLogger(__name__)


@SourceRegistry.register
class FREDSource(BaseSource):
    """Federal Reserve Economic Data — 800K+ economic time series."""

    name = "fred"
    tier = SourceTier.ECONOMIC
    timeout_seconds = 15

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self._api_key = (config or {}).get("api_key", "")

    async def sweep(self) -> SourceResult:
        """Sweep key FRED indicators."""
        import httpx

        if not self._api_key:
            return SourceResult(
                source=self.name,
                tier=self.tier,
                error="FRED API key not configured",
            )

        indicators = {
            "DFF": "federal_funds_rate",
            "DGS10": "treasury_10y",
            "T10Y2Y": "yield_spread_10y2y",
            "CPIAUCSL": "cpi",
            "UNRATE": "unemployment",
        }

        results = {}
        base_url = "https://api.stlouisfed.org/fred/series/observations"

        async with httpx.AsyncClient(timeout=15) as client:
            for series_id, label in indicators.items():
                try:
                    params = {
                        "series_id": series_id,
                        "api_key": self._api_key,
                        "file_type": "json",
                        "sort_order": "desc",
                        "limit": 1,
                    }
                    resp = await client.get(base_url, params=params)
                    resp.raise_for_status()
                    data = resp.json()
                    observations = data.get("observations", [])
                    if observations:
                        val = observations[0].get("value", ".")
                        if val != ".":
                            results[label] = {
                                "value": float(val),
                                "date": observations[0].get("date", ""),
                            }
                except Exception as exc:
                    logger.debug("FRED %s failed: %s", series_id, exc)

        return SourceResult(
            source=self.name,
            tier=self.tier,
            data=results,
            metadata={"indicators_requested": len(indicators), "indicators_received": len(results)},
        )


@SourceRegistry.register
class BLSSource(BaseSource):
    """Bureau of Labor Statistics — Employment, inflation, productivity."""

    name = "bls"
    tier = SourceTier.ECONOMIC
    timeout_seconds = 15

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self._api_key = (config or {}).get("api_key", "")

    async def sweep(self) -> SourceResult:
        import httpx

        if not self._api_key:
            return SourceResult(source=self.name, tier=self.tier, error="BLS API key not configured")

        series = {"LNS14000000": "unemployment_rate", "CUSR0000SA0": "cpi_all_items"}
        results = {}

        async with httpx.AsyncClient(timeout=15) as client:
            try:
                resp = await client.post(
                    "https://api.bls.gov/publicAPI/v2/timeseries/data/",
                    json={"seriesid": list(series.keys()), "api_key": self._api_key},
                )
                resp.raise_for_status()
                data = resp.json()

                for series_data in data.get("Results", {}).get("series", []):
                    sid = series_data.get("seriesID", "")
                    label = series.get(sid, sid)
                    observations = series_data.get("data", [])
                    if observations:
                        results[label] = {
                            "value": observations[0].get("value", ""),
                            "period": observations[0].get("periodName", ""),
                        }
            except Exception as exc:
                logger.debug("BLS sweep failed: %s", exc)

        return SourceResult(source=self.name, tier=self.tier, data=results)


@SourceRegistry.register
class EIASource(BaseSource):
    """Energy Information Administration — Oil, gas, energy data."""

    name = "eia"
    tier = SourceTier.ECONOMIC
    timeout_seconds = 15

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self._api_key = (config or {}).get("api_key", "")

    async def sweep(self) -> SourceResult:
        import httpx

        if not self._api_key:
            return SourceResult(source=self.name, tier=self.tier, error="EIA API key not configured")

        results = {}
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                # WTI Crude Oil Price
                resp = await client.get(
                    "https://api.eia.gov/v2/petroleum/pri/spt/data/",
                    params={"api_key": self._api_key, "frequency": "daily", "data[]": "value", "sort[0][column]": "period", "sort[0][direction]": "desc", "length": 1},
                )
                resp.raise_for_status()
                data = resp.json()
                if data.get("response", {}).get("data"):
                    item = data["response"]["data"][0]
                    results["wti_crude"] = {"value": item.get("value", ""), "period": item.get("period", "")}
            except Exception as exc:
                logger.debug("EIA sweep failed: %s", exc)

        return SourceResult(source=self.name, tier=self.tier, data=results)


@SourceRegistry.register
class TreasurySource(BaseSource):
    """US Treasury — Yield curves, debt, fiscal data."""

    name = "treasury"
    tier = SourceTier.ECONOMIC
    timeout_seconds = 15

    async def sweep(self) -> SourceResult:
        import httpx

        results = {}
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                resp = await client.get(
                    "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/avg_interest_rates",
                    params={"sort": "-record_date", "page[size]": 5},
                )
                resp.raise_for_status()
                data = resp.json()
                for item in data.get("data", []):
                    security = item.get("security_desc", "unknown")
                    results[security] = {
                        "rate": item.get("avg_interest_rate_amt", ""),
                        "date": item.get("record_date", ""),
                    }
            except Exception as exc:
                logger.debug("Treasury sweep failed: %s", exc)

        return SourceResult(source=self.name, tier=self.tier, data=results)


__all__ = ["FREDSource", "BLSSource", "EIASource", "TreasurySource"]
