"""Bitget Exchange Client — V2 Mix API (Spot + USDT Futures).

Supports Bitget V2 API with HMAC-SHA256 + Base64 request signing
for both spot and USDT-margined perpetual markets.

API docs: https://bitgetlimited.github.io/apidoc/en/
"""

from __future__ import annotations

import base64
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


class BitgetClient(BaseRestClient):
    """Bitget V2 Mix REST client for spot and USDT futures.

    Signing:
    - ACCESS-SIGN = base64(hmac_sha256(secret, timestamp + method + request_path + body))

    Capabilities: SPOT, FUTURES, PERPETUALS, MARGIN, WEBSOCKET.
    """

    exchange_id = "bitget"
    capabilities = (
        ExchangeCapability.SPOT
        | ExchangeCapability.FUTURES
        | ExchangeCapability.PERPETUALS
        | ExchangeCapability.MARGIN
        | ExchangeCapability.WEBSOCKET
    )

    BASE_URL = "https://api.bitget.com"

    def __init__(self, config: RestClientConfig) -> None:
        config.base_url = config.base_url or self.BASE_URL
        super().__init__(config)
        self._product_type = "USDT-FUTURES"

    # ----- Signing -----

    def _sign_bitget(self, timestamp: str, method: str, path: str, body: str = "") -> Dict[str, str]:
        """Sign request using Bitget auth method."""
        prehash = f"{timestamp}{method.upper()}{path}{body}"
        mac = hmac.new(
            self._config.api_secret.encode("utf-8"),
            prehash.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        sign = base64.b64encode(mac).decode("utf-8")

        return {
            "ACCESS-KEY": self._config.api_key,
            "ACCESS-SIGN": sign,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": self._config.passphrase,
            "Content-Type": "application/json",
            "locale": "en-US",
        }

    async def _bitget_request(
        self, method: str, endpoint: str, params: Optional[Dict] = None,
        body: Optional[Dict] = None, signed: bool = False,
    ) -> Any:
        """Make a Bitget V2 API request."""
        import httpx
        import json

        await self._rate_limit()
        params = params or {}
        url = f"{self._config.base_url}{endpoint}"

        headers: Dict[str, str] = {"Content-Type": "application/json", "locale": "en-US"}
        request_body = ""

        if method.upper() == "GET":
            query = "&".join(f"{k}={v}" for k, v in params.items())
            path = f"{endpoint}?{query}" if query else endpoint
            if signed and self._config.api_key:
                ts = str(int(time.time() * 1000))
                headers = self._sign_bitget(ts, "GET", path)
            async with httpx.AsyncClient(timeout=self._config.timeout) as client:
                response = await httpx.AsyncClient(timeout=self._config.timeout).__aenter__()
                fn = getattr(response, method.lower())
                resp = await fn(url, params=params, headers=headers)
                await response.__aexit__(None, None, None)
                resp.raise_for_status()
                data = resp.json()
        else:
            request_body = json.dumps(body) if body else ""
            if signed and self._config.api_key:
                ts = str(int(time.time() * 1000))
                headers = self._sign_bitget(ts, "POST", endpoint, request_body)
            async with httpx.AsyncClient(timeout=self._config.timeout) as client:
                fn = getattr(client, method.lower())
                resp = await fn(url, content=request_body, headers=headers)
                resp.raise_for_status()
                data = resp.json()

        if isinstance(data, dict):
            c = str(data.get("code") or "")
            if c and c not in ("00000", "0"):
                raise ValueError(f"Bitget API error: {data.get('msg', 'unknown')}")

        return data.get("data", data) if isinstance(data, dict) else data

    # ----- Helpers -----

    @staticmethod
    def _normalize_symbol(symbol: str) -> str:
        return symbol.replace("/", "").upper()

    # ----- Abstract method implementations -----

    async def place_order(self, order: OrderRequest) -> OrderResult:
        """Place order on Bitget."""
        sym = self._normalize_symbol(order.symbol)

        body: Dict[str, Any] = {
            "symbol": sym,
            "productType": self._product_type,
            "marginCoin": "USDT",
            "marginMode": "crossed",
            "side": order.side.lower(),
            "size": str(order.quantity),
        }
        if order.order_type == "market":
            body["orderType"] = "market"
        else:
            body["orderType"] = "limit"
            body["price"] = str(order.price or 0)
        if order.client_order_id:
            body["clientOid"] = order.client_order_id

        data = await self._bitget_request("POST", "/api/v2/mix/order/place-order", body=body, signed=True)

        order_id = str(data.get("orderId", "")) if isinstance(data, dict) else ""

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
        """Cancel order on Bitget."""
        sym = self._normalize_symbol(symbol)
        try:
            await self._bitget_request(
                "POST", "/api/v2/mix/order/cancel-order",
                body={"symbol": sym, "productType": self._product_type, "marginCoin": "USDT", "orderId": order_id},
                signed=True,
            )
            return True
        except Exception as exc:
            logger.warning("Bitget cancel failed: %s", exc)
            return False

    async def get_balance(self, asset: Optional[str] = None) -> List[BalanceInfo]:
        """Get account balance from Bitget."""
        data = await self._bitget_request(
            "GET", "/api/v2/mix/account/accounts",
            params={"productType": self._product_type},
            signed=True,
        )

        balances = []
        if isinstance(data, list):
            for acct in data:
                if not isinstance(acct, dict):
                    continue
                coin = str(acct.get("marginCoin", acct.get("coin", "")))
                if asset and coin != asset:
                    continue
                free = float(acct.get("available", acct.get("availableBalance", 0)) or 0)
                total = float(acct.get("equity", acct.get("balance", 0)) or 0)
                used = total - free
                if free > 0 or used > 0:
                    balances.append(BalanceInfo(
                        asset=coin,
                        free=free,
                        used=used,
                        total=total,
                    ))
        return balances

    async def get_positions(self, symbol: Optional[str] = None) -> List[PositionInfo]:
        """Get positions from Bitget."""
        params: Dict[str, Any] = {"productType": self._product_type}
        if symbol:
            params["symbol"] = self._normalize_symbol(symbol)

        data = await self._bitget_request(
            "GET", "/api/v2/mix/position/all-position", params=params, signed=True,
        )

        positions = []
        if isinstance(data, list):
            for p in data:
                if not isinstance(p, dict):
                    continue
                qty = float(p.get("total", 0))
                if qty <= 0:
                    continue
                hold_side = str(p.get("holdSide", "")).lower()
                positions.append(PositionInfo(
                    symbol=str(p.get("symbol", "")),
                    side="LONG" if hold_side == "long" else "SHORT",
                    quantity=qty,
                    entry_price=float(p.get("averageOpenPrice", 0)),
                    unrealized_pnl=float(p.get("unrealizedPL", 0)),
                    leverage=1,
                    liquidation_price=0.0,
                ))
        return positions

    async def get_orderbook(self, symbol: str, limit: int = 20) -> OrderbookData:
        """Get order book from Bitget."""
        sym = self._normalize_symbol(symbol)
        data = await self._bitget_request(
            "GET", "/api/v2/mix/market/depth",
            params={"symbol": sym, "productType": self._product_type, "limit": str(limit)},
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
        """Get klines from Bitget."""
        sym = self._normalize_symbol(symbol)
        data = await self._bitget_request(
            "GET", "/api/v2/mix/market/candles",
            params={"symbol": sym, "productType": self._product_type, "granularity": interval, "limit": str(limit)},
            signed=False,
        )

        bars = []
        if isinstance(data, list):
            from datetime import datetime, timezone
            for candle in data:
                if not isinstance(candle, list) or len(candle) < 6:
                    continue
                bars.append(KlineBar(
                    timestamp=datetime.fromtimestamp(int(candle[0]) // 1000, tz=timezone.utc).isoformat(),
                    open=float(candle[1]),
                    high=float(candle[2]),
                    low=float(candle[3]),
                    close=float(candle[4]),
                    volume=float(candle[5]),
                ))
        bars.sort(key=lambda x: x.timestamp)
        return bars


__all__ = ["BitgetClient"]
