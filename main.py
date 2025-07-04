#!/usr/bin/env python3
"""
🚀 Ultimate AGI Force v7.0.0 - Main Entry Point
Primary startup script for autonomous AGI system

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import asyncio
import sys
import os
import json
import time
import signal
import threading
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import core components
from launcher import UltimateAGIForce, print_banner, check_dependencies
from core.ai_selector import ai_selector
from core.memory_bus import memory_bus
from core.prompt_master import prompt_master
from core.scheduler import agent_scheduler
from core.sync_engine import sync_engine

class MainSystemController:
    """
    Main system controller for Ultimate AGI Force
    Coordinates all components and handles system lifecycle
    """
    
    def __init__(self):
        self.system_name = "Ultimate AGI Force Main Controller"
        self.version = "7.0.0"
        self.owner = "Mulky Malikul Dhaher"
        self.owner_id = "1108151509970001"
        
        self.agi_force = None
        self.is_running = False
        self.shutdown_event = threading.Event()
        
        # System components
        self.core_systems = {
            'ai_selector': ai_selector,
            'memory_bus': memory_bus,
            'prompt_master': prompt_master,
            'scheduler': agent_scheduler,
            'sync_engine': sync_engine
        }
        
        print(f"🛡️ {self.system_name} v{self.version}")
        print(f"👑 Owned by: {self.owner} ({self.owner_id})")
        print("🇮🇩 Made with ❤️ in Indonesia")
    
    async def initialize_system(self):
        """Initialize all system components"""
        print("\n🔧 Initializing system components...")
        
        # Create necessary directories
        self._create_system_directories()
        
        # Initialize core systems
        await self._initialize_core_systems()
        
        # Initialize AGI Force
        self.agi_force = UltimateAGIForce()
        
        print("✅ System initialization complete!")
    
    def _create_system_directories(self):
        """Create required system directories"""
        directories = [
            "data", "data/logs", "data/agents", "data/system",
            "data/task_queue", "data/backups", "data/deployment",
            "logs", "temp", "cache"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        print("📁 System directories created")
    
    async def _initialize_core_systems(self):
        """Initialize core system components"""
        print("🔧 Starting core systems...")
        
        for name, system in self.core_systems.items():
            try:
                if hasattr(system, 'initialize'):
                    await system.initialize()
                print(f"  ✅ {name}: Ready")
            except Exception as e:
                print(f"  ⚠️ {name}: {e}")
    
    async def start_system(self):
        """Start the entire system"""
        print("\n🚀 Starting Ultimate AGI Force system...")
        
        try:
            # Start AGI Force
            await self.agi_force.start()
            
            self.is_running = True
            print(f"\n✅ {self.system_name} is fully operational!")
            
            # Start system monitoring
            await self._start_system_monitoring()
            
            # Run forever
            await self.agi_force.run_forever()
            
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested by user")
            await self.shutdown_system()
        except Exception as e:
            print(f"\n🔥 Critical system error: {e}")
            await self.shutdown_system()
    
    async def _start_system_monitoring(self):
        """Start system monitoring and health checks"""
        print("🩺 Starting system monitoring...")
        
        # Start monitoring in background
        threading.Thread(
            target=self._monitoring_loop, 
            daemon=True
        ).start()
        
        # Start health checks
        threading.Thread(
            target=self._health_check_loop, 
            daemon=True
        ).start()
        
        print("  ✅ System monitoring active")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_running and not self.shutdown_event.is_set():
            try:
                # Monitor system health
                self._log_system_status()
                
                # Check memory usage
                self._check_memory_usage()
                
                # Check agent status
                self._check_agent_status()
                
                time.sleep(60)  # Monitor every minute
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(120)
    
    def _health_check_loop(self):
        """Background health check loop"""
        while self.is_running and not self.shutdown_event.is_set():
            try:
                # Check core components
                for name, system in self.core_systems.items():
                    if hasattr(system, 'health_check'):
                        system.health_check()
                
                # Check AGI Force health
                if self.agi_force and hasattr(self.agi_force, 'health_check'):
                    self.agi_force.health_check()
                
                time.sleep(30)  # Health check every 30 seconds
            except Exception as e:
                print(f"Health check error: {e}")
                time.sleep(60)
    
    def _log_system_status(self):
        """Log current system status"""
        try:
            status = {
                "timestamp": datetime.now().isoformat(),
                "system": self.system_name,
                "version": self.version,
                "owner": self.owner,
                "owner_id": self.owner_id,
                "status": "running" if self.is_running else "stopped",
                "uptime": time.time(),
                "components": {}
            }
            
            # Add component status
            for name, system in self.core_systems.items():
                status["components"][name] = {
                    "status": getattr(system, 'status', 'unknown'),
                    "last_activity": getattr(system, 'last_activity', None)
                }
            
            # Save status
            with open("data/system/main_status.json", "w") as f:
                json.dump(status, f, indent=2)
                
        except Exception as e:
            print(f"Status logging error: {e}")
    
    def _check_memory_usage(self):
        """Check system memory usage"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            if memory.percent > 85:
                print(f"⚠️ High memory usage: {memory.percent}%")
                
        except ImportError:
            pass  # psutil not available
        except Exception as e:
            print(f"Memory check error: {e}")
    
    def _check_agent_status(self):
        """Check agent status and health"""
        try:
            if self.agi_force and hasattr(self.agi_force, 'working_agents'):
                for agent_id, agent in self.agi_force.working_agents.items():
                    status = getattr(agent, 'status', 'unknown')
                    if status == 'error' or status == 'failed':
                        print(f"⚠️ Agent {agent_id} in error state: {status}")
                        
        except Exception as e:
            print(f"Agent status check error: {e}")
    
    async def shutdown_system(self):
        """Gracefully shutdown the system"""
        print("\n🛑 Shutting down Ultimate AGI Force system...")
        
        self.is_running = False
        self.shutdown_event.set()
        
        # Shutdown AGI Force
        if self.agi_force:
            await self.agi_force.stop()
        
        # Shutdown core systems
        for name, system in self.core_systems.items():
            try:
                if hasattr(system, 'shutdown'):
                    await system.shutdown()
                print(f"  ✅ {name}: Shutdown complete")
            except Exception as e:
                print(f"  ⚠️ {name}: Shutdown error - {e}")
        
        print("✅ System shutdown complete")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            print(f"\n🛑 Received signal {signum}")
            asyncio.create_task(self.shutdown_system())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """Main entry point"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed. Please install missing packages.")
        sys.exit(1)
    
    # Create main controller
    controller = MainSystemController()
    controller.setup_signal_handlers()
    
    try:
        # Initialize system
        await controller.initialize_system()
        
        # Start system
        await controller.start_system()
        
    except Exception as e:
        print(f"🔥 Fatal error: {e}")
        await controller.shutdown_system()
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting Ultimate AGI Force from main.py...")
    print("👑 Absolute loyalty to Mulky Malikul Dhaher (1108151509970001)")
    print("🇮🇩 Made with ❤️ in Indonesia")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Shutdown complete")
    except Exception as e:
        print(f"🔥 Critical error: {e}")
        sys.exit(1)