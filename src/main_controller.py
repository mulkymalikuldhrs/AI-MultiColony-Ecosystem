"""
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
        # Note: Other skills will be implemented separately
        
        # Initialize API and Web interface
        self.api_server = APIServer(self)
        self.web_interface = WebInterface(self)
        
        # Set cross-references after initialization
        self.agent_manager.set_model_manager(self.model_manager)
        self.cursor_editor.set_model_manager(self.model_manager)
        self.cursor_editor.set_agent_manager(self.agent_manager)
        
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
            logger.info("✅ Skills initialized")
            
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
            
            # Other request types can be added here when more skills are implemented
            
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
                "api_server": bool(self.api_server),
                "web_interface": bool(self.web_interface)
            }
        }
