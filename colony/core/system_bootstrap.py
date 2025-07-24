# colony/core/system_bootstrap.py
"""
System Bootstrap - Initialize and configure all system components
Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import logging
import sys
from colony.core.config_loader import config
from colony.core.agent_registry import reload_registry

def setup_logging():
    """Configure system-wide logging based on the loaded configuration."""
    log_level = config.get("logging.level", "INFO").upper()
    log_file = config.get("logging.file_path", "logs/colony_activity.log")

    # Create logs directory if it doesn't exist
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logging.getLogger("system_bootstrap").info(f"Logging system initialized at level {log_level}")

def bootstrap_system():
    """
    Main system bootstrap function. Initializes logging, configuration,
    and agent registry.
    """
    # 1. Setup logging
    setup_logging()
    logger = logging.getLogger("system_bootstrap")
    logger.info("🚀 Starting system bootstrap...")

    # 2. Configuration is already loaded by the singleton ConfigManager
    logger.info(f"✅ Configuration loaded for '{config.get('system.name', 'Unknown System')}'")

    # 3. Initialize agent registry
    logger.info("Discovering agents...")
    reload_registry()
    logger.info("✅ Agent registry initialized.")
    
    # Further initializations (like DB connections, memory manager, etc.) can go here.
    
    logger.info("✅ System bootstrap completed successfully.")
    return True

# For backward compatibility, aliasing the main function
bootstrap_systems = bootstrap_system