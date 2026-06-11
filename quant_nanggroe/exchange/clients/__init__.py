"""Exchange REST Clients — Multi-exchange REST API client implementations.

Provides exchange-specific REST clients for 10+ cryptocurrency
exchanges, with unified interface, rate limiting, and error handling.
"""

from quant_nanggroe.exchange.clients.base_rest_client import (
    BaseRestClient,
    ExchangeCapability,
    RestClientConfig,
    OrderRequest,
    OrderResult,
    BalanceInfo,
    PositionInfo,
    OrderbookData,
    OrderbookEntry,
    KlineBar,
)
from quant_nanggroe.exchange.clients.binance_client import BinanceClient
from quant_nanggroe.exchange.clients.bybit_client import BybitClient
from quant_nanggroe.exchange.clients.okx_client import OKXClient
from quant_nanggroe.exchange.clients.coinbase_client import CoinbaseClient
from quant_nanggroe.exchange.clients.kucoin_client import KuCoinClient
from quant_nanggroe.exchange.clients.bitget_client import BitgetClient
from quant_nanggroe.exchange.clients.kraken_client import KrakenClient
from quant_nanggroe.exchange.clients.gate_client import GateClient
from quant_nanggroe.exchange.clients.bitfinex_client import BitfinexClient
from quant_nanggroe.exchange.clients.longbridge_client import LongbridgeClient

# Registry mapping exchange_id → client class
EXCHANGE_REGISTRY: dict[str, type[BaseRestClient]] = {
    "binance": BinanceClient,
    "bybit": BybitClient,
    "okx": OKXClient,
    "coinbase": CoinbaseClient,
    "kucoin": KuCoinClient,
    "bitget": BitgetClient,
    "kraken": KrakenClient,
    "gate": GateClient,
    "bitfinex": BitfinexClient,
    "longbridge": LongbridgeClient,
}

__all__ = [
    # Base classes & models
    "BaseRestClient",
    "ExchangeCapability",
    "RestClientConfig",
    "OrderRequest",
    "OrderResult",
    "BalanceInfo",
    "PositionInfo",
    "OrderbookData",
    "OrderbookEntry",
    "KlineBar",
    # Client classes
    "BinanceClient",
    "BybitClient",
    "OKXClient",
    "CoinbaseClient",
    "KuCoinClient",
    "BitgetClient",
    "KrakenClient",
    "GateClient",
    "BitfinexClient",
    "LongbridgeClient",
    # Registry
    "EXCHANGE_REGISTRY",
]
