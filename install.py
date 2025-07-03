#!/usr/bin/env python3
"""
🚀 Autonomous Agent Colony - All-in-One Installer
Comprehensive setup script for the entire ecosystem
"""

import os
import sys
import subprocess
import json
import shutil
import platform
from pathlib import Path
import urllib.request
import zipfile
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutonomousColonyInstaller:
    def __init__(self):
        self.project_root = Path.cwd()
        self.system_os = platform.system().lower()
        self.python_version = sys.version_info
        self.required_python = (3, 11)
        
        # Installation paths
        self.config_dir = self.project_root / "config"
        self.data_dir = self.project_root / "data" 
        self.logs_dir = self.project_root / "logs"
        self.models_dir = self.project_root / "local_models"
        self.workspace_dir = self.project_root / "workspace"
        
        print(f"""
🐫 Autonomous Agent Colony System Installer
==========================================
🔧 System: {platform.system()} {platform.release()}
🐍 Python: {sys.version}
📁 Install Path: {self.project_root}
        """)
    
    def check_python_version(self):
        """Check if Python version is compatible"""
        print("🔍 Checking Python version...")
        if self.python_version < self.required_python:
            print(f"❌ Python {self.required_python[0]}.{self.required_python[1]}+ required!")
            print(f"   Current version: {self.python_version[0]}.{self.python_version[1]}")
            return False
        print(f"✅ Python version OK: {self.python_version[0]}.{self.python_version[1]}")
        return True
    
    def create_directory_structure(self):
        """Create necessary directory structure"""
        print("📁 Creating directory structure...")
        directories = [
            self.config_dir,
            self.data_dir,
            self.logs_dir,
            self.models_dir,
            self.workspace_dir,
            self.project_root / "repl_projects",
            self.project_root / "cursor_workspace",
            self.project_root / "autonomous_workspace",
            self.project_root / "docker",
            self.project_root / "tests",
            self.project_root / "scripts"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"   📂 Created: {directory}")
        
        print("✅ Directory structure created")
    
    def install_dependencies(self):
        """Install all required dependencies"""
        print("📦 Installing dependencies...")
        
        # Upgrade pip first
        print("   ⬆️ Upgrading pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=False)
        
        # Core dependencies
        core_deps = [
            "camel-ai[all]>=0.2.0",
            "fastapi>=0.115.0",
            "uvicorn[standard]>=0.30.0",
            "websockets>=13.0",
            "aiohttp>=3.10.0",
            "aiofiles>=24.1.0",
            "docker>=7.1.0",
            "redis>=5.1.0",
            "asyncio-mqtt>=0.16.0"
        ]
        
        # AI/ML dependencies
        ai_deps = [
            "transformers>=4.45.0",
            "torch>=2.1.0",
            "sentence-transformers>=3.0.0",
            "openai>=1.50.0",
            "anthropic>=0.21.0",
            "google-generativeai>=0.8.0"
        ]
        
        # Development dependencies
        dev_deps = [
            "jinja2>=3.1.4",
            "pyyaml>=6.0.2",
            "python-dotenv>=1.0.1",
            "rich>=13.8.0",
            "typer>=0.12.0",
            "loguru>=0.7.2"
        ]
        
        # Data processing
        data_deps = [
            "pandas>=2.2.0",
            "numpy>=2.1.0",
            "sqlite3",  # Built-in
            "chromadb>=0.5.0",
            "faiss-cpu>=1.8.0"
        ]
        
        all_deps = core_deps + ai_deps + dev_deps + data_deps
        
        for dep in all_deps:
            if dep == "sqlite3":  # Skip built-in modules
                continue
            print(f"   📦 Installing {dep}...")
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", dep
                ], check=True, capture_output=True)
                print(f"   ✅ {dep} installed")
            except subprocess.CalledProcessError as e:
                print(f"   ⚠️ Failed to install {dep}: {e}")
        
        print("✅ Dependencies installation completed")
    
    def create_environment_file(self):
        """Create .env file with default configuration"""
        print("🔧 Creating environment configuration...")
        
        env_content = """# Autonomous Agent Colony Configuration
# ===========================================

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# Anthropic Configuration  
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_BASE_URL=https://api.anthropic.com

# Google AI Configuration
GOOGLE_API_KEY=your_google_api_key_here

# DeepSeek Configuration (Free/Open)
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# Groq Configuration (Free)
GROQ_API_KEY=your_groq_api_key_here
GROQ_BASE_URL=https://api.groq.com/openai/v1

# Together AI Configuration
TOGETHER_API_KEY=your_together_api_key_here
TOGETHER_BASE_URL=https://api.together.xyz/v1

# Ollama Local Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# System Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
MAX_WORKERS=4
TIMEOUT_SECONDS=300

# Database Configuration
DATABASE_URL=sqlite:///./data/autonomous_colony.db
REDIS_URL=redis://localhost:6379

# Security Configuration
SECRET_KEY=your_secret_key_here
ENCRYPTION_KEY=your_encryption_key_here
SANDBOX_MODE=true

# Colony Configuration
COLONY_ID=autonomous_colony_001
MASTER_AGENT_MODEL=gpt-4o-mini
DEFAULT_MODEL_PROVIDER=openai
ENABLE_LOCAL_MODELS=true

# Features Configuration
ENABLE_CURSOR_FEATURES=true
ENABLE_REPLIT_FEATURES=true
ENABLE_MANUS_FEATURES=true
ENABLE_BACKGROUND_AGENTS=true
ENABLE_AUTO_SCALING=true
"""
        
        env_file = self.project_root / ".env"
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"✅ Environment file created: {env_file}")
        print("   📝 Please edit .env file with your API keys")
    
    def create_main_config(self):
        """Create main configuration file"""
        print("⚙️ Creating main configuration...")
        
        config = {
            "system": {
                "name": "Autonomous Agent Colony",
                "version": "1.0.0",
                "environment": "development",
                "debug": True
            },
            "colony": {
                "id": "autonomous_colony_001",
                "max_agents": 50,
                "auto_scaling": True,
                "health_check_interval": 60
            },
            "models": {
                "default_provider": "openai",
                "fallback_provider": "groq",
                "local_models_enabled": True,
                "model_rotation": True,
                "providers": {
                    "openai": {
                        "models": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
                        "default_model": "gpt-4o-mini"
                    },
                    "anthropic": {
                        "models": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
                        "default_model": "claude-3-haiku-20240307"
                    },
                    "groq": {
                        "models": ["llama-3.1-8b-instant", "mixtral-8x7b-32768"],
                        "default_model": "llama-3.1-8b-instant"
                    },
                    "deepseek": {
                        "models": ["deepseek-chat", "deepseek-coder"],
                        "default_model": "deepseek-chat"
                    }
                }
            },
            "features": {
                "cursor_like_editor": {
                    "enabled": True,
                    "ai_completion": True,
                    "background_agents": True,
                    "intelligent_refactoring": True
                },
                "replit_like_collab": {
                    "enabled": True,
                    "ghostwriter": True,
                    "multi_agent_collab": True,
                    "project_environments": True
                },
                "manus_like_super_agent": {
                    "enabled": True,
                    "ensemble_reasoning": True,
                    "autonomous_processing": True,
                    "self_learning": True
                }
            },
            "security": {
                "sandbox_mode": True,
                "encryption_enabled": True,
                "audit_logging": True,
                "rate_limiting": True
            },
            "performance": {
                "max_concurrent_requests": 100,
                "request_timeout": 300,
                "memory_limit_gb": 8,
                "cpu_limit_cores": 4
            }
        }
        
        config_file = self.config_dir / "main_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Main configuration created: {config_file}")
    
    def create_launcher_script(self):
        """Create main launcher script"""
        print("🚀 Creating main launcher...")
        
        launcher_content = '''#!/usr/bin/env python3
"""
🚀 Autonomous Agent Colony - Main Launcher
Entry point for the entire system
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import all main components
from src.main_controller import AutonomousColonyController
from src.utils.logger import setup_logger
from src.utils.config_manager import ConfigManager

async def main():
    """Main entry point for Autonomous Agent Colony"""
    try:
        print("""
🐫 Autonomous Agent Colony System Starting...
=============================================
        """)
        
        # Setup logging
        logger = setup_logger()
        logger.info("Starting Autonomous Agent Colony System")
        
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Initialize main controller
        controller = AutonomousColonyController(config)
        
        # Start the system
        await controller.start()
        
        print("✅ System started successfully!")
        print("🌐 Web interface: http://localhost:8000")
        print("📚 API docs: http://localhost:8000/docs")
        print("🔧 Admin panel: http://localhost:8000/admin")
        
        # Keep running
        await controller.run_forever()
        
    except KeyboardInterrupt:
        print("\\n🛑 Shutting down gracefully...")
        await controller.shutdown()
    except Exception as e:
        print(f"❌ Error starting system: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        launcher_file = self.project_root / "main.py"
        with open(launcher_file, 'w') as f:
            f.write(launcher_content)
        
        # Make executable on Unix systems
        if self.system_os in ['linux', 'darwin']:
            os.chmod(launcher_file, 0o755)
        
        print(f"✅ Main launcher created: {launcher_file}")
    
    def create_source_structure(self):
        """Create source code structure"""
        print("📂 Creating source code structure...")
        
        src_dir = self.project_root / "src"
        src_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        subdirs = [
            "agents",
            "models", 
            "tools",
            "memory",
            "tasks",
            "utils",
            "api",
            "web",
            "skills"
        ]
        
        for subdir in subdirs:
            (src_dir / subdir).mkdir(exist_ok=True)
            # Create __init__.py files
            with open(src_dir / subdir / "__init__.py", 'w') as f:
                f.write(f'"""\\n{subdir.title()} module for Autonomous Agent Colony\\n"""\\n')
        
        print(f"✅ Source structure created in: {src_dir}")
    
    def create_main_controller(self):
        """Create main system controller"""
        print("🎛️ Creating main controller...")
        
        controller_content = '''"""
Main Controller for Autonomous Agent Colony System
Orchestrates all components and manages the entire ecosystem
"""

