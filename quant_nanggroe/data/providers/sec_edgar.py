"""SEC EDGAR data provider for US public company filings and financials.

Implements the DataProvider interface for the SEC EDGAR REST API.
Provides access to 10-K, 10-Q, 8-K filings, financial statements,
insider transactions, and company facts.

SEC EDGAR API is free and requires no API key, but is rate limited
to 10 requests per second. A User-Agent header with contact email
is required.

Symbol convention: Standard ticker symbols (e.g., 'AAPL', 'MSFT').
The provider resolves tickers to CIK (Central Index Key) internally.
"""

from __future__ import annotations

import asyncio
import logging
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

from quant_nanggroe.data.providers.base import DataProvider
from quant_nanggroe.types.market import OHLCV, OrderBook, Ticker, TimeFrame

logger = logging.getLogger(__name__)

# SEC EDGAR API endpoints
EDGAR_BASE_URL = "https://efts.sec.gov/LATEST/search-index?q="
EDGAR_FILINGS_URL = "https://efts.sec.gov/LATEST/search-index"
EDGAR_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts"
EDGAR_SUBMISSIONS_URL = "https://data.sec.gov/submissions"
EDGAR_COMPANY_SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"

# Rate limiter: max 10 requests per second for SEC EDGAR
_RATE_LIMIT_INTERVAL = 0.1  # 100ms between requests = 10 req/s


class SECEdgarError(Exception):
    """SEC EDGAR API error."""


