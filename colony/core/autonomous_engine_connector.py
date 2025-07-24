"""
Autonomous Engine Connector - Bridge between the unified launcher and autonomous engines
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
logger = logging.getLogger("autonomous_engine_connector")

class AutonomousEngineConnector:
    """
    Connector class to bridge the unified launcher with autonomous engines.
    Handles engine discovery, instantiation, and management.
    """
    
    def __init__(self):
        """Initialize the autonomous engine connector."""
        self.engines = {}  # Dictionary of engine instances
        self.engine_threads = {}  # Dictionary of engine threads
        self.running_engines = set()  # Set of running engine IDs
        
        # Default engine configurations
        self.engine_configs = {
            "AUTONOMOUS_DEVELOPMENT_ENGINE": {
                "enabled": True,
                "interval": 3600,  # 1 hour
                "description": "Autonomously develops new agents and capabilities"
            },
            "AUTONOMOUS_EXECUTION_ENGINE": {
                "enabled": True,
                "interval": 300,  # 5 minutes
                "description": "Executes tasks autonomously based on system goals"
            },
            "AUTONOMOUS_IMPROVEMENT_ENGINE": {
                "enabled": True,
                "interval": 1800,  # 30 minutes
                "description": "Continuously improves existing agents and systems"
            },
            "CONTINUOUS_IMPROVEMENT_CYCLE": {
                "enabled": True,
                "interval": 7200,  # 2 hours
                "description": "Meta-engine that coordinates all improvement activities"
            }
        }
    
    def discover_engines(self) -> List[str]:
        """
        Discover available engines.
        
        Returns:
            List of engine names
        """
        engines = []
        
        # Check for engine modules in colony/core
        core_dir = Path(__file__).parent
        
        for engine_name in self.engine_configs.keys():
            module_path = core_dir / f"{engine_name.lower()}.py"
            if module_path.exists():
                engines.append(engine_name)
                logger.info(f"Discovered engine: {engine_name}")
        
        logger.info(f"Discovered {len(engines)} engines")
        return engines
    
    def instantiate_engine(self, engine_name: str) -> Optional[Any]:
        """
        Instantiate an engine by name.
        
        Args:
            engine_name: Name of the engine to instantiate
            
        Returns:
            Engine instance or None if not found
        """
        try:
            # Convert engine name to module name (lowercase)
            module_name = engine_name.lower()
            
            # Try to import the module
            module_path = f"colony.core.{module_name}"
            module = importlib.import_module(module_path)
            
            # Check if the module has an Engine class
            if hasattr(module, "Engine"):
                engine_cls = getattr(module, "Engine")
                engine = engine_cls()
                self.engines[engine_name] = engine
                logger.info(f"Instantiated engine: {engine_name}")
                return engine
            
            # If no Engine class, check for start_engine function
            elif hasattr(module, "start_engine"):
                # Create a wrapper object
                class EngineWrapper:
                    def __init__(self, module):
                        self.module = module
                    
                    def start(self):
                        return self.module.start_engine()
                    
                    def stop(self):
                        if hasattr(self.module, "stop_engine"):
                            return self.module.stop_engine()
                        return True
                
                engine = EngineWrapper(module)
                self.engines[engine_name] = engine
                logger.info(f"Created wrapper for engine: {engine_name}")
                return engine
            
            else:
                logger.warning(f"Engine module {engine_name} has no Engine class or start_engine function")
                return None
        
        except ImportError:
            logger.warning(f"Engine module not found: {engine_name}")
            return None
        except Exception as e:
            logger.error(f"Error instantiating engine {engine_name}: {e}")
            return None
    
    def start_engine(self, engine_name: str) -> bool:
        """
        Start an engine by name.
        
        Args:
            engine_name: Name of the engine to start
            
        Returns:
            True if started successfully, False otherwise
        """
        # Check if engine is already running
        if engine_name in self.running_engines:
            logger.warning(f"Engine {engine_name} is already running")
            return True
        
        # Check if engine is enabled
        if not self.engine_configs.get(engine_name, {}).get("enabled", True):
            logger.warning(f"Engine {engine_name} is disabled")
            return False
        
        # Get or instantiate the engine
        engine = self.engines.get(engine_name)
        if not engine:
            engine = self.instantiate_engine(engine_name)
            if not engine:
                return False
        
        try:
            # Start in a background thread
            thread = threading.Thread(
                target=self._run_engine_thread,
                args=(engine_name, engine),
                daemon=True
            )
            thread.start()
            self.engine_threads[engine_name] = thread
            self.running_engines.add(engine_name)
            logger.info(f"Engine {engine_name} started")
            return True
        except Exception as e:
            logger.error(f"Error starting engine {engine_name}: {e}")
            return False
    
    def _run_engine_thread(self, engine_name: str, engine: Any):
        """
        Run an engine in a thread (internal method).
        
        Args:
            engine_name: Name of the engine
            engine: Engine instance
        """
        try:
            # Get interval from config
            interval = self.engine_configs.get(engine_name, {}).get("interval", 3600)
            
            logger.info(f"Engine {engine_name} thread started (interval: {interval}s)")
            
            while engine_name in self.running_engines:
                try:
                    # Start the engine
                    if hasattr(engine, "start"):
                        engine.start()
                    
                    # Sleep for the interval
                    logger.info(f"Engine {engine_name} cycle completed, sleeping for {interval}s")
                    time.sleep(interval)
                
                except Exception as cycle_e:
                    logger.error(f"Error in engine {engine_name} cycle: {cycle_e}")
                    time.sleep(60)  # Sleep for a minute before retrying
        
        except Exception as e:
            logger.error(f"Error in engine {engine_name} thread: {e}")
        
        finally:
            self.running_engines.discard(engine_name)
            logger.info(f"Engine {engine_name} thread stopped")
    
    def stop_engine(self, engine_name: str) -> bool:
        """
        Stop a running engine.
        
        Args:
            engine_name: Name of the engine to stop
            
        Returns:
            True if stopped successfully, False otherwise
        """
        if engine_name not in self.running_engines:
            logger.warning(f"Engine {engine_name} is not running")
            return True
        
        try:
            # Remove from running engines set
            self.running_engines.discard(engine_name)
            
            # Call stop method if available
            engine = self.engines.get(engine_name)
            if engine and hasattr(engine, "stop"):
                engine.stop()
            
            logger.info(f"Engine {engine_name} stopped")
            return True
        
        except Exception as e:
            logger.error(f"Error stopping engine {engine_name}: {e}")
            return False
    
    def start_all_engines(self) -> Dict[str, bool]:
        """
        Start all available engines.
        
        Returns:
            Dictionary of engine names to success status
        """
        engines = self.discover_engines()
        results = {}
        
        for engine_name in engines:
            if self.engine_configs.get(engine_name, {}).get("enabled", True):
                results[engine_name] = self.start_engine(engine_name)
            else:
                logger.info(f"Skipping disabled engine: {engine_name}")
                results[engine_name] = False
        
        logger.info(f"Start all engines: {sum(results.values())}/{len(results)} succeeded")
        return results
    
    def stop_all_engines(self) -> Dict[str, bool]:
        """
        Stop all running engines.
        
        Returns:
            Dictionary of engine names to success status
        """
        results = {}
        
        for engine_name in list(self.running_engines):
            results[engine_name] = self.stop_engine(engine_name)
        
        logger.info(f"Stop all engines: {sum(results.values())}/{len(results)} succeeded")
        return results
    
    def get_engine_status(self, engine_name: str) -> Dict[str, Any]:
        """
        Get the status of an engine.
        
        Args:
            engine_name: Name of the engine
            
        Returns:
            Status dictionary
        """
        # Get config
        config = self.engine_configs.get(engine_name, {})
        
        # Basic status
        status = {
            "name": engine_name,
            "running": engine_name in self.running_engines,
            "instantiated": engine_name in self.engines,
            "enabled": config.get("enabled", True),
            "interval": config.get("interval", 3600),
            "description": config.get("description", "")
        }
        
        return status
    
    def get_all_engine_statuses(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the status of all engines.
        
        Returns:
            Dictionary of engine names to status dictionaries
        """
        statuses = {}
        
        # Get status for all configured engines
        for engine_name in self.engine_configs:
            statuses[engine_name] = self.get_engine_status(engine_name)
        
        return statuses
    
    def update_engine_config(self, engine_name: str, config: Dict[str, Any]) -> bool:
        """
        Update the configuration of an engine.
        
        Args:
            engine_name: Name of the engine
            config: New configuration
            
        Returns:
            True if updated successfully, False otherwise
        """
        if engine_name not in self.engine_configs:
            logger.warning(f"Engine {engine_name} not found in configurations")
            return False
        
        try:
            # Update config
            self.engine_configs[engine_name].update(config)
            logger.info(f"Updated configuration for engine {engine_name}")
            
            # Restart if running and enabled/disabled changed
            if "enabled" in config and engine_name in self.running_engines and not config["enabled"]:
                self.stop_engine(engine_name)
            elif "enabled" in config and engine_name not in self.running_engines and config["enabled"]:
                self.start_engine(engine_name)
            
            return True
        
        except Exception as e:
            logger.error(f"Error updating configuration for engine {engine_name}: {e}")
            return False

