#!/usr/bin/env python3
"""
🚀 Autonomous Agent Colony - Standalone Main Launcher
Entry point for the entire system with minimal dependencies
"""

import asyncio
import sys
import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class StandaloneLogger:
    """Standalone logger without external dependencies"""
    
    def __init__(self):
        self.setup_logging()
    
    def setup_logging(self):
        """Setup basic logging"""
        logs_dir = project_root / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(log_format))
        
        # File handler
        log_file = logs_dir / f"colony_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        
        # Setup root logger
        self.logger = logging.getLogger("autonomous_colony")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def info(self, message):
        self.logger.info(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def warning(self, message):
        self.logger.warning(message)

class StandaloneConfigManager:
    """Standalone configuration manager"""
    
    def __init__(self):
        self.project_root = project_root
        self.config_dir = self.project_root / "config"
        self.load_env_file()
    
    def load_env_file(self):
        """Load .env file manually without python-dotenv"""
        env_file = self.project_root / ".env"
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
            except Exception as e:
                print(f"Warning: Could not load .env file: {e}")
    
    def load_config(self) -> Dict[str, Any]:
        """Load main configuration"""
        config_file = self.config_dir / "main_config.json"
        
        if not config_file.exists():
            return self._get_default_config()
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
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
                "environment": "standalone"
            },
            "features": {
                "web_interface": False,  # Disabled for standalone
                "api_server": False,     # Disabled for standalone
                "cursor_editor": True,
                "autonomous_agents": True
            }
        }

class MockModelManager:
    """Mock model manager for standalone operation"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.models = {}
        self.providers = {}
        
    async def initialize(self):
        """Initialize mock model manager"""
        print("🤖 Mock Model Manager initialized (no external models)")
        
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate mock response"""
        return f"Mock response for: {prompt[:50]}..."
    
    async def health_check(self) -> bool:
        """Mock health check"""
        return True
    
    async def shutdown(self):
        """Mock shutdown"""
        print("🤖 Mock Model Manager shutdown")
    
    def get_status(self) -> Dict[str, Any]:
        """Get mock status"""
        return {
            "total_models": 0,
            "healthy_models": 0,
            "providers": [],
            "mock_mode": True
        }

class MockAgent:
    """Mock agent for standalone operation"""
    
    def __init__(self, agent_id: str, role: str):
        self.agent_id = agent_id
        self.role = role
        self.status = "ready"
        self.task_count = 0
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process mock task"""
        self.task_count += 1
        self.last_activity = datetime.now()
        self.status = "working"
        
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        self.status = "ready"
        
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "task_id": task.get("id"),
            "success": True,
            "response": f"Mock response from {self.role} for task: {task.get('content', '')[:50]}...",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "status": self.status,
            "task_count": self.task_count,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat()
        }

class MockAgentManager:
    """Mock agent manager for standalone operation"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agents = {}
        self.task_queue = asyncio.Queue()
        
    async def initialize(self):
        """Initialize mock agent manager"""
        # Create some default agents
        await self.create_agent("developer")
        await self.create_agent("analyst")
        await self.create_agent("researcher")
        print(f"🤖 Mock Agent Manager initialized with {len(self.agents)} agents")
        
        # Start task processor
        asyncio.create_task(self._process_tasks())
    
    async def create_agent(self, role: str) -> str:
        """Create a mock agent"""
        agent_id = f"{role}_{len(self.agents) + 1}"
        agent = MockAgent(agent_id, role)
        self.agents[agent_id] = agent
        return agent_id
    
    async def submit_task(self, task: Dict[str, Any]) -> str:
        """Submit task to queue"""
        task_id = task.get("id", f"task_{datetime.now().strftime('%H%M%S')}")
        task["id"] = task_id
        await self.task_queue.put(task)
        print(f"📝 Task {task_id} submitted")
        return task_id
    
    async def _process_tasks(self):
        """Process tasks from queue"""
        while True:
            try:
                task = await self.task_queue.get()
                
                # Find available agent
                available_agents = [a for a in self.agents.values() if a.status == "ready"]
                if available_agents:
                    agent = available_agents[0]
                    result = await agent.process_task(task)
                    print(f"✅ Task {task.get('id')} completed by {agent.agent_id}")
                else:
                    # Put task back if no agents available
                    await self.task_queue.put(task)
                    await asyncio.sleep(1)
                
                self.task_queue.task_done()
                
            except Exception as e:
                print(f"Error processing task: {e}")
                await asyncio.sleep(1)
    
    async def health_check(self) -> bool:
        """Mock health check"""
        return len(self.agents) > 0
    
    async def shutdown(self):
        """Mock shutdown"""
        print("🤖 Mock Agent Manager shutdown")
    
    def get_status(self) -> Dict[str, Any]:
        """Get status"""
        return {
            "total_agents": len(self.agents),
            "agents": {aid: agent.get_status() for aid, agent in self.agents.items()},
            "queue_size": self.task_queue.qsize(),
            "mock_mode": True
        }

class MockCursorEditor:
    """Mock cursor editor for standalone operation"""
    
    def __init__(self):
        self.file_contexts = {}
        
    async def initialize(self):
        """Initialize mock cursor editor"""
        print("📝 Mock Cursor Editor initialized")
    
    async def ai_code_completion(self, file_path: str, code_context: str, cursor_position: int) -> Dict[str, Any]:
        """Mock code completion"""
        return {
            "success": True,
            "completions": [
                {
                    "text": "# Mock completion",
                    "label": "Mock suggestion",
                    "detail": "Generated by standalone system",
                    "priority": 5
                }
            ],
            "context": {
                "file_path": file_path,
                "cursor_position": cursor_position,
                "mock_mode": True
            }
        }
    
    def set_model_manager(self, model_manager):
        """Set model manager reference"""
        pass

