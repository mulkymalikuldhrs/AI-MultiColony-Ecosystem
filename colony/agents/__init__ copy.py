"""Agent implementations for the Agentic AI System"""

import pkgutil
import importlib
from pathlib import Path
from .agent_registry import agent_registry, register_agent

# Dynamically load agents from the current directory
# This ensures that all agent files are scanned and their classes
# (decorated with @register_agent) are added to the registry.
print("🔍 Scanning for agent modules...")
for loader, module_name, is_pkg in pkgutil.iter_modules([str(Path(__file__).parent)]):
    # Only consider files starting with 'agent_' and ending with '.py'
    # and not the agent_registry.py itself
    if module_name.startswith('agent_') and module_name.endswith('.py') and module_name != 'agent_registry':
        try:
            # Import the module
            module = importlib.import_module(f".{module_name}", package="src.agents")
            print(f"✅ Successfully loaded agent module: {module_name}")
        except Exception as e:
            print(f"❌ Failed to load agent module {module_name}: {e}")

# Expose the global agent_registry instance
AGENTS_REGISTRY = agent_registry
