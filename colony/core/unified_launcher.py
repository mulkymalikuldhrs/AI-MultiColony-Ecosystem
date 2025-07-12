"""
Unified Launcher - Central entry point for the AI-MultiColony-Ecosystem
Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import os
import sys
import logging
import importlib
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

# Setup logger
logger = logging.getLogger("unified_launcher")

class UnifiedLauncher:
    """
    Unified launcher for the AI-MultiColony-Ecosystem.
    Provides a central entry point for all system components.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the unified launcher.
        
        Args:
            config_path: Path to the launcher configuration file (optional)
        """
        self.config_path = config_path or "config/launcher_config.yaml"
        self.config = self._load_config()
        
        # Import connectors
        self.web_ui_connector = self._import_connector("web_ui_connector")
        self.agent_connector = self._import_connector("launcher_agent_connector")
        self.engine_connector = self._import_connector("autonomous_engine_connector")
        
        logger.info("Unified launcher initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load launcher configuration from file.
        
        Returns:
            Configuration dictionary
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)
                logger.info(f"Loaded configuration from {self.config_path}")
                return config
            else:
                logger.warning(f"Configuration file not found: {self.config_path}")
                return {}
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return {}
    
    def _import_connector(self, connector_name: str) -> Optional[Any]:
        """
        Import a connector module.
        
        Args:
            connector_name: Name of the connector module
            
        Returns:
            Connector module or None if not found
        """
        try:
            module = importlib.import_module(f"colony.core.{connector_name}")
            logger.info(f"Imported connector: {connector_name}")
            return module
        except ImportError as e:
            logger.warning(f"Could not import connector {connector_name}: {e}")
            return None
    
    def start_web_ui(self, background: bool = True) -> bool:
        """
        Start the web UI.
        
        Args:
            background: Whether to run in the background
            
        Returns:
            True if started successfully, False otherwise
        """
        if self.web_ui_connector:
            # Get configuration
            port = self.config.get("web_interface", {}).get("port", 8080)
            host = self.config.get("web_interface", {}).get("host", "0.0.0.0")
            
            # Start web UI
            return self.web_ui_connector.start_web_ui(background, port, host)
        else:
            logger.error("Web UI connector not available")
            return False
    
    def stop_web_ui(self) -> bool:
        """
        Stop the web UI.
        
        Returns:
            True if stopped successfully, False otherwise
        """
        if self.web_ui_connector:
            return self.web_ui_connector.stop_web_ui()
        else:
            logger.error("Web UI connector not available")
            return False
    
    def start_agent(self, agent_name: str, background: bool = False) -> bool:
        """
        Start an agent.
        
        Args:
            agent_name: Name of the agent to start
            background: Whether to run in the background
            
        Returns:
            True if started successfully, False otherwise
        """
        if self.agent_connector:
            return self.agent_connector.run_agent(agent_name, background)
        else:
            logger.error("Agent connector not available")
            return False
    
    def stop_agent(self, agent_name: str) -> bool:
        """
        Stop an agent.
        
        Args:
            agent_name: Name of the agent to stop
            
        Returns:
            True if stopped successfully, False otherwise
        """
        if self.agent_connector:
            return self.agent_connector.stop_agent(agent_name)
        else:
            logger.error("Agent connector not available")
            return False
    
    def start_all_agents(self, background: bool = True) -> Dict[str, bool]:
        """
        Start all agents.
        
        Args:
            background: Whether to run in the background
            
        Returns:
            Dictionary of agent names to success status
        """
        if self.agent_connector:
            return self.agent_connector.run_all_agents(background)
        else:
            logger.error("Agent connector not available")
            return {}
    
    def stop_all_agents(self) -> Dict[str, bool]:
        """
        Stop all agents.
        
        Returns:
            Dictionary of agent names to success status
        """
        if self.agent_connector:
            return self.agent_connector.stop_all_agents()
        else:
            logger.error("Agent connector not available")
            return {}
    
    def start_engine(self, engine_name: str) -> bool:
        """
        Start an engine.
        
        Args:
            engine_name: Name of the engine to start
            
        Returns:
            True if started successfully, False otherwise
        """
        if self.engine_connector:
            return self.engine_connector.start_engine(engine_name)
        else:
            logger.error("Engine connector not available")
            return False
    
    def stop_engine(self, engine_name: str) -> bool:
        """
        Stop an engine.
        
        Args:
            engine_name: Name of the engine to stop
            
        Returns:
            True if stopped successfully, False otherwise
        """
        if self.engine_connector:
            return self.engine_connector.stop_engine(engine_name)
        else:
            logger.error("Engine connector not available")
            return False
    
    def start_all_engines(self) -> Dict[str, bool]:
        """
        Start all engines.
        
        Returns:
            Dictionary of engine names to success status
        """
        if self.engine_connector:
            return self.engine_connector.start_all_engines()
        else:
            logger.error("Engine connector not available")
            return {}
    
    def stop_all_engines(self) -> Dict[str, bool]:
        """
        Stop all engines.
        
        Returns:
            Dictionary of engine names to success status
        """
        if self.engine_connector:
            return self.engine_connector.stop_all_engines()
        else:
            logger.error("Engine connector not available")
            return {}
    
    def start_all(self, background: bool = True) -> Dict[str, Any]:
        """
        Start all components (web UI, agents, engines).
        
        Args:
            background: Whether to run in the background
            
        Returns:
            Dictionary of component types to success status
        """
        results = {
            "web_ui": self.start_web_ui(background),
            "agents": self.start_all_agents(background),
            "engines": self.start_all_engines()
        }
        
        logger.info(f"Started all components: web_ui={results['web_ui']}, agents={sum(results['agents'].values())}/{len(results['agents'])}, engines={sum(results['engines'].values())}/{len(results['engines'])}")
        return results
    
    def stop_all(self) -> Dict[str, Any]:
        """
        Stop all components (web UI, agents, engines).
        
        Returns:
            Dictionary of component types to success status
        """
        results = {
            "web_ui": self.stop_web_ui(),
            "agents": self.stop_all_agents(),
            "engines": self.stop_all_engines()
        }
        
        logger.info(f"Stopped all components: web_ui={results['web_ui']}, agents={sum(results['agents'].values())}/{len(results['agents'])}, engines={sum(results['engines'].values())}/{len(results['engines'])}")
        return results
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get the status of the entire system.
        
        Returns:
            System status dictionary
        """
        # Get web UI status
        web_ui_status = self.web_ui_connector.get_web_ui_status() if self.web_ui_connector else {"running": False, "error": "Web UI connector not available"}
        
        # Get agent statuses
        agent_statuses = self.agent_connector.get_all_agent_statuses() if self.agent_connector else {}
        
        # Get engine statuses
        engine_statuses = self.engine_connector.get_all_engine_statuses() if self.engine_connector else {}
        
        # Count running components
        running_agents = sum(1 for status in agent_statuses.values() if status.get("running", False))
        running_engines = sum(1 for status in engine_statuses.values() if status.get("running", False))
        
        # System info
        system_info = self.config.get("system", {})
        
        return {
            "system": {
                "name": system_info.get("name", "AI MultiColony Ecosystem"),
                "version": system_info.get("version", "7.2.0"),
                "owner": system_info.get("owner", "Mulky Malikul Dhaher"),
                "owner_id": system_info.get("owner_id", "1108151509970001"),
                "status": "running" if web_ui_status.get("running") or running_agents > 0 or running_engines > 0 else "stopped"
            },
            "components": {
                "web_ui": web_ui_status,
                "agents": {
                    "total": len(agent_statuses),
                    "running": running_agents,
                    "statuses": agent_statuses
                },
                "engines": {
                    "total": len(engine_statuses),
                    "running": running_engines,
                    "statuses": engine_statuses
                }
            }
        }

