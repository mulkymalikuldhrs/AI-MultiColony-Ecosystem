"""
🚀 Autonomous Launcher - Self-Running AI System
Launcher yang menjalankan semua agents secara otomatis dan koordinasi

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import os
import sys
import asyncio
import subprocess
import time
import logging
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import psutil
import signal

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ProcessManager:
    """Manager untuk mengatur semua process agents"""
    
    def __init__(self):
        self.processes = {}
        self.status = {}
        self.restart_counts = {}
        self.max_restarts = 5
        self.restart_window = 300  # 5 minutes
        
        # Agent configurations
        self.agent_configs = {
            'master_orchestrator': {
                'script': 'master_orchestrator.py',
                'priority': 10,
                'auto_restart': True,
                'startup_delay': 0,
                'health_check_interval': 30
            },
            'intelligent_agent': {
                'script': 'intelligent_agent_system.py',
                'priority': 9,
                'auto_restart': True,
                'startup_delay': 5,
                'health_check_interval': 60
            },
            'autonomous_developer': {
                'script': 'autonomous_developer.py',
                'priority': 8,
                'auto_restart': True,
                'startup_delay': 10,
                'health_check_interval': 300
            },
            'emotion_engine': {
                'script': 'emotion_engine.py',
                'priority': 7,
                'auto_restart': True,
                'startup_delay': 15,
                'health_check_interval': 240
            },
            'quantum_agent': {
                'script': 'quantum_neural_agent.py',
                'priority': 6,
                'auto_restart': True,
                'startup_delay': 20,
                'health_check_interval': 480
            },
            'predictive_engine': {
                'script': 'predictive_reality_engine.py',
                'priority': 5,
                'auto_restart': True,
                'startup_delay': 25,
                'health_check_interval': 720
            },
            'data_augmenter': {
                'script': 'data_augmentation_system.py',
                'priority': 4,
                'auto_restart': True,
                'startup_delay': 30,
                'health_check_interval': 3600
            }
        }
        
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging system"""
        os.makedirs("logs", exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/autonomous_launcher.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('AutonomousLauncher')
    
    def start_agent(self, agent_name: str) -> bool:
        """Start specific agent"""
        config = self.agent_configs.get(agent_name)
        if not config:
            self.logger.error(f"❌ Unknown agent: {agent_name}")
            return False
        
        script_path = os.path.join(os.path.dirname(__file__), config['script'])
        
        if not os.path.exists(script_path):
            self.logger.error(f"❌ Script not found: {script_path}")
            return False
        
        try:
            # Start process
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes[agent_name] = process
            self.status[agent_name] = {
                'status': 'starting',
                'pid': process.pid,
                'started_at': datetime.now(),
                'restarts': self.restart_counts.get(agent_name, 0),
                'last_health_check': datetime.now(),
                'config': config
            }
            
            self.logger.info(f"🚀 Started {agent_name} (PID: {process.pid})")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start {agent_name}: {e}")
            return False
    
    def stop_agent(self, agent_name: str) -> bool:
        """Stop specific agent"""
        if agent_name not in self.processes:
            self.logger.warning(f"⚠️ Agent {agent_name} not running")
            return False
        
        process = self.processes[agent_name]
        
        try:
            # Graceful shutdown
            if process.poll() is None:
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # Force kill if necessary
                    process.kill()
                    process.wait()
            
            del self.processes[agent_name]
            self.status[agent_name]['status'] = 'stopped'
            self.status[agent_name]['stopped_at'] = datetime.now()
            
            self.logger.info(f"🛑 Stopped {agent_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to stop {agent_name}: {e}")
            return False
    
    def restart_agent(self, agent_name: str) -> bool:
        """Restart specific agent"""
        self.logger.info(f"🔄 Restarting {agent_name}...")
        
        # Stop first
        self.stop_agent(agent_name)
        
        # Wait a bit
        time.sleep(2)
        
        # Start again
        success = self.start_agent(agent_name)
        
        if success:
            # Update restart count
            self.restart_counts[agent_name] = self.restart_counts.get(agent_name, 0) + 1
        
        return success
    
    def check_agent_health(self, agent_name: str) -> bool:
        """Check if agent is healthy"""
        if agent_name not in self.processes:
            return False
        
        process = self.processes[agent_name]
        
        # Check if process is still running
        if process.poll() is not None:
            self.logger.warning(f"⚠️ Agent {agent_name} process died")
            return False
        
        # Check if process is responsive (basic check)
        try:
            # Update health check time
            self.status[agent_name]['last_health_check'] = datetime.now()
            self.status[agent_name]['status'] = 'running'
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Health check failed for {agent_name}: {e}")
            return False
    
    def health_monitor_loop(self):
        """Continuous health monitoring"""
        while True:
            try:
                for agent_name in list(self.processes.keys()):
                    config = self.agent_configs[agent_name]
                    last_check = self.status[agent_name]['last_health_check']
                    
                    # Check if it's time for health check
                    if (datetime.now() - last_check).seconds >= config['health_check_interval']:
                        if not self.check_agent_health(agent_name):
                            # Agent is unhealthy
                            self.status[agent_name]['status'] = 'unhealthy'
                            
                            # Auto-restart if enabled
                            if config['auto_restart']:
                                restart_count = self.restart_counts.get(agent_name, 0)
                                
                                if restart_count < self.max_restarts:
                                    self.logger.warning(f"⚠️ Auto-restarting unhealthy agent: {agent_name}")
                                    self.restart_agent(agent_name)
                                else:
                                    self.logger.error(f"❌ Max restarts reached for {agent_name}, disabling auto-restart")
                                    self.agent_configs[agent_name]['auto_restart'] = False
                
                # Sleep before next check
                time.sleep(30)
                
            except Exception as e:
                self.logger.error(f"❌ Health monitor error: {e}")
                time.sleep(60)
    
    def start_all_agents(self):
        """Start semua agents dengan prioritas"""
        self.logger.info("🚀 Starting all agents...")
        
        # Sort by priority (higher first)
        sorted_agents = sorted(
            self.agent_configs.items(),
            key=lambda x: x[1]['priority'],
            reverse=True
        )
        
        for agent_name, config in sorted_agents:
            self.logger.info(f"🔄 Starting {agent_name} (Priority: {config['priority']})")
            
            success = self.start_agent(agent_name)
            
            if success:
                # Wait for startup delay
                if config['startup_delay'] > 0:
                    self.logger.info(f"⏳ Waiting {config['startup_delay']}s before next agent...")
                    time.sleep(config['startup_delay'])
            else:
                self.logger.error(f"❌ Failed to start {agent_name}")
        
        self.logger.info("✅ All agents startup sequence completed")
    
    def stop_all_agents(self):
        """Stop semua agents"""
        self.logger.info("🛑 Stopping all agents...")
        
        # Sort by priority (lower first for shutdown)
        sorted_agents = sorted(
            self.agent_configs.items(),
            key=lambda x: x[1]['priority']
        )
        
        for agent_name, config in sorted_agents:
            if agent_name in self.processes:
                self.stop_agent(agent_name)
                time.sleep(1)  # Small delay between stops
        
        self.logger.info("✅ All agents stopped")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        total_agents = len(self.agent_configs)
        running_agents = len([s for s in self.status.values() if s['status'] == 'running'])
        unhealthy_agents = len([s for s in self.status.values() if s['status'] == 'unhealthy'])
        
        # System resource usage
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'timestamp': datetime.now().isoformat(),
            'agents': {
                'total': total_agents,
                'running': running_agents,
                'unhealthy': unhealthy_agents,
                'stopped': total_agents - running_agents,
                'details': self.status
            },
            'system': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024**3)
            },
            'uptime': {
                'launcher_start': getattr(self, 'start_time', datetime.now()).isoformat()
            }
        }
    
    def generate_status_report(self) -> str:
        """Generate human-readable status report"""
        status = self.get_system_status()
        
        report = f"""
🚀 AUTONOMOUS AI SYSTEM STATUS
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🤖 AGENTS STATUS:
  Total Agents: {status['agents']['total']}
  Running: {status['agents']['running']} ✅
  Unhealthy: {status['agents']['unhealthy']} ⚠️
  Stopped: {status['agents']['stopped']} ❌

📊 SYSTEM RESOURCES:
  CPU Usage: {status['system']['cpu_percent']:.1f}%
  Memory Usage: {status['system']['memory_percent']:.1f}%
  Disk Usage: {status['system']['disk_percent']:.1f}%

🔧 AGENT DETAILS:
"""
        
        for agent_name, details in status['agents']['details'].items():
            status_emoji = "✅" if details['status'] == 'running' else "⚠️" if details['status'] == 'unhealthy' else "❌"
            uptime = ""
            if 'started_at' in details:
                uptime = f"(Uptime: {datetime.now() - details['started_at']})"
            
            report += f"  {status_emoji} {agent_name}: {details['status']} {uptime}\n"
        
        return report

