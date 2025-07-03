"""
Configuration Manager for Autonomous Agent Colony
Handles loading and managing all system configurations
"""

import json
import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

class ConfigManager:
    """Manages system configuration"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.config_dir = self.project_root / "config"
        
        # Load environment variables
        load_dotenv(self.project_root / ".env")
    
    def load_config(self) -> Dict[str, Any]:
        """Load main configuration"""
        config_file = self.config_dir / "main_config.json"
        
        if not config_file.exists():
            return self._get_default_config()
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Override with environment variables
            self._apply_env_overrides(config)
            return config
            
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "system": {
                "name": "Autonomous Agent Colony",
                "version": "1.0.0",
                "environment": "development"
            },
            "models": {
                "default_provider": "openai",
                "providers": {
                    "openai": {
                        "api_key": os.getenv("OPENAI_API_KEY"),
                        "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                        "default_model": "gpt-4o-mini"
                    }
                }
            }
        }
    
    def _apply_env_overrides(self, config: Dict[str, Any]):
        """Apply environment variable overrides"""
        # Override API keys from environment
        if "models" in config and "providers" in config["models"]:
            providers = config["models"]["providers"]
            
            if "openai" in providers:
                providers["openai"]["api_key"] = os.getenv("OPENAI_API_KEY")
                providers["openai"]["base_url"] = os.getenv("OPENAI_BASE_URL", providers["openai"].get("base_url"))
            
            if "anthropic" in providers:
                providers["anthropic"]["api_key"] = os.getenv("ANTHROPIC_API_KEY")
            
            if "groq" in providers:
                providers["groq"]["api_key"] = os.getenv("GROQ_API_KEY")
