"""Bitfinex Exchange Client — V2 API (Spot + Derivatives).

Supports Bitfinex V2 API with HMAC-SHA384 request signing
for spot exchange orders and derivatives.

API docs: https://docs.bitfinex.com/docs
"""

from __future__ import annotations

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


class BitfinexClient(BaseRestClient):
    """Bitfinex V2 REST client for spot and derivatives.

    Auth headers:
    - bfx-apikey
    - bfx-nonce
    - bfx-signature = hex(hmac_sha384(secret, "/api/v2" + path + nonce + body))

    Capabilities: SPOT, FUTURES, PERPETUALS, MARGIN, WEBSOCKET.
    """

    exchange_id = "bitfinex"
    capabilities = (
        ExchangeCapability.SPOT
        | ExchangeCapability.FUTURES
        | ExchangeCapability.PERPETUALS
        | ExchangeCapability.MARGIN
        | ExchangeCapability.WEBSOCKET
    )

    BASE_URL = "https://api.bitfinex.com"

    def __init__(self, config: RestClientConfig) -> None:
        config.base_url = config.base_url or self.BASE_URL
        super().__init__(config)

    # ----- Signing -----

    def _sign_bitfinex(self, path: str, nonce: str, body: str = "") -> Dict[str, str]:
        """Sign request using Bitfinex auth method."""
        payload = f"/api/v2{path}{nonce}{body}"
        sign = hmac.new(
            self._config.api_secret.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha384,
        ).hexdigest()

        return {
            "bfx-apikey": self._config.api_key,
            "bfx-nonce": nonce,
            "bfx-signature": sign,
            "content-type": "application/json",
        }

    async def _bitfinex_public_request(
        self, endpoint: str, params: Optional[Dict] = None,
    ) -> Any:
        """Make a Bitfinex public API request."""
        import httpx

        await self._rate_limit()
        url = f"{self._config.base_url}{endpoint}"
        async with httpx.AsyncClient(timeout=self._config.timeout) as client:
            response = await client.get(url, params=params or {})
            response.raise_for_status()
            return response.json()

    async def _bitfinex_private_request(
        self, method: str, endpoint: str, body: Optional[Dict] = None,
    ) -> Any:
        """Make a Bitfinex authenticated API request."""
        import httpx
        import json

        await self._rate_limit()
        nonce = str(int(time.time() * 1000))
        request_body = json.dumps(body) if body else ""
        headers = self._sign_bitfinex(endpoint, nonce, request_body)

        url = f"{self._config.base_url}{endpoint}"
        async with httpx.AsyncClient(timeout=self._config.timeout) as client:
            if method.upper() == "POST":
                response = await client.post(url, content=request_body, headers=headers)
            else:
                response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()

    # ----- Helpers -----

    @staticmethod
    def _normalize_symbol(symbol: str) -> str:
        parts = symbol.replace("-", "/").split("/")
        if len(parts) == 2:
            base, quote = parts[0].upper(), parts[1].upper()
            return f"t{base}{quote}"
        return f"t{symbol.upper()}"

    # ----- Abstract method implementations -----

    async def place_order(self, order: OrderRequest) -> OrderResult:
        """Place order on Bitfinex."""
        sym = self._normalize_symbol(order.symbol)
        sd = order.side.lower()
        amt = order.quantity if sd == "buy" else -order.quantity

        if order.order_type == "market":
            order_type_str = "EXCHANGE MARKET"
        else:
            order_type_str = "EXCHANGE LIMIT"

        body: Dict[str, Any] = {
            "type": order_type_str,
            "symbol": sym,
            "amount": str(amt),
        }
        if order.order_type == "limit" and order.price:
            body["price"] = str(order.price)
        elif order.order_type == "market":
            body["price"] = "0"
        if order.client_order_id:
            try:
                cid = int("".join(c for c in str(order.client_order_id) if c.isdigit())[:18] or "0")
                if cid > 0:
                    body["cid"] = cid
            except Exception:
                pass

        raw = await self._bitfinex_private_request("POST", "/v2/auth/w/order/submit", body=body)

        order_id = ""
        try:
            if isinstance(raw, list) and len(raw) >= 4 and isinstance(raw[3], list) and raw[3]:
                inner = raw[3][0]
                if isinstance(inner, list) and inner:
                    order_id = str(inner[0])
        except Exception:
            order_id = ""

        return OrderResult(
            order_id=order_id,
            client_order_id=order.client_order_id or "",
            symbol=order.symbol,
            side=order.side,
            order_type=order.order_type,
            status="NEW",
            price=order.price or 0.0,
            quantity=order.quantity,
        )

    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancel order on Bitfinex."""
        try:
            oid = int(float(order_id))
            await self._bitfinex_private_request(
                "POST", "/v2/auth/w/order/cancel", body={"id": oid},
            )
            return True
        except Exception as exc:
            logger.warning("Bitfinex cancel failed: %s", exc)
            return False

    async def get_balance(self, asset: Optional[str] = None) -> List[BalanceInfo]:
        """Get account balance from Bitfinex."""
        raw = await self._bitfinex_private_request("POST", "/v2/auth/r/wallets", body={})

        balances = []
        if isinstance(raw, list):
            for w in raw:
                if isinstance(w, list) and len(w) >= 4:
                    ccy = str(w[1])
                    if asset and ccy != asset:
                        continue
                    avail = float(w[4] if len(w) > 4 else w[2])
                    total = float(w[3] if len(w) > 3 else w[2])
                    used = total - avail
                    if avail > 0 or used > 0:
                        balances.append(BalanceInfo(
                            asset=ccy,
                            free=avail,
                            used=used,
                            total=total,
                        ))
        return balances

    async def get_positions(self, symbol: Optional[str] = None) -> List[PositionInfo]:
        """Get positions from Bitfinex."""
        try:
            raw = await self._bitfinex_private_request("POST", "/v2/auth/r/positions", body={})

            positions = []
            if isinstance(raw, list):
                for p in raw:
                    if not isinstance(p, list) or len(p) < 6:
                        continue
                    amt = float(p[2] or 0)
                    if amt == 0:
                        continue
                    entry = float(p[3] or 0)
                    positions.append(PositionInfo(
                        symbol=str(p[1] or ""),
                        side="LONG" if amt > 0 else "SHORT",
                        quantity=abs(amt),
                        entry_price=entry,
                        unrealized_pnl=float(p[4] or 0),
                        leverage=1,
                        liquidation_price=0.0,
                    ))
            return positions
        except Exception:
            return []

    async def get_orderbook(self, symbol: str, limit: int = 20) -> OrderbookData:
        """Get order book from Bitfinex."""
        sym = self._normalize_symbol(symbol)
        raw = await self._bitfinex_public_request(
            f"/v2/book/{sym}/P0",
            params={"limit": limit},
        )

        bids = []
        asks = []
        if isinstance(raw, list):
            for entry in raw:
                if not isinstance(entry, list) or len(entry) < 3:
                    continue
                price, count, amount = float(entry[0]), float(entry[1]), float(entry[2])
                level = OrderbookEntry(price=price, quantity=abs(amount))
                if amount > 0:
                    bids.append(level)
                else:
                    asks.append(level)

        return OrderbookData(
            symbol=symbol,
            bids=bids[:limit],
            asks=asks[:limit],
            timestamp=str(int(time.time() * 1000)),
        )

    async def get_klines(
        self, symbol: str, interval: str = "1h", limit: int = 100,
    ) -> List[KlineBar]:
        """Get klines from Bitfinex."""
        sym = self._normalize_symbol(symbol)
        raw = await self._bitfinex_public_request(
            f"/v2/candles/trade:{interval}:{sym}/hist",
            params={"limit": limit},
        )

        bars = []
        if isinstance(raw, list):
            from datetime import datetime, timezone
            for candle in raw:
                if not isinstance(candle, list) or len(candle) < 6:
                    continue
                bars.append(KlineBar(
                    timestamp=datetime.fromtimestamp(int(candle[0]) // 1000, tz=timezone.utc).isoformat(),
                    open=float(candle[1]),
                    high=float(candle[3]),
                    low=float(candle[4]),
                    close=float(candle[2]),
                    volume=float(candle[5]),
                ))
        bars.sort(key=lambda x: x.timestamp)
        return bars


__all__ = ["BitfinexClient"]