import asyncio
import signal
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from .utils.config_manager import ConfigManager
from .utils.logger import get_logger
from .agents.agent_manager import AgentManager
from .models.model_manager import ModelManager
from .skills.cursor_like_editor import CursorLikeCodeEditor
from .skills.replit_like_collab import ReplitLikeCollaborativeEnvironment
from .skills.manus_like_super_agent import ManusLikeSuperAgent
from .api.api_server import APIServer
from .web.web_interface import WebInterface

logger = get_logger(__name__)

class AutonomousColonyController:
    """Main controller for the autonomous agent colony system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.running = False
        self.components = {}
        
        # Initialize managers
        self.model_manager = ModelManager(config.get("models", {}))
        self.agent_manager = AgentManager(config.get("colony", {}))
        
        # Initialize skills
        self.cursor_editor = CursorLikeCodeEditor()
        self.replit_collab = ReplitLikeCollaborativeEnvironment()
        self.manus_super_agent = ManusLikeSuperAgent()
        
        # Initialize API and Web interface
        self.api_server = APIServer(self)
        self.web_interface = WebInterface(self)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    async def start(self):
        """Start all system components"""
        try:
            logger.info("Starting Autonomous Colony Controller")
            
            # Start model manager
            await self.model_manager.initialize()
            logger.info("✅ Model manager initialized")
            
            # Start agent manager
            await self.agent_manager.initialize()
            logger.info("✅ Agent manager initialized")
            
            # Initialize skills
            await self.cursor_editor.initialize()
            await self.replit_collab.initialize_project_environment()
            await self.manus_super_agent.initialize_super_agent()
            logger.info("✅ All skills initialized")
            
            # Start API server
            await self.api_server.start()
            logger.info("✅ API server started")
            
            # Start web interface
            await self.web_interface.start()
            logger.info("✅ Web interface started")
            
            self.running = True
            logger.info("🚀 Autonomous Colony System fully operational!")
            
        except Exception as e:
            logger.error(f"Failed to start system: {e}")
            raise
    
    async def run_forever(self):
        """Keep the system running"""
        while self.running:
            try:
                # Health check all components
                await self._health_check()
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(5)
    
    async def shutdown(self):
        """Gracefully shutdown all components"""
        logger.info("Shutting down Autonomous Colony System...")
        self.running = False
        
        # Shutdown in reverse order
        if hasattr(self, 'web_interface'):
            await self.web_interface.stop()
            
        if hasattr(self, 'api_server'):
            await self.api_server.stop()
            
        if hasattr(self, 'agent_manager'):
            await self.agent_manager.shutdown()
            
        if hasattr(self, 'model_manager'):
            await self.model_manager.shutdown()
        
        logger.info("✅ System shutdown complete")
    
    async def _health_check(self):
        """Perform health check on all components"""
        try:
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "model_manager": await self.model_manager.health_check(),
                "agent_manager": await self.agent_manager.health_check(),
                "api_server": self.api_server.is_healthy(),
                "web_interface": self.web_interface.is_healthy()
            }
            
            # Log any unhealthy components
            for component, status in health_status.items():
                if component != "timestamp" and not status:
                    logger.warning(f"Component {component} is unhealthy")
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating shutdown...")
        self.running = False
    
    # Public API methods for external access
    async def process_request(self, request_type: str, data: Dict[str, Any]):
        """Process external requests"""
        try:
            if request_type == "cursor_completion":
                return await self.cursor_editor.ai_code_completion(
                    data.get("file_path", ""),
                    data.get("code_context", ""),
                    data.get("cursor_position", 0)
                )
            
            elif request_type == "replit_coding":
                return await self.replit_collab.ghostwriter_auto_coding(
                    data.get("prompt", ""),
                    data.get("context", "")
                )
            
            elif request_type == "manus_processing":
                return await self.manus_super_agent.autonomous_super_processing(
                    data.get("task", "")
                )
            
            else:
                return {"error": f"Unknown request type: {request_type}"}
                
        except Exception as e:
            logger.error(f"Request processing failed: {e}")
            return {"error": str(e)}
    
    def get_system_status(self):
        """Get current system status"""
        return {
            "running": self.running,
            "uptime": datetime.now().isoformat(),
            "components": {
                "model_manager": bool(self.model_manager),
                "agent_manager": bool(self.agent_manager),
                "cursor_editor": bool(self.cursor_editor),
                "replit_collab": bool(self.replit_collab),
                "manus_super_agent": bool(self.manus_super_agent),
                "api_server": bool(self.api_server),
                "web_interface": bool(self.web_interface)
            }
        }
'''
        
        controller_file = self.project_root / "src" / "main_controller.py"
        with open(controller_file, 'w') as f:
            f.write(controller_content)
        
        print(f"✅ Main controller created: {controller_file}")
    
    def create_essential_utilities(self):
        """Create essential utility modules"""
        print("🔧 Creating utility modules...")
        
        utils_dir = self.project_root / "src" / "utils"
        
        # Config Manager
        config_manager_content = '''"""
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
'''
        
        with open(utils_dir / "config_manager.py", 'w') as f:
            f.write(config_manager_content)
        
        # Logger utility
        logger_content = '''"""
Logging utilities for Autonomous Agent Colony
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logger():
    """Setup main system logger"""
    project_root = Path(__file__).parent.parent.parent
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup file handler
    log_file = logs_dir / f"colony_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Setup root logger
    logger = logging.getLogger("autonomous_colony")
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str):
    """Get logger for specific module"""
    return logging.getLogger(f"autonomous_colony.{name}")
'''
        
        with open(utils_dir / "logger.py", 'w') as f:
            f.write(logger_content)
        
        print("✅ Utility modules created")
    
    def run_post_install_tests(self):
        """Run basic tests to verify installation"""
        print("🧪 Running post-installation tests...")
        
        tests = [
            ("Python imports", self._test_python_imports),
            ("Configuration files", self._test_config_files),
            ("Directory structure", self._test_directory_structure),
            ("Dependencies", self._test_dependencies)
        ]
        
        all_passed = True
        for test_name, test_func in tests:
            try:
                result = test_func()
                if result:
                    print(f"   ✅ {test_name}")
                else:
                    print(f"   ❌ {test_name}")
                    all_passed = False
            except Exception as e:
                print(f"   ❌ {test_name}: {e}")
                all_passed = False
        
        if all_passed:
            print("✅ All tests passed!")
        else:
            print("⚠️ Some tests failed. Check the output above.")
        
        return all_passed
    
    def _test_python_imports(self):
        """Test if key Python modules can be imported"""
        try:
            import asyncio
            import json
            import pathlib
            return True
        except ImportError:
            return False
    
    def _test_config_files(self):
        """Test if configuration files exist"""
        required_files = [
            self.project_root / ".env",
            self.config_dir / "main_config.json",
            self.project_root / "main.py"
        ]
        
        return all(f.exists() for f in required_files)
    
    def _test_directory_structure(self):
        """Test if directory structure is correct"""
        required_dirs = [
            self.config_dir,
            self.data_dir,
            self.logs_dir,
            self.project_root / "src"
        ]
        
        return all(d.exists() and d.is_dir() for d in required_dirs)
    
    def _test_dependencies(self):
        """Test if key dependencies are installed"""
        try:
            import fastapi
            import uvicorn
            import asyncio
            return True
        except ImportError:
            return False
    
    def run_installation(self):
        """Run complete installation process"""
        print("🚀 Starting Autonomous Agent Colony Installation...")
        
        try:
            # Step 1: Check Python version
            if not self.check_python_version():
                return False
            
            # Step 2: Create directory structure
            self.create_directory_structure()
            
            # Step 3: Install dependencies
            self.install_dependencies()
            
            # Step 4: Create configuration files
            self.create_environment_file()
            self.create_main_config()
            
            # Step 5: Create source code structure
            self.create_source_structure()
            self.create_main_controller()
            self.create_essential_utilities()
            
            # Step 6: Create launcher
            self.create_launcher_script()
            
            # Step 7: Run tests
            if not self.run_post_install_tests():
                print("⚠️ Installation completed with warnings")
            
            print(f"""
🎉 Installation Complete!
========================

✅ Autonomous Agent Colony System installed successfully!

📁 Installation directory: {self.project_root}
🔧 Configuration: {self.config_dir}
📝 Logs: {self.logs_dir}

🚀 Next Steps:
1. Edit .env file with your API keys: {self.project_root}/.env
2. Review configuration: {self.config_dir}/main_config.json
3. Start the system: python main.py

🌐 After starting, visit:
   - Web interface: http://localhost:8000
   - API docs: http://localhost:8000/docs

📚 Documentation and examples in the project directory.

Happy coding with your Autonomous Agent Colony! 🐫🚀
            """)
            
            return True
            
        except Exception as e:
            print(f"❌ Installation failed: {e}")
            return False

def main():
    """Main installation function"""
    installer = AutonomousColonyInstaller()
    success = installer.run_installation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()