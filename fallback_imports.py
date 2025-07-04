#!/usr/bin/env python3
"""
🔧 Fallback Imports v7.0.0
Simplified implementations when external dependencies are not available

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import os
import sys
import json
import time
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# Environment Variables Fallback
class FallbackDotenv:
    """Fallback for python-dotenv"""
    
    @staticmethod
    def load_dotenv(dotenv_path=None):
        """Load environment variables from .env file"""
        try:
            env_file = dotenv_path or '.env'
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.strip() and not line.startswith('#'):
                            if '=' in line:
                                key, value = line.strip().split('=', 1)
                                os.environ[key] = value
                print("✅ Environment variables loaded (fallback)")
            else:
                print("⚠️ .env file not found (fallback)")
        except Exception as e:
            print(f"⚠️ Failed to load .env: {e}")

# HTTP Client Fallback
class FallbackAiohttp:
    """Fallback for aiohttp"""
    
    class ClientSession:
        def __init__(self):
            pass
        
        async def __aenter__(self):
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        
        async def post(self, url, headers=None, json=None, timeout=30):
            """Simulate HTTP POST"""
            return FallbackResponse(
                status=200,
                data={
                    "choices": [{
                        "message": {
                            "content": f"[Fallback Response] Simulated response for: {json.get('messages', [{}])[-1].get('content', 'No content')[:100]}..."
                        }
                    }],
                    "usage": {"total_tokens": 50}
                }
            )
    
    class FallbackResponse:
        def __init__(self, status: int, data: Dict):
            self.status = status
            self._data = data
        
        async def json(self):
            return self._data

# Flask Fallback
class FallbackFlask:
    """Simplified Flask fallback"""
    
    def __init__(self, name):
        self.name = name
        self.config = {}
        self.routes = {}
        
    def route(self, path, methods=None):
        def decorator(func):
            self.routes[path] = func
            return func
        return decorator
    
    def run(self, host='127.0.0.1', port=5000, debug=False):
        print(f"🌐 Fallback Flask server would run on http://{host}:{port}")
        print("⚠️ Web interface not available (Flask not installed)")

class FallbackSocketIO:
    """Simplified SocketIO fallback"""
    
    def __init__(self, app, cors_allowed_origins="*"):
        self.app = app
        self.events = {}
    
    def on(self, event):
        def decorator(func):
            self.events[event] = func
            return func
        return decorator
    
    def emit(self, event, data, room=None):
        print(f"📡 Would emit {event}: {data}")
    
    def run(self, app, host='127.0.0.1', port=5000, debug=False, **kwargs):
        print(f"🌐 Fallback SocketIO server would run on http://{host}:{port}")

def emit(event, data):
    """Fallback emit function"""
    print(f"📡 Would emit {event}: {data}")

# YAML Fallback
class FallbackYaml:
    """Simplified YAML fallback"""
    
    @staticmethod
    def safe_load(stream):
        """Basic YAML parser fallback"""
        try:
            # Very basic YAML parsing - convert to JSON-like structure
            if isinstance(stream, str):
                lines = stream.split('\n')
            else:
                lines = stream.read().split('\n')
            
            result = {}
            current_section = result
            stack = [result]
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if value:
                        # Try to parse value
                        if value.lower() in ['true', 'false']:
                            current_section[key] = value.lower() == 'true'
                        elif value.isdigit():
                            current_section[key] = int(value)
                        else:
                            current_section[key] = value
                    else:
                        # New section
                        current_section[key] = {}
                        current_section = current_section[key]
            
            return result
        except Exception as e:
            print(f"⚠️ YAML parsing failed: {e}")
            return {}

# System Information Fallback
class FallbackPsutil:
    """Simplified psutil fallback"""
    
    class VirtualMemory:
        def __init__(self):
            self.percent = 50  # Default 50%
    
    @staticmethod
    def virtual_memory():
        return FallbackPsutil.VirtualMemory()

# Colorama Fallback
class FallbackColorama:
    """Color printing fallback"""
    
    class Fore:
        RED = ''
        GREEN = ''
        YELLOW = ''
        BLUE = ''
        MAGENTA = ''
        CYAN = ''
        WHITE = ''
        RESET = ''
    
    class Style:
        BRIGHT = ''
        DIM = ''
        RESET_ALL = ''

# Requests Fallback
class FallbackRequests:
    """HTTP requests fallback"""
    
    class Response:
        def __init__(self, status_code=200, text="Fallback response"):
            self.status_code = status_code
            self.text = text
        
        def json(self):
            return {"message": "Fallback response", "status": "simulated"}
    
    @staticmethod
    def get(url, **kwargs):
        print(f"📡 Would GET {url}")
        return FallbackRequests.Response()
    
    @staticmethod
    def post(url, **kwargs):
        print(f"📡 Would POST {url}")
        return FallbackRequests.Response()

# Smart Import Function
def smart_import(module_name, fallback=None):
    """Import module with fallback"""
    try:
        return __import__(module_name)
    except ImportError:
        if fallback:
            print(f"⚠️ {module_name} not available, using fallback")
            return fallback
        else:
            print(f"❌ {module_name} not available and no fallback provided")
            raise

# Setup fallback modules
def setup_fallbacks():
    """Setup all fallback modules"""
    fallbacks = {
        'dotenv': FallbackDotenv(),
        'aiohttp': FallbackAiohttp(),
        'flask': FallbackFlask,
        'flask_socketio': type('FallbackModule', (), {
            'SocketIO': FallbackSocketIO,
            'emit': emit
        })(),
        'yaml': FallbackYaml(),
        'psutil': FallbackPsutil(),
        'colorama': FallbackColorama(),
        'requests': FallbackRequests()
    }
    
    # Add fallbacks to sys.modules if not already present
    for name, fallback in fallbacks.items():
        try:
            __import__(name)
        except ImportError:
            sys.modules[name] = fallback
    
    print("🔧 Fallback modules initialized")

# Enhanced Config Loader with Fallbacks
def load_config_with_fallbacks():
    """Load configuration with fallback mechanisms"""
    print("🔧 Loading configuration with fallbacks...")
    
    # Basic configuration structure
    default_config = {
        'system': {
            'name': 'Ultimate AGI Force',
            'version': '7.0.0',
            'author': 'Mulky Malikul Dhaher',
            'country': 'Indonesia 🇮🇩'
        },
        'core': {
            'prompt_master': {'enabled': True},
            'memory_bus': {'enabled': True},
            'sync_engine': {'enabled': True},
            'scheduler': {'enabled': True},
            'ai_selector': {'enabled': True}
        },
        'llm': {
            'primary_provider': 'llm7',
            'providers': {
                'llm7': {
                    'enabled': True,
                    'api_key': os.getenv('LLM7_API_KEY', 'demo-key'),
                    'base_url': 'https://api.llm7.com/v1',
                    'models': ['gpt-3.5-turbo']
                },
                'openrouter': {
                    'enabled': True,
                    'api_key': os.getenv('OPENROUTER_API_KEY', 'demo-key'),
                    'base_url': 'https://openrouter.ai/api/v1'
                },
                'camel': {
                    'enabled': True,
                    'api_key': os.getenv('CAMEL_API_KEY', 'demo-key'),
                    'base_url': 'https://api.camel-ai.org/v1'
                }
            }
        },
        'web_interface': {
            'enabled': True,
            'host': '0.0.0.0',
            'port': int(os.getenv('WEB_INTERFACE_PORT', '5000')),
            'debug': False,
            'security': {
                'secret_key': os.getenv('SECRET_KEY', 'ultimate-agi-secret-2024')
            }
        },
        'database': {
            'primary': {
                'type': 'sqlite',
                'url': 'sqlite:///data/agentic.db'
            }
        }
    }
    
    # Try to load from YAML if available
    config_file = 'config/system_config.yaml'
    if os.path.exists(config_file):
        try:
            import yaml
            with open(config_file, 'r') as f:
                file_config = yaml.safe_load(f)
            
            # Merge with defaults
            def merge_dict(default, override):
                for key, value in override.items():
                    if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                        merge_dict(default[key], value)
                    else:
                        default[key] = value
            
            merge_dict(default_config, file_config)
            print("✅ Configuration loaded from YAML file")
        except Exception as e:
            print(f"⚠️ Failed to load YAML config: {e}, using defaults")
    
    # Replace environment variables
    def replace_env_vars(obj):
        if isinstance(obj, dict):
            return {k: replace_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_env_vars(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
            env_var = obj[2:-1]
            return os.getenv(env_var, '')
        else:
            return obj
    
    config = replace_env_vars(default_config)
    
    print("✅ Configuration loaded with fallbacks")
    return config

if __name__ == "__main__":
    print("🔧 Testing fallback imports...")
    setup_fallbacks()
    config = load_config_with_fallbacks()
    print(f"✅ Config test: {config['system']['name']}")