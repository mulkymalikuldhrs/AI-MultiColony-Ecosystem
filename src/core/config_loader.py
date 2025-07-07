#!/usr/bin/env python3
"""
🔧 Config Loader with Advanced Fallback Support
Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import os
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Advanced fallback imports
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    def load_dotenv(*args, **kwargs):
        """Fallback dotenv loader"""
        pass

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    
    class FallbackYAML:
        @staticmethod
        def safe_load(content):
            """Basic YAML fallback - converts simple YAML to dict"""
            if not content:
                return {}
            
            # Simple YAML parser for basic configs
            result = {}
            lines = content.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if ':' in line and not line.startswith('#'):
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    
                    # Convert boolean strings
                    if value.lower() == 'true':
                        value = True
                    elif value.lower() == 'false':
                        value = False
                    # Convert numeric strings
                    elif value.isdigit():
                        value = int(value)
                    elif value.replace('.', '').isdigit():
                        value = float(value)
                    
                    result[key] = value
            
            return result
    
    yaml = FallbackYAML()

class UltimateConfigLoader:
    """
    Ultimate Configuration Loader with Complete Fallback Support
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.config_dir = self.project_root / "config"
        self.env_file = self.project_root / ".env"
        self.logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Default configuration
        self.default_config = {
            'system': {
                'name': 'Ultimate AGI Force v7.0.0',
                'version': '7.0.0',
                'owner': 'Mulky Malikul Dhaher',
                'owner_id': '1108151509970001',
                'region': 'Indonesia'
            },
            'web_interface': {
                'host': '0.0.0.0',
                'port': 5000,
                'debug': True
            },
            'autonomous_engines': {
                'development': {
                    'enabled': True,
                    'cycle_interval': 300
                },
                'execution': {
                    'enabled': True,
                    'cycle_interval': 60
                },
                'improvement': {
                    'enabled': True,
                    'cycle_interval': 900
                }
            },
            'agents': {
                'max_concurrent': 500,
                'auto_scaling': True,
                'performance_monitoring': True
            },
            'api_keys': {
                'llm7': 'demo_key_llm7_indonesia',
                'openrouter': 'demo_key_openrouter_global',
                'camel': 'demo_key_camel_ai_collaboration'
            },
            'logging': {
                'level': 'INFO',
                'file_rotation': True,
                'max_log_size': '100MB'
            }
        }
        
        self.config = self.default_config.copy()
        self.load_configuration()
    
    def load_configuration(self):
        """Load configuration from multiple sources with fallbacks"""
        self.logger.info("🔧 Loading Ultimate AGI Force configuration...")
        
        # 1. Load environment variables
        self._load_env_file()
        self._load_env_variables()
        
        # 2. Load YAML configuration files
        self._load_yaml_configs()
        
        # 3. Apply environment overrides
        self._apply_env_overrides()
        
        self.logger.info("✅ Configuration loaded successfully with fallbacks")
    
    def _load_env_file(self):
        """Load .env file if available"""
        if DOTENV_AVAILABLE and self.env_file.exists():
            try:
                load_dotenv(self.env_file)
                self.logger.info(f"  ✅ Loaded .env file: {self.env_file}")
            except Exception as e:
                self.logger.warning(f"  ⚠️ Failed to load .env file: {e}")
        elif self.env_file.exists():
            # Manual .env parsing
            try:
                with open(self.env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip().strip('"\'')
                self.logger.info(f"  ✅ Manually parsed .env file: {self.env_file}")
            except Exception as e:
                self.logger.warning(f"  ⚠️ Failed to parse .env file: {e}")
        else:
            self.logger.info("  ℹ️ No .env file found, using defaults")
    
    def _load_env_variables(self):
        """Load configuration from environment variables"""
        env_mapping = {
            'SYSTEM_NAME': ['system', 'name'],
            'OWNER_NAME': ['system', 'owner'],
            'OWNER_ID': ['system', 'owner_id'],
            'REGION': ['system', 'region'],
            'WEB_INTERFACE_HOST': ['web_interface', 'host'],
            'WEB_INTERFACE_PORT': ['web_interface', 'port'],
            'DEBUG_MODE': ['web_interface', 'debug'],
            'LLM7_API_KEY': ['api_keys', 'llm7'],
            'OPENROUTER_API_KEY': ['api_keys', 'openrouter'],
            'CAMEL_API_KEY': ['api_keys', 'camel'],
            'LOG_LEVEL': ['logging', 'level'],
            'MAX_CONCURRENT_AGENTS': ['agents', 'max_concurrent']
        }
        
        for env_key, config_path in env_mapping.items():
            value = os.getenv(env_key)
            if value is not None:
                # Convert value to appropriate type with better logic
                value = self._convert_env_value(env_key, value)
                
                # Set nested configuration value
                current = self.config
                for key in config_path[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                current[config_path[-1]] = value
    
    def _convert_env_value(self, env_key: str, value: str) -> Any:
        """Convert environment variable value to appropriate type"""
        value_lower = value.lower()
        
        if value_lower in ('true', 'false'):
            return value_lower == 'true'
        elif value.isdigit():
            return int(value)
        elif value.replace('.', '', 1).isdigit(): # Check for float
            try:
                return float(value)
            except ValueError:
                pass # Fallback to string if float conversion fails
        return value
    
    def _load_yaml_configs(self):
        """Load YAML configuration files"""
        yaml_files = [
            'system_config.yaml',
            'agent_config.yaml',
            'deployment_config.yaml'
        ]
        
        for yaml_file in yaml_files:
            config_path = self.config_dir / yaml_file
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        yaml_config = yaml.safe_load(content)
                        if yaml_config:
                            self._merge_config(self.config, yaml_config)
                        self.logger.info(f"  ✅ Loaded YAML config: {yaml_file}")
                except Exception as e:
                    self.logger.warning(f"  ⚠️ Failed to load {yaml_file}: {e}")
            else:
                self.logger.info(f"  ℹ️ YAML config not found: {yaml_file}")
    
    def _apply_env_overrides(self):
        """Apply final environment variable overrides"""
        # Override critical settings from environment
        if 'WEB_INTERFACE_PORT' in os.environ:
            try:
                self.config['web_interface']['port'] = int(os.environ['WEB_INTERFACE_PORT'])
            except ValueError:
                pass
        
        if 'AUTONOMY_LEVEL' in os.environ:
            try:
                autonomy_level = int(os.environ['AUTONOMY_LEVEL'])
                self.config['autonomous_engines']['autonomy_level'] = autonomy_level
            except ValueError:
                pass
    
    def _merge_config(self, base_config, new_config):
        """Recursively merge configuration dictionaries"""
        for key, value in new_config.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._merge_config(base_config[key], value)
            else:
                base_config[key] = value
    
    def get(self, key_path, default=None):
        """Get configuration value using dot notation"""
        keys = key_path.split('.')
        current = self.config
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current
    
    def set(self, key_path, value):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        current = self.config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def get_api_key(self, provider):
        """Get API key for specific provider"""
        return self.get(f'api_keys.{provider}', f'demo_key_{provider}_fallback')
    
    def get_web_config(self):
        """Get web interface configuration"""
        return self.config.get('web_interface', {
            'host': '0.0.0.0',
            'port': 5000,
            'debug': True
        })
    
    def get_agent_config(self):
        """Get agent configuration"""
        return self.config.get('agents', {
            'max_concurrent': 500,
            'auto_scaling': True,
            'performance_monitoring': True
        })
    
    def get_autonomous_config(self):
        """Get autonomous engines configuration"""
        return self.config.get('autonomous_engines', {
            'development': {'enabled': True, 'cycle_interval': 300},
            'execution': {'enabled': True, 'cycle_interval': 60},
            'improvement': {'enabled': True, 'cycle_interval': 900}
        })
    
    def save_config(self, config_file='runtime_config.json'):
        """Save current configuration to file"""
        config_path = self.project_root / config_file
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.logger.info(f"✅ Configuration saved to: {config_path}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to save configuration: {e}")
            return False
    
    def print_config_summary(self):
        """Print configuration summary"""
        self.logger.info("\n" + "="*70)
        self.logger.info("🔧 Ultimate AGI Force v7.0.0 - Configuration Summary")
        self.logger.info("="*70)
        self.logger.info(f"👑 Owner: {self.get('system.owner')} ({self.get('system.owner_id')})")
        self.logger.info(f"🇮🇩 Region: {self.get('system.region')}")
        self.logger.info(f"🌐 Web Interface: {self.get('web_interface.host')}:{self.get('web_interface.port')}")
        self.logger.info(f"🤖 Max Agents: {self.get('agents.max_concurrent')}")
        self.logger.info(f"🔧 Development Engine: {'✅' if self.get('autonomous_engines.development.enabled') else '❌'}")
        self.logger.info(f"⚡ Execution Engine: {'✅' if self.get('autonomous_engines.execution.enabled') else '❌'}")
        self.logger.info(f"📈 Improvement Engine: {'✅' if self.get('autonomous_engines.improvement.enabled') else '❌'}")
        self.logger.info(f"🔑 API Keys: {len([k for k in self.get('api_keys', {}).keys()])} configured")
        self.logger.info("="*70)

# Create global configuration instance
config_loader = UltimateConfigLoader()
config = config_loader.config

# Convenience functions
def get_config(key_path, default=None):
    """Get configuration value"""
    return config_loader.get(key_path, default)

def get_api_key(provider):
    """Get API key for provider"""
    return config_loader.get_api_key(provider)

def get_web_config():
    """Get web configuration"""
    return config_loader.get_web_config()

def get_agent_config():
    """Get agent configuration"""
    return config_loader.get_agent_config()

def print_config_summary():
    """Print configuration summary"""
    config_loader.print_config_summary()

# Auto-load configuration
if __name__ == "__main__":
    config_loader.print_config_summary()
else:
    # Ensure logging is configured before this message
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.getLogger(__name__).info("🔧 Ultimate AGI Force configuration loaded with advanced fallbacks")