class SECEdgarProvider(DataProvider):
    """SEC EDGAR data provider for US public company filings and financials.

    Provides access to:
    - Company financial facts (XBRL taxonomy)
    - 10-K, 10-Q, 8-K filings
    - Insider transactions (Form 3, 4, 5)
    - Company submissions and metadata

    No API key required. Rate limited to 10 req/s.
    User-Agent header with contact email is required by SEC.

    Example:
        >>> provider = SECEdgarProvider(user_email="dev@example.com")
        >>> fundamentals = await provider.get_fundamentals("AAPL")
        >>> filings = await provider.get_filings("AAPL", filing_type="10-K")
    """

    def __init__(
        self,
        user_email: Optional[str] = None,
        user_name: str = "QuantNanggroeAI",
        priority: int = 35,
        **kwargs,
    ):
        """Initialize SEC EDGAR provider.

        Args:
            user_email: Contact email for SEC User-Agent header.
                        Falls back to QNAI_SEC_USER_EMAIL env var.
                        Required by SEC API usage policy.
            user_name: Organization or user name for User-Agent.
            priority: Failover priority (lower = higher priority). Default 35
                      (fundamental data, lower priority than real-time data).
        """
        super().__init__(name="sec_edgar", priority=priority, **kwargs)
        self._user_email = user_email
        self._user_name = user_name
        self._client: Optional[httpx.AsyncClient] = None
        self._cik_cache: Dict[str, str] = {}  # ticker -> CIK
        self._last_request_time: float = 0.0

    def _get_user_email(self) -> str:
        """Get contact email for User-Agent header."""
        email = self._user_email
        if not email:
            import os
            email = os.environ.get("QNAI_SEC_USER_EMAIL", "")
        if not email:
            email = "dev@quant-nanggroe.local"
        return email

    def _get_user_agent(self) -> str:
        """Build User-Agent header value as required by SEC."""
        return f"{self._user_name}/{self._get_user_email()}"

    def _get_client(self) -> httpx.AsyncClient:
        """Lazy-initialize the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                headers={"User-Agent": self._get_user_agent()},
            )
        return self._client

    async def _rate_limited_request(self, url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a rate-limited request to SEC EDGAR.

        Enforces 10 req/s rate limit.

        Args:
            url: Full URL to request.
            params: Optional query parameters.

        Returns:
            Parsed JSON response.

        Raises:
            SECEdgarError: On API errors.
        """
        # Rate limiting
        elapsed = time.monotonic() - self._last_request_time
        if elapsed < _RATE_LIMIT_INTERVAL:
            await asyncio.sleep(_RATE_LIMIT_INTERVAL - elapsed)

        client = self._get_client()

        try:
            self._last_request_time = time.monotonic()
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            self.mark_error(f"SEC EDGAR API error: {e.response.status_code}")
            raise SECEdgarError(
                f"SEC EDGAR returned {e.response.status_code}"
            ) from e
        except httpx.RequestError as e:
            self.mark_error(f"SEC EDGAR request error: {e}")
            raise SECEdgarError(f"SEC EDGAR request failed: {e}") from e

    async def _resolve_cik(self, ticker: str) -> Optional[str]:
        """Resolve a ticker symbol to a CIK number.

        Uses the SEC company ticker map for resolution.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL').

        Returns:
            CIK number as a zero-padded 10-digit string, or None.
        """
        if ticker.upper() in self._cik_cache:
            return self._cik_cache[ticker.upper()]

        try:
            url = "https://www.sec.gov/files/company_tickers.json"
            data = await self._rate_limited_request(url)

            # Build cache from the full ticker map
            for _key, entry in data.items():
                t = entry.get("ticker", "").upper()
                cik = str(entry.get("cik_str", "")).zfill(10)
                if t:
                    self._cik_cache[t] = cik

            return self._cik_cache.get(ticker.upper())

        except Exception as e:
            logger.warning(f"Failed to resolve CIK for {ticker}: {e}")
            return None

    async def get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Fetch company financial facts from SEC EDGAR XBRL data.

        Provides standardized financial data from 10-K and 10-Q filings
        organized by XBRL taxonomy (GAAP and IFRS).

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL').

        Returns:
            Dict with company facts organized by taxonomy and concept.
            Structure: {'us-gaap': {concept: {units: {unit: [facts]}}}}
        """
        try:
            cik = await self._resolve_cik(symbol)
            if not cik:
                self.mark_error(f"Could not resolve CIK for {symbol}")
                return {}

            url = f"{EDGAR_FACTS_URL}/CIK{cik}.json"
            data = await self._rate_limited_request(url)

            facts = data.get("facts", {})
            self.mark_success()
            return facts

        except SECEdgarError:
            return {}
        except Exception as e:
            self.mark_error(str(e))
            logger.warning(f"SEC EDGAR fundamentals error for {symbol}: {e}")
            return {}

    async def get_filings(
        self,
        symbol: str,
        filing_type: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Fetch SEC filings for a company.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL').
            filing_type: Filing type filter (e.g., '10-K', '10-Q', '8-K',
                         '3', '4', '5' for insider transactions).
            start: Start date filter.
            end: End date filter.
            limit: Maximum number of filings to return.

        Returns:
            List of filing dicts with keys: accession_number, filing_date,
            form, file_number, primary_document, etc.
        """
        try:
            cik = await self._resolve_cik(symbol)
            if not cik:
                self.mark_error(f"Could not resolve CIK for {symbol}")
                return []

            url = f"{EDGAR_SUBMISSIONS_URL}/CIK{cik}.json"
            data = await self._rate_limited_request(url)

            recent = data.get("filings", {}).get("recent", {})

            forms = recent.get("form", [])
            dates = recent.get("filingDate", [])
            accession_numbers = recent.get("accessionNumber", [])
            primary_docs = recent.get("primaryDocument", [])
            descriptions = recent.get("primaryDocDescription", [])

            result = []
            for i in range(len(forms)):
                form = forms[i] if i < len(forms) else ""
                date_str = dates[i] if i < len(dates) else ""

                # Filter by filing type
                if filing_type and form != filing_type:
                    continue

                # Filter by date range
                if start or end:
                    try:
                        filing_date = datetime.strptime(date_str, "%Y-%m-%d")
                        if start and filing_date < start:
                            continue
                        if end and filing_date > end:
                            continue
                    except ValueError:
                        continue

                result.append({
                    "accession_number": accession_numbers[i] if i < len(accession_numbers) else "",
                    "filing_date": date_str,
                    "form": form,
                    "primary_document": primary_docs[i] if i < len(primary_docs) else "",
                    "description": descriptions[i] if i < len(descriptions) else "",
                    "cik": cik,
                })

                if len(result) >= limit:
                    break

            self.mark_success()
            return result

        except SECEdgarError:
            return []
        except Exception as e:
            self.mark_error(str(e))
            logger.warning(f"SEC EDGAR filings error for {symbol}: {e}")
            return []

    async def get_insider_transactions(
        self,
        symbol: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Fetch insider transactions (Forms 3, 4, 5).

        Args:
            symbol: Stock ticker symbol.
            limit: Maximum number of transactions to return.

        Returns:
            List of insider transaction dicts.
        """
        try:
            # Fetch Forms 3, 4, 5 filings
            all_transactions = []

            for form_type in ["3", "4", "5"]:
                filings = await self.get_filings(
                    symbol, filing_type=form_type, limit=limit
                )
                all_transactions.extend(filings)

            self.mark_success()
            return all_transactions[:limit]

        except Exception as e:
            self.mark_error(str(e))
            logger.warning(f"SEC EDGAR insider transactions error for {symbol}: {e}")
            return []

    async def get_financial_statements(
        self,
        symbol: str,
        statement_type: str = "income_statement",
        period: str = "annual",
    ) -> Dict[str, Any]:
        """Fetch parsed financial statements from XBRL data.

        Args:
            symbol: Stock ticker symbol.
            statement_type: One of 'income_statement', 'balance_sheet',
                            'cash_flow', 'equity_statement'.
            period: 'annual' or 'quarterly'.

        Returns:
            Dict with financial statement data.
        """
        try:
            facts = await self.get_fundamentals(symbol)
            if not facts:
                return {}

            gaap = facts.get("us-gaap", {})

            # Map statement types to XBRL concepts
            concept_map = {
                "income_statement": [
                    "Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax",
                    "CostOfRevenue", "GrossProfit", "OperatingExpenses",
                    "OperatingIncomeLoss", "NetIncomeLoss", "EarningsPerShareBasic",
                ],
                "balance_sheet": [
                    "Assets", "CurrentAssets", "CashAndCashEquivalentsAtCarryingValue",
                    "Liabilities", "CurrentLiabilities", "StockholdersEquity",
                    "LongTermDebt", "InventoryNet",
                ],
                "cash_flow": [
                    "NetCashProvidedByUsedInOperatingActivities",
                    "NetCashProvidedByUsedInInvestingActivities",
                    "NetCashProvidedByUsedInFinancingActivities",
                    "CashAndCashEquivalentsPeriodIncreaseDecrease",
                ],
            }

            concepts = concept_map.get(statement_type, [])
            result: Dict[str, Any] = {}

            for concept in concepts:
                if concept in gaap:
                    units_data = gaap[concept].get("units", {})
                    for unit_type, entries in units_data.items():
                        # Filter by period
                        if period == "annual":
                            entries = [e for e in entries if e.get("form") == "10-K"]
                        elif period == "quarterly":
                            entries = [e for e in entries if e.get("form") == "10-Q"]

                        if entries:
                            # Sort by filing date, most recent first
                            entries.sort(key=lambda x: x.get("filed", ""), reverse=True)
                            result[concept] = entries[:4]  # Last 4 periods

            self.mark_success()
            return result

        except Exception as e:
            self.mark_error(str(e))
            logger.warning(f"SEC EDGAR financial statements error for {symbol}: {e}")
            return {}

    # ─── DataProvider interface methods ───────────────────────────────────

    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: TimeFrame = TimeFrame.D1,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 500,
    ) -> List[OHLCV]:
        """SEC EDGAR does not provide OHLCV market data.

        This method returns an empty list. Use YahooFinanceProvider or
        AlpacaProvider for market price data.
        """
        logger.debug("SEC EDGAR does not provide OHLCV data")
        return []

    async def get_ticker(self, symbol: str) -> Optional[Ticker]:
        """SEC EDGAR does not provide ticker/quote data.

        Returns None. Use market data providers for real-time quotes.
        """
        logger.debug("SEC EDGAR does not provide ticker data")
        return None

    async def get_orderbook(self, symbol: str, limit: int = 20) -> Optional[OrderBook]:
        """SEC EDGAR does not support order book data."""
        logger.debug("SEC EDGAR does not support order book data")
        return None

    async def health_check(self) -> bool:
        """Check if the SEC EDGAR API is accessible.

        Returns:
            True if the API responds successfully.
        """
        try:
            url = "https://www.sec.gov/files/company_tickers.json"
            await self._rate_limited_request(url)
            self._is_available = True
            return True
        except Exception as e:
            self._is_available = False
            self._last_error = str(e)
            return False

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
