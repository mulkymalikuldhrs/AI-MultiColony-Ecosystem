"""KuCoin Exchange Client — Spot + USDT Futures.

Supports KuCoin V2 API with HMAC-SHA256 + Base64 request signing
(including signed passphrase) for both spot and futures markets.

API docs: https://www.kucoin.com/docs-rest/
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


class KuCoinClient(BaseRestClient):
    """KuCoin Spot + Futures REST client.

    Signing (V2):
    - KC-API-SIGN = base64(hmac_sha256(secret, timestamp + method + requestPath + body))
    - KC-API-PASSPHRASE = base64(hmac_sha256(secret, passphrase))

    Capabilities: SPOT, FUTURES, PERPETUALS, MARGIN, WEBSOCKET.
    """

    exchange_id = "kucoin"
    capabilities = (
        ExchangeCapability.SPOT
        | ExchangeCapability.FUTURES
        | ExchangeCapability.PERPETUALS
        | ExchangeCapability.MARGIN
        | ExchangeCapability.WEBSOCKET
    )

    SPOT_URL = "https://api.kucoin.com"
    FUTURES_URL = "https://api-futures.kucoin.com"

    def __init__(self, config: RestClientConfig) -> None:
        config.base_url = config.base_url or self.SPOT_URL
        super().__init__(config)
        self._market_type = "spot"

    # ----- Signing -----

    def _b64_hmac_sha256(self, key: str, msg: str) -> str:
        mac = hmac.new(key.encode("utf-8"), msg.encode("utf-8"), hashlib.sha256).digest()
        return base64.b64encode(mac).decode("utf-8")

    def _sign_kucoin(self, method: str, endpoint: str, params: Optional[Dict] = None, body: str = "") -> Dict[str, str]:
        """Sign request using KuCoin V2 auth method."""
        ts_ms = str(int(time.time() * 1000))
        qs = ""
        if params and method.upper() == "GET":
            norm = {str(k): "" if v is None else str(v) for k, v in params.items()}
            qs = urlencode(sorted(norm.items()), doseq=True)
        signed_path = f"{endpoint}?{qs}" if qs else endpoint
        prehash = f"{ts_ms}{method.upper()}{signed_path}{body}"
        sign = self._b64_hmac_sha256(self._config.api_secret, prehash)
        passphrase_signed = self._b64_hmac_sha256(self._config.api_secret, self._config.passphrase)

        return {
            "KC-API-KEY": self._config.api_key,
            "KC-API-SIGN": sign,
            "KC-API-TIMESTAMP": ts_ms,
            "KC-API-PASSPHRASE": passphrase_signed,
            "KC-API-KEY-VERSION": "2",
            "Content-Type": "application/json",
        }

    async def _kucoin_request(
        self, method: str, endpoint: str, params: Optional[Dict] = None,
        body: Optional[Dict] = None, signed: bool = False,
    ) -> Any:
        """Make a KuCoin API request."""
        import httpx
        import json

        await self._rate_limit()
        params = params or {}
        base_url = self._config.base_url
        url = f"{base_url}{endpoint}"

        request_body = json.dumps(body) if body else ""
        headers = self._sign_kucoin(method, endpoint, params, request_body) if (signed and self._config.api_key) else {"Content-Type": "application/json"}

        async with httpx.AsyncClient(timeout=self._config.timeout) as client:
            fn = getattr(client, method.lower())
            if method.upper() == "GET":
                response = await fn(url, params=params, headers=headers)
            else:
                response = await fn(url, content=request_body, headers=headers)
            response.raise_for_status()
            data = response.json()

            if isinstance(data, dict):
                code = str(data.get("code", ""))
                if code not in ("200000", "0", ""):
                    raise ValueError(f"KuCoin error (code={code}): {data.get('msg', 'unknown')}")

            return data.get("data", data) if isinstance(data, dict) else data

    # ----- Helpers -----

    @staticmethod
    def _normalize_symbol(symbol: str) -> str:
        return symbol.replace("/", "-").upper()

    # ----- Abstract method implementations -----

    async def place_order(self, order: OrderRequest) -> OrderResult:
        """Place order on KuCoin."""
        sym = self._normalize_symbol(order.symbol)

        body: Dict[str, Any] = {
            "clientOid": order.client_order_id or str(int(time.time() * 1000)),
            "side": order.side.lower(),
            "symbol": sym,
            "type": "market" if order.order_type == "market" else "limit",
        }

        if order.order_type == "market":
            body["size"] = str(order.quantity)
        else:
            body["size"] = str(order.quantity)
            body["price"] = str(order.price or 0)
            body["timeInForce"] = order.time_in_force or "GTC"

        data = await self._kucoin_request("POST", "/api/v1/orders", body=body, signed=True)

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
        """Cancel order on KuCoin."""
        try:
            await self._kucoin_request("DELETE", f"/api/v1/orders/{order_id}", signed=True)
            return True
        except Exception as exc:
            logger.warning("KuCoin cancel failed: %s", exc)
            return False

    async def get_balance(self, asset: Optional[str] = None) -> List[BalanceInfo]:
        """Get account balance from KuCoin."""
        data = await self._kucoin_request("GET", "/api/v1/accounts", signed=True)

        balances = []
        if isinstance(data, list):
            for acct in data:
                if not isinstance(acct, dict):
                    continue
                ccy = str(acct.get("currency", ""))
                if asset and ccy != asset:
                    continue
                free = float(acct.get("available", 0) or 0)
                used = float(acct.get("holds", 0) or 0)
                if free > 0 or used > 0:
                    balances.append(BalanceInfo(
                        asset=ccy,
                        free=free,
                        used=used,
                        total=free + used,
                    ))
        return balances

    async def get_positions(self, symbol: Optional[str] = None) -> List[PositionInfo]:
        """Get positions from KuCoin futures."""
        try:
            params: Dict[str, Any] = {}
            if symbol:
                params["symbol"] = self._normalize_symbol(symbol)
            data = await self._kucoin_request("GET", "/api/v1/positions", params=params, signed=True)

            positions = []
            if isinstance(data, list):
                for p in data:
                    if not isinstance(p, dict):
                        continue
                    qty = float(p.get("currentQty", 0))
                    if qty == 0:
                        continue
                    positions.append(PositionInfo(
                        symbol=str(p.get("symbol", "")),
                        side="LONG" if qty > 0 else "SHORT",
                        quantity=abs(qty),
                        entry_price=float(p.get("avgEntryPrice", 0)),
                        unrealized_pnl=float(p.get("unrealisedPnl", 0)),
                        leverage=1,
                        liquidation_price=0.0,
                    ))
            return positions
        except Exception:
            return []

    async def get_orderbook(self, symbol: str, limit: int = 20) -> OrderbookData:
        """Get order book from KuCoin."""
        sym = self._normalize_symbol(symbol)
        data = await self._kucoin_request(
            "GET", "/api/v1/market/orderbook/level2_20",
            params={"symbol": sym}, signed=False,
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
        """Get klines from KuCoin."""
        sym = self._normalize_symbol(symbol)
        data = await self._kucoin_request(
            "GET", "/api/v1/market/candles",
            params={"symbol": sym, "type": interval, "limit": min(limit, 200)},
            signed=False,
        )

        bars = []
        if isinstance(data, list):
            from datetime import datetime, timezone
            for candle in data:
                if not isinstance(candle, list) or len(candle) < 7:
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


__all__ = ["KuCoinClient"]
