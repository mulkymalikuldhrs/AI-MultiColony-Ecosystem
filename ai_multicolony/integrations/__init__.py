"""
Integrations — Bridge modules connecting all ecosystem packages.

Packages:
  - crucix_client: OSINT intelligence service client
  - hermes_bridge: Quantitative trading engine bridge
  - organism_bridge: Autonomous organism service client
"""

from ai_multicolony.integrations.crucix_client import CrucixClient
from ai_multicolony.integrations.hermes_bridge import HermesQuantBridge
from ai_multicolony.integrations.organism_bridge import OrganismBridge

__all__ = ["CrucixClient", "HermesQuantBridge", "OrganismBridge"]
