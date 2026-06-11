"""Economic data feeds for the AI-MultiColony ecosystem.

Provides the :class:`EconomicSource` that fetches macroeconomic indicators
including GDP, inflation (CPI), interest rates, employment data, trade
balances, and central bank policy decisions.

Data is normalised into a consistent :class:`EconomicIndicator` model
that can be used by agents for decision-making.
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


class EconomicIndicator(BaseModel):
    """A single economic indicator measurement."""

    model_config = ConfigDict(frozen=False)

    indicator_id: str = ""
    name: str = ""
    country: str = ""
    value: float = 0.0
    previous_value: Optional[float] = None
    unit: str = ""
    frequency: str = "monthly"  # daily, weekly, monthly, quarterly, annual
    source_agency: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    change_pct: Optional[float] = None
    category: str = ""  # gdp, inflation, employment, trade, monetary, fiscal

    def to_item(self) -> SourceItem:
        """Convert to a SourceItem for unified source pipeline."""
        content = (
            f"{self.country} {self.name}: {self.value} {self.unit}"
            f" (previous: {self.previous_value})"
            f" (change: {self.change_pct}%)" if self.change_pct is not None else
            f"{self.country} {self.name}: {self.value} {self.unit}"
        )
        return SourceItem(
            source_name="economic",
            category=SourceCategory.ECONOMIC,
            title=f"{self.country} – {self.name}",
            summary=f"{self.name} for {self.country} is {self.value} {self.unit}",
            content=content,
            relevance_score=0.7,
            confidence=0.9,
            tags=["economic", self.category, self.country.lower()],
        )


class GDPRate(BaseModel):
    """GDP growth rate data."""
    country: str = ""
    annual_growth_pct: float = 0.0
    quarterly_growth_pct: float = 0.0
    gdp_nominal_usd_bn: float = 0.0
    gdp_per_capita_usd: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InflationData(BaseModel):
    """Inflation / CPI data."""
    country: str = ""
    cpi_yoy_pct: float = 0.0
    cpi_mom_pct: float = 0.0
    core_cpi_yoy_pct: float = 0.0
    ppi_yoy_pct: Optional[float] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InterestRateData(BaseModel):
    """Central bank interest rate data."""
    country: str = ""
    central_bank: str = ""
    policy_rate_pct: float = 0.0
    previous_rate_pct: Optional[float] = None
    next_meeting_date: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ── Country economic profiles ───────────────────────────────────────────────

ECONOMIC_PROFILES: Dict[str, Dict[str, Any]] = {
    "US": {
        "gdp_growth_annual": 2.5,
        "gdp_quarterly": 0.8,
        "gdp_nominal_bn": 27360,
        "gdp_per_capita": 81600,
        "cpi_yoy": 3.2,
        "cpi_mom": 0.3,
        "core_cpi_yoy": 3.8,
        "ppi_yoy": 1.2,
        "policy_rate": 5.25,
        "central_bank": "Federal Reserve",
        "unemployment_rate": 3.9,
        "trade_balance_bn": -68.3,
    },
    "EU": {
        "gdp_growth_annual": 0.6,
        "gdp_quarterly": 0.2,
        "gdp_nominal_bn": 18700,
        "gdp_per_capita": 42000,
        "cpi_yoy": 2.4,
        "cpi_mom": 0.2,
        "core_cpi_yoy": 2.8,
        "ppi_yoy": -1.5,
        "policy_rate": 4.50,
        "central_bank": "ECB",
        "unemployment_rate": 6.4,
        "trade_balance_bn": 32.1,
    },
    "CN": {
        "gdp_growth_annual": 5.2,
        "gdp_quarterly": 1.3,
        "gdp_nominal_bn": 17960,
        "gdp_per_capita": 12700,
        "cpi_yoy": 0.2,
        "cpi_mom": -0.1,
        "core_cpi_yoy": 0.7,
        "ppi_yoy": -2.7,
        "policy_rate": 3.45,
        "central_bank": "PBOC",
        "unemployment_rate": 5.2,
        "trade_balance_bn": 823.2,
    },
    "JP": {
        "gdp_growth_annual": 1.9,
        "gdp_quarterly": 0.5,
        "gdp_nominal_bn": 4210,
        "gdp_per_capita": 33800,
        "cpi_yoy": 2.8,
        "cpi_mom": 0.3,
        "core_cpi_yoy": 2.5,
        "ppi_yoy": 0.5,
        "policy_rate": 0.1,
        "central_bank": "BOJ",
        "unemployment_rate": 2.6,
        "trade_balance_bn": -45.6,
    },
    "GB": {
        "gdp_growth_annual": 0.5,
        "gdp_quarterly": 0.1,
        "gdp_nominal_bn": 3160,
        "gdp_per_capita": 47000,
        "cpi_yoy": 4.0,
        "cpi_mom": 0.4,
        "core_cpi_yoy": 3.9,
        "ppi_yoy": 0.3,
        "policy_rate": 5.25,
        "central_bank": "BOE",
        "unemployment_rate": 4.2,
        "trade_balance_bn": -156.7,
    },
    "DE": {
        "gdp_growth_annual": -0.1,
        "gdp_quarterly": -0.1,
        "gdp_nominal_bn": 4460,
        "gdp_per_capita": 53100,
        "cpi_yoy": 2.2,
        "cpi_mom": 0.2,
        "core_cpi_yoy": 2.7,
        "ppi_yoy": -3.2,
        "policy_rate": 4.50,
        "central_bank": "Bundesbank/ECB",
        "unemployment_rate": 3.1,
        "trade_balance_bn": 223.4,
    },
    "IN": {
        "gdp_growth_annual": 7.2,
        "gdp_quarterly": 1.8,
        "gdp_nominal_bn": 3940,
        "gdp_per_capita": 2800,
        "cpi_yoy": 5.1,
        "cpi_mom": 0.4,
        "core_cpi_yoy": 4.3,
        "ppi_yoy": 1.8,
        "policy_rate": 6.50,
        "central_bank": "RBI",
        "unemployment_rate": 7.8,
        "trade_balance_bn": -265.3,
    },
    "BR": {
        "gdp_growth_annual": 2.9,
        "gdp_quarterly": 0.7,
        "gdp_nominal_bn": 2170,
        "gdp_per_capita": 10100,
        "cpi_yoy": 4.5,
        "cpi_mom": 0.3,
        "core_cpi_yoy": 4.8,
        "ppi_yoy": 2.1,
        "policy_rate": 10.50,
        "central_bank": "BCB",
        "unemployment_rate": 7.8,
        "trade_balance_bn": 98.7,
    },
}


class EconomicSource(SourceProvider):
    """Economic data feed provider.

    Fetches macroeconomic indicators from a curated database of
    country-level economic profiles.  Supports targeted queries
    by country and indicator type.

    Usage::

        source = EconomicSource()
        result = await source.fetch("US inflation", max_items=10)
        result = await source.scan(max_items=50)
    """

    def __init__(
        self,
        config: Optional[SourceConfig] = None,
        countries: Optional[List[str]] = None,
    ):
        super().__init__(
            name="economic",
            category=SourceCategory.ECONOMIC,
            reliability=SourceReliability.RELIABLE,
            config=config,
        )
        self._countries = countries or list(ECONOMIC_PROFILES.keys())

    async def fetch(self, query: str, max_items: int = 50, **kwargs: Any) -> SourceResult:
        """Fetch economic indicators matching a query.

        Parameters
        ----------
        query:
            Search query (e.g. "US inflation", "GDP growth", "interest rates").
        max_items:
            Maximum items to return.

        Returns
        -------
        SourceResult
            Matched economic indicators.
        """
        start = time.monotonic()
        self._record_fetch()
        items: List[SourceItem] = []
        errors: List[str] = []
        query_lower = query.lower()

        try:
            for country in self._countries:
                profile = ECONOMIC_PROFILES.get(country)
                if profile is None:
                    continue
                indicators = self._build_indicators(country, profile)
                for indicator in indicators:
                    text = f"{indicator.name} {indicator.country} {indicator.category}".lower()
                    if query_lower in text or any(w in text for w in query_lower.split()):
                        items.append(indicator.to_item())
                        if len(items) >= max_items:
                            break
                if len(items) >= max_items:
                    break
        except Exception as exc:
            errors.append(str(exc))
            self._record_error()

        elapsed = (time.monotonic() - start) * 1000
        return self._make_result(
            items=items,
            total_available=len(items),
            errors=errors,
            elapsed_ms=elapsed,
        )

    async def scan(self, max_items: int = 100, **kwargs: Any) -> SourceResult:
        """Scan all economic indicators across countries.

        Parameters
        ----------
        max_items:
            Maximum items to return.

        Returns
        -------
        SourceResult
            Latest economic indicators from all tracked countries.
        """
        start = time.monotonic()
        self._record_scan()
        items: List[SourceItem] = []
        errors: List[str] = []

        try:
            for country in self._countries:
                profile = ECONOMIC_PROFILES.get(country)
                if profile is None:
                    continue
                indicators = self._build_indicators(country, profile)
                for indicator in indicators:
                    items.append(indicator.to_item())
                    if len(items) >= max_items:
                        break
                if len(items) >= max_items:
                    break
        except Exception as exc:
            errors.append(str(exc))
            self._record_error()

        elapsed = (time.monotonic() - start) * 1000
        return self._make_result(
            items=items,
            total_available=len(items),
            errors=errors,
            elapsed_ms=elapsed,
        )

    def _build_indicators(
        self,
        country: str,
        profile: Dict[str, Any],
    ) -> List[EconomicIndicator]:
        """Build economic indicators from a country profile."""
        now = datetime.now(timezone.utc)
        indicators: List[EconomicIndicator] = []

        # GDP
        indicators.append(EconomicIndicator(
            indicator_id=f"{country}_gdp",
            name="GDP Growth Rate",
            country=country,
            value=profile["gdp_growth_annual"],
            unit="% annual",
            frequency="quarterly",
            source_agency=profile["central_bank"],
            timestamp=now,
            category="gdp",
        ))

        # Inflation
        indicators.append(EconomicIndicator(
            indicator_id=f"{country}_cpi",
            name="Consumer Price Index (YoY)",
            country=country,
            value=profile["cpi_yoy"],
            previous_value=profile.get("cpi_yoy"),
            unit="%",
            frequency="monthly",
            source_agency="National Statistics",
            timestamp=now,
            change_pct=None,
            category="inflation",
        ))

        # Interest Rate
        indicators.append(EconomicIndicator(
            indicator_id=f"{country}_rate",
            name="Policy Interest Rate",
            country=country,
            value=profile["policy_rate"],
            unit="%",
            frequency="irregular",
            source_agency=profile["central_bank"],
            timestamp=now,
            category="monetary",
        ))

        # Unemployment
        indicators.append(EconomicIndicator(
            indicator_id=f"{country}_unemp",
            name="Unemployment Rate",
            country=country,
            value=profile["unemployment_rate"],
            unit="%",
            frequency="monthly",
            source_agency="Labor Bureau",
            timestamp=now,
            category="employment",
        ))

        # Trade Balance
        indicators.append(EconomicIndicator(
            indicator_id=f"{country}_trade",
            name="Trade Balance",
            country=country,
            value=profile["trade_balance_bn"],
            unit="USD billions",
            frequency="monthly",
            source_agency="Customs/Trade Authority",
            timestamp=now,
            category="trade",
        ))

        return indicators

    def get_gdp_data(self, country: str) -> Optional[GDPRate]:
        """Get GDP data for a specific country."""
        profile = ECONOMIC_PROFILES.get(country)
        if profile is None:
            return None
        return GDPRate(
            country=country,
            annual_growth_pct=profile["gdp_growth_annual"],
            quarterly_growth_pct=profile["gdp_quarterly"],
            gdp_nominal_usd_bn=profile["gdp_nominal_bn"],
            gdp_per_capita_usd=profile["gdp_per_capita"],
        )

    def get_inflation_data(self, country: str) -> Optional[InflationData]:
        """Get inflation data for a specific country."""
        profile = ECONOMIC_PROFILES.get(country)
        if profile is None:
            return None
        return InflationData(
            country=country,
            cpi_yoy_pct=profile["cpi_yoy"],
            cpi_mom_pct=profile["cpi_mom"],
            core_cpi_yoy_pct=profile["core_cpi_yoy"],
            ppi_yoy_pct=profile.get("ppi_yoy"),
        )

    def get_interest_rate_data(self, country: str) -> Optional[InterestRateData]:
        """Get central bank interest rate data for a specific country."""
        profile = ECONOMIC_PROFILES.get(country)
        if profile is None:
            return None
        return InterestRateData(
            country=country,
            central_bank=profile["central_bank"],
            policy_rate_pct=profile["policy_rate"],
        )

    @property
    def tracked_countries(self) -> List[str]:
        """List of tracked country codes."""
        return list(self._countries)
