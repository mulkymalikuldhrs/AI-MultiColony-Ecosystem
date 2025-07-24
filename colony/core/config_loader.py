# colony/core/config_loader.py
import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
from typing import Any, Dict, Optional

class ConfigManager:
    """
    A centralized configuration manager that loads settings from a YAML file
    and overrides them with environment variables.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.config: Dict[str, Any] = {}
        self._load_config()
        self._initialized = True

    def _load_config(self):
        """Loads configuration from YAML and environment variables."""
        # Load .env file
        load_dotenv()

        # Base configuration from YAML
        config_path = Path(__file__).parent.parent / "config" / "system_config.yaml"
        if config_path.exists():
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f) or {}

        # Override with environment variables
        # This allows nested keys to be overridden using format: PARENT_CHILD_KEY=value
        for key, value in os.environ.items():
            keys = key.lower().split('_')
            d = self.config
            for k in keys[:-1]:
                d = d.setdefault(k, {})
            d[keys[-1]] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieves a configuration value.

        Args:
            key: The configuration key to retrieve (e.g., "server.port").
            default: The default value to return if the key is not found.

        Returns:
            The configuration value or the default.
        """
        keys = key.split('.')
        value = self.config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def reload(self):
        """Reloads the configuration."""
        self._load_config()

# Singleton instance
config = ConfigManager()

# For backward compatibility
def get_config(key: str, default: Any = None) -> Any:
    return config.get(key, default)
