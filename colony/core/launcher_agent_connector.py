"""
Launcher Agent Connector - Bridge between the unified launcher and agent system
Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import os
import sys
import json
import logging
import threading
import importlib
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Type, Union

# Setup logger
logger = logging.getLogger("launcher_agent_connector")

class LauncherAgentConnector:
    """
    Connector class to bridge the unified launcher with the agent system.
    Handles agent discovery, instantiation, and management.
    """
    
    def __init__(self):
        """Initialize the launcher agent connector."""
        self.agents = {}  # Dictionary of agent instances
        self.agent_threads = {}  # Dictionary of agent threads
        self.running_agents = set()  # Set of running agent IDs
        
        # Try to import agent registry
        try:
            from colony.core.agent_registry import get_agent, list_all_agents, get_agent_info
            self.get_agent = get_agent
            self.list_all_agents = list_all_agents
            self.get_agent_info = get_agent_info
            logger.info("Agent registry imported successfully")
        except ImportError as e:
            logger.warning(f"Could not import agent registry: {e}")
            self.get_agent = lambda x: None
            self.list_all_agents = lambda: []
            self.get_agent_info = lambda x: None
    
    def discover_agents(self) -> List[str]:
        """
        Discover available agents.
        
        Returns:
            List of agent names
        """
        try:
            agents = self.list_all_agents()
            logger.info(f"Discovered {len(agents)} agents")
            return agents
        except Exception as e:
            logger.error(f"Error discovering agents: {e}")
            return []
    
    def instantiate_agent(self, agent_name: str) -> Optional[Any]:
        """
        Instantiate an agent by name.
        
        Args:
            agent_name: Name of the agent to instantiate
            
        Returns:
            Agent instance or None if not found
        """
        try:
            agent_cls = self.get_agent(agent_name)
            if agent_cls:
                agent = agent_cls()
                self.agents[agent_name] = agent
                logger.info(f"Instantiated agent: {agent_name}")
                return agent
            else:
                logger.warning(f"Agent not found: {agent_name}")
                return None
        except Exception as e:
            logger.error(f"Error instantiating agent {agent_name}: {e}")
            return None
    
    def run_agent(self, agent_name: str, background: bool = False) -> bool:
        """
        Run an agent by name.
        
        Args:
            agent_name: Name of the agent to run
            background: Whether to run in the background
            
        Returns:
            True if started successfully, False otherwise
        """
        # Check if agent is already running
        if agent_name in self.running_agents:
            logger.warning(f"Agent {agent_name} is already running")
            return True
        
        # Get or instantiate the agent
        agent = self.agents.get(agent_name)
        if not agent:
            agent = self.instantiate_agent(agent_name)
            if not agent:
                return False
        
        try:
            # Run in background if requested
            if background:
                thread = threading.Thread(
                    target=self._run_agent_thread,
                    args=(agent_name, agent),
                    daemon=True
                )
                thread.start()
                self.agent_threads[agent_name] = thread
                self.running_agents.add(agent_name)
                logger.info(f"Agent {agent_name} started in background")
                return True
            else:
                # Run directly (blocking)
                logger.info(f"Running agent {agent_name}")
                agent.run()
                logger.info(f"Agent {agent_name} completed")
                return True
        except Exception as e:
            logger.error(f"Error running agent {agent_name}: {e}")
            return False
    
    def _run_agent_thread(self, agent_name: str, agent: Any):
        """
        Run an agent in a thread (internal method).
        
        Args:
            agent_name: Name of the agent
            agent: Agent instance
        """
        try:
            agent.run()
        except Exception as e:
            logger.error(f"Error in agent {agent_name} thread: {e}")
        finally:
            self.running_agents.discard(agent_name)
            logger.info(f"Agent {agent_name} thread completed")
    
    def stop_agent(self, agent_name: str) -> bool:
        """
        Stop a running agent.
        
        Args:
            agent_name: Name of the agent to stop
            
        Returns:
            True if stopped successfully, False otherwise
        """
        if agent_name not in self.running_agents:
            logger.warning(f"Agent {agent_name} is not running")
            return True
        
        try:
            agent = self.agents.get(agent_name)
            if agent and hasattr(agent, 'stop'):
                agent.stop()
                logger.info(f"Agent {agent_name} stopped")
                self.running_agents.discard(agent_name)
                return True
            else:
                logger.warning(f"Agent {agent_name} does not have a stop method")
                return False
        except Exception as e:
            logger.error(f"Error stopping agent {agent_name}: {e}")
            return False
    
    def restart_agent(self, agent_name: str) -> bool:
        """
        Restart a running agent.
        
        Args:
            agent_name: Name of the agent to restart
            
        Returns:
            True if restarted successfully, False otherwise
        """
        logger.info(f"Restarting agent {agent_name}")
        
        # Stop if running
        if agent_name in self.running_agents:
            if not self.stop_agent(agent_name):
                logger.error(f"Failed to stop agent {agent_name} for restart")
                return False
        
        # Start again
        return self.run_agent(agent_name, background=True)
    
    def run_all_agents(self, background: bool = True) -> Dict[str, bool]:
        """
        Run all available agents.
        
        Args:
            background: Whether to run in the background
            
        Returns:
            Dictionary of agent names to success status
        """
        agents = self.discover_agents()
        results = {}
        
        for agent_name in agents:
            results[agent_name] = self.run_agent(agent_name, background)
        
        logger.info(f"Run all agents: {sum(results.values())}/{len(results)} succeeded")
        return results
    
    def stop_all_agents(self) -> Dict[str, bool]:
        """
        Stop all running agents.
        
        Returns:
            Dictionary of agent names to success status
        """
        results = {}
        
        for agent_name in list(self.running_agents):
            results[agent_name] = self.stop_agent(agent_name)
        
        logger.info(f"Stop all agents: {sum(results.values())}/{len(results)} succeeded")
        return results
    
    def get_agent_status(self, agent_name: str) -> Dict[str, Any]:
        """
        Get the status of an agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Status dictionary
        """
        agent = self.agents.get(agent_name)
        
        if not agent:
            return {
                "name": agent_name,
                "running": False,
                "instantiated": False,
                "error": "Agent not instantiated"
            }
        
        try:
            if hasattr(agent, 'get_status'):
                # Use agent's own status method if available
                agent_status = agent.get_status()
                agent_status.update({
                    "name": agent_name,
                    "running": agent_name in self.running_agents,
                    "instantiated": True
                })
                return agent_status
            else:
                # Basic status
                return {
                    "name": agent_name,
                    "running": agent_name in self.running_agents,
                    "instantiated": True
                }
        except Exception as e:
            logger.error(f"Error getting status for agent {agent_name}: {e}")
            return {
                "name": agent_name,
                "running": agent_name in self.running_agents,
                "instantiated": True,
                "error": str(e)
            }
    
    def get_all_agent_statuses(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the status of all agents.
        
        Returns:
            Dictionary of agent names to status dictionaries
        """
        statuses = {}
        
        # Get status for instantiated agents
        for agent_name in self.agents:
            statuses[agent_name] = self.get_agent_status(agent_name)
        
        # Add discovered but not instantiated agents
        for agent_name in self.discover_agents():
            if agent_name not in statuses:
                statuses[agent_name] = {
                    "name": agent_name,
                    "running": False,
                    "instantiated": False
                }
        
        return statuses

