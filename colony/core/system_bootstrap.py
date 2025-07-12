# colony/core/system_bootstrap.py
"""
System Bootstrap - Initialize and configure all system components
Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import os
import sys
import logging
import importlib
from pathlib import Path

# Setup logging
def setup_logging():
    """Configure system-wide logging"""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/colony_activity.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger("system_bootstrap")
    logger.info("Logging system initialized")
    return logger

# Create necessary directories
def create_directories():
    """Create necessary system directories"""
    directories = [
        "logs",
        "data",
        "data/task_queue",
        "agent_output",
        "projects"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    logger = logging.getLogger("system_bootstrap")
    logger.info(f"Created system directories: {', '.join(directories)}")

# Import and initialize agent registry
def initialize_agent_registry():
    """Initialize the agent registry and discover agents"""
    try:
        # Try to import from colony.core first
        from colony.core.agent_registry import discover_agents
        discover_agents()
        logger = logging.getLogger("system_bootstrap")
        logger.info("Agent registry initialized from colony.core")
    except (ImportError, AttributeError):
        try:
            # Try to import from colony.agents as fallback
            from colony.agents.agent_registry import agent_registry
            logger = logging.getLogger("system_bootstrap")
            logger.info("Agent registry initialized from colony.agents")
        except ImportError as e:
            logger = logging.getLogger("system_bootstrap")
            logger.error(f"Failed to initialize agent registry: {e}")
            raise

# Initialize core components
def initialize_core_components():
    """Initialize essential system components"""
    logger = logging.getLogger("system_bootstrap")
    
    # List of core components to initialize
    core_components = [
        "colony.core.agent_manager.AgentManager",
        "colony.core.memory_manager.MemoryManager",
        "colony.core.memory_bus.MemoryBus",
        "colony.core.prompt_master.PromptMaster",
        "colony.core.scheduler.Scheduler"
    ]
    
    initialized_components = []
    
    for component_path in core_components:
        try:
            # Split into module path and class name
            module_path, class_name = component_path.rsplit(".", 1)
            
            # Try to import the module
            module = importlib.import_module(module_path)
            
            # Get the class and initialize it
            component_class = getattr(module, class_name)
            component = component_class()
            
            # Store in initialized components
            initialized_components.append((class_name, component))
            logger.info(f"Initialized {class_name}")
        except (ImportError, AttributeError) as e:
            logger.warning(f"Could not initialize {component_path}: {e}")
    
    return initialized_components

# Load configuration
def load_configuration():
    """Load system configuration from files"""
    logger = logging.getLogger("system_bootstrap")
    
    try:
        # Try to import config loader
        from colony.core.config_loader import load_config
        config = load_config()
        logger.info("Configuration loaded successfully")
        return config
    except ImportError:
        logger.warning("Config loader not found, using default configuration")
        return {"system": {"name": "AI MultiColony Ecosystem", "version": "7.2.0"}}

# Initialize LLM providers
def initialize_llm_providers():
    """Initialize LLM providers and gateway"""
    logger = logging.getLogger("system_bootstrap")
    
    try:
        # Try to import LLM gateway
        from connectors.llm_gateway import initialize_llm_gateway
        llm_gateway = initialize_llm_gateway()
        logger.info("LLM Gateway initialized")
        return llm_gateway
    except ImportError:
        logger.warning("LLM Gateway not found, LLM functionality will be limited")
        return None

# Main bootstrap function
def bootstrap_systems():
    """Main system bootstrap function"""
    # Setup logging first
    logger = setup_logging()
    logger.info("Starting system bootstrap")
    
    # Create necessary directories
    create_directories()
    
    # Load configuration
    config = load_configuration()
    logger.info(f"Loaded configuration for {config.get('system', {}).get('name', 'Unknown System')}")
    
    # Initialize agent registry
    initialize_agent_registry()
    
    # Initialize core components
    components = initialize_core_components()
    logger.info(f"Initialized {len(components)} core components")
    
    # Initialize LLM providers
    llm_gateway = initialize_llm_providers()
    
    # Set environment variables if needed (don't override if already set)
    if "WEB_INTERFACE_PORT" not in os.environ:
        os.environ["WEB_INTERFACE_PORT"] = "8080"
    
    if "WEB_INTERFACE_HOST" not in os.environ:
        os.environ["WEB_INTERFACE_HOST"] = "0.0.0.0"
    
    logger.info("System bootstrap completed successfully")
    return {
        "config": config,
        "components": components,
        "llm_gateway": llm_gateway
    }