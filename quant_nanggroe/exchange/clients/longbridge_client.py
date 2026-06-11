"""Longbridge Exchange Client — Stock & Options Trading.

Supports Longbridge Securities API for stock and options trading
on US, HK, and CN markets.

API docs: https://open.longportapp.com/en/docs
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


class LongbridgeClient(BaseRestClient):
    """Longbridge Securities REST client for stock and options trading.

    Supports US, HK, and CN stock markets via the Longbridge OpenAPI.

    Signing:
    - X-Api-Signature = hex(hmac_sha256(secret, timestamp + method + path + body))
    - X-Api-Key: API key
    - X-Timestamp: Unix seconds

    Capabilities: SPOT, MARGIN, WEBSOCKET.
    """

    exchange_id = "longbridge"
    capabilities = (
        ExchangeCapability.SPOT
        | ExchangeCapability.MARGIN
        | ExchangeCapability.WEBSOCKET
    )

    BASE_URL = "https://openapi.longportapp.com"

    def __init__(self, config: RestClientConfig) -> None:
        config.base_url = config.base_url or self.BASE_URL
        super().__init__(config)

    # ----- Signing -----

    def _sign_longbridge(self, method: str, path: str, body: str = "") -> Dict[str, str]:
        """Sign request using Longbridge auth method."""
        ts = str(int(time.time()))
        prehash = f"{ts}{method.upper()}{path}{body}"
        sign = hmac.new(
            self._config.api_secret.encode("utf-8"),
            prehash.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        headers = {
            "X-Api-Key": self._config.api_key,
            "X-Api-Signature": sign,
            "X-Timestamp": ts,
            "Content-Type": "application/json",
        }
        if self._config.passphrase:
            headers["X-App-Key"] = self._config.passphrase
        return headers

    async def _longbridge_request(
        self, method: str, endpoint: str, params: Optional[Dict] = None,
        body: Optional[Dict] = None, signed: bool = False,
    ) -> Any:
        """Make a Longbridge API request."""
        import httpx
        import json

        await self._rate_limit()
        params = params or {}
        url = f"{self._config.base_url}{endpoint}"

        headers: Dict[str, str] = {"Content-Type": "application/json"}
        request_body = ""

        if method.upper() == "GET":
            if signed and self._config.api_key:
                headers = self._sign_longbridge("GET", endpoint)
            async with httpx.AsyncClient(timeout=self._config.timeout) as client:
                response = await client.get(url, params=params, headers=headers)
        else:
            request_body = json.dumps(body) if body else ""
            if signed and self._config.api_key:
                headers = self._sign_longbridge("POST", endpoint, request_body)
            async with httpx.AsyncClient(timeout=self._config.timeout) as client:
                response = await client.post(url, content=request_body, headers=headers)

        response.raise_for_status()
        data = response.json()
        return data.get("data", data) if isinstance(data, dict) else data

    # ----- Abstract method implementations -----

    async def place_order(self, order: OrderRequest) -> OrderResult:
        """Place order on Longbridge."""
        sd = order.side.upper()
        quantity_int = int(order.quantity)

        body: Dict[str, Any] = {
            "symbol": order.symbol,
            "side": sd,
            "quantity": quantity_int,
        }

        if order.order_type == "market":
            body["order_type"] = "MO"
        elif order.order_type == "limit":
            body["order_type"] = "LO"
            if order.price:
                body["price"] = str(order.price)
        elif order.order_type == "stop":
            body["order_type"] = "STO"
            if order.stop_price:
                body["trigger_price"] = str(order.stop_price)
        else:
            body["order_type"] = "MO"

        if order.client_order_id:
            body["client_order_id"] = order.client_order_id

        data = await self._longbridge_request("POST", "/v1/trade/order", body=body, signed=True)

        order_id = str(data.get("order_id", "")) if isinstance(data, dict) else ""

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
        """Cancel order on Longbridge."""
        try:
            await self._longbridge_request(
                "POST", "/v1/trade/order/cancel",
                body={"order_id": order_id},
                signed=True,
            )
            return True
        except Exception as exc:
            logger.warning("Longbridge cancel failed: %s", exc)
            return False

    async def get_balance(self, asset: Optional[str] = None) -> List[BalanceInfo]:
        """Get account balance from Longbridge."""
        data = await self._longbridge_request("GET", "/v1/asset/account", signed=True)

        balances = []
        if isinstance(data, dict):
            cash = data.get("cash", {})
            if isinstance(cash, dict):
                for ccy, val in cash.items():
                    if asset and ccy.upper() != asset:
                        continue
                    try:
                        v = float(val)
                        if v > 0:
                            balances.append(BalanceInfo(
                                asset=ccy.upper(),
                                free=v,
                                used=0.0,
                                total=v,
                            ))
                    except (ValueError, TypeError):
                        pass
        return balances

    async def get_positions(self, symbol: Optional[str] = None) -> List[PositionInfo]:
        """Get positions from Longbridge."""
        data = await self._longbridge_request("GET", "/v1/asset/stock/positions", signed=True)

        positions = []
        channels = data.get("channels", []) if isinstance(data, dict) else []
        if isinstance(channels, list):
            for channel in channels:
                if not isinstance(channel, dict):
                    continue
                for p in channel.get("positions", []):
                    if not isinstance(p, dict):
                        continue
                    qty = float(p.get("quantity", 0))
                    if qty <= 0:
                        continue
                    sym = str(p.get("symbol", ""))
                    if symbol and sym != symbol:
                        continue
                    entry = float(p.get("cost_price", 0))
                    positions.append(PositionInfo(
                        symbol=sym,
                        side="LONG",
                        quantity=qty,
                        entry_price=entry,
                        unrealized_pnl=float(p.get("unrealized_pnl", 0)),
                        leverage=1,
                        liquidation_price=0.0,
                    ))
        return positions

    async def get_orderbook(self, symbol: str, limit: int = 20) -> OrderbookData:
        """Get order book from Longbridge."""
        data = await self._longbridge_request(
            "GET", "/v1/quote/depth",
            params={"symbol": symbol, "limit": limit},
            signed=False,
        )

        asks_list = data.get("asks", []) if isinstance(data, dict) else []
        bids_list = data.get("bids", []) if isinstance(data, dict) else []

        bids = [
            OrderbookEntry(price=float(b.get("price", 0)), quantity=float(b.get("volume", 0)))
            for b in bids_list if isinstance(b, dict) and b.get("price")
        ]
        asks = [
            OrderbookEntry(price=float(a.get("price", 0)), quantity=float(a.get("volume", 0)))
            for a in asks_list if isinstance(a, dict) and a.get("price")
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
        """Get klines from Longbridge."""
        period_map = {
            "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
            "1h": "60m", "4h": "60m", "1d": "1d", "1w": "1w", "1M": "1M",
        }
        period = period_map.get(interval, "60m")

        data = await self._longbridge_request(
            "GET", "/v1/quote/candlestick",
            params={"symbol": symbol, "period": period, "count": limit},
            signed=False,
        )

        bars = []
        if isinstance(data, list):
            from datetime import datetime, timezone
            for candle in data:
                if not isinstance(candle, dict):
                    continue
                ts = int(candle.get("timestamp", 0))
                bars.append(KlineBar(
                    timestamp=datetime.fromtimestamp(ts, tz=timezone.utc).isoformat() if ts > 0 else "",
                    open=float(candle.get("open", 0)),
                    high=float(candle.get("high", 0)),
                    low=float(candle.get("low", 0)),
                    close=float(candle.get("close", 0)),
                    volume=float(candle.get("volume", 0)),
                ))
        bars.sort(key=lambda x: x.timestamp)
        return bars[:limit]


__all__ = ["LongbridgeClient"]
