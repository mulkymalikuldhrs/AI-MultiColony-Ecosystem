"""
🔗 MCP (Model Context Protocol) Connector
Enables integration with MCP-compatible tools and resources

🇮🇩 Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import asyncio
import json
import websockets
import uuid
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging

class MCPConnector:
    """
    Model Context Protocol Connector
    
    Enables the Agentic AI System to:
    - Connect to MCP servers
    - Access MCP tools and resources
    - Execute MCP prompts
    - Share context across agents
    """
    
    def __init__(self):
        self.connections = {}
        self.tools = {}
        self.resources = {}
        self.prompts = {}
        self.session_id = str(uuid.uuid4())
        
        # MCP protocol version
        self.protocol_version = "2024-11-05"
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
    async def connect_to_server(self, server_url: str, server_name: str = None) -> bool:
        """Connect to an MCP server"""
        try:
            if not server_name:
                server_name = server_url.split('/')[-1]
            
            # Establish WebSocket connection
            websocket = await websockets.connect(server_url)
            
            # Initialize MCP handshake
            initialization = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "initialize",
                "params": {
                    "protocolVersion": self.protocol_version,
                    "capabilities": {
                        "tools": {"listChanged": True},
                        "resources": {"subscribe": True, "listChanged": True},
                        "prompts": {"listChanged": True},
                        "logging": {}
                    },
                    "clientInfo": {
                        "name": "Agentic AI System",
                        "version": "3.0.0",
                        "creator": "Mulky Malikul Dhaher"
                    }
                }
            }
            
            await websocket.send(json.dumps(initialization))
            response = await websocket.recv()
            init_response = json.loads(response)
            
            if "result" in init_response:
                # Store successful connection
                self.connections[server_name] = {
                    "websocket": websocket,
                    "url": server_url,
                    "capabilities": init_response["result"].get("capabilities", {}),
                    "server_info": init_response["result"].get("serverInfo", {}),
                    "connected_at": datetime.now().isoformat()
                }
                
                # Send initialized notification
                initialized = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized",
                    "params": {}
                }
                await websocket.send(json.dumps(initialized))
                
                # Load available tools and resources
                await self._load_server_capabilities(server_name)
                
                self.logger.info(f"✅ Connected to MCP server: {server_name}")
                return True
            else:
                self.logger.error(f"❌ Failed to initialize MCP server: {server_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error connecting to MCP server {server_name}: {e}")
            return False
    
    async def _load_server_capabilities(self, server_name: str):
        """Load tools, resources, and prompts from MCP server"""
        connection = self.connections[server_name]
        websocket = connection["websocket"]
        
        try:
            # List tools
            if connection["capabilities"].get("tools"):
                tools_request = {
                    "jsonrpc": "2.0",
                    "id": str(uuid.uuid4()),
                    "method": "tools/list",
                    "params": {}
                }
                
                await websocket.send(json.dumps(tools_request))
                tools_response = await websocket.recv()
                tools_data = json.loads(tools_response)
                
                if "result" in tools_data:
                    for tool in tools_data["result"].get("tools", []):
                        tool_id = f"{server_name}::{tool['name']}"
                        self.tools[tool_id] = {
                            **tool,
                            "server": server_name,
                            "type": "mcp_tool"
                        }
            
            # List resources
            if connection["capabilities"].get("resources"):
                resources_request = {
                    "jsonrpc": "2.0",
                    "id": str(uuid.uuid4()),
                    "method": "resources/list",
                    "params": {}
                }
                
                await websocket.send(json.dumps(resources_request))
                resources_response = await websocket.recv()
                resources_data = json.loads(resources_response)
                
                if "result" in resources_data:
                    for resource in resources_data["result"].get("resources", []):
                        resource_id = f"{server_name}::{resource['uri']}"
                        self.resources[resource_id] = {
                            **resource,
                            "server": server_name,
                            "type": "mcp_resource"
                        }
            
            # List prompts
            if connection["capabilities"].get("prompts"):
                prompts_request = {
                    "jsonrpc": "2.0",
                    "id": str(uuid.uuid4()),
                    "method": "prompts/list",
                    "params": {}
                }
                
                await websocket.send(json.dumps(prompts_request))
                prompts_response = await websocket.recv()
                prompts_data = json.loads(prompts_response)
                
                if "result" in prompts_data:
                    for prompt in prompts_data["result"].get("prompts", []):
                        prompt_id = f"{server_name}::{prompt['name']}"
                        self.prompts[prompt_id] = {
                            **prompt,
                            "server": server_name,
                            "type": "mcp_prompt"
                        }
                        
        except Exception as e:
            self.logger.error(f"❌ Error loading capabilities from {server_name}: {e}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call an MCP tool"""
        try:
            # Find tool
            tool_id = None
            tool_info = None
            
            for tid, tinfo in self.tools.items():
                if tinfo["name"] == tool_name or tid == tool_name:
                    tool_id = tid
                    tool_info = tinfo
                    break
            
            if not tool_info:
                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' not found"
                }
            
            server_name = tool_info["server"]
            connection = self.connections[server_name]
            websocket = connection["websocket"]
            
            # Prepare tool call request
            tool_request = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/call",
                "params": {
                    "name": tool_info["name"],
                    "arguments": arguments or {}
                }
            }
            
            await websocket.send(json.dumps(tool_request))
            response = await websocket.recv()
            tool_response = json.loads(response)
            
            if "result" in tool_response:
                return {
                    "success": True,
                    "result": tool_response["result"],
                    "tool": tool_name,
                    "server": server_name,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                error = tool_response.get("error", {})
                return {
                    "success": False,
                    "error": error.get("message", "Unknown error"),
                    "code": error.get("code"),
                    "tool": tool_name,
                    "server": server_name
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error calling tool {tool_name}: {str(e)}"
            }
    
    async def read_resource(self, resource_uri: str) -> Dict[str, Any]:
        """Read an MCP resource"""
        try:
            # Find resource
            resource_id = None
            resource_info = None
            
            for rid, rinfo in self.resources.items():
                if rinfo["uri"] == resource_uri or rid == resource_uri:
                    resource_id = rid
                    resource_info = rinfo
                    break
            
            if not resource_info:
                return {
                    "success": False,
                    "error": f"Resource '{resource_uri}' not found"
                }
            
            server_name = resource_info["server"]
            connection = self.connections[server_name]
            websocket = connection["websocket"]
            
            # Prepare resource read request
            resource_request = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "resources/read",
                "params": {
                    "uri": resource_info["uri"]
                }
            }
            
            await websocket.send(json.dumps(resource_request))
            response = await websocket.recv()
            resource_response = json.loads(response)
            
            if "result" in resource_response:
                return {
                    "success": True,
                    "contents": resource_response["result"].get("contents", []),
                    "resource": resource_uri,
                    "server": server_name,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                error = resource_response.get("error", {})
                return {
                    "success": False,
                    "error": error.get("message", "Unknown error"),
                    "resource": resource_uri,
                    "server": server_name
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error reading resource {resource_uri}: {str(e)}"
            }
    
    async def get_prompt(self, prompt_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get an MCP prompt"""
        try:
            # Find prompt
            prompt_id = None
            prompt_info = None
            
            for pid, pinfo in self.prompts.items():
                if pinfo["name"] == prompt_name or pid == prompt_name:
                    prompt_id = pid
                    prompt_info = pinfo
                    break
            
            if not prompt_info:
                return {
                    "success": False,
                    "error": f"Prompt '{prompt_name}' not found"
                }
            
            server_name = prompt_info["server"]
            connection = self.connections[server_name]
            websocket = connection["websocket"]
            
            # Prepare prompt get request
            prompt_request = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "prompts/get",
                "params": {
                    "name": prompt_info["name"],
                    "arguments": arguments or {}
                }
            }
            
            await websocket.send(json.dumps(prompt_request))
            response = await websocket.recv()
            prompt_response = json.loads(response)
            
            if "result" in prompt_response:
                return {
                    "success": True,
                    "messages": prompt_response["result"].get("messages", []),
                    "prompt": prompt_name,
                    "server": server_name,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                error = prompt_response.get("error", {})
                return {
                    "success": False,
                    "error": error.get("message", "Unknown error"),
                    "prompt": prompt_name,
                    "server": server_name
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting prompt {prompt_name}: {str(e)}"
            }
    
    def list_available_tools(self) -> List[Dict[str, Any]]:
        """List all available MCP tools"""
        return list(self.tools.values())
    
    def list_available_resources(self) -> List[Dict[str, Any]]:
        """List all available MCP resources"""
        return list(self.resources.values())
    
    def list_available_prompts(self) -> List[Dict[str, Any]]:
        """List all available MCP prompts"""
        return list(self.prompts.values())
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get status of all MCP connections"""
        status = {}
        
        for server_name, connection in self.connections.items():
            try:
                websocket = connection["websocket"]
                is_connected = websocket.open
            except:
                is_connected = False
            
            status[server_name] = {
                "connected": is_connected,
                "url": connection["url"],
                "capabilities": connection["capabilities"],
                "server_info": connection["server_info"],
                "connected_at": connection["connected_at"],
                "tools_count": len([t for t in self.tools.values() if t["server"] == server_name]),
                "resources_count": len([r for r in self.resources.values() if r["server"] == server_name]),
                "prompts_count": len([p for p in self.prompts.values() if p["server"] == server_name])
            }
        
        return status
    
    async def disconnect_from_server(self, server_name: str) -> bool:
        """Disconnect from an MCP server"""
        try:
            if server_name in self.connections:
                connection = self.connections[server_name]
                await connection["websocket"].close()
                
                # Remove tools, resources, and prompts from this server
                self.tools = {k: v for k, v in self.tools.items() if v["server"] != server_name}
                self.resources = {k: v for k, v in self.resources.items() if v["server"] != server_name}
                self.prompts = {k: v for k, v in self.prompts.items() if v["server"] != server_name}
                
                del self.connections[server_name]
                
                self.logger.info(f"✅ Disconnected from MCP server: {server_name}")
                return True
            else:
                self.logger.warning(f"⚠️ Server {server_name} not connected")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error disconnecting from {server_name}: {e}")
            return False
    
    async def disconnect_all(self):
        """Disconnect from all MCP servers"""
        servers = list(self.connections.keys())
        for server_name in servers:
            await self.disconnect_from_server(server_name)

# Global MCP connector instance
mcp_connector = MCPConnector()

# Common MCP server configurations
COMMON_MCP_SERVERS = {
    "filesystem": {
        "url": "ws://localhost:8765",
        "description": "File system access via MCP"
    },
    "database": {
        "url": "ws://localhost:8766", 
        "description": "Database operations via MCP"
    },
    "browser": {
        "url": "ws://localhost:8767",
        "description": "Web browser automation via MCP"
    },
    "git": {
        "url": "ws://localhost:8768",
        "description": "Git operations via MCP"
    }
}

async def auto_connect_servers():
    """Auto-connect to common MCP servers"""
    for server_name, config in COMMON_MCP_SERVERS.items():
        try:
            success = await mcp_connector.connect_to_server(config["url"], server_name)
            if success:
                print(f"✅ Connected to MCP server: {server_name}")
            else:
                print(f"⚠️ Could not connect to MCP server: {server_name}")
        except Exception as e:
            print(f"❌ Error connecting to {server_name}: {e}")

# Initialize MCP connections on import
if __name__ == "__main__":
    asyncio.run(auto_connect_servers())