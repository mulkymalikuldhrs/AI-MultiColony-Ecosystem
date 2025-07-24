<<<<<<< HEAD
<<<<<<< HEAD:src/core/agent_registry.py
"""
Centralized Agent Registry
"""

# Import all agent instances
from agents.agent_maker import agent_maker
from agents.ai_research_agent import ai_research_agent
from agents.authentication_agent import authentication_agent
from agents.auto_deployment_system import auto_deployment_system
from agents.autonomous_maintainer import autonomous_maintainer
from agents.code_executor import code_executor
from agents.credential_manager import credential_manager
from agents.cybershell import cybershell_agent
from agents.data_sync import data_sync_agent
from agents.deploy_manager import deploy_manager
from agents.dev_engine import dev_engine_agent
from agents.fullstack_dev import fullstack_dev_agent
from agents.llm_provider_manager import llm_provider_manager
from agents.meta_agent_creator import meta_agent_creator
from agents.prompt_generator import prompt_generator
from agents.specialist_agents import specialist_agents
from agents.system_optimizer import system_optimizer
from agents.system_supervisor import system_supervisor
from agents.ui_designer import ui_designer_agent

# Centralized agent registry
agent_registry = {
    "agent_maker": agent_maker,
    "ai_research_agent": ai_research_agent,
    "authentication_agent": authentication_agent,
    "auto_deployment_system": auto_deployment_system,
    "autonomous_maintainer": autonomous_maintainer,
    "code_executor": code_executor,
    "credential_manager": credential_manager,
    "cybershell": cybershell_agent,
    "data_sync": data_sync_agent,
    "deploy_manager": deploy_manager,
    "dev_engine": dev_engine_agent,
    "fullstack_dev": fullstack_dev_agent,
    "llm_provider_manager": llm_provider_manager,
    "meta_agent_creator": meta_agent_creator,
    "prompt_generator": prompt_generator,
    "specialist_agents": specialist_agents,
    "system_optimizer": system_optimizer,
    "system_supervisor": system_supervisor,
    "ui_designer": ui_designer_agent,
}
=======
=======
<<<<<<< HEAD:colony/core/agent_registry.py
>>>>>>> origin/kamis24juli2025
# colony/core/agent_registry.py
"""
Agent Registry - Central registry for all agents in the system
Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import importlib
import pkgutil
import inspect
import logging
from pathlib import Path
from typing import Dict, Type, Any, List, Optional, Callable

from colony.core.base_agent import BaseAgent

# Global registry
REGISTRY: Dict[str, Type[BaseAgent]] = {}
AGENT_INFO: Dict[str, Dict[str, Any]] = {}

# Setup logger
logger = logging.getLogger("agent_registry")

def register_agent(name: str, route: str = None, dependencies: List[str] = None, description: str = "") -> Callable:
    """
    Decorator to register an agent class with the registry.
    
    Args:
        name: Unique identifier for the agent
        route: API route for the agent (optional)
        dependencies: List of dependencies required by the agent (optional)
        description: Description of the agent (optional)
        
    Returns:
        Decorator function
    """
    if dependencies is None:
        dependencies = []
    
    def decorator(cls: Type[Any]) -> Type[Any]:
        if not issubclass(cls, BaseAgent):
            logger.warning(f"Warning: {cls.__name__} is not a subclass of BaseAgent")
        
        # Generate route if not provided
        agent_route = route or f"/api/agents/{name}"
        
        # Create metadata
        metadata = {
            "id": name,
            "name": name.replace('_', ' ').title(),
            "route": agent_route,
            "dependencies": dependencies,
            "description": description or cls.__doc__ or f"Agent {name}",
            "status": "inactive"  # Default status
        }
        
        # Register in both dictionaries
        REGISTRY[name] = cls
        AGENT_INFO[name] = {
            "name": name,
            "class": cls,
            "metadata": metadata
        }
        
        logger.info(f"Registered agent '{name}' with route '{agent_route}'")
        return cls
    
    return decorator

def discover_agents():
    """
    Discover and register all agent classes in the colony/agents directory.
    """
    logger.info("Discovering agents...")
    
    # Path to agents directory
    agents_dir = Path(__file__).parent.parent / "agents"
    
    if not agents_dir.exists():
        logger.warning(f"Agents directory not found at {agents_dir}")
        return
    
    # Count of discovered agents
    discovered_count = 0
    
    # Iterate through all modules in the agents directory
    for module_info in pkgutil.iter_modules([str(agents_dir)]):
        try:
            # Import the module
            module_name = f"colony.agents.{module_info.name}"
            module = importlib.import_module(module_name)
            
            # Look for agent classes in the module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                # Check if it's a class and a subclass of BaseAgent
                if (isinstance(attr, type) and 
                    issubclass(attr, BaseAgent) and 
                    attr is not BaseAgent and
                    attr.__module__ == module_name):
                    
                    # Register the agent if not already registered
                    if attr_name not in REGISTRY:
                        # Auto-register with minimal metadata
                        register_agent(
                            name=attr_name,
                            route=f"/api/agents/{attr_name.lower()}",
                            description=attr.__doc__ or f"Agent {attr_name}"
                        )(attr)
                        
                        discovered_count += 1
        
        except (ImportError, AttributeError) as e:
            logger.warning(f"Error importing module {module_info.name}: {e}")
    
    logger.info(f"Discovered {discovered_count} agents")
    logger.info(f"Total registered agents: {len(REGISTRY)}")

def get_agent_by_name(name: str) -> Optional[Type[BaseAgent]]:
    """
    Get an agent class by name.
    
    Args:
        name: Name of the agent
        
    Returns:
        Agent class or None if not found
    """
    return REGISTRY.get(name)

def reload_registry():
    """
    Reloads the agent registry by discovering all agents again.
    """
    logger.info("Reloading agent registry...")
    # Clear existing registry before discovering again
    REGISTRY.clear()
    AGENT_INFO.clear()
    discover_agents()
    logger.info(f"Registry reloaded. Found {len(REGISTRY)} agents.")

def get_agent_info(name: str) -> Optional[Dict[str, Any]]:
    """
    Get agent information by name.
    
    Args:
        name: Name of the agent
        
    Returns:
        Agent information dictionary or None if not found
    """
    return AGENT_INFO.get(name)

def list_all_agents() -> List[str]:
    """
    List all registered agent names.
    
    Returns:
        List of agent names
    """
    return list(REGISTRY.keys())

def get_all_agents() -> Dict[str, Dict[str, Any]]:
    """
    Get all agent information.
    
    Returns:
        Dictionary of all agent information
    """
    return AGENT_INFO

def update_agent_status(name: str, status: str) -> bool:
    """
    Update the status of an agent.
    
    Args:
        name: Name of the agent
        status: New status
        
    Returns:
        True if successful, False otherwise
    """
    if name in AGENT_INFO:
        AGENT_INFO[name]["metadata"]["status"] = status
        logger.info(f"Updated status of agent '{name}' to '{status}'")
        return True
    return False

# Initialize the registry
discover_agents()
<<<<<<< HEAD
>>>>>>> origin/jules-refactor-all:colony/core/agent_registry.py
=======
=======
"""
Centralized Agent Registry
"""

# Import all agent instances
from agents.agent_maker import agent_maker
from agents.ai_research_agent import ai_research_agent
from agents.authentication_agent import authentication_agent
from agents.auto_deployment_system import auto_deployment_system
from agents.autonomous_maintainer import autonomous_maintainer
from agents.code_executor import code_executor
from agents.credential_manager import credential_manager
from agents.cybershell import cybershell_agent
from agents.data_sync import data_sync_agent
from agents.deploy_manager import deploy_manager
from agents.dev_engine import dev_engine_agent
from agents.fullstack_dev import fullstack_dev_agent
from agents.llm_provider_manager import llm_provider_manager
from agents.meta_agent_creator import meta_agent_creator
from agents.prompt_generator import prompt_generator
from agents.specialist_agents import specialist_agents
from agents.system_optimizer import system_optimizer
from agents.system_supervisor import system_supervisor
from agents.ui_designer import ui_designer_agent

# Centralized agent registry
agent_registry = {
    "agent_maker": agent_maker,
    "ai_research_agent": ai_research_agent,
    "authentication_agent": authentication_agent,
    "auto_deployment_system": auto_deployment_system,
    "autonomous_maintainer": autonomous_maintainer,
    "code_executor": code_executor,
    "credential_manager": credential_manager,
    "cybershell": cybershell_agent,
    "data_sync": data_sync_agent,
    "deploy_manager": deploy_manager,
    "dev_engine": dev_engine_agent,
    "fullstack_dev": fullstack_dev_agent,
    "llm_provider_manager": llm_provider_manager,
    "meta_agent_creator": meta_agent_creator,
    "prompt_generator": prompt_generator,
    "specialist_agents": specialist_agents,
    "system_optimizer": system_optimizer,
    "system_supervisor": system_supervisor,
    "ui_designer": ui_designer_agent,
}
>>>>>>> origin/feature/system-refactor-and-ui-update:src/core/agent_registry.py
>>>>>>> origin/kamis24juli2025