# Global instance
launcher_agent_connector = LauncherAgentConnector()

def discover_agents() -> List[str]:
    """
    Discover available agents using the global connector.
    
    Returns:
        List of agent names
    """
    global launcher_agent_connector
    return launcher_agent_connector.discover_agents()

def run_agent(agent_name: str, background: bool = False) -> bool:
    """
    Run an agent by name using the global connector.
    
    Args:
        agent_name: Name of the agent to run
        background: Whether to run in the background
        
    Returns:
        True if started successfully, False otherwise
    """
    global launcher_agent_connector
    return launcher_agent_connector.run_agent(agent_name, background)

def stop_agent(agent_name: str) -> bool:
    """
    Stop a running agent using the global connector.
    
    Args:
        agent_name: Name of the agent to stop
        
    Returns:
        True if stopped successfully, False otherwise
    """
    global launcher_agent_connector
    return launcher_agent_connector.stop_agent(agent_name)

def restart_agent(agent_name: str) -> bool:
    """
    Restart a running agent using the global connector.
    
    Args:
        agent_name: Name of the agent to restart
        
    Returns:
        True if restarted successfully, False otherwise
    """
    global launcher_agent_connector
    return launcher_agent_connector.restart_agent(agent_name)

def run_all_agents(background: bool = True) -> Dict[str, bool]:
    """
    Run all available agents using the global connector.
    
    Args:
        background: Whether to run in the background
        
    Returns:
        Dictionary of agent names to success status
    """
    global launcher_agent_connector
    return launcher_agent_connector.run_all_agents(background)

def stop_all_agents() -> Dict[str, bool]:
    """
    Stop all running agents using the global connector.
    
    Returns:
        Dictionary of agent names to success status
    """
    global launcher_agent_connector
    return launcher_agent_connector.stop_all_agents()

def get_agent_status(agent_name: str) -> Dict[str, Any]:
    """
    Get the status of an agent using the global connector.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        Status dictionary
    """
    global launcher_agent_connector
    return launcher_agent_connector.get_agent_status(agent_name)

def get_all_agent_statuses() -> Dict[str, Dict[str, Any]]:
    """
    Get the status of all agents using the global connector.
    
    Returns:
        Dictionary of agent names to status dictionaries
    """
    global launcher_agent_connector
    return launcher_agent_connector.get_all_agent_statuses()