# Global instance
unified_launcher = UnifiedLauncher()

def start_web_ui(background: bool = True) -> bool:
    """
    Start the web UI using the global launcher.
    
    Args:
        background: Whether to run in the background
        
    Returns:
        True if started successfully, False otherwise
    """
    global unified_launcher
    return unified_launcher.start_web_ui(background)

def stop_web_ui() -> bool:
    """
    Stop the web UI using the global launcher.
    
    Returns:
        True if stopped successfully, False otherwise
    """
    global unified_launcher
    return unified_launcher.stop_web_ui()

def start_agent(agent_name: str, background: bool = False) -> bool:
    """
    Start an agent using the global launcher.
    
    Args:
        agent_name: Name of the agent to start
        background: Whether to run in the background
        
    Returns:
        True if started successfully, False otherwise
    """
    global unified_launcher
    return unified_launcher.start_agent(agent_name, background)

def stop_agent(agent_name: str) -> bool:
    """
    Stop an agent using the global launcher.
    
    Args:
        agent_name: Name of the agent to stop
        
    Returns:
        True if stopped successfully, False otherwise
    """
    global unified_launcher
    return unified_launcher.stop_agent(agent_name)

def start_all_agents(background: bool = True) -> Dict[str, bool]:
    """
    Start all agents using the global launcher.
    
    Args:
        background: Whether to run in the background
        
    Returns:
        Dictionary of agent names to success status
    """
    global unified_launcher
    return unified_launcher.start_all_agents(background)

def stop_all_agents() -> Dict[str, bool]:
    """
    Stop all agents using the global launcher.
    
    Returns:
        Dictionary of agent names to success status
    """
    global unified_launcher
    return unified_launcher.stop_all_agents()

def start_engine(engine_name: str) -> bool:
    """
    Start an engine using the global launcher.
    
    Args:
        engine_name: Name of the engine to start
        
    Returns:
        True if started successfully, False otherwise
    """
    global unified_launcher
    return unified_launcher.start_engine(engine_name)

def stop_engine(engine_name: str) -> bool:
    """
    Stop an engine using the global launcher.
    
    Args:
        engine_name: Name of the engine to stop
        
    Returns:
        True if stopped successfully, False otherwise
    """
    global unified_launcher
    return unified_launcher.stop_engine(engine_name)

def start_all_engines() -> Dict[str, bool]:
    """
    Start all engines using the global launcher.
    
    Returns:
        Dictionary of engine names to success status
    """
    global unified_launcher
    return unified_launcher.start_all_engines()

def stop_all_engines() -> Dict[str, bool]:
    """
    Stop all engines using the global launcher.
    
    Returns:
        Dictionary of engine names to success status
    """
    global unified_launcher
    return unified_launcher.stop_all_engines()

def start_all(background: bool = True) -> Dict[str, Any]:
    """
    Start all components using the global launcher.
    
    Args:
        background: Whether to run in the background
        
    Returns:
        Dictionary of component types to success status
    """
    global unified_launcher
    return unified_launcher.start_all(background)

def stop_all() -> Dict[str, Any]:
    """
    Stop all components using the global launcher.
    
    Returns:
        Dictionary of component types to success status
    """
    global unified_launcher
    return unified_launcher.stop_all()

def get_system_status() -> Dict[str, Any]:
    """
    Get the status of the entire system using the global launcher.
    
    Returns:
        System status dictionary
    """
    global unified_launcher
    return unified_launcher.get_system_status()