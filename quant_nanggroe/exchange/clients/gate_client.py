"""Gate.io Exchange Client — V4 API (Spot + USDT Futures).

Supports Gate.io V4 API with HMAC-SHA512 request signing
for both spot and USDT-margined perpetual markets.

API docs: https://www.gate.io/docs/developers/apiv4/
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

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


class GateClient(BaseRestClient):
    """Gate.io V4 REST client for spot and USDT futures.

    Signing (V4):
    SIGN = hex(hmac_sha512(secret, method + "\\n" + url + "\\n" + query + "\\n" + body + "\\n" + timestamp))

    Capabilities: SPOT, FUTURES, PERPETUALS, MARGIN, WEBSOCKET.
    """

    exchange_id = "gate"
    capabilities = (
        ExchangeCapability.SPOT
        | ExchangeCapability.FUTURES
        | ExchangeCapability.PERPETUALS
        | ExchangeCapability.MARGIN
        | ExchangeCapability.WEBSOCKET
    )

    BASE_URL = "https://api.gateio.ws"

    def __init__(self, config: RestClientConfig) -> None:
        config.base_url = config.base_url or self.BASE_URL
        super().__init__(config)
        self._market_type = "spot"

    # ----- Signing -----

    def _sign_gate(self, method: str, path: str, qs: str = "", body: str = "") -> Dict[str, str]:
        """Sign request using Gate.io V4 auth method."""
        ts = str(int(time.time()))
        msg = f"{method.upper()}\n{path}\n{qs}\n{body}\n{ts}"
        sign = hmac.new(
            self._config.api_secret.encode("utf-8"),
            msg.encode("utf-8"),
            hashlib.sha512,
        ).hexdigest()

        return {
            "KEY": self._config.api_key,
            "Timestamp": ts,
            "SIGN": sign,
            "Content-Type": "application/json",
        }

    async def _gate_request(
        self, method: str, endpoint: str, params: Optional[Dict] = None,
        body: Optional[Dict] = None, signed: bool = False,
    ) -> Any:
        """Make a Gate.io V4 API request."""
        import httpx
        import json

        await self._rate_limit()
        params = params or {}
        url = f"{self._config.base_url}{endpoint}"

        headers: Dict[str, str] = {"Content-Type": "application/json"}
        request_body = json.dumps(body) if body else ""

        if method.upper() == "GET":
            qs = urlencode(sorted(params.items())) if params else ""
            if signed and self._config.api_key:
                headers = self._sign_gate("GET", endpoint, qs=qs)
            async with httpx.AsyncClient(timeout=self._config.timeout) as client:
                response = await client.get(url, params=params, headers=headers)
        else:
            if signed and self._config.api_key:
                headers = self._sign_gate("POST", endpoint, body=request_body)
            async with httpx.AsyncClient(timeout=self._config.timeout) as client:
                response = await client.post(url, content=request_body, headers=headers)

        response.raise_for_status()
        return response.json()

    # ----- Helpers -----

    @staticmethod
    def _normalize_currency_pair(symbol: str) -> str:
        return symbol.replace("/", "_").replace("-", "_").upper()

    # ----- Abstract method implementations -----

    async def place_order(self, order: OrderRequest) -> OrderResult:
        """Place order on Gate.io (spot)."""
        pair = self._normalize_currency_pair(order.symbol)

        body: Dict[str, Any] = {
            "currency_pair": pair,
            "side": order.side.lower(),
            "type": "market" if order.order_type == "market" else "limit",
            "amount": str(order.quantity),
        }
        if order.order_type == "limit" and order.price:
            body["price"] = str(order.price)
            body["time_in_force"] = "gtc"
        if order.client_order_id:
            body["text"] = str(order.client_order_id)

        data = await self._gate_request("POST", "/api/v4/spot/orders", body=body, signed=True)

        order_id = str(data.get("id", "")) if isinstance(data, dict) else ""

        return OrderResult(
            order_id=order_id,
            client_order_id=order.client_order_id or "",
            symbol=order.symbol,
            side=order.side,
            order_type=order.order_type,
            status=str(data.get("status", "NEW")),
            price=float(data.get("price", 0) or order.price or 0),
            quantity=order.quantity,
        )

    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancel order on Gate.io."""
        try:
            await self._gate_request("DELETE", f"/api/v4/spot/orders/{order_id}", signed=True)
            return True
        except Exception as exc:
            logger.warning("Gate cancel failed: %s", exc)
            return False

    async def get_balance(self, asset: Optional[str] = None) -> List[BalanceInfo]:
        """Get account balance from Gate.io."""
        data = await self._gate_request("GET", "/api/v4/spot/accounts", signed=True)

        balances = []
        if isinstance(data, list):
            for acct in data:
                if not isinstance(acct, dict):
                    continue
                ccy = str(acct.get("currency", ""))
                if asset and ccy != asset:
                    continue
                free = float(acct.get("available", 0) or 0)
                used = float(acct.get("locked", 0) or 0)
                if free > 0 or used > 0:
                    balances.append(BalanceInfo(
                        asset=ccy,
                        free=free,
                        used=used,
                        total=free + used,
                    ))
        return balances

    async def get_positions(self, symbol: Optional[str] = None) -> List[PositionInfo]:
        """Get positions from Gate.io futures."""
        try:
            data = await self._gate_request("GET", "/api/v4/futures/usdt/positions", signed=True)

            positions = []
            if isinstance(data, list):
                for p in data:
                    if not isinstance(p, dict):
                        continue
                    qty = float(p.get("size", 0))
                    if qty == 0:
                        continue
                    positions.append(PositionInfo(
                        symbol=str(p.get("contract", "")),
                        side="LONG" if qty > 0 else "SHORT",
                        quantity=abs(qty),
                        entry_price=float(p.get("entry_price", 0)),
                        unrealized_pnl=float(p.get("unrealised_pnl", 0)),
                        leverage=1,
                        liquidation_price=0.0,
                    ))
            return positions
        except Exception:
            return []

    async def get_orderbook(self, symbol: str, limit: int = 20) -> OrderbookData:
        """Get order book from Gate.io."""
        pair = self._normalize_currency_pair(symbol)
        data = await self._gate_request(
            "GET", "/api/v4/spot/order_book",
            params={"currency_pair": pair, "limit": limit},
            signed=False,
        )

        bids = [
            OrderbookEntry(price=float(b[0]), quantity=float(b[1]))
            for b in data.get("bids", []) if len(b) >= 2
        ]
        asks = [
            OrderbookEntry(price=float(a[0]), quantity=float(a[1]))
            for a in data.get("asks", []) if len(a) >= 2
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
        """Get klines from Gate.io."""
        pair = self._normalize_currency_pair(symbol)
        data = await self._gate_request(
            "GET", "/api/v4/spot/candlesticks",
            params={"currency_pair": pair, "interval": interval, "limit": limit},
            signed=False,
        )

        bars = []
        if isinstance(data, list):
            from datetime import datetime, timezone
            for candle in data:
                if not isinstance(candle, dict):
                    continue
                ts = int(candle.get("t", candle.get("timestamp", 0)))
                bars.append(KlineBar(
                    timestamp=datetime.fromtimestamp(ts, tz=timezone.utc).isoformat() if ts > 0 else "",
                    open=float(candle.get("o", candle.get("open", 0))),
                    high=float(candle.get("h", candle.get("high", 0))),
                    low=float(candle.get("l", candle.get("low", 0))),
                    close=float(candle.get("c", candle.get("close", 0))),
                    volume=float(candle.get("v", candle.get("volume", 0))),
                ))
        bars.sort(key=lambda x: x.timestamp)
        return bars[:limit]


__all__ = ["GateClient"]
