"""
Unified Agent Registry v7.3.0
Centralized agent management system for AI-MultiColony-Ecosystem
Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import os
import json
import logging
import importlib
import inspect
from typing import Dict, Any, List, Optional, Type, Union
from pathlib import Path
from datetime import datetime
from .base_agent import BaseAgent

class UnifiedAgentRegistry:
    """
    Unified registry for all agents in the system.
    Handles dynamic agent discovery, registration, and lifecycle management.
    """
    
    def __init__(self):
        self.agents = {}
        self.agent_classes = {}
        self.agent_instances = {}
        self.agent_metadata = {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize the registry
        self._initialize_registry()
        
    def _initialize_registry(self):
        """Initialize the agent registry by discovering all available agents."""
        self.logger.info("Initializing Unified Agent Registry...")
        
        # Discover agents from the agents directory
        self._discover_agents()
        
        # Load agent metadata
        self._load_agent_metadata()
        
        self.logger.info(f"Registry initialized with {len(self.agent_classes)} agent classes")
    
    def _discover_agents(self):
        """Dynamically discover all agent classes in the agents directory."""
        agents_dir = Path(__file__).parent.parent / 'agents'
        
        if not agents_dir.exists():
            self.logger.warning(f"Agents directory not found: {agents_dir}")
            return
            
        for file_path in agents_dir.glob('*.py'):
            if file_path.name.startswith('__'):
                continue
                
            module_name = file_path.stem
            try:
                # Import the module
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find agent classes
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, BaseAgent) and 
                        obj != BaseAgent):
                        
                        agent_name = getattr(obj, 'agent_name', name.lower())
                        self.agent_classes[agent_name] = obj
                        self.logger.debug(f"Discovered agent: {agent_name}")
                        
            except Exception as e:
                self.logger.error(f"Error loading agent module {module_name}: {e}")
    
    def _load_agent_metadata(self):
        """Load agent metadata from configuration files."""
        metadata_file = Path(__file__).parent.parent / 'data' / 'agent_metadata.json'
        
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    self.agent_metadata = json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading agent metadata: {e}")
                self.agent_metadata = {}
        else:
            self.agent_metadata = {}
    
    def register_agent(self, name: str, agent_class: Type[BaseAgent], 
                      metadata: Optional[Dict[str, Any]] = None):
        """
        Register an agent class with the registry.
        
        Args:
            name: Unique identifier for the agent
            agent_class: The agent class to register
            metadata: Optional metadata about the agent
        """
        if not issubclass(agent_class, BaseAgent):
            raise ValueError(f"Agent class must inherit from BaseAgent")
            
        self.agent_classes[name] = agent_class
        
        if metadata:
            self.agent_metadata[name] = metadata
            
        self.logger.info(f"Registered agent: {name}")
    
    def create_agent(self, name: str, config: Optional[Dict[str, Any]] = None, 
                    instance_name: Optional[str] = None) -> BaseAgent:
        """
        Create an instance of a registered agent.
        
        Args:
            name: Name of the agent class to instantiate
            config: Configuration for the agent
            instance_name: Unique name for this instance
            
        Returns:
            BaseAgent: Instance of the requested agent
        """
        if name not in self.agent_classes:
            raise ValueError(f"Agent '{name}' not found in registry")
            
        agent_class = self.agent_classes[name]
        
        if not instance_name:
            instance_name = f"{name}_{len(self.agent_instances)}"
            
        try:
            agent_instance = agent_class(instance_name, config)
            self.agent_instances[instance_name] = agent_instance
            
            self.logger.info(f"Created agent instance: {instance_name}")
            return agent_instance
            
        except Exception as e:
            self.logger.error(f"Error creating agent {name}: {e}")
            raise
    
    def get_agent(self, instance_name: str) -> Optional[BaseAgent]:
        """Get an agent instance by name."""
        return self.agent_instances.get(instance_name)
    
    def get_agent_by_name(self, name: str) -> Optional[BaseAgent]:
        """Get the first agent instance of a given class name."""
        for instance_name, agent in self.agent_instances.items():
            if agent.__class__.__name__.lower() == name.lower():
                return agent
        return None
    
    def list_all_agents(self) -> List[str]:
        """List all available agent classes."""
        return list(self.agent_classes.keys())
    
    def list_active_agents(self) -> List[str]:
        """List all active agent instances."""
        return list(self.agent_instances.keys())
    
    def get_agent_info(self, name: str) -> Dict[str, Any]:
        """Get information about an agent class."""
        if name not in self.agent_classes:
            return {}
            
        agent_class = self.agent_classes[name]
        metadata = self.agent_metadata.get(name, {})
        
        return {
            'name': name,
            'class': agent_class.__name__,
            'module': agent_class.__module__,
            'docstring': agent_class.__doc__,
            'metadata': metadata,
            'active_instances': [
                instance_name for instance_name, agent in self.agent_instances.items()
                if isinstance(agent, agent_class)
            ]
        }
    
    def save_registry_state(self, filepath: Optional[str] = None):
        """Save the current registry state to a file."""
        if not filepath:
            filepath = Path(__file__).parent.parent / 'data' / 'registry_state.json'
            
        state = {
            'timestamp': datetime.now().isoformat(),
            'agent_classes': list(self.agent_classes.keys()),
            'active_instances': list(self.agent_instances.keys()),
            'metadata': self.agent_metadata
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
            self.logger.info(f"Registry state saved to {filepath}")
        except Exception as e:
            self.logger.error(f"Error saving registry state: {e}")
    
    def remove_agent_instance(self, instance_name: str) -> bool:
        """Remove an agent instance from the registry."""
        if instance_name in self.agent_instances:
            del self.agent_instances[instance_name]
            self.logger.info(f"Removed agent instance: {instance_name}")
            return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        return {
            'total_agent_classes': len(self.agent_classes),
            'active_instances': len(self.agent_instances),
            'registry_classes': list(self.agent_classes.keys()),
            'active_instance_names': list(self.agent_instances.keys()),
            'last_updated': datetime.now().isoformat()
        }


# Global registry instance
unified_registry = UnifiedAgentRegistry()

# Convenience functions for backward compatibility
def get_agent_by_name(name: str) -> Optional[BaseAgent]:
    """Get an agent instance by name."""
    return unified_registry.get_agent_by_name(name)

def list_all_agents() -> List[str]:
    """List all available agent classes."""
    return unified_registry.list_all_agents()

def register_agent(name: str, agent_class: Type[BaseAgent], 
                  metadata: Optional[Dict[str, Any]] = None):
    """Register an agent class."""
    return unified_registry.register_agent(name, agent_class, metadata)

def create_agent(name: str, config: Optional[Dict[str, Any]] = None, 
                instance_name: Optional[str] = None) -> BaseAgent:
    """Create an agent instance."""
    return unified_registry.create_agent(name, config, instance_name)