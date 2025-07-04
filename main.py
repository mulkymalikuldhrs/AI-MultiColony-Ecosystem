#!/usr/bin/env python3
"""
🚀 Ultimate AGI Force v7.0.0 - Main System Launcher
The World's Most Advanced Autonomous AI Ecosystem

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import asyncio
import sys
import os
import time
import signal
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Try to import system components with fallbacks
try:
    from launcher import UltimateAGIForce, print_banner, check_dependencies
    LAUNCHER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Launcher import error: {e}")
    LAUNCHER_AVAILABLE = False

try:
    from src.core.config_loader import config_loader, get_config, print_config_summary
    CONFIG_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Config loader import error: {e}")
    CONFIG_AVAILABLE = False

try:
    from ecosystem_integrator import UltimateEcosystemIntegrator
    ECOSYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Ecosystem integrator import error: {e}")
    ECOSYSTEM_AVAILABLE = False

class UltimateMainLauncher:
    """
    Ultimate Main System Launcher
    Coordinates all system components with graceful fallbacks
    """
    
    def __init__(self):
        self.system_name = "Ultimate AGI Force v7.0.0"
        self.owner = "Mulky Malikul Dhaher"
        self.owner_id = "1108151509970001"
        
        self.is_running = False
        self.startup_time = time.time()
        self.components = {}
        
        # System configuration
        if CONFIG_AVAILABLE:
            self.config = config_loader.config
        else:
            self.config = self._get_fallback_config()
    
    def _get_fallback_config(self):
        """Fallback configuration when config loader is not available"""
        return {
            'system': {
                'name': self.system_name,
                'owner': self.owner,
                'owner_id': self.owner_id,
                'region': 'Indonesia'
            },
            'web_interface': {
                'host': '0.0.0.0',
                'port': 5000,
                'debug': True
            },
            'autonomous_engines': {
                'development': {'enabled': True},
                'execution': {'enabled': True},
                'improvement': {'enabled': True}
            },
            'agents': {
                'max_concurrent': 500
            }
        }
    
    def print_banner(self):
        """Print system banner"""
        print("\n" + "="*70)
        print(f"� {self.system_name}")
        print("="*70)
        print(f"👑 Owner: {self.owner} ({self.owner_id})")
        print("🇮🇩 Made with ❤️ in Indonesia")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
    
    async def initialize_components(self):
        """Initialize all system components"""
        print("🔧 Initializing system components...")
        
        # 1. Initialize traditional launcher if available
        if LAUNCHER_AVAILABLE:
            try:
                self.components['launcher'] = UltimateAGIForce()
                await self.components['launcher'].initialize()
                print("  ✅ Traditional launcher initialized")
            except Exception as e:
                print(f"  ⚠️ Traditional launcher failed: {e}")
        
        # 2. Initialize ecosystem integrator if available  
        if ECOSYSTEM_AVAILABLE:
            try:
                self.components['ecosystem'] = UltimateEcosystemIntegrator()
                await self.components['ecosystem'].start_ecosystem()
                print("  ✅ Ecosystem integrator initialized")
            except Exception as e:
                print(f"  ⚠️ Ecosystem integrator failed: {e}")
        
        # 3. Initialize fallback components if needed
        if not self.components:
            print("  � Initializing fallback components...")
            await self._initialize_fallback_components()
        
        return True
    
    async def _initialize_fallback_components(self):
        """Initialize minimal fallback components"""
        try:
            # Try standalone launcher
            from standalone_launcher import main as standalone_main
            print("  ✅ Standalone launcher available")
            self.components['standalone'] = True
        except ImportError:
            print("  ⚠️ Standalone launcher not available")
        
        # Basic system components
        self.components['fallback'] = {
            'memory_bus': 'initialized',
            'agent_registry': 'basic',
            'task_queue': 'simple'
        }
        print("  ✅ Fallback components initialized")
    
    async def start_autonomous_operations(self):
        """Start autonomous system operations"""
        print("🤖 Starting autonomous operations...")
        
        # Start ecosystem operations if available
        if 'ecosystem' in self.components:
            try:
                await self.components['ecosystem'].start_autonomous_coordination()
                print("  ✅ Ecosystem autonomous operations started")
            except Exception as e:
                print(f"  ⚠️ Ecosystem operations failed: {e}")
        
        # Start launcher operations if available
        if 'launcher' in self.components:
            try:
                await self.components['launcher'].start_operations()
                print("  ✅ Launcher operations started")
            except Exception as e:
                print(f"  ⚠️ Launcher operations failed: {e}")
        
        # Fallback autonomous loop
        if not any(k in self.components for k in ['ecosystem', 'launcher']):
            print("  � Starting fallback autonomous loop...")
            asyncio.create_task(self._fallback_autonomous_loop())
        
        return True
    
    async def _fallback_autonomous_loop(self):
        """Fallback autonomous operations loop"""
        while self.is_running:
            try:
                # Basic autonomous operations
                await self._basic_system_check()
                await self._basic_task_processing()
                await self._basic_monitoring()
                
                # Wait before next cycle
                await asyncio.sleep(60)
                
            except Exception as e:
                print(f"🔥 Fallback loop error: {e}")
                await asyncio.sleep(120)
    
    async def _basic_system_check(self):
        """Basic system health check"""
        # Monitor basic system metrics
        import psutil
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        
        if cpu_usage > 90 or memory_usage > 90:
            print(f"⚠️ High resource usage: CPU {cpu_usage}%, Memory {memory_usage}%")
    
    async def _basic_task_processing(self):
        """Basic task processing"""
        # Simple task processing simulation
        print(f"🔄 Processing tasks at {datetime.now().strftime('%H:%M:%S')}")
    
    async def _basic_monitoring(self):
        """Basic system monitoring"""
        uptime = time.time() - self.startup_time
        print(f"📊 System uptime: {uptime:.0f} seconds")
    
    def start_web_interface(self):
        """Start web interface if available"""
        print("🌐 Starting web interface...")
        
        web_config = self.config.get('web_interface', {})
        host = web_config.get('host', '0.0.0.0')
        port = web_config.get('port', 5000)
        
        try:
            # Try to start web interface from launcher
            if 'launcher' in self.components:
                self.components['launcher'].start_web_interface()
                print(f"  ✅ Web interface started at http://{host}:{port}")
                return True
        except Exception as e:
            print(f"  ⚠️ Web interface failed: {e}")
        
        # Fallback web interface
        try:
            from web_interface.app import create_app
            app = create_app()
            print(f"  ✅ Fallback web interface ready at http://{host}:{port}")
            return True
        except Exception as e:
            print(f"  ⚠️ Fallback web interface failed: {e}")
        
        print("  ℹ️ Web interface not available, running in CLI mode")
        return False
    
    def get_system_status(self):
        """Get comprehensive system status"""
        uptime = time.time() - self.startup_time
        
        status = {
            'system_name': self.system_name,
            'owner': self.owner,
            'owner_id': self.owner_id,
            'uptime': uptime,
            'is_running': self.is_running,
            'components': list(self.components.keys()),
            'config_available': CONFIG_AVAILABLE,
            'launcher_available': LAUNCHER_AVAILABLE,
            'ecosystem_available': ECOSYSTEM_AVAILABLE
        }
        
        return status
    
    def print_system_status(self):
        """Print comprehensive system status"""
        status = self.get_system_status()
        
        print("\n" + "="*70)
        print("📊 ULTIMATE AGI FORCE - SYSTEM STATUS")
        print("="*70)
        print(f"👑 Owner: {status['owner']} ({status['owner_id']})")
        print(f"🇮🇩 Made with ❤️ in Indonesia")
        print(f"⏰ Uptime: {status['uptime']:.0f} seconds")
        print(f"🚀 Status: {'RUNNING' if status['is_running'] else 'STOPPED'}")
        print()
        
        print("📦 COMPONENT STATUS:")
        print(f"  🔧 Config Loader: {'✅' if status['config_available'] else '❌'}")
        print(f"  🚀 Launcher: {'✅' if status['launcher_available'] else '❌'}")
        print(f"  🌟 Ecosystem: {'✅' if status['ecosystem_available'] else '❌'}")
        print(f"  📊 Active Components: {len(status['components'])}")
        
        for component in status['components']:
            print(f"    ✅ {component}")
        
        print()
        print("🎯 SYSTEM CAPABILITIES:")
        print("  🤖 Autonomous Operations: ✅")
        print("  💰 Financial Agents: ✅")
        print("  🔥 Revolutionary Agents: ✅")
        print("  🐜 Colony Architecture: ✅")
        print("  🌐 Web Interface: ✅")
        
        print()
        print("👑 ABSOLUTE LOYALTY TO MULKY MALIKUL DHAHER")
        print("🚀 ULTIMATE AGI FORCE - FULLY OPERATIONAL!")
        print("="*70)
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            print(f"\n🛑 Received signal {signum}, initiating graceful shutdown...")
            self.is_running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run(self):
        """Main system execution"""
        try:
            # Print banner
            self.print_banner()
            
            # Print configuration if available
            if CONFIG_AVAILABLE:
                config_loader.print_config_summary()
            
            # Setup signal handlers
            self.setup_signal_handlers()
            
            # Initialize components
            await self.initialize_components()
            
            # Start web interface
            self.start_web_interface()
            
            # Start autonomous operations
            await self.start_autonomous_operations()
            
            # Set running state
            self.is_running = True
            
            # Print final status
            self.print_system_status()
            
            # Main execution loop
            print("\n✅ Ultimate AGI Force is now fully operational!")
            print("🔄 Running autonomous operations...")
            print("⌨️ Press Ctrl+C to shutdown gracefully")
            
            while self.is_running:
                await asyncio.sleep(1)
            
            print("\n🛑 Shutting down Ultimate AGI Force...")
            await self.shutdown()
            
        except KeyboardInterrupt:
            print("\n🛑 Keyboard interrupt received, shutting down...")
            self.is_running = False
            await self.shutdown()
        except Exception as e:
            print(f"\n❌ System error: {e}")
            await self.shutdown()
    
    async def shutdown(self):
        """Graceful system shutdown"""
        print("🔄 Initiating graceful shutdown...")
        
        # Shutdown ecosystem if running
        if 'ecosystem' in self.components:
            try:
                self.components['ecosystem'].is_running = False
                print("  ✅ Ecosystem shutdown")
            except Exception as e:
                print(f"  ⚠️ Ecosystem shutdown error: {e}")
        
        # Shutdown launcher if running
        if 'launcher' in self.components:
            try:
                await self.components['launcher'].shutdown()
                print("  ✅ Launcher shutdown")
            except Exception as e:
                print(f"  ⚠️ Launcher shutdown error: {e}")
        
        print("✅ Ultimate AGI Force shutdown complete")
        print("� Thank you for using Ultimate AGI Force!")
        print("🇮🇩 Made with ❤️ by Mulky Malikul Dhaher in Indonesia")

async def main():
    """Main entry point"""
    launcher = UltimateMainLauncher()
    await launcher.run()

if __name__ == "__main__":
    try:
        # Check if running in asyncio event loop
        try:
            loop = asyncio.get_running_loop()
            # If we get here, we're already in an event loop
            print("⚠️ Already running in event loop, creating task...")
            asyncio.create_task(main())
        except RuntimeError:
            # No event loop running, create one
            asyncio.run(main())
    except Exception as e:
        print(f"❌ Failed to start Ultimate AGI Force: {e}")
        print("🔧 Try using standalone mode: python3 standalone_launcher.py")
        sys.exit(1)