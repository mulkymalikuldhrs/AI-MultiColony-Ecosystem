"""🔗 CloneConnectorAgent
Discovers other instances of Agentic AI Ecosystem and registers them into mesh_network.
• GitHub mode: search for repos containing 'Agentic-AI-Ecosystem'.
• URL mode: iterate CLONE_DISCOVERY_URLS (comma-sep) env var.
"""
from __future__ import annotations
import os
import requests
from typing import List
from core import mesh_network

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

class CloneConnectorAgent:
    status = "ready"
    capabilities = [
        "discover_repos",
        "ping_nodes",
        "register_mesh",
    ]

    def discover(self) -> List[str]:
        urls: List[str] = []
        # 1) URLs from env
        for u in os.getenv("CLONE_DISCOVERY_URLS", "").split(","):
            u = u.strip()
            if u:
                urls.append(u)
        # 2) GitHub search (public)
        if GITHUB_TOKEN:
            headers = {"Authorization": f"token {GITHUB_TOKEN}"}
            q = "Agentic-AI-Ecosystem in:name fork:true"
            r = requests.get("https://api.github.com/search/repositories", params={"q": q, "per_page": 10}, headers=headers, timeout=15)
            for item in r.json().get("items", []):
                repo_url = item.get("html_url", "")
                urls.append(repo_url)
        return list(set(urls))

    def connect(self):
        count = 0
        for url in self.discover():
            if mesh_network.ping_node(url):
                mesh_network.register_node(url, {"source": "clone_discovery"})
                count += 1
        print(f"[CloneConnector] Registered {count} nodes to mesh network")

# factory

def clone_connector_agent():
    return CloneConnectorAgent()