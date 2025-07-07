#!/usr/bin/env python3
"""
🚀 AI-MultiColony-Ecosystem - Unified Launcher System
The Ultimate Launcher that consolidates all system modes

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import asyncio
import sys
import os
import json
import signal
import subprocess
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

class UnifiedLauncher:
    """
    Unified Launcher System - All modes in one place
    """
    
    def __init__(self):
        self.system_name = "AI-MultiColony-Ecosystem"
        self.version = "7.0.0"
        self.owner = "Mulky Malikul Dhaher"
        self.owner_id = "1108151509970001"
        
        # System state
        self.is_running = False
        self.current_mode = None
        self.startup_time = time.time()
        self.components = {}
        self.processes = {}
        
        # Create required directories
        self._create_directories()
        
        # Configure LLM7 API
        self._configure_llm7()
        
        # Configure network ports
        self._configure_network()
        
        # Setup signal handlers
        self._setup_signal_handlers()
    
    def _create_directories(self):
        """Create required directories"""
        directories = [
            "agent_output",
            "logs",
            "data",
            "data/task_queue",
            "data/system",
            "data/logs",
            "data/backups"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        print("📁 Created required directories")
    
    def _configure_llm7(self):
        """Configure LLM7 API settings"""
        os.environ["OPENAI_API_KEY"] = "unused"
        os.environ["OPENAI_API_BASE_URL"] = "https://api.llm7.io/v1"
        os.environ["LLM7_API_KEY"] = "unused"
        os.environ["LLM7_API_BASE_URL"] = "https://api.llm7.io/v1"
        
        print("🔑 Configured LLM7 API endpoint")
    
    def _configure_network(self):
        """Configure network ports for external access"""
        # Set web interface port
        os.environ["WEB_INTERFACE_PORT"] = "8080"
        os.environ["WEB_INTERFACE_HOST"] = "0.0.0.0"
        
        # Set websocket port
        os.environ["WEBSOCKET_PORT"] = "8765"
        
        # Set API port
        os.environ["API_PORT"] = "8080"
        
        print("🌐 Configured network ports - Web: 8080, WebSocket: 8765")
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            print(f"\n🛑 Received signal {signum}, shutting down...")
            self.shutdown()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def print_banner(self):
        """Print system banner"""
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                🚀 AI-MultiColony-Ecosystem v7.0.0 🚀                         ║
║                                                                              ║
║                        Unified Launcher System                               ║
║                                                                              ║
║                 🇮🇩 Made with ❤️ by Mulky Malikul Dhaher 🇮🇩                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
        print(f"👑 Owner: {self.owner} ({self.owner_id})")
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 LLM7 API: https://api.llm7.io/v1")
        print("="*80)
    
    def show_mode_menu(self):
        """Show available launcher modes"""
        print("\n🎯 Available Launcher Modes:")
        print("1. 🌐 Web UI Only - Modern web interface (RECOMMENDED)")
        print("2. � Web UI + Background - Web interface with autonomous engines")
        print("3. �️  CLI Mode - Interactive command line interface")
        print("4. � Termux Shell - Compatible with Android Termux")
        print("5. ❌ Exit - Shutdown launcher")
        print("="*80)
    
    def get_mode_choice(self) -> int:
        """Get user's mode choice"""
        try:
            choice = input("\n🎯 Select mode (1-5): ").strip()
            return int(choice)
        except (ValueError, KeyboardInterrupt):
            return 5
    
    async def run_cli_mode(self):
        """Run CLI mode"""
        self.current_mode = "cli"
        print("\n🖥️ Starting CLI Mode...")
        
        # Initialize core components
        await self._initialize_components()
        
        # CLI interaction loop
        print("\n✅ CLI Mode active. Type 'help' for commands.")
        
        while self.is_running:
            try:
                command = input("🔹 colony> ").strip().lower()
                
                if command in ['exit', 'quit', 'q']:
                    break
                elif command == 'help':
                    self._show_cli_help()
                elif command == 'status':
                    await self._show_system_status()
                elif command == 'agents':
                    await self._show_agents()
                elif command.startswith('run '):
                    await self._run_agent_command(command[4:])
                elif command == 'logs':
                    self._show_logs()
                elif command == 'web':
                    await self._launch_web_ui()
                else:
                    print(f"❓ Unknown command: {command}")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    async def run_termux_mode(self):
        """Run Termux-compatible mode"""
        self.current_mode = "termux"
        print("\n📱 Starting Termux Mode...")
        
        # Termux-specific optimizations
        os.environ["TERM"] = "xterm-256color"
        os.environ["TERMUX_VERSION"] = "0.118.0"
        
        # Initialize components with Termux compatibility
        await self._initialize_components()
        
        # Show Termux-specific interface
        print("\n📱 Termux Mode active - Optimized for Android")
        print("🎯 Available commands:")
        print("  • status - Show system status")
        print("  • agents - List all agents")
        print("  • web - Launch web interface")
        print("  • daemon - Run in background")
        print("  • exit - Exit system")
        
        # Simplified command loop for Termux
        while self.is_running:
            try:
                command = input("📱 > ").strip().lower()
                
                if command in ['exit', 'quit']:
                    break
                elif command == 'status':
                    await self._show_system_status()
                elif command == 'agents':
                    await self._show_agents()
                elif command == 'web':
                    await self._launch_web_ui()
                elif command == 'daemon':
                    await self._run_background_daemon()
                elif command == 'help':
                    print("📱 Available: status, agents, web, daemon, exit")
                else:
                    print(f"❓ Unknown: {command}")
                    
            except KeyboardInterrupt:
                break
    
    async def run_web_ui_only(self):
        """Run Web UI Only mode"""
        self.current_mode = "web_only"
        print("\n🌐 Starting Web UI Only Mode...")
        
        # Initialize components
        await self._initialize_components()
        
        # Launch web interface
        await self._launch_web_ui()
        
        # Keep web UI running
        print("\n🌐 Web UI is running at http://0.0.0.0:8080")
        print("🔗 Access: http://localhost:8080 or http://YOUR_IP:8080")
        print("🔄 Press Ctrl+C to stop the web interface")
        
        try:
            while self.is_running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping Web UI...")
    
    
    async def run_web_with_background(self):
        """Run Web UI with Background Engines"""
        self.current_mode = "web_background"
        print("\n🔄 Starting Web UI + Background Engines...")
        
        # Initialize components
        await self._initialize_components()
        
        # Start autonomous engines
        await self._start_autonomous_engines()
        
        # Launch web interface
        await self._launch_web_ui()
        
        print("\n🔄 Systems running:")
        print("  🌐 Web UI: http://0.0.0.0:8080")
        print("  🤖 Autonomous Engines: Active")
        print("  📄 Logs: logs/colony_activity.log")
        print("🔄 Press Ctrl+C to stop all systems")
        
        try:
            while self.is_running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping all systems...")
    
    
    async def run_autonomous_mode(self):
        """Run Autonomous Engine mode"""
        self.current_mode = "autonomous"
        print("\n🤖 Starting Autonomous Engine Mode...")
        
        # Initialize components
        await self._initialize_components()
        
        # Start autonomous engines
        await self._start_autonomous_engines()
        
        print("\n🤖 Autonomous Mode active - System is self-managing")
        print("🔄 Running autonomous cycles...")
        
        # Autonomous operation loop
        while self.is_running:
            try:
                await self._autonomous_cycle()
                await asyncio.sleep(60)  # 1-minute cycles
            except KeyboardInterrupt:
                break
    
    async def run_background_daemon(self):
        """Run Background Daemon mode"""
        self.current_mode = "daemon"
        print("\n🔧 Starting Background Daemon Mode...")
        
        # Initialize components
        await self._initialize_components()
        
        # Setup logging for daemon mode
        self._setup_daemon_logging()
        
        print("\n🔧 Background Daemon active - Running silently")
        print("📄 Logs are saved to: logs/colony_activity.log")
        
        # Background operation loop
        while self.is_running:
            try:
                await self._daemon_cycle()
                await asyncio.sleep(30)  # 30-second cycles
            except KeyboardInterrupt:
                break
    
    async def run_all_modes(self):
        """Run all modes simultaneously"""
        self.current_mode = "all"
        print("\n🔄 Starting All Modes Simultaneously...")
        
        # Initialize components
        await self._initialize_components()
        
        # Start all systems
        tasks = [
            asyncio.create_task(self._launch_web_ui()),
            asyncio.create_task(self._start_autonomous_engines()),
            asyncio.create_task(self._run_background_daemon()),
        ]
        
        print("\n🔄 All systems running:")
        print("  🌐 Web UI: http://localhost:5000")
        print("  🤖 Autonomous Engine: Active")
        print("  🔧 Background Daemon: Active")
        print("  📄 Logs: logs/colony_activity.log")
        
        # Keep all systems running
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except KeyboardInterrupt:
            print("\n🛑 Stopping all systems...")
            for task in tasks:
                task.cancel()
    
    async def _initialize_components(self):
        """Initialize system components"""
        print("🔧 Initializing system components...")
        
        # Try to load existing components
        try:
            # Load configuration
            from src.core.config_loader import config_loader
            self.components['config'] = config_loader
            print("  ✅ Configuration loaded")
        except ImportError:
            print("  ⚠️ Configuration loader not available")
        
        try:
            # Load agents
            from agents import initialize_agents, AGENTS_REGISTRY
            from connectors.llm_gateway import llm_gateway
            initialize_agents(llm_provider=llm_gateway)
            self.components['agents'] = AGENTS_REGISTRY
            print(f"  ✅ {len(AGENTS_REGISTRY)} agents loaded")
        except ImportError:
            print("  ⚠️ Agents not available")
        
        try:
            # Load core systems
            from core.memory_bus import memory_bus
            from core.scheduler import agent_scheduler
            self.components['memory_bus'] = memory_bus
            self.components['scheduler'] = agent_scheduler
            print("  ✅ Core systems loaded")
        except ImportError:
            print("  ⚠️ Core systems not available")
        
        # Save system status
        self._save_system_status()
    
    async def _launch_web_ui(self):
        """Launch web interface"""
        if 'web_ui' in self.processes:
            print("🌐 Web UI already running")
            return
        
        try:
            # Start web interface process
            web_command = [sys.executable, "-c", f"""
import sys
sys.path.append('{str(project_root)}')
from web_interface.app import app, socketio
socketio.run(app, host='0.0.0.0', port=8080, debug=False, allow_unsafe_werkzeug=True)
"""]

            self.processes['web_ui'] = subprocess.Popen(
                web_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Wait for web UI to start
            await asyncio.sleep(3)
            print("  ✅ Web UI launched at http://0.0.0.0:8080")

        except Exception as e:
            print(f"  ❌ Failed to launch Web UI: {e}")
    
    async def _start_autonomous_engines(self):
        """Start autonomous engines"""
        print("🤖 Starting autonomous engines...")
        
        # Start autonomous operation threads
        engines = [
            ('development', self._development_engine),
            ('execution', self._execution_engine),
            ('improvement', self._improvement_engine)
        ]
        
        for name, engine in engines:
            thread = threading.Thread(target=engine, daemon=True)
            thread.start()
            self.processes[f'engine_{name}'] = thread
            print(f"  ✅ {name.title()} engine started")
    
    def _development_engine(self):
        """Development engine loop"""
        while self.is_running:
            try:
                self._log_activity("Development engine cycle")
                # Development logic here
                time.sleep(300)  # 5-minute cycles
            except Exception as e:
                self._log_activity(f"Development engine error: {e}")
                time.sleep(600)
    
    def _execution_engine(self):
        """Execution engine loop"""
        while self.is_running:
            try:
                self._log_activity("Execution engine cycle")
                self._process_task_queue()
                time.sleep(60)  # 1-minute cycles
            except Exception as e:
                self._log_activity(f"Execution engine error: {e}")
                time.sleep(120)
    
    def _improvement_engine(self):
        """Improvement engine loop"""
        while self.is_running:
            try:
                self._log_activity("Improvement engine cycle")
                # Improvement logic here
                time.sleep(900)  # 15-minute cycles
            except Exception as e:
                self._log_activity(f"Improvement engine error: {e}")
                time.sleep(1800)
    
    def _process_task_queue(self):
        """Process task queue"""
        task_queue_dir = Path("data/task_queue")
        if not task_queue_dir.exists():
            return
        
        for task_file in task_queue_dir.glob("*.json"):
            try:
                with open(task_file, 'r') as f:
                    task_data = json.load(f)
                
                # Process task
                self._log_activity(f"Processing task: {task_data.get('task_id')}")
                
                # Remove processed task
                task_file.unlink()
                
            except Exception as e:
                self._log_activity(f"Task processing error: {e}")
    
    async def _autonomous_cycle(self):
        """Autonomous operation cycle"""
        self._log_activity("Autonomous cycle running")
        
        # Check system health
        await self._check_system_health()
        
        # Process pending tasks
        self._process_task_queue()
        
        # Update system status
        self._save_system_status()
    
    async def _daemon_cycle(self):
        """Background daemon cycle"""
        self._log_activity("Daemon cycle running")
        
        # Monitor system resources
        await self._monitor_resources()
        
        # Check for system updates
        await self._check_updates()
        
        # Cleanup old files
        self._cleanup_old_files()
    
    async def _check_system_health(self):
        """Check system health"""
        try:
            # Check CPU and memory usage
            import psutil
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            if cpu_percent > 80 or memory_percent > 80:
                self._log_activity(f"High resource usage: CPU {cpu_percent}%, Memory {memory_percent}%")
        except ImportError:
            pass
    
    async def _monitor_resources(self):
        """Monitor system resources"""
        self._log_activity("Resource monitoring cycle")
    
    async def _check_updates(self):
        """Check for system updates"""
        self._log_activity("Update check cycle")
    
    def _cleanup_old_files(self):
        """Cleanup old files"""
        try:
            # Clean up old logs
            log_dir = Path("logs")
            if log_dir.exists():
                for log_file in log_dir.glob("*.log"):
                    if log_file.stat().st_mtime < time.time() - 7 * 24 * 3600:  # 7 days old
                        log_file.unlink()
        except Exception as e:
            self._log_activity(f"Cleanup error: {e}")
    
    def _show_cli_help(self):
        """Show CLI help"""
        print("\n📋 Available CLI Commands:")
        print("  help     - Show this help message")
        print("  status   - Show system status")
        print("  agents   - List all agents")
        print("  run <cmd> - Run agent command")
        print("  logs     - Show recent logs")
        print("  web      - Launch web interface")
        print("  exit     - Exit CLI mode")
    
    async def _show_system_status(self):
        """Show system status"""
        uptime = time.time() - self.startup_time
        
        print(f"\n📊 System Status:")
        print(f"  🏠 Mode: {self.current_mode}")
        print(f"  ⏱️ Uptime: {uptime:.0f} seconds")
        print(f"  🔧 Components: {len(self.components)}")
        print(f"  🖥️ Processes: {len(self.processes)}")
        print(f"  📄 Logs: logs/colony_activity.log")
        print(f"  📁 Output: agent_output/")
    
    async def _show_agents(self):
        """Show agents"""
        if 'agents' in self.components:
            agents = self.components['agents']
            print(f"\n🤖 Available Agents ({len(agents)}):")
            for agent_id, agent in agents.items():
                name = getattr(agent, 'name', agent_id)
                status = getattr(agent, 'status', 'unknown')
                print(f"  • {name} ({agent_id}): {status}")
        else:
            print("\n⚠️ No agents loaded")
    
    async def _run_agent_command(self, command: str):
        """Run agent command"""
        print(f"🤖 Running agent command: {command}")
        self._log_activity(f"Agent command: {command}")
    
    def _show_logs(self):
        """Show recent logs"""
        log_file = Path("logs/colony_activity.log")
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    recent_lines = lines[-10:]  # Show last 10 lines
                    print("\n📄 Recent Logs:")
                    for line in recent_lines:
                        print(f"  {line.strip()}")
            except Exception as e:
                print(f"❌ Error reading logs: {e}")
        else:
            print("📄 No logs found")
    
    def _setup_daemon_logging(self):
        """Setup daemon logging"""
        import logging
        
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'colony_activity.log'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('colony')
    
    def _log_activity(self, message: str):
        """Log activity"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        
        # Write to log file
        log_file = Path("logs/colony_activity.log")
        with open(log_file, 'a') as f:
            f.write(log_entry + '\n')
        
        # Print to console if in daemon mode
        if self.current_mode == 'daemon':
            print(log_entry)
    
    def _save_system_status(self):
        """Save system status"""
        try:
            status = {
                "system_name": self.system_name,
                "version": self.version,
                "status": "running" if self.is_running else "stopped",
                "mode": self.current_mode,
                "owner": self.owner,
                "owner_id": self.owner_id,
                "timestamp": datetime.now().isoformat(),
                "uptime": time.time() - self.startup_time,
                "components": list(self.components.keys()),
                "processes": list(self.processes.keys()),
                "working_agents": {}
            }
            
            # Add agent information if available
            if 'agents' in self.components:
                for agent_id, agent in self.components['agents'].items():
                    status["working_agents"][agent_id] = {
                        'id': agent_id,
                        'name': getattr(agent, 'name', agent_id),
                        'status': getattr(agent, 'status', 'unknown'),
                        'capabilities': getattr(agent, 'capabilities', [])
                    }
            
            # Save to file
            with open("data/system_status.json", "w") as f:
                json.dump(status, f, indent=2)
                
        except Exception as e:
            print(f"💾 Status save error: {e}")
    
    def shutdown(self):
        """Shutdown the system"""
        print("\n🛑 Shutting down AI-MultiColony-Ecosystem...")
        
        self.is_running = False
        
        # Stop all processes
        for name, process in self.processes.items():
            try:
                if isinstance(process, subprocess.Popen):
                    process.terminate()
                    process.wait(timeout=5)
                print(f"  ✅ Stopped {name}")
            except Exception as e:
                print(f"  ⚠️ Error stopping {name}: {e}")
        
        # Save final status
        self._save_system_status()
        
        print("✅ Shutdown complete")
        print("🇮🇩 Thank you for using AI-MultiColony-Ecosystem!")
    
    async def run(self):
        """Main launcher execution"""
        self.is_running = True
        
        try:
            # Show banner
            self.print_banner()
            
            while self.is_running:
                # Show mode menu
                self.show_mode_menu()
                
                # Get user choice
                choice = self.get_mode_choice()
                
                if choice == 1:
                    await self.run_web_ui_only()
                elif choice == 2:
                    await self.run_web_with_background()
                elif choice == 3:
                    await self.run_cli_mode()
                elif choice == 4:
                    await self.run_termux_mode()
                elif choice == 5:
                    break
                else:
                    print("❌ Invalid choice. Please select 1-5.")
                    continue
                
                # Ask if user wants to continue
                if self.is_running:
                    try:
                        continue_choice = input("\n🔄 Return to main menu? (y/n): ").strip().lower()
                        if continue_choice in ['n', 'no']:
                            break
                    except KeyboardInterrupt:
                        break
            
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            self.shutdown()

async def main():
    """Main entry point"""
    launcher = UnifiedLauncher()
    await launcher.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Launcher interrupted")
    except Exception as e:
        print(f"❌ Failed to start launcher: {e}")
        print("🔧 Check your Python installation and try again")
        sys.exit(1)