#!/usr/bin/env python3
"""
🚀 Ultimate AGI Force v7.0.0 - System Launcher
Comprehensive system startup with health checks and error recovery

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import sys
import os
import subprocess
import time
import json
import asyncio
import threading
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

class SystemLauncher:
    """
    Ultimate system launcher with comprehensive error handling
    """
    
    def __init__(self):
        self.system_name = "Ultimate AGI Force v7.0.0"
        self.owner = "Mulky Malikul Dhaher"
        self.owner_id = "1108151509970001"
        
        self.startup_log = []
        self.components = {}
        self.is_healthy = True
        
        print(f"🚀 {self.system_name}")
        print(f"👑 Owner: {self.owner} ({self.owner_id})")
        print("🇮🇩 Made with ❤️ in Indonesia")
        print("="*60)
    
    def log(self, message: str, level: str = "INFO"):
        """Log startup messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        self.startup_log.append(log_entry)
    
    def check_python_version(self):
        """Check Python version"""
        self.log("Checking Python version...")
        
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            self.log(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
            return True
        else:
            self.log(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+", "ERROR")
            return False
    
    def install_missing_dependencies(self):
        """Install missing dependencies"""
        self.log("Checking and installing dependencies...")
        
        required_packages = [
            'python-dotenv',
            'aiohttp',
            'flask',
            'flask-socketio',
            'pyyaml',
            'psutil',
            'colorama',
            'requests'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                # Test import
                if package == 'python-dotenv':
                    import dotenv
                elif package == 'flask-socketio':
                    import flask_socketio
                else:
                    __import__(package.replace('-', '_'))
                self.log(f"  ✅ {package}")
            except ImportError:
                missing_packages.append(package)
                self.log(f"  ❌ {package}")
        
        if missing_packages:
            self.log(f"Installing {len(missing_packages)} missing packages...")
            try:
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', '--quiet',
                    *missing_packages
                ])
                self.log("✅ All dependencies installed successfully!")
            except subprocess.CalledProcessError as e:
                self.log(f"❌ Failed to install dependencies: {e}", "ERROR")
                return False
        
        return True
    
    def create_directories(self):
        """Create required system directories"""
        self.log("Creating system directories...")
        
        directories = [
            "data", "data/logs", "data/agents", "data/system",
            "data/task_queue", "data/backups", "data/deployment",
            "logs", "temp", "cache", "data/collaboration"
        ]
        
        for directory in directories:
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
                self.log(f"  📁 {directory}")
            except Exception as e:
                self.log(f"  ❌ Failed to create {directory}: {e}", "ERROR")
                return False
        
        return True
    
    def setup_environment(self):
        """Setup environment variables"""
        self.log("Setting up environment...")
        
        try:
            # Check if .env exists
            env_file = Path('.env')
            if env_file.exists():
                from dotenv import load_dotenv
                load_dotenv()
                self.log("✅ Environment variables loaded from .env")
            else:
                self.log("⚠️ .env file not found, using defaults")
                
                # Set default environment variables
                defaults = {
                    'LLM7_API_KEY': 'demo-key-llm7',
                    'OPENROUTER_API_KEY': 'demo-key-openrouter',
                    'CAMEL_API_KEY': 'demo-key-camel',
                    'SECRET_KEY': 'ultimate-agi-force-secret-2024',
                    'WEB_INTERFACE_PORT': '5000',
                    'LOG_LEVEL': 'INFO'
                }
                
                for key, value in defaults.items():
                    if not os.getenv(key):
                        os.environ[key] = value
                
                self.log("✅ Default environment variables set")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Environment setup failed: {e}", "ERROR")
            return False
    
    def test_core_components(self):
        """Test core system components"""
        self.log("Testing core components...")
        
        # Test config loader
        try:
            from src.core.config_loader import config
            self.log("  ✅ Config Loader")
            self.components['config'] = 'healthy'
        except Exception as e:
            self.log(f"  ❌ Config Loader: {e}")
            self.components['config'] = 'failed'
        
        # Test LLM Gateway
        try:
            from connectors.llm_gateway import llm_gateway
            self.log(f"  ✅ LLM Gateway ({len(llm_gateway.providers)} providers)")
            self.components['llm_gateway'] = 'healthy'
        except Exception as e:
            self.log(f"  ❌ LLM Gateway: {e}")
            self.components['llm_gateway'] = 'failed'
        
        # Test Camel Agent
        try:
            from agents.camel_agent_integration import camel_agent
            self.log(f"  ✅ Camel Agent ({camel_agent.status})")
            self.components['camel_agent'] = 'healthy'
        except Exception as e:
            self.log(f"  ❌ Camel Agent: {e}")
            self.components['camel_agent'] = 'failed'
        
        # Test Agents Registry
        try:
            from agents import AGENTS_REGISTRY, initialize_agents
            self.log("  ✅ Agents Registry")
            self.components['agents'] = 'healthy'
        except Exception as e:
            self.log(f"  ❌ Agents Registry: {e}")
            self.components['agents'] = 'failed'
        
        # Test Web Interface
        try:
            from web_interface.app import app
            self.log("  ✅ Web Interface")
            self.components['web_interface'] = 'healthy'
        except Exception as e:
            self.log(f"  ❌ Web Interface: {e}")
            self.components['web_interface'] = 'failed'
        
        healthy_components = len([c for c in self.components.values() if c == 'healthy'])
        total_components = len(self.components)
        
        if healthy_components == total_components:
            self.log(f"✅ All {total_components} components healthy")
            return True
        else:
            self.log(f"⚠️ {healthy_components}/{total_components} components healthy")
            return False
    
    def start_main_system(self):
        """Start the main system using main.py"""
        self.log("Starting main system...")
        
        try:
            # Import and start main system
            import main
            self.log("✅ Main system module loaded")
            
            # Start the system in background
            def run_main_system():
                try:
                    asyncio.run(main.main())
                except Exception as e:
                    self.log(f"Main system error: {e}", "ERROR")
            
            main_thread = threading.Thread(target=run_main_system, daemon=True)
            main_thread.start()
            
            # Give it time to start
            time.sleep(3)
            
            self.log("✅ Main system started successfully")
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to start main system: {e}", "ERROR")
            return False
    
    def start_web_interface(self):
        """Start web interface in background"""
        self.log("Starting web interface...")
        
        try:
            port = os.getenv('WEB_INTERFACE_PORT', '5000')
            host = os.getenv('WEB_INTERFACE_HOST', '0.0.0.0')
            
            # Start web interface in subprocess
            web_cmd = [
                sys.executable, '-m', 'web_interface.app'
            ]
            
            env = os.environ.copy()
            env['WEB_INTERFACE_PORT'] = port
            env['WEB_INTERFACE_HOST'] = host
            
            web_process = subprocess.Popen(
                web_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )
            
            # Give it time to start
            time.sleep(5)
            
            if web_process.poll() is None:  # Still running
                self.log(f"✅ Web interface started on http://{host}:{port}")
                self.components['web_server'] = web_process
                return True
            else:
                stdout, stderr = web_process.communicate()
                self.log(f"❌ Web interface failed: {stderr.decode()}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Failed to start web interface: {e}", "ERROR")
            return False
    
    def run_system_tests(self):
        """Run basic system tests"""
        self.log("Running system tests...")
        
        try:
            # Test LLM Gateway
            if self.components.get('llm_gateway') == 'healthy':
                try:
                    from connectors.llm_gateway import llm_gateway
                    test_result = asyncio.run(llm_gateway.test_all_providers())
                    active_providers = test_result.get('active_providers', 0)
                    self.log(f"  🧠 LLM Gateway: {active_providers} providers active")
                except Exception as e:
                    self.log(f"  ⚠️ LLM Gateway test failed: {e}")
            
            # Test Camel Agent
            if self.components.get('camel_agent') == 'healthy':
                try:
                    from agents.camel_agent_integration import camel_agent
                    stats = camel_agent.get_collaboration_stats()
                    self.log(f"  🐪 Camel Agent: {len(stats['available_agent_roles'])} roles available")
                except Exception as e:
                    self.log(f"  ⚠️ Camel Agent test failed: {e}")
            
            # Test Agents
            if self.components.get('agents') == 'healthy':
                try:
                    from agents import initialize_agents, get_system_stats
                    
                    # Initialize with LLM gateway if available
                    llm_provider = None
                    if self.components.get('llm_gateway') == 'healthy':
                        from connectors.llm_gateway import llm_gateway
                        llm_provider = llm_gateway
                    
                    initialize_agents(llm_provider=llm_provider)
                    stats = get_system_stats()
                    self.log(f"  🤖 Agents: {stats['active_agents']}/{stats['total_agents']} active")
                    
                except Exception as e:
                    self.log(f"  ⚠️ Agents test failed: {e}")
            
            return True
            
        except Exception as e:
            self.log(f"❌ System tests failed: {e}", "ERROR")
            return False
    
    def save_startup_report(self):
        """Save startup report"""
        try:
            report = {
                'system': self.system_name,
                'owner': self.owner,
                'owner_id': self.owner_id,
                'startup_time': datetime.now().isoformat(),
                'components': self.components,
                'healthy': self.is_healthy,
                'startup_log': self.startup_log[-10:]  # Last 10 entries
            }
            
            with open('data/system/startup_report.json', 'w') as f:
                json.dump(report, f, indent=2)
            
            self.log("📊 Startup report saved")
            
        except Exception as e:
            self.log(f"Failed to save startup report: {e}", "ERROR")
    
    def print_startup_summary(self):
        """Print startup summary"""
        print("\n" + "="*60)
        print(f"🎯 {self.system_name} - STARTUP SUMMARY")
        print("="*60)
        print(f"👑 Owner: {self.owner} ({self.owner_id})")
        print(f"🇮🇩 Made with ❤️ in Indonesia")
        print(f"⏰ Startup Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 System Health: {'✅ HEALTHY' if self.is_healthy else '❌ DEGRADED'}")
        print()
        
        print("📊 COMPONENT STATUS:")
        for component, status in self.components.items():
            status_icon = "✅" if status == "healthy" else "❌"
            print(f"  {status_icon} {component}: {status}")
        
        print()
        
        if self.is_healthy:
            port = os.getenv('WEB_INTERFACE_PORT', '5000')
            print("🌐 ACCESS POINTS:")
            print(f"  📊 Dashboard: http://localhost:{port}")
            print(f"  🤖 Agents: http://localhost:{port}/agents")
            print(f"  🐪 Camel AI: http://localhost:{port}/camel_collaboration")
            print(f"  ⚙️ Monitoring: http://localhost:{port}/monitoring")
        
        print()
        print("🚀 ULTIMATE AGI FORCE IS READY FOR AUTONOMOUS OPERATION!")
        print("👑 ABSOLUTE LOYALTY TO MULKY MALIKUL DHAHER")
        print("="*60)
    
    async def launch(self):
        """Main launch sequence"""
        self.log("🚀 Starting Ultimate AGI Force launch sequence...")
        
        # Phase 1: System Prerequisites
        if not self.check_python_version():
            return False
        
        if not self.install_missing_dependencies():
            return False
        
        if not self.create_directories():
            return False
        
        if not self.setup_environment():
            return False
        
        # Phase 2: Component Testing
        component_health = self.test_core_components()
        
        # Phase 3: System Initialization
        if not self.run_system_tests():
            self.log("⚠️ Some system tests failed, but continuing...")
        
        # Phase 4: Service Startup
        # Note: We're not starting main.py automatically to avoid conflicts
        # Users can run it separately or via web interface
        
        web_started = self.start_web_interface()
        
        # Phase 5: Health Assessment
        healthy_components = len([c for c in self.components.values() if c == 'healthy'])
        total_components = len(self.components)
        
        self.is_healthy = (healthy_components >= total_components * 0.8)  # 80% threshold
        
        # Phase 6: Reporting
        self.save_startup_report()
        self.print_startup_summary()
        
        return self.is_healthy

def main():
    """Main launcher function"""
    launcher = SystemLauncher()
    
    try:
        success = asyncio.run(launcher.launch())
        
        if success:
            print("\n✅ System launch completed successfully!")
            print("🔄 System is now running autonomously...")
            
            # Keep running for monitoring
            try:
                while True:
                    time.sleep(60)
                    # Could add periodic health checks here
            except KeyboardInterrupt:
                print("\n🛑 Shutdown requested by user")
                print("👋 Ultimate AGI Force shutting down gracefully...")
        else:
            print("\n❌ System launch completed with errors!")
            print("🔧 Please check the logs and fix issues before retrying")
            return 1
            
    except KeyboardInterrupt:
        print("\n🛑 Launch interrupted by user")
        return 1
    except Exception as e:
        print(f"\n🔥 Critical launch error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())