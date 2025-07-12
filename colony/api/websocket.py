"""
WebSocket Server for Real-time Communication
Provides WebSocket endpoints for real-time updates and agent communication
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Set, Optional
import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel

# Setup logger
logger = logging.getLogger("api.websocket")

# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections and message broadcasting."""
    
    def __init__(self):
        """Initialize the connection manager."""
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {
            "system_updates": {},
            "agent_logs": {},
            "chat": {}
        }
    
    async def connect(self, websocket: WebSocket, client_id: str, channel: str):
        """
        Connect a client to a channel.
        
        Args:
            websocket: WebSocket connection
            client_id: Client ID
            channel: Channel to connect to
        """
        await websocket.accept()
        
        if channel not in self.active_connections:
            self.active_connections[channel] = {}
        
        self.active_connections[channel][client_id] = websocket
        logger.info(f"Client {client_id} connected to channel {channel}")
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connection_established",
            "channel": channel,
            "client_id": client_id
        })
    
    async def disconnect(self, client_id: str, channel: str):
        """
        Disconnect a client from a channel.
        
        Args:
            client_id: Client ID
            channel: Channel to disconnect from
        """
        if channel in self.active_connections and client_id in self.active_connections[channel]:
            del self.active_connections[channel][client_id]
            logger.info(f"Client {client_id} disconnected from channel {channel}")
    
    async def send_personal_message(self, message: Dict[str, Any], client_id: str, channel: str):
        """
        Send a message to a specific client.
        
        Args:
            message: Message to send
            client_id: Client ID
            channel: Channel to send to
        """
        if channel in self.active_connections and client_id in self.active_connections[channel]:
            await self.active_connections[channel][client_id].send_json(message)
    
    async def broadcast(self, message: Dict[str, Any], channel: str):
        """
        Broadcast a message to all clients in a channel.
        
        Args:
            message: Message to broadcast
            channel: Channel to broadcast to
        """
        if channel in self.active_connections:
            disconnected_clients = []
            
            for client_id, connection in self.active_connections[channel].items():
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to client {client_id}: {str(e)}")
                    disconnected_clients.append(client_id)
            
            # Clean up disconnected clients
            for client_id in disconnected_clients:
                await self.disconnect(client_id, channel)

# Create connection manager
manager = ConnectionManager()

# WebSocket routes
def setup_websocket_routes(app: FastAPI):
    """
    Setup WebSocket routes.
    
    Args:
        app: FastAPI application
    """
    @app.websocket("/ws/system")
    async def websocket_system_endpoint(websocket: WebSocket):
        """WebSocket endpoint for system updates."""
        client_id = str(uuid.uuid4())
        channel = "system_updates"
        
        await manager.connect(websocket, client_id, channel)
        
        try:
            while True:
                # Wait for messages from the client
                data = await websocket.receive_text()
                
                # Process message
                try:
                    message = json.loads(data)
                    logger.info(f"Received message from client {client_id}: {message}")
                    
                    # Echo message back to client
                    await manager.send_personal_message({
                        "type": "echo",
                        "content": message
                    }, client_id, channel)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from client {client_id}: {data}")
                    await manager.send_personal_message({
                        "type": "error",
                        "content": "Invalid JSON"
                    }, client_id, channel)
        except WebSocketDisconnect:
            await manager.disconnect(client_id, channel)
        except Exception as e:
            logger.error(f"Error in system websocket: {str(e)}")
            await manager.disconnect(client_id, channel)
    
    @app.websocket("/ws/agent/{agent_id}")
    async def websocket_agent_endpoint(websocket: WebSocket, agent_id: str):
        """WebSocket endpoint for agent logs."""
        client_id = str(uuid.uuid4())
        channel = f"agent_logs_{agent_id}"
        
        # Create channel if it doesn't exist
        if channel not in manager.active_connections:
            manager.active_connections[channel] = {}
        
        await manager.connect(websocket, client_id, channel)
        
        try:
            while True:
                # Wait for messages from the client
                data = await websocket.receive_text()
                
                # Process message
                try:
                    message = json.loads(data)
                    logger.info(f"Received message from client {client_id} for agent {agent_id}: {message}")
                    
                    # Echo message back to client
                    await manager.send_personal_message({
                        "type": "echo",
                        "content": message
                    }, client_id, channel)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from client {client_id}: {data}")
                    await manager.send_personal_message({
                        "type": "error",
                        "content": "Invalid JSON"
                    }, client_id, channel)
        except WebSocketDisconnect:
            await manager.disconnect(client_id, channel)
        except Exception as e:
            logger.error(f"Error in agent websocket: {str(e)}")
            await manager.disconnect(client_id, channel)
    
    @app.websocket("/ws/chat")
    async def websocket_chat_endpoint(websocket: WebSocket):
        """WebSocket endpoint for chat."""
        client_id = str(uuid.uuid4())
        channel = "chat"
        
        await manager.connect(websocket, client_id, channel)
        
        try:
            while True:
                # Wait for messages from the client
                data = await websocket.receive_text()
                
                # Process message
                try:
                    message = json.loads(data)
                    logger.info(f"Received chat message from client {client_id}: {message}")
                    
                    # Broadcast message to all clients
                    await manager.broadcast({
                        "type": "chat_message",
                        "client_id": client_id,
                        "content": message
                    }, channel)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from client {client_id}: {data}")
                    await manager.send_personal_message({
                        "type": "error",
                        "content": "Invalid JSON"
                    }, client_id, channel)
        except WebSocketDisconnect:
            await manager.disconnect(client_id, channel)
        except Exception as e:
            logger.error(f"Error in chat websocket: {str(e)}")
            await manager.disconnect(client_id, channel)

# Function to broadcast system update
async def broadcast_system_update(update: Dict[str, Any]):
    """
    Broadcast a system update to all clients.
    
    Args:
        update: Update to broadcast
    """
    await manager.broadcast({
        "type": "system_update",
        "timestamp": update.get("timestamp", None),
        "content": update
    }, "system_updates")

# Function to broadcast agent log
async def broadcast_agent_log(agent_id: str, log: Dict[str, Any]):
    """
    Broadcast an agent log to all clients subscribed to the agent.
    
    Args:
        agent_id: Agent ID
        log: Log to broadcast
    """
    channel = f"agent_logs_{agent_id}"
    
    # Create channel if it doesn't exist
    if channel not in manager.active_connections:
        manager.active_connections[channel] = {}
    
    await manager.broadcast({
        "type": "agent_log",
        "agent_id": agent_id,
        "timestamp": log.get("timestamp", None),
        "content": log
    }, channel)