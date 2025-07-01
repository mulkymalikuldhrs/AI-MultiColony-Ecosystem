"""📦 ColonyExpansionBot – duplicates current node to new host (stub)."""
from core import mesh_network
from agents.colony_agents import ColonyAgent

class ColonyExpansionBot:
    status = "ready"
    capabilities = ["duplicate_node", "sync_parent"]

    def expand(self, new_node_url: str):
        print(f"[ColonyExpansion] Registering new clone at {new_node_url}")
        mesh_network.register_node(new_node_url, {"source": "expansion"})
        # In real deployment, would trigger git clone + deploy script on remote


def colony_expansion_agent():
    return ColonyExpansionBot()