class StandaloneController:
    """Standalone controller for autonomous agent colony"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.running = False
        self.logger = StandaloneLogger()
        
        # Initialize components
        self.model_manager = MockModelManager(config.get("models", {}))
        self.agent_manager = MockAgentManager(config.get("colony", {}))
        self.cursor_editor = MockCursorEditor()
        
        # Set cross-references
        self.cursor_editor.set_model_manager(self.model_manager)
    
    async def start(self):
        """Start all system components"""
        try:
            self.logger.info("Starting Standalone Colony Controller")
            
            # Initialize components
            await self.model_manager.initialize()
            await self.agent_manager.initialize()
            await self.cursor_editor.initialize()
            
            self.running = True
            self.logger.info("🚀 Standalone Colony System fully operational!")
            
        except Exception as e:
            self.logger.error(f"Failed to start system: {e}")
            raise
    
    async def run_forever(self):
        """Keep the system running"""
        print("""
🐫 Autonomous Agent Colony System Running
========================================

Available Commands:
- 'task <description>' : Submit a task to agents
- 'status' : Show system status
- 'agents' : List all agents
- 'completion <code>' : Test code completion
- 'help' : Show this help
- 'quit' : Exit system

Type your command:
        """)
        
        while self.running:
            try:
                # Simple CLI interface
                command = input(">>> ").strip()
                
                if command.lower() in ['quit', 'exit']:
                    break
                elif command.lower() == 'status':
                    await self._show_status()
                elif command.lower() == 'agents':
                    await self._show_agents()
                elif command.lower() == 'help':
                    self._show_help()
                elif command.startswith('task '):
                    task_desc = command[5:]
                    await self._submit_task(task_desc)
                elif command.startswith('completion '):
                    code = command[11:]
                    await self._test_completion(code)
                elif command:
                    print(f"Unknown command: {command}. Type 'help' for available commands.")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
    
    async def _show_status(self):
        """Show system status"""
        agent_status = self.agent_manager.get_status()
        model_status = self.model_manager.get_status()
        
        print(f"""
System Status:
--------------
🤖 Total Agents: {agent_status['total_agents']}
📋 Queue Size: {agent_status['queue_size']}
🧠 Models: {model_status['total_models']} (Mock Mode)
⚡ Status: {'Running' if self.running else 'Stopped'}
        """)
    
    async def _show_agents(self):
        """Show all agents"""
        status = self.agent_manager.get_status()
        print("\nAgent List:")
        print("-----------")
        for agent_id, agent_data in status['agents'].items():
            print(f"🤖 {agent_id} ({agent_data['role']}) - {agent_data['status']} - Tasks: {agent_data['task_count']}")
    
    def _show_help(self):
        """Show help"""
        print("""
Available Commands:
-------------------
task <description>    - Submit a task to the agent colony
status               - Show system status
agents              - List all agents
completion <code>   - Test AI code completion
help                - Show this help
quit/exit           - Exit the system
        """)
    
    async def _submit_task(self, description: str):
        """Submit a task"""
        task = {
            "type": "general",
            "content": description,
            "context": {}
        }
        
        task_id = await self.agent_manager.submit_task(task)
        print(f"✅ Task '{description}' submitted with ID: {task_id}")
    
    async def _test_completion(self, code: str):
        """Test code completion"""
        result = await self.cursor_editor.ai_code_completion(
            "test.py", code, len(code)
        )
        
        print(f"\nCode Completion for: {code}")
        print("--------------------")
        for completion in result['completions']:
            print(f"💡 {completion['label']}: {completion['text']}")
    
    async def shutdown(self):
        """Gracefully shutdown all components"""
        self.logger.info("Shutting down Standalone Colony System...")
        self.running = False
        
        await self.agent_manager.shutdown()
        await self.model_manager.shutdown()
        
        self.logger.info("✅ System shutdown complete")
    
    def get_system_status(self):
        """Get system status"""
        return {
            "running": self.running,
            "components": {
                "model_manager": True,
                "agent_manager": True,
                "cursor_editor": True
            },
            "mode": "standalone"
        }

async def main():
    """Main entry point for Standalone Autonomous Agent Colony"""
    try:
        print("""
🐫 Autonomous Agent Colony - Standalone Mode
===========================================
Running with minimal dependencies (Python built-ins only)
        """)
        
        # Load configuration
        config_manager = StandaloneConfigManager()
        config = config_manager.load_config()
        
        # Initialize main controller
        controller = StandaloneController(config)
        
        # Start the system
        await controller.start()
        
        print("✅ System started successfully!")
        print("🎯 Standalone mode - No external dependencies required")
        
        # Keep running with interactive CLI
        await controller.run_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down gracefully...")
        if 'controller' in locals():
            await controller.shutdown()
    except Exception as e:
        print(f"❌ Error starting system: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Check if we're in an event loop already
    try:
        asyncio.get_running_loop()
        # If we're already in an event loop, create a new one
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(lambda: asyncio.run(main()))
            future.result()
    except RuntimeError:
        # No event loop running, safe to use asyncio.run
        asyncio.run(main())