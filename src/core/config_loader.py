import yaml
import os
import re
from dotenv import load_dotenv
from pathlib import Path

def _replace_env_vars(config_value):
    """Recursively replace environment variable placeholders in config."""
    if isinstance(config_value, str):
        # Regex to find ${VAR_NAME} or $VAR_NAME
        pattern = re.compile(r'\$\{(\w+)\}|\$(\w+)')
        
        def replace_match(match):
            # Find the first non-None group
            var_name = next((g for g in match.groups() if g is not None), None)
            if var_name:
                return os.getenv(var_name, '') # Return empty string if not found
            return match.group(0) # Should not happen with this pattern

        return pattern.sub(replace_match, config_value)
        
    elif isinstance(config_value, dict):
        return {k: _replace_env_vars(v) for k, v in config_value.items()}
    elif isinstance(config_value, list):
        return [_replace_env_vars(i) for i in config_value]
    else:
        return config_value

def load_config():
    """
    Loads the system configuration from YAML and environment variables.
    
    1. Loads .env file into environment variables.
    2. Loads the base configuration from config/system_config.yaml.
    3. Recursively replaces placeholders like ${VAR_NAME} with actual environment variables.
    
    Returns:
        A dictionary containing the fully resolved configuration.
    """
    # Load environment variables from .env file
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)

    # Load base YAML configuration
    config_path = Path('config') / 'system_config.yaml'
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Replace placeholders with environment variables
    resolved_config = _replace_env_vars(config)
    
    print("✅ Configuration loaded and resolved.")
    return resolved_config

# Singleton instance of the configuration
config = load_config()

if __name__ == '__main__':
    # Example of how to use the loaded config
    print("\n--- LLM Provider Config ---")
    print(f"Primary Provider: {config['llm']['primary_provider']}")
    print(f"LLM7 API Key: {config['llm']['providers']['llm7']['api_key']}")
    print(f"OpenRouter API Key: {config['llm']['providers']['openrouter']['api_key']}")
    print("\n--- Database Config ---")
    print(f"Database URL: {config['database']['primary']['url']}")
    print("\n--- Web Interface Config ---")
    print(f"Secret Key: {config['web_interface']['security']['secret_key']}")
