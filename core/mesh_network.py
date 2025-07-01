"""🌐 Mesh Network Registry for Agentic AI Ecosystem
Stores and syncs list of known Agentic AI nodes.
"""
from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Dict, List
import requests

_STORE = Path("data/mesh_nodes.json")


def _load() -> Dict[str, Dict]:
    if _STORE.exists():
        return json.loads(_STORE.read_text())
    return {}


def _save(data: Dict[str, Dict]):
    _STORE.parent.mkdir(parents=True, exist_ok=True)
    _STORE.write_text(json.dumps(data, indent=2))


def register_node(url: str, meta: Dict[str, str] | None = None):
    nodes = _load()
    nodes[url] = {
        "last_seen": int(time.time()),
        **(meta or {}),
    }
    _save(nodes)


def get_nodes() -> List[str]:
    return list(_load().keys())


def ping_node(url: str, timeout: int = 5) -> bool:
    try:
        r = requests.get(url.rstrip("/") + "/.well-known/agentic-node", timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False