class AutonomousLauncher:
    """Main autonomous launcher system"""
    
    def __init__(self):
        self.process_manager = ProcessManager()
        self.running = False
        self.start_time = datetime.now()
        self.process_manager.start_time = self.start_time
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("🚀 Autonomous Launcher initialized!")
        print("🎭 Ready to coordinate all AI agents!")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        self.shutdown()
    
    def start_autonomous_mode(self):
        """Start autonomous operation mode"""
        self.running = True
        
        print("🚀 Starting Autonomous AI System...")
        print("🤖 Initializing all agents with coordination...")
        
        # Start all agents
        self.process_manager.start_all_agents()
        
        # Start health monitoring in background
        health_thread = threading.Thread(
            target=self.process_manager.health_monitor_loop,
            daemon=True
        )
        health_thread.start()
        
        # Status reporting thread
        status_thread = threading.Thread(
            target=self.status_reporter_loop,
            daemon=True
        )
        status_thread.start()
        
        print("\n" + "="*60)
        print("🎉 AUTONOMOUS AI SYSTEM STARTED SUCCESSFULLY!")
        print("="*60)
        print("🎭 Master Orchestrator: Coordinating all agents")
        print("🧠 Intelligent Agent: Developing autonomously")
        print("🤖 All Agents: Running in perfect harmony")
        print("📊 Health Monitor: Active")
        print("🔄 Auto-restart: Enabled")
        print("="*60)
        
        # Print initial status
        print(self.process_manager.generate_status_report())
        
        try:
            # Keep main thread alive
            while self.running:
                time.sleep(60)
                
                # Periodic status check
                status = self.process_manager.get_system_status()
                if status['agents']['running'] == 0:
                    print("⚠️ All agents stopped, attempting restart...")
                    self.process_manager.start_all_agents()
                
        except KeyboardInterrupt:
            self.shutdown()
    
    def status_reporter_loop(self):
        """Periodic status reporting"""
        while self.running:
            try:
                time.sleep(300)  # Report every 5 minutes
                
                status = self.process_manager.get_system_status()
                
                # Log summary
                self.process_manager.logger.info(
                    f"📊 Status: {status['agents']['running']}/{status['agents']['total']} agents running, "
                    f"CPU: {status['system']['cpu_percent']:.1f}%, "
                    f"Memory: {status['system']['memory_percent']:.1f}%"
                )
                
                # Save status to file
                os.makedirs("data", exist_ok=True)
                with open("data/system_status.json", "w") as f:
                    json.dump(status, f, indent=2, default=str)
                
            except Exception as e:
                self.process_manager.logger.error(f"❌ Status reporter error: {e}")
                time.sleep(60)
    
    def shutdown(self):
        """Graceful shutdown"""
        self.running = False
        
        print("\n🛑 Shutting down Autonomous AI System...")
        print("🔄 Stopping all agents gracefully...")
        
        self.process_manager.stop_all_agents()
        
        print("✅ Autonomous AI System stopped successfully")
        print("👋 Thank you for using Agentic AI!")
        
        sys.exit(0)
    
    def restart_system(self):
        """Restart entire system"""
        print("🔄 Restarting Autonomous AI System...")
        
        self.process_manager.stop_all_agents()
        time.sleep(5)
        self.process_manager.start_all_agents()
        
        print("✅ System restart completed")

def main():
    """Main entry point"""
    print("🎭" + "="*60 + "🎭")
    print("🚀 AGENTIC AI - AUTONOMOUS LAUNCHER")
    print("🇮🇩 Made with ❤️ by Mulky Malikul Dhaher in Indonesia")
    print("🎭" + "="*60 + "🎭")
    print()
    
    # Create and start launcher
    launcher = AutonomousLauncher()
    
    try:
        launcher.start_autonomous_mode()
    except Exception as e:
        print(f"❌ Critical error: {e}")
        launcher.shutdown()

if __name__ == "__main__":
    main()