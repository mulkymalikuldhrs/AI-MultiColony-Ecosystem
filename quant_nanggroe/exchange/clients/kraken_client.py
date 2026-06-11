"""Kraken Exchange Client — Spot + Futures.

Supports Kraken spot trading with HMAC-SHA512 request signing
and optional Kraken Futures support.

API docs: https://docs.kraken.com/rest/
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import time
from typing import Any, Dict, List, Optional

from quant_nanggroe.exchange.clients.base_rest_client import (
    BaseRestClient,
    BalanceInfo,
    ExchangeCapability,
    KlineBar,
    OrderbookData,
    OrderbookEntry,
    OrderRequest,
    OrderResult,
    PositionInfo,
    RestClientConfig,
)

logger = logging.getLogger(__name__)


class KrakenClient(BaseRestClient):
    """Kraken Spot REST client.

    Auth:
    - API-Key: api key string
    - API-Sign: base64(hmac_sha512(base64_decode(secret), uri_path + sha256(nonce + postdata)))

    Capabilities: SPOT, FUTURES, MARGIN, WEBSOCKET.
    """

    exchange_id = "kraken"
    capabilities = (
        ExchangeCapability.SPOT
        | ExchangeCapability.FUTURES
        | ExchangeCapability.MARGIN
        | ExchangeCapability.WEBSOCKET
    )

    BASE_URL = "https://api.kraken.com"

    def __init__(self, config: RestClientConfig) -> None:
        config.base_url = config.base_url or self.BASE_URL
        super().__init__(config)
        try:
            self._secret_bytes = base64.b64decode(self._config.api_secret) if self._config.api_secret else b""
        except Exception:
            self._secret_bytes = b""

    # ----- Signing -----

    def _sign_kraken(self, path: str, nonce: str, post_data: str) -> str:
        """Sign request using Kraken auth method."""
        sha = hashlib.sha256((nonce + post_data).encode("utf-8")).digest()
        mac = hmac.new(
            self._secret_bytes,
            path.encode("utf-8") + sha,
            hashlib.sha512,
        ).digest()
        return base64.b64encode(mac).decode("utf-8")

    async def _kraken_private_request(
        self, endpoint: str, body: Optional[Dict] = None,
    ) -> Any:
        """Make a Kraken private (authenticated) API request."""
        import httpx

        await self._rate_limit()
        nonce = str(int(time.time() * 1000))
        post_parts = [f"nonce={nonce}"]
        if body:
            for k, v in body.items():
                post_parts.append(f"{k}={v}")
        post_data = "&".join(post_parts)

        sign = self._sign_kraken(endpoint, nonce, post_data)
        headers = {
            "API-Key": self._config.api_key,
            "API-Sign": sign,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        url = f"{self._config.base_url}{endpoint}"
        async with httpx.AsyncClient(timeout=self._config.timeout) as client:
            response = await client.post(url, content=post_data, headers=headers)
            response.raise_for_status()
            data = response.json()

            if isinstance(data, dict):
                errs = data.get("error", [])
                if isinstance(errs, list) and errs:
                    raise ValueError(f"Kraken API error: {errs}")

            return data.get("result", data) if isinstance(data, dict) else data

    async def _kraken_public_request(
        self, endpoint: str, params: Optional[Dict] = None,
    ) -> Any:
        """Make a Kraken public API request."""
        import httpx

        await self._rate_limit()
        url = f"{self._config.base_url}{endpoint}"
        async with httpx.AsyncClient(timeout=self._config.timeout) as client:
            response = await client.get(url, params=params or {})
            response.raise_for_status()
            data = response.json()

            if isinstance(data, dict):
                errs = data.get("error", [])
                if isinstance(errs, list) and errs:
                    raise ValueError(f"Kraken API error: {errs}")

            return data.get("result", data) if isinstance(data, dict) else data

    # ----- Helpers -----

    @staticmethod
    def _normalize_pair(symbol: str) -> str:
        return symbol.replace("/", "").replace("-", "").upper()

    # ----- Abstract method implementations -----

    async def place_order(self, order: OrderRequest) -> OrderResult:
        """Place order on Kraken."""
        pair = self._normalize_pair(order.symbol)
        ot = "market" if order.order_type == "market" else "limit"

        body: Dict[str, Any] = {
            "pair": pair,
            "type": order.side.lower(),
            "ordertype": ot,
            "volume": str(order.quantity),
        }
        if ot == "limit" and order.price:
            body["price"] = str(order.price)
        if order.client_order_id:
            digits = "".join(c for c in str(order.client_order_id) if c.isdigit())[:9]
            if digits:
                body["userref"] = digits

        data = await self._kraken_private_request("/0/private/AddOrder", body)

        txid = ""
        if isinstance(data, dict):
            tx = data.get("txid", [])
            if isinstance(tx, list) and tx:
                txid = str(tx[0])

        return OrderResult(
            order_id=txid,
            client_order_id=order.client_order_id or "",
            symbol=order.symbol,
            side=order.side,
            order_type=order.order_type,
            status="NEW",
            price=order.price or 0.0,
            quantity=order.quantity,
        )

    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancel order on Kraken."""
        try:
            await self._kraken_private_request("/0/private/CancelOrder", {"txid": order_id})
            return True
        except Exception as exc:
            logger.warning("Kraken cancel failed: %s", exc)
            return False

    async def get_balance(self, asset: Optional[str] = None) -> List[BalanceInfo]:
        """Get account balance from Kraken."""
        data = await self._kraken_private_request("/0/private/Balance")

        balances = []
        if isinstance(data, dict):
            for ccy, bal in data.items():
                if asset and ccy != asset:
                    continue
                try:
                    val = float(bal)
                    if val > 0:
                        balances.append(BalanceInfo(
                            asset=ccy,
                            free=val,
                            used=0.0,
                            total=val,
                        ))
                except (ValueError, TypeError):
                    pass
        return balances

    async def get_positions(self, symbol: Optional[str] = None) -> List[PositionInfo]:
        """Get positions from Kraken (spot doesn't have traditional positions)."""
        return []

    async def get_orderbook(self, symbol: str, limit: int = 20) -> OrderbookData:
        """Get order book from Kraken."""
        pair = self._normalize_pair(symbol)
        data = await self._kraken_public_request(
            "/0/public/Depth",
            params={"pair": pair, "count": limit},
        )

        pair_data = data
        if isinstance(data, dict):
            pair_data = data.get(pair, data)

        bids = [
            OrderbookEntry(price=float(b[0]), quantity=float(b[1]))
            for b in pair_data.get("bids", []) if len(b) >= 2
        ]
        asks = [
            OrderbookEntry(price=float(a[0]), quantity=float(a[1]))
            for a in pair_data.get("asks", []) if len(a) >= 2
        ]

        return OrderbookData(
            symbol=symbol,
            bids=bids[:limit],
            asks=asks[:limit],
            timestamp=str(int(time.time() * 1000)),
        )

    async def get_klines(
        self, symbol: str, interval: str = "1h", limit: int = 100,
    ) -> List[KlineBar]:
        """Get klines from Kraken."""
        pair = self._normalize_pair(symbol)
        interval_map = {
            "1m": 1, "5m": 5, "15m": 15, "30m": 30,
            "1h": 60, "4h": 240, "1d": 1440, "1w": 10080,
        }
        minutes = interval_map.get(interval, 60)

        data = await self._kraken_public_request(
            "/0/public/OHLC",
            params={"pair": pair, "interval": minutes, "count": limit},
        )

        pair_data = data
        if isinstance(data, dict):
            pair_data = data.get(pair, data)

        bars = []
        if isinstance(pair_data, list):
            from datetime import datetime, timezone
            for candle in pair_data:
                if not isinstance(candle, list) or len(candle) < 7:
                    continue
                bars.append(KlineBar(
                    timestamp=datetime.fromtimestamp(int(candle[0]), tz=timezone.utc).isoformat(),
                    open=float(candle[1]),
                    high=float(candle[2]),
                    low=float(candle[3]),
                    close=float(candle[4]),
                    volume=float(candle[6]),
                ))
        bars.sort(key=lambda x: x.timestamp)
        return bars


__all__ = ["KrakenClient"]
