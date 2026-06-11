"""Crucix Bridge — OSINT intelligence engine integration for AI-MultiColony.

Provides access to Crucix's 26+ intelligence sources (GDELT, CISA-KEV,
OFAC, OpenSanctions, FRED, EIA, ACLED, FIRMS, etc.) via the Crucix
HTTP API.

All network calls use ``httpx`` and degrade gracefully when the Crucix
service is not running.

Crucix API reference (from ``server.mjs``)
-------------------------------------------
- ``GET /api/data``  — current synthesised dashboard data
- ``GET /api/health`` — health / uptime / sweep metadata
- ``GET /events``     — SSE live-updates stream

The bridge also provides higher-level helpers that aggregate raw source
data into actionable intelligence (threat analysis, geopolitical risk,
supply-chain risk).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
import structlog

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class CrucixBridgeError(Exception):
    """Base exception for Crucix bridge failures."""


class CrucixUnavailableError(CrucixBridgeError):
    """Raised when the Crucix service is unreachable."""


class SourceNotFoundError(CrucixBridgeError):
    """Raised when a requested OSINT source does not exist."""


class IntelligenceError(CrucixBridgeError):
    """Raised when intelligence analysis fails."""

# ---------------------------------------------------------------------------
# Source catalogue (from crucix/apis/sources/*.mjs)
# ---------------------------------------------------------------------------

OSINT_SOURCES: Dict[str, Dict[str, str]] = {
    # Tier 1: Core OSINT & Geopolitical
    "GDELT":            {"tier": "1", "category": "geopolitical", "description": "Global event database, 100+ languages"},
    "OpenSky":          {"tier": "1", "category": "geopolitical", "description": "Aviation/flight tracking"},
    "FIRMS":            {"tier": "1", "category": "environmental", "description": "Fire/thermal anomaly detection (NASA)"},
    "Maritime":         {"tier": "1", "category": "geopolitical", "description": "Ship tracking / maritime intelligence"},
    "Safecast":         {"tier": "1", "category": "environmental", "description": "Radiation monitoring"},
    "ACLED":            {"tier": "1", "category": "geopolitical", "description": "Armed conflict location & event data"},
    "ReliefWeb":        {"tier": "1", "category": "humanitarian", "description": "Humanitarian crisis monitoring"},
    "WHO":              {"tier": "1", "category": "health",        "description": "World Health Organization alerts"},
    "OFAC":             {"tier": "1", "category": "sanctions",     "description": "US Treasury sanctions list"},
    "OpenSanctions":    {"tier": "1", "category": "sanctions",     "description": "Consolidated sanctions data"},
    "ADS-B":            {"tier": "1", "category": "geopolitical", "description": "Aircraft transponder data"},
    # Tier 2: Economic & Financial
    "FRED":             {"tier": "2", "category": "economic",      "description": "Federal Reserve economic data"},
    "Treasury":         {"tier": "2", "category": "economic",      "description": "US Treasury yield curves"},
    "BLS":              {"tier": "2", "category": "economic",      "description": "Bureau of Labor Statistics"},
    "EIA":              {"tier": "2", "category": "energy",        "description": "Energy Information Administration"},
    "GSCPI":            {"tier": "2", "category": "supply_chain",  "description": "Global Supply Chain Pressure Index"},
    "USAspending":      {"tier": "2", "category": "economic",      "description": "US federal spending data"},
    "Comtrade":         {"tier": "2", "category": "trade",         "description": "UN commodity trade statistics"},
    # Tier 3: Weather, Environment, Technology, Social
    "NOAA":             {"tier": "3", "category": "weather",       "description": "National weather alerts"},
    "EPA":              {"tier": "3", "category": "environmental", "description": "Environmental Protection Agency data"},
    "Patents":          {"tier": "3", "category": "technology",    "description": "USPTO patent filings"},
    "Bluesky":          {"tier": "3", "category": "social",        "description": "Bluesky social feed"},
    "Reddit":           {"tier": "3", "category": "social",        "description": "Reddit signal monitoring"},
    "Telegram":         {"tier": "3", "category": "social",        "description": "Telegram channel monitoring"},
    "KiwiSDR":          {"tier": "3", "category": "signals",       "description": "Software-defined radio monitoring"},
    # Tier 4: Space & Satellites
    "Space":            {"tier": "4", "category": "space",         "description": "Space launch / satellite tracking"},
    # Tier 5: Live Market Data
    "YFinance":         {"tier": "5", "category": "markets",       "description": "Live market data (Yahoo Finance)"},
    # Tier 6: Cyber & Infrastructure
    "CISA-KEV":         {"tier": "6", "category": "cyber",         "description": "Known Exploited Vulnerabilities catalog"},
    "Cloudflare-Radar": {"tier": "6", "category": "cyber",         "description": "Internet traffic / outage data"},
}

# ---------------------------------------------------------------------------
# Crucix Bridge
# ---------------------------------------------------------------------------


class CrucixBridge:
    """Bridge to the Crucix OSINT intelligence engine.

    Parameters
    ----------
    config : dict
        Configuration dictionary.  Recognized keys:

        - ``crucix_url`` (str): Base URL for the Crucix HTTP API
          (default ``http://localhost:3117``).
        - ``timeout`` (float): HTTP request timeout in seconds
          (default ``30.0``).
    """

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self._base_url = self.config.get("crucix_url", "http://localhost:3117").rstrip("/")
        self._timeout = self.config.get("timeout", 30.0)
        self._client = httpx.AsyncClient(timeout=self._timeout)

        logger.info(
            "crucix_bridge_initialised",
            base_url=self._base_url,
            source_count=len(OSINT_SOURCES),
        )

    # ------------------------------------------------------------------
    # Low-level HTTP helpers
    # ------------------------------------------------------------------

    async def _get(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Perform a GET request against the Crucix API."""
        url = f"{self._base_url}{path}"
        try:
            resp = await self._client.get(url, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as exc:
            logger.warning("crucix_http_error", url=url, error=str(exc))
            raise CrucixUnavailableError(f"Crucix service unreachable: {exc}") from exc

    # ------------------------------------------------------------------
    # Data access
    # ------------------------------------------------------------------

    async def fetch_intelligence(
        self,
        query: str = "",
        sources: List[str] | None = None,
    ) -> Dict[str, Any]:
        """Fetch OSINT data, optionally filtered by query and sources.

        Parameters
        ----------
        query : str
            Search query string (used for GDELT searches, etc.).
        sources : list[str] or None
            Specific source names to filter.  If ``None``, all sources
            from the latest sweep are returned.

        Returns
        -------
        dict
            Intelligence data with ``data_source`` and ``timestamp`` keys.
        """
        timestamp = datetime.now().isoformat()

        try:
            data = await self._get("/api/data")
        except CrucixUnavailableError:
            return {
                "error": "Crucix service unavailable",
                "data_source": "crucix_bridge",
                "status": "unavailable",
                "timestamp": timestamp,
            }

        # Extract raw sources from Crucix's synthesised output
        raw_sources = data.get("sources", {})

        # Apply source filter
        if sources:
            filtered = {k: v for k, v in raw_sources.items() if k in sources}
            missing = [s for s in sources if s not in raw_sources]
            if missing:
                logger.debug("crucix_sources_missing", missing=missing)
        else:
            filtered = raw_sources

        # If a query is provided, attempt GDELT-specific search
        gdelt_results: Dict[str, Any] = {}
        if query:
            gdelt_results = await self._search_gdelt(query)

        result: Dict[str, Any] = {
            "sources": filtered,
            "source_count": len(filtered),
            "query": query,
            "meta": data.get("meta", {}),
            "news": data.get("news", []),
            "newsFeed": data.get("newsFeed", []),
            "data_source": "crucix_intelligence",
            "timestamp": timestamp,
        }

        if gdelt_results:
            result["gdelt_search"] = gdelt_results

        return result

    async def get_available_sources(self) -> List[str]:
        """List all known OSINT source names supported by Crucix.

        Returns the static catalogue regardless of service availability.
        """
        return list(OSINT_SOURCES.keys())

    async def get_source_details(self, source_name: str) -> Dict[str, Any]:
        """Get metadata about a specific OSINT source.

        Raises
        ------
        SourceNotFoundError
            If *source_name* is not in the catalogue.
        """
        if source_name not in OSINT_SOURCES:
            raise SourceNotFoundError(f"Source '{source_name}' not found in Crucix catalogue")
        return {
            "name": source_name,
            **OSINT_SOURCES[source_name],
            "data_source": "crucix_catalogue",
        }

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    async def health_check(self) -> Dict[str, Any]:
        """Check Crucix service connectivity and sweep status."""
        try:
            data = await self._get("/api/health")
            data.setdefault("data_source", "crucix_health")
            data.setdefault("timestamp", datetime.now().isoformat())
            return data
        except CrucixUnavailableError:
            return {
                "status": "unavailable",
                "data_source": "crucix_bridge",
                "timestamp": datetime.now().isoformat(),
            }

    # ------------------------------------------------------------------
    # Higher-level intelligence analysis
    # ------------------------------------------------------------------

    async def analyze_threats(self, data: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Analyze threat signals from Crucix intelligence data.

        Aggregates signals from cyber (CISA-KEV), geopolitical (GDELT,
        ACLED), and sanctions (OFAC, OpenSanctions) sources.

        Parameters
        ----------
        data : dict or None
            Pre-fetched intelligence data.  If ``None``, a fresh fetch
            is performed.
        """
        timestamp = datetime.now().isoformat()

        if data is None:
            try:
                data = await self._get("/api/data")
            except CrucixUnavailableError:
                return {
                    "error": "Crucix service unavailable",
                    "data_source": "crucix_bridge",
                    "status": "unavailable",
                    "timestamp": timestamp,
                }

        threats: List[Dict[str, Any]] = []

        # Cyber threats from CISA-KEV
        cisa_data = data.get("sources", {}).get("CISA-KEV", {})
        if isinstance(cisa_data, dict):
            cisa_signals = cisa_data.get("signals", [])
            for signal in cisa_signals:
                threats.append({
                    "type": "cyber",
                    "severity": signal.get("severity", "unknown"),
                    "description": signal.get("signal", ""),
                    "source": "CISA-KEV",
                })

        # Geopolitical threats from GDELT
        gdelt_data = data.get("sources", {}).get("GDELT", {})
        if isinstance(gdelt_data, dict):
            conflict_count = len(gdelt_data.get("conflicts", []))
            crisis_count = len(gdelt_data.get("crisis", []))
            if conflict_count > 0:
                threats.append({
                    "type": "geopolitical_conflict",
                    "severity": "high" if conflict_count > 10 else "medium",
                    "description": f"{conflict_count} conflict-related articles detected",
                    "source": "GDELT",
                })
            if crisis_count > 0:
                threats.append({
                    "type": "geopolitical_crisis",
                    "severity": "high" if crisis_count > 5 else "medium",
                    "description": f"{crisis_count} crisis-related articles detected",
                    "source": "GDELT",
                })

        # Sanctions from OFAC
        ofac_data = data.get("sources", {}).get("OFAC", {})
        if isinstance(ofac_data, dict):
            sdn_entries = ofac_data.get("sampleEntries", [])
            if sdn_entries:
                threats.append({
                    "type": "sanctions",
                    "severity": "medium",
                    "description": f"{len(sdn_entries)} recent OFAC SDN entries",
                    "source": "OFAC",
                })

        # Delta direction from Crucix
        delta = data.get("delta", {})
        delta_direction = "unknown"
        if isinstance(delta, dict):
            summary = delta.get("summary", {})
            if isinstance(summary, dict):
                delta_direction = summary.get("direction", "unknown")

        # Compute overall threat level
        critical_count = sum(1 for t in threats if t.get("severity") == "critical")
        high_count = sum(1 for t in threats if t.get("severity") == "high")
        if critical_count > 0:
            overall_level = "critical"
        elif high_count > 2:
            overall_level = "high"
        elif high_count > 0:
            overall_level = "elevated"
        else:
            overall_level = "low"

        return {
            "threat_count": len(threats),
            "threat_level": overall_level,
            "threats": threats,
            "delta_direction": delta_direction,
            "data_source": "crucix_threat_analysis",
            "timestamp": timestamp,
        }

    async def get_geopolitical_risk(self, region: str = "global") -> Dict[str, Any]:
        """Get geopolitical risk score for a specific region.

        Uses GDELT conflict/crisis data and ACLED armed-conflict
        events to compute a 0–100 risk score.

        Parameters
        ----------
        region : str
            Region name (e.g. ``"global"``, ``"middle_east"``,
            ``"europe"``, ``"asia"``).
        """
        timestamp = datetime.now().isoformat()

        try:
            data = await self._get("/api/data")
        except CrucixUnavailableError:
            return {
                "region": region,
                "risk_score": 0,
                "error": "Crucix service unavailable",
                "data_source": "crucix_bridge",
                "status": "unavailable",
                "timestamp": timestamp,
            }

        gdelt = data.get("sources", {}).get("GDELT", {})
        acled = data.get("sources", {}).get("ACLED", {})

        # Base risk from GDELT conflict/crisis counts
        conflict_count = 0
        crisis_count = 0
        if isinstance(gdelt, dict):
            conflict_count = len(gdelt.get("conflicts", []))
            crisis_count = len(gdelt.get("crisis", []))

        # ACLED events
        acled_events = 0
        if isinstance(acled, dict):
            acled_events = acled.get("totalEvents", 0)
            if isinstance(acled_events, dict):
                acled_events = 0

        # Region keyword filter (simplified)
        region_keywords: Dict[str, List[str]] = {
            "middle_east": ["iran", "israel", "syria", "yemen", "gaza", "lebanon", "iraq"],
            "europe":      ["ukraine", "russia", "nato", "eu", "europe"],
            "asia":        ["china", "taiwan", "korea", "japan", "india", "pakistan"],
            "africa":      ["sudan", "ethiopia", "somalia", "congo", "nigeria"],
        }
        keywords = region_keywords.get(region.lower(), [])

        # Filter articles by region keywords if not global
        regional_conflict_count = conflict_count
        regional_crisis_count = crisis_count
        if keywords and isinstance(gdelt, dict):
            all_articles = gdelt.get("allArticles", [])
            regional_articles = [
                a for a in all_articles
                if any(kw in (a.get("title", "") or "").lower() for kw in keywords)
            ]
            regional_conflict_count = sum(
                1 for a in regional_articles
                if any(kw in (a.get("title", "") or "").lower()
                       for kw in ["military", "conflict", "war", "attack", "troops"])
            )
            regional_crisis_count = sum(
                1 for a in regional_articles
                if any(kw in (a.get("title", "") or "").lower()
                       for kw in ["crisis", "disaster", "emergency", "refugee"])
            )

        # Risk score computation (0-100)
        risk_score = min(100, (
            regional_conflict_count * 3
            + regional_crisis_count * 2
            + min(acled_events, 50) * 0.5
        ))

        # Classify
        if risk_score >= 75:
            level = "critical"
        elif risk_score >= 50:
            level = "high"
        elif risk_score >= 25:
            level = "elevated"
        else:
            level = "low"

        # Delta direction
        delta = data.get("delta", {})
        delta_direction = "unknown"
        if isinstance(delta, dict):
            summary = delta.get("summary", {})
            if isinstance(summary, dict):
                delta_direction = summary.get("direction", "unknown")

        return {
            "region": region,
            "risk_score": round(risk_score, 1),
            "risk_level": level,
            "conflict_articles": regional_conflict_count,
            "crisis_articles": regional_crisis_count,
            "acled_events": acled_events,
            "delta_direction": delta_direction,
            "data_source": "crucix_geopolitical_risk",
            "timestamp": timestamp,
        }

    async def get_supply_chain_risk(self, commodity: str = "general") -> Dict[str, Any]:
        """Get supply-chain risk analysis for a commodity.

        Uses GSCPI (Global Supply Chain Pressure Index), EIA energy
        data, and Comtrade trade-flow data.

        Parameters
        ----------
        commodity : str
            Commodity category (e.g. ``"oil"``, ``"gas"``, ``"semiconductor"``,
            ``"general"``).
        """
        timestamp = datetime.now().isoformat()

        try:
            data = await self._get("/api/data")
        except CrucixUnavailableError:
            return {
                "commodity": commodity,
                "risk_score": 0,
                "error": "Crucix service unavailable",
                "data_source": "crucix_bridge",
                "status": "unavailable",
                "timestamp": timestamp,
            }

        # Extract relevant source data
        gscpi_data = data.get("sources", {}).get("GSCPI", {})
        eia_data = data.get("sources", {}).get("EIA", {})
        comtrade_data = data.get("sources", {}).get("Comtrade", {})
        energy_data = data.get("energy", {})
        metals_data = data.get("metals", {})

        # GSCPI pressure index
        gscpi_value = 0.0
        gscpi_trend = "stable"
        if isinstance(gscpi_data, dict):
            gscpi_value = gscpi_data.get("value", 0.0)
            if isinstance(gscpi_value, str):
                try:
                    gscpi_value = float(gscpi_value)
                except ValueError:
                    gscpi_value = 0.0
            gscpi_trend = gscpi_data.get("trend", "stable")

        # Energy prices
        wti = energy_data.get("wti")
        brent = energy_data.get("brent")
        natgas = energy_data.get("natgas")

        # Commodity-specific scoring
        risk_factors: List[Dict[str, Any]] = []

        if gscpi_value > 1.0:
            risk_factors.append({
                "factor": "high_supply_chain_pressure",
                "value": gscpi_value,
                "severity": "high",
            })
        elif gscpi_value > 0.5:
            risk_factors.append({
                "factor": "elevated_supply_chain_pressure",
                "value": gscpi_value,
                "severity": "medium",
            })

        # Commodity-specific logic
        if commodity in ("oil", "energy"):
            if wti and isinstance(wti, (int, float)) and wti > 90:
                risk_factors.append({
                    "factor": "high_oil_price",
                    "value": wti,
                    "severity": "medium",
                })
        elif commodity in ("gas", "natural_gas"):
            if natgas and isinstance(natgas, (int, float)) and natgas > 5:
                risk_factors.append({
                    "factor": "high_natgas_price",
                    "value": natgas,
                    "severity": "high",
                })
        elif commodity in ("gold", "metals"):
            gold = metals_data.get("gold")
            if gold and isinstance(gold, (int, float)):
                risk_factors.append({
                    "factor": "gold_price",
                    "value": gold,
                    "severity": "low",
                })

        # Overall risk score (0–100)
        severity_scores = {"critical": 40, "high": 25, "medium": 15, "low": 5}
        risk_score = min(100, sum(severity_scores.get(f.get("severity", "low"), 5) for f in risk_factors))

        if risk_score >= 75:
            level = "critical"
        elif risk_score >= 50:
            level = "high"
        elif risk_score >= 25:
            level = "elevated"
        else:
            level = "low"

        return {
            "commodity": commodity,
            "risk_score": round(risk_score, 1),
            "risk_level": level,
            "gscpi_value": gscpi_value,
            "gscpi_trend": gscpi_trend,
            "energy": {"wti": wti, "brent": brent, "natgas": natgas},
            "metals": metals_data,
            "risk_factors": risk_factors,
            "data_source": "crucix_supply_chain_risk",
            "timestamp": timestamp,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _search_gdelt(self, query: str) -> Dict[str, Any]:
        """Search GDELT via the Crucix data pipeline.

        Returns raw GDELT data if available, or an empty dict.
        """
        try:
            data = await self._get("/api/data")
            gdelt = data.get("sources", {}).get("GDELT", {})

            if not isinstance(gdelt, dict):
                return {}

            # Filter articles matching query
            all_articles = gdelt.get("allArticles", [])
            query_lower = query.lower()
            matching = [
                a for a in all_articles
                if query_lower in (a.get("title", "") or "").lower()
            ][:20]

            return {
                "query": query,
                "total_articles": len(all_articles),
                "matching_articles": len(matching),
                "articles": matching,
                "data_source": "crucix_gdelt",
            }
        except CrucixUnavailableError:
            return {"query": query, "error": "service_unavailable", "data_source": "crucix_bridge"}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()
        logger.info("crucix_bridge_closed")
