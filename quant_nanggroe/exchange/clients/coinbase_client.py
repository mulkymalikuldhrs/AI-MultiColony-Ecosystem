"""Coinbase Exchange Client — Coinbase Exchange (Pro/Advanced) REST API.

Supports Coinbase Exchange with HMAC-SHA256 + Base64 request signing
including passphrase.

API docs: https://docs.cloud.coinbase.com/exchange/reference/
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


class CoinbaseClient(BaseRestClient):
    """Coinbase Exchange REST client.

    Auth headers:
    - CB-ACCESS-KEY
    - CB-ACCESS-SIGN = base64(hmac_sha256(base64_decode(secret), timestamp + method + path + body))
    - CB-ACCESS-TIMESTAMP (seconds)
    - CB-ACCESS-PASSPHRASE

    Capabilities: SPOT, FUTURES, WEBSOCKET.
    """

    exchange_id = "coinbase"
    capabilities = (
        ExchangeCapability.SPOT
        | ExchangeCapability.FUTURES
        | ExchangeCapability.WEBSOCKET
    )

    BASE_URL = "https://api.exchange.coinbase.com"

    def __init__(self, config: RestClientConfig) -> None:
        config.base_url = config.base_url or self.BASE_URL
        super().__init__(config)
        try:
            self._secret_bytes = base64.b64decode(self._config.api_secret) if self._config.api_secret else b""
        except Exception:
            self._secret_bytes = b""

    # ----- Signing -----

    def _sign_coinbase(self, method: str, path: str, body: str = "") -> Dict[str, str]:
        """Sign request using Coinbase auth method."""
        ts = str(int(time.time()))
        prehash = f"{ts}{method.upper()}{path}{body}"
        mac = hmac.new(self._secret_bytes, prehash.encode("utf-8"), hashlib.sha256).digest()
        sign = base64.b64encode(mac).decode("utf-8")

        return {
            "CB-ACCESS-KEY": self._config.api_key,
            "CB-ACCESS-SIGN": sign,
            "CB-ACCESS-TIMESTAMP": ts,
            "CB-ACCESS-PASSPHRASE": self._config.passphrase,
            "Content-Type": "application/json",
        }

    async def _coinbase_request(
        self, method: str, endpoint: str, params: Optional[Dict] = None,
        body: Optional[Dict] = None, signed: bool = False,
    ) -> Any:
        """Make a Coinbase API request."""
        import httpx
        import json

        await self._rate_limit()
        params = params or {}
        url = f"{self._config.base_url}{endpoint}"

        headers: Dict[str, str] = {"Content-Type": "application/json"}
        request_body = ""

        if signed and self._config.api_key:
            if method.upper() == "GET":
                query = "&".join(f"{k}={v}" for k, v in params.items())
                path = f"{endpoint}?{query}" if query else endpoint
                headers = self._sign_coinbase("GET", path)
            else:
                request_body = json.dumps(body) if body else ""
                headers = self._sign_coinbase(method.upper(), endpoint, request_body)

        async with httpx.AsyncClient(timeout=self._config.timeout) as client:
            fn = getattr(client, method.lower())
            if method.upper() == "GET":
                response = await fn(url, params=params, headers=headers)
            else:
                response = await fn(url, content=request_body, headers=headers)
            response.raise_for_status()
            return response.json()

    # ----- Helpers -----

    @staticmethod
    def _normalize_product_id(symbol: str) -> str:
        parts = symbol.replace("-", "/").split("/")
        if len(parts) == 2:
            return f"{parts[0].upper()}-{parts[1].upper()}"
        return symbol.upper()

    # ----- Abstract method implementations -----

    async def place_order(self, order: OrderRequest) -> OrderResult:
        """Place order on Coinbase."""
        product_id = self._normalize_product_id(order.symbol)

        body: Dict[str, Any] = {
            "product_id": product_id,
            "side": order.side.lower(),
            "type": "market" if order.order_type == "market" else "limit",
            "size": str(order.quantity),
        }
        if order.order_type == "limit" and order.price:
            body["price"] = str(order.price)
            body["time_in_force"] = order.time_in_force or "GTC"
        if order.client_order_id:
            body["client_oid"] = order.client_order_id

        data = await self._coinbase_request("POST", "/orders", body=body, signed=True)

        return OrderResult(
            order_id=str(data.get("id", "")),
            client_order_id=data.get("client_oid", ""),
            symbol=order.symbol,
            side=order.side,
            order_type=order.order_type,
            status=str(data.get("status", "")),
            price=float(data.get("price", 0) or 0),
            quantity=float(data.get("size", order.quantity)),
            filled_quantity=float(data.get("filled_size", 0) or 0),
            timestamp=str(data.get("created_at", "")),
        )

    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancel order on Coinbase."""
        try:
            await self._coinbase_request("DELETE", f"/orders/{order_id}", signed=True)
            return True
        except Exception as exc:
            logger.warning("Coinbase cancel order failed: %s", exc)
            return False

    async def get_balance(self, asset: Optional[str] = None) -> List[BalanceInfo]:
        """Get account balance from Coinbase."""
        raw = await self._coinbase_request("GET", "/accounts", signed=True)

        balances = []
        if isinstance(raw, list):
            for acct in raw:
                if not isinstance(acct, dict):
                    continue
                ccy = str(acct.get("currency", ""))
                if asset and ccy != asset:
                    continue
                free = float(acct.get("available", 0))
                used = float(acct.get("hold", 0))
                if free > 0 or used > 0:
                    balances.append(BalanceInfo(
                        asset=ccy,
                        free=free,
                        used=used,
                        total=free + used,
                    ))
        return balances

    async def get_positions(self, symbol: Optional[str] = None) -> List[PositionInfo]:
        """Get positions from Coinbase (spot doesn't have traditional positions)."""
        return []

    async def get_orderbook(self, symbol: str, limit: int = 20) -> OrderbookData:
        """Get order book from Coinbase."""
        product_id = self._normalize_product_id(symbol)
        data = await self._coinbase_request(
            "GET", f"/products/{product_id}/book",
            params={"level": 2},
        )

        return OrderbookData(
            symbol=symbol,
            bids=[OrderbookEntry(price=float(b[0]), quantity=float(b[1])) for b in data.get("bids", []) if len(b) >= 2],
            asks=[OrderbookEntry(price=float(a[0]), quantity=float(a[1])) for a in data.get("asks", []) if len(a) >= 2],
            timestamp=str(int(time.time() * 1000)),
        )

    async def get_klines(
        self, symbol: str, interval: str = "1h", limit: int = 100,
    ) -> List[KlineBar]:
        """Get klines from Coinbase."""
        product_id = self._normalize_product_id(symbol)
        granularity_map = {
            "1m": 60, "5m": 300, "15m": 900, "1h": 3600,
            "6h": 21600, "1d": 86400,
        }
        granularity = granularity_map.get(interval, 3600)

        data = await self._coinbase_request(
            "GET", f"/products/{product_id}/candles",
            params={"granularity": granularity},
        )

        bars = []
        if isinstance(data, list):
            from datetime import datetime, timezone
            for candle in data:
                if not isinstance(candle, list) or len(candle) < 6:
                    continue
                bars.append(KlineBar(
                    timestamp=datetime.fromtimestamp(int(candle[0]), tz=timezone.utc).isoformat(),
                    open=float(candle[3]),
                    high=float(candle[2]),
                    low=float(candle[1]),
                    close=float(candle[4]),
                    volume=float(candle[5]),
                ))
        bars.sort(key=lambda x: x.timestamp)
        return bars[:limit]


__all__ = ["CoinbaseClient"]
