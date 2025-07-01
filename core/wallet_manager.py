"""💸 WalletManager for Dhaher AI Ecosystem
Simplified multi-chain balance tracker & withdraw helper.
Extensible: plug real web3 / CEX SDK later.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Dict
import requests

_DB = Path("data/wallet_state.json")


class WalletManager:
    """Track revenue across chains & handle withdrawals."""

    def __init__(self) -> None:
        self.main_address = os.getenv("MAIN_WALLET_ADDRESS", "")
        self.state: Dict = {"balances": {}, "tx": []}
        self._load()

    def _load(self):
        if _DB.exists():
            self.state = json.loads(_DB.read_text())

    def _save(self):
        _DB.parent.mkdir(parents=True, exist_ok=True)
        _DB.write_text(json.dumps(self.state, indent=2))

    # ------------------------------------------------------
    def record_income(self, chain: str, amount: float, txid: str, source: str):
        self.state["tx"].append({
            "ts": int(time.time()),
            "chain": chain,
            "amount": amount,
            "txid": txid,
            "src": source,
        })
        self.state["balances"].setdefault(chain, 0.0)
        self.state["balances"][chain] += amount
        self._save()

    # ------------------------------------------------------
    def balance(self, chain: str) -> float:
        return self.state.get("balances", {}).get(chain, 0.0)

    def total_usd(self) -> float:
        usd = 0.0
        for ch, amt in self.state.get("balances", {}).items():
            usd += amt * self._price_usd(ch)
        return usd

    def _price_usd(self, chain: str) -> float:
        symbol = {
            "btc": "bitcoin",
            "eth": "ethereum",
        }.get(chain.lower(), chain.lower())
        try:
            r = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd", timeout=8)
            return r.json()[symbol]["usd"]
        except Exception:
            return 0.0

    # ------------------------------------------------------
    def withdraw_all(self):
        for ch, amt in list(self.state.get("balances", {}).items()):
            if amt <= 0:
                continue
            print(f"[WalletManager] Withdraw {amt} {ch.upper()} to {self.main_address} – manual step")
            self.state["balances"][ch] = 0.0
        self._save()


wallet_manager = WalletManager()