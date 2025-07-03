"""
FastAPI Server for Autonomous Agent Colony
Provides REST API endpoints for all system functionality
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import uuid

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from ..utils.logger import get_logger

logger = get_logger(__name__)

# Pydantic models for API
class TaskRequest(BaseModel):
    type: str
    content: str
    context: Optional[Dict[str, Any]] = {}
    preferred_role: Optional[str] = None
    priority: int = 5

class CodeCompletionRequest(BaseModel):
    file_path: str
    code_context: str
    cursor_position: int
    language: Optional[str] = None

class RefactoringRequest(BaseModel):
    file_path: str
    code: str
    refactor_type: str

class AgentCreateRequest(BaseModel):
    role: str
    config: Optional[Dict[str, Any]] = {}

class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_text(json.dumps(message))
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                # Remove stale connections
                self.active_connections.remove(connection)

class APIServer:
    """FastAPI server for the autonomous agent colony"""
    
    def __init__(self, controller):
        self.controller = controller
        self.app = FastAPI(
            title="Autonomous Agent Colony API",
            description="API for managing autonomous AI agents and intelligent code editing",
            version="1.0.0"
        )
        self.websocket_manager = WebSocketManager()
        self.server = None
        
        # Configure CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup all API routes"""
        
        @self.app.get("/")
        async def root():
            return {
                "message": "Autonomous Agent Colony API",
                "version": "1.0.0",
                "status": "operational",
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.get("/health")
        async def health_check():
            """System health check"""
            try:
                status = self.controller.get_system_status()
                
                health_status = {
                    "status": "healthy" if status.get("running") else "unhealthy",
                    "timestamp": datetime.now().isoformat(),
                    "components": status.get("components", {}),
                    "uptime": status.get("uptime"),
                    "version": "1.0.0"
                }
                
                return health_status
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
        
        # Agent Management Routes
        @self.app.post("/agents")
        async def create_agent(request: AgentCreateRequest):
            """Create a new agent"""
            try:
                agent_id = await self.controller.agent_manager.create_agent(
                    request.role,
                    request.config
                )
                
                # Broadcast agent creation
                await self.websocket_manager.broadcast({
                    "type": "agent_created",
                    "agent_id": agent_id,
                    "role": request.role,
                    "timestamp": datetime.now().isoformat()
                })
                
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "role": request.role,
                    "message": f"Agent {agent_id} created successfully"
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/agents")
        async def list_agents():
            """List all agents"""
            try:
                status = self.controller.agent_manager.get_status()
                return {
                    "success": True,
                    "agents": status.get("agents", {}),
                    "summary": {
                        "total_agents": status.get("total_agents", 0),
                        "agent_types": status.get("agent_types", {}),
                        "queue_size": status.get("queue_size", 0)
                    }
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/agents/{agent_id}")
        async def get_agent(agent_id: str):
            """Get specific agent details"""
            try:
                agent = self.controller.agent_manager.agents.get(agent_id)
                if not agent:
                    raise HTTPException(status_code=404, detail="Agent not found")
                
                return {
                    "success": True,
                    "agent": agent.get_status()
                }
                
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.delete("/agents/{agent_id}")
        async def remove_agent(agent_id: str):
            """Remove an agent"""
            try:
                await self.controller.agent_manager.remove_agent(agent_id)
                
                # Broadcast agent removal
                await self.websocket_manager.broadcast({
                    "type": "agent_removed",
                    "agent_id": agent_id,
                    "timestamp": datetime.now().isoformat()
                })
                
                return {
                    "success": True,
                    "message": f"Agent {agent_id} removed successfully"
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Task Management Routes
        @self.app.post("/tasks")
        async def submit_task(request: TaskRequest):
            """Submit a task to the agent colony"""
            try:
                task = {
                    "type": request.type,
                    "content": request.content,
                    "context": request.context,
                    "preferred_role": request.preferred_role,
                    "priority": request.priority
                }
                
                task_id = await self.controller.agent_manager.submit_task(task)
                
                # Broadcast task submission
                await self.websocket_manager.broadcast({
                    "type": "task_submitted",
                    "task_id": task_id,
                    "task_type": request.type,
                    "timestamp": datetime.now().isoformat()
                })
                
                return {
                    "success": True,
                    "task_id": task_id,
                    "message": "Task submitted successfully"
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/tasks/{task_id}")
        async def get_task_status(task_id: str):
            """Get task status"""
            # This would require implementing task tracking in the agent manager
            return {
                "success": True,
                "task_id": task_id,
                "status": "processing",
                "message": "Task status tracking not yet implemented"
            }
        
        # Code Editor Routes
        @self.app.post("/code/completion")
        async def code_completion(request: CodeCompletionRequest):
            """Get AI code completions"""
            try:
                result = await self.controller.cursor_editor.ai_code_completion(
                    request.file_path,
                    request.code_context,
                    request.cursor_position
                )
                
                return result
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/code/refactor")
        async def code_refactoring(request: RefactoringRequest):
            """Get code refactoring suggestions"""
            try:
                result = await self.controller.cursor_editor.intelligent_refactoring(
                    request.file_path,
                    request.code,
                    request.refactor_type
                )
                
                return result
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/code/analyze")
        async def analyze_code(file_path: str, code: str):
            """Analyze code for issues and suggestions"""
            try:
                # Update file context for background analysis
                self.controller.cursor_editor.update_file_context(file_path, code)
                
                # Get current suggestions
                suggestions = self.controller.cursor_editor.get_suggestions(file_path)
                
                return {
                    "success": True,
                    "file_path": file_path,
                    "suggestions": suggestions,
                    "analysis_timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Model Management Routes
        @self.app.get("/models")
        async def list_models():
            """List available models"""
            try:
                status = self.controller.model_manager.get_status()
                return {
                    "success": True,
                    "models": status
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/models/generate")
        async def generate_response(prompt: str, model_name: str = None, **kwargs):
            """Generate response using model manager"""
            try:
                response = await self.controller.model_manager.generate_response(
                    prompt, model_name, **kwargs
                )
                
                return {
                    "success": True,
                    "response": response,
                    "model_used": model_name or "auto_selected",
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # System Management Routes
        @self.app.get("/system/status")
        async def system_status():
            """Get comprehensive system status"""
            try:
                return {
                    "success": True,
                    "system": self.controller.get_system_status(),
                    "agents": self.controller.agent_manager.get_status(),
                    "models": self.controller.model_manager.get_status(),
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/system/shutdown")
        async def shutdown_system():
            """Gracefully shutdown the system"""
            try:
                # Broadcast shutdown notice
                await self.websocket_manager.broadcast({
                    "type": "system_shutdown",
                    "message": "System is shutting down gracefully",
                    "timestamp": datetime.now().isoformat()
                })
                
                # Schedule shutdown
                asyncio.create_task(self._delayed_shutdown())
                
                return {
                    "success": True,
                    "message": "System shutdown initiated"
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # WebSocket Route
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates"""
            await self.websocket_manager.connect(websocket)
            try:
                while True:
                    # Keep connection alive and handle incoming messages
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    # Echo back for now (can add more sophisticated handling)
                    await self.websocket_manager.send_personal_message({
                        "type": "echo",
                        "data": message,
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
                    
            except WebSocketDisconnect:
                self.websocket_manager.disconnect(websocket)
        
        # Development/Testing Routes
        @self.app.get("/dev/ping")
        async def ping():
            """Simple ping endpoint for testing"""
            return {
                "message": "pong",
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.post("/dev/test-agent")
        async def test_agent():
            """Create a test agent and task for development"""
            try:
                # Create test agent
                agent_id = await self.controller.agent_manager.create_agent("developer")
                
                # Submit test task
                test_task = {
                    "type": "coding",
                    "content": "Write a simple hello world function in Python",
                    "context": {},
                    "preferred_role": "developer"
                }
                
                task_id = await self.controller.agent_manager.submit_task(test_task)
                
                return {
                    "success": True,
                    "test_agent_id": agent_id,
                    "test_task_id": task_id,
                    "message": "Test agent and task created"
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    
    async def _delayed_shutdown(self):
        """Delayed shutdown to allow response to be sent"""
        await asyncio.sleep(2)
        await self.controller.shutdown()
    
    async def start(self):
        """Start the API server"""
        try:
            config = uvicorn.Config(
                app=self.app,
                host="0.0.0.0",
                port=8000,
                log_level="info",
                access_log=True
            )
            
            self.server = uvicorn.Server(config)
            
            # Start server in background
            asyncio.create_task(self.server.serve())
            
            logger.info("✅ API Server started on http://0.0.0.0:8000")
            
        except Exception as e:
            logger.error(f"Failed to start API server: {e}")
            raise
    
    async def stop(self):
        """Stop the API server"""
        if self.server:
            self.server.should_exit = True
            logger.info("✅ API Server stopped")
    
    def is_healthy(self) -> bool:
        """Check if API server is healthy"""
        return self.server is not None and not getattr(self.server, 'should_exit', True)