# Global instance
autonomous_engine_connector = AutonomousEngineConnector()

def discover_engines() -> List[str]:
    """
    Discover available engines using the global connector.
    
    Returns:
        List of engine names
    """
    global autonomous_engine_connector
    return autonomous_engine_connector.discover_engines()

def start_engine(engine_name: str) -> bool:
    """
    Start an engine by name using the global connector.
    
    Args:
        engine_name: Name of the engine to start
        
    Returns:
        True if started successfully, False otherwise
    """
    global autonomous_engine_connector
    return autonomous_engine_connector.start_engine(engine_name)

def stop_engine(engine_name: str) -> bool:
    """
    Stop a running engine using the global connector.
    
    Args:
        engine_name: Name of the engine to stop
        
    Returns:
        True if stopped successfully, False otherwise
    """
    global autonomous_engine_connector
    return autonomous_engine_connector.stop_engine(engine_name)

def start_all_engines() -> Dict[str, bool]:
    """
    Start all available engines using the global connector.
    
    Returns:
        Dictionary of engine names to success status
    """
    global autonomous_engine_connector
    return autonomous_engine_connector.start_all_engines()

def stop_all_engines() -> Dict[str, bool]:
    """
    Stop all running engines using the global connector.
    
    Returns:
        Dictionary of engine names to success status
    """
    global autonomous_engine_connector
    return autonomous_engine_connector.stop_all_engines()

def get_engine_status(engine_name: str) -> Dict[str, Any]:
    """
    Get the status of an engine using the global connector.
    
    Args:
        engine_name: Name of the engine
        
    Returns:
        Status dictionary
    """
    global autonomous_engine_connector
    return autonomous_engine_connector.get_engine_status(engine_name)

def get_all_engine_statuses() -> Dict[str, Dict[str, Any]]:
    """
    Get the status of all engines using the global connector.
    
    Returns:
        Dictionary of engine names to status dictionaries
    """
    global autonomous_engine_connector
    return autonomous_engine_connector.get_all_engine_statuses()

def update_engine_config(engine_name: str, config: Dict[str, Any]) -> bool:
    """
    Update the configuration of an engine using the global connector.
    
    Args:
        engine_name: Name of the engine
        config: New configuration
        
    Returns:
        True if updated successfully, False otherwise
    """
    global autonomous_engine_connector
    return autonomous_engine_connector.update_engine_config(engine_name, config)