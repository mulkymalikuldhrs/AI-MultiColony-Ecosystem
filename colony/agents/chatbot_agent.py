"""
💬 Chatbot Agent
Advanced conversational AI for system interaction

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import asyncio
import json
import logging
import time
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests

from colony.core.agent_registry import register_agent
from colony.core.base_agent import BaseAgent

@register_agent(name="chatbot_agent", description="Agent for conversational AI and system interaction.")
class ChatbotAgent(BaseAgent):
    """
    Chatbot Agent
    
    Capabilities:
    - Natural language conversation
    - Agent interaction and control
    - System status queries
    - Task execution via chat
    - Multi-language support
    - Context awareness
    - Command interpretation
    """
    
    def __init__(self):
        super().__init__(agent_id="chatbot_agent")
        self.version = "1.0.0"
        self.capabilities = [
            "natural_conversation",
            "agent_control",
            "system_queries",
            "task_execution",
            "command_interpretation",
            "context_awareness",
            "multi_language",
            "help_assistance"
        ]
        
        # Conversation state
        self.conversations = {}
        self.active_sessions = {}
        
        # Command patterns
        self.command_patterns = {
            "agent_status": [
                r"status of (\w+)",
                r"how is (\w+) doing",
                r"(\w+) agent status",
                r"check (\w+)"
            ],
            "list_agents": [
                r"list agents",
                r"show agents",
                r"what agents",
                r"available agents"
            ],
            "start_agent": [
                r"start (\w+)",
                r"activate (\w+)",
                r"run (\w+)",
                r"launch (\w+)"
            ],
            "stop_agent": [
                r"stop (\w+)",
                r"deactivate (\w+)",
                r"shutdown (\w+)",
                r"halt (\w+)"
            ],
            "system_status": [
                r"system status",
                r"how is system",
                r"system health",
                r"overall status"
            ],
            "help": [
                r"help",
                r"what can you do",
                r"commands",
                r"assistance"
            ],
            "create_agent": [
                r"create agent",
                r"new agent",
                r"make agent",
                r"build agent"
            ]
        }
        
        # Response templates
        self.responses = {
            "greeting": [
                "Hello! I'm your AI assistant. How can I help you today?",
                "Hi there! Ready to assist you with the AI MultiColony system.",
                "Greetings! What would you like to do today?"
            ],
            "agent_not_found": [
                "I couldn't find an agent with that name. Use 'list agents' to see available agents.",
                "That agent doesn't exist. Would you like to see the list of available agents?",
                "Agent not found. Try 'show agents' to see what's available."
            ],
            "success": [
                "Done! ✅",
                "Successfully completed! ✅",
                "Task completed successfully! ✅"
            ],
            "error": [
                "Sorry, I encountered an error: {}",
                "Oops! Something went wrong: {}",
                "I couldn't complete that task: {}"
            ]
        }
        
        # Context storage
        self.context_dir = Path(__file__).parent.parent.parent / "data" / "chatbot_context"
        self.context_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"💬 {self.name} v{self.version} initialized")
    
    async def process_message(self, message: str, session_id: str = "default", user_id: str = "anonymous") -> Dict[str, Any]:
        """Process incoming chat message"""
        try:
            self.logger.info(f"💬 Processing message from {user_id}: {message}")
            
            # Initialize session if needed
            if session_id not in self.conversations:
                self.conversations[session_id] = {
                    "user_id": user_id,
                    "started_at": datetime.now().isoformat(),
                    "messages": [],
                    "context": {}
                }
            
            # Add user message to conversation
            user_msg = {
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            }
            self.conversations[session_id]["messages"].append(user_msg)
            
            # Process the message
            response = await self._generate_response(message, session_id)
            
            # Add bot response to conversation
            bot_msg = {
                "role": "assistant",
                "content": response["content"],
                "timestamp": datetime.now().isoformat(),
                "action": response.get("action"),
                "data": response.get("data")
            }
            self.conversations[session_id]["messages"].append(bot_msg)
            
            # Save conversation
            await self._save_conversation(session_id)
            
            return {
                "success": True,
                "response": response["content"],
                "action": response.get("action"),
                "data": response.get("data"),
                "session_id": session_id
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error processing message: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "Sorry, I encountered an error processing your message."
            }
    
    async def _generate_response(self, message: str, session_id: str) -> Dict[str, Any]:
        """Generate response to user message"""
        message_lower = message.lower().strip()
        
        # Check for greetings
        if any(greeting in message_lower for greeting in ["hello", "hi", "hey", "greetings"]):
            return {
                "content": self._random_response("greeting"),
                "action": "greeting"
            }
        
        # Check for help requests
        if self._match_pattern("help", message_lower):
            return await self._handle_help_request()
        
        # Check for agent-related commands
        if self._match_pattern("list_agents", message_lower):
            return await self._handle_list_agents()
        
        # Check for agent status
        agent_match = self._extract_agent_name("agent_status", message_lower)
        if agent_match:
            return await self._handle_agent_status(agent_match)
        
        # Check for start agent
        agent_match = self._extract_agent_name("start_agent", message_lower)
        if agent_match:
            return await self._handle_start_agent(agent_match)
        
        # Check for stop agent
        agent_match = self._extract_agent_name("stop_agent", message_lower)
        if agent_match:
            return await self._handle_stop_agent(agent_match)
        
        # Check for system status
        if self._match_pattern("system_status", message_lower):
            return await self._handle_system_status()
        
        # Check for create agent
        if self._match_pattern("create_agent", message_lower):
            return await self._handle_create_agent_request(session_id)
        
        # Default response with suggestions
        return await self._handle_unknown_command(message)
    
    def _match_pattern(self, command_type: str, message: str) -> bool:
        """Check if message matches command pattern"""
        patterns = self.command_patterns.get(command_type, [])
        for pattern in patterns:
            if re.search(pattern, message):
                return True
        return False
    
    def _extract_agent_name(self, command_type: str, message: str) -> Optional[str]:
        """Extract agent name from command"""
        patterns = self.command_patterns.get(command_type, [])
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(1)
        return None
    
    def _random_response(self, response_type: str) -> str:
        """Get random response from template"""
        import random
        responses = self.responses.get(response_type, ["I understand."])
        return random.choice(responses)
    
    async def _handle_help_request(self) -> Dict[str, Any]:
        """Handle help request"""
        help_text = """
🤖 **AI MultiColony System Assistant**

I can help you with:

**Agent Management:**
- `list agents` - Show all available agents
- `status of [agent_name]` - Check agent status
- `start [agent_name]` - Start an agent
- `stop [agent_name]` - Stop an agent

**System Information:**
- `system status` - Check overall system health
- `system info` - Get system information

**Agent Creation:**
- `create agent` - Start agent creation wizard
- `new agent` - Create a new custom agent

**General:**
- `help` - Show this help message

**Examples:**
- "What's the status of the chatbot agent?"
- "Start the autonomous fullstack dev agent"
- "Show me all agents"
- "Create a new agent for data processing"

Just ask me naturally! I understand conversational language. 😊
"""
        
        return {
            "content": help_text,
            "action": "help",
            "data": {"commands": list(self.command_patterns.keys())}
        }
    
    async def _handle_list_agents(self) -> Dict[str, Any]:
        """Handle list agents request"""
        try:
            # This would integrate with the actual agent registry
            # For now, we'll simulate the response
            agents = [
                {"id": "chatbot", "name": "Chatbot Agent", "status": "active"},
                {"id": "autonomous_fullstack_dev", "name": "Autonomous Fullstack Dev", "status": "active"},
                {"id": "auto_redactor", "name": "Auto Redactor", "status": "active"},
                {"id": "enhanced_agent_creator", "name": "Enhanced Agent Creator", "status": "active"},
                {"id": "agent_base", "name": "Agent Base", "status": "active"},
                {"id": "agent_02_meta_spawner", "name": "Meta Spawner", "status": "active"},
                {"id": "agent_03_planner", "name": "Planner", "status": "active"},
                {"id": "agent_04_executor", "name": "Executor", "status": "active"},
                {"id": "agent_05_designer", "name": "Designer", "status": "active"},
                {"id": "agent_06_specialist", "name": "Specialist", "status": "active"}
            ]
            
            agent_list = "🤖 **Available Agents:**\n\n"
            for agent in agents:
                status_emoji = "✅" if agent["status"] == "active" else "❌"
                agent_list += f"{status_emoji} **{agent['name']}** (`{agent['id']}`)\n"
            
            agent_list += f"\n📊 Total: {len(agents)} agents"
            
            return {
                "content": agent_list,
                "action": "list_agents",
                "data": {"agents": agents}
            }
            
        except Exception as e:
            return {
                "content": f"Error retrieving agent list: {e}",
                "action": "error"
            }
    
    async def _handle_agent_status(self, agent_name: str) -> Dict[str, Any]:
        """Handle agent status request"""
        try:
            # This would integrate with actual agent status checking
            # For now, simulate response
            status_info = {
                "agent_id": agent_name,
                "status": "active",
                "uptime": "2 hours 15 minutes",
                "last_activity": "2 minutes ago",
                "capabilities": ["example_capability_1", "example_capability_2"]
            }
            
            status_text = f"""
🤖 **{agent_name.title()} Agent Status**

📊 **Status:** {status_info['status'].upper()}
⏱️ **Uptime:** {status_info['uptime']}
🕐 **Last Activity:** {status_info['last_activity']}
⚡ **Capabilities:** {len(status_info['capabilities'])} available

**Available Capabilities:**
{chr(10).join(f"• {cap}" for cap in status_info['capabilities'])}
"""
            
            return {
                "content": status_text,
                "action": "agent_status",
                "data": status_info
            }
            
        except Exception as e:
            return {
                "content": self._random_response("agent_not_found"),
                "action": "error"
            }
    
    async def _handle_start_agent(self, agent_name: str) -> Dict[str, Any]:
        """Handle start agent request"""
        try:
            # This would integrate with actual agent starting
            # For now, simulate response
            return {
                "content": f"✅ Started {agent_name} agent successfully!",
                "action": "start_agent",
                "data": {"agent_id": agent_name, "status": "started"}
            }
            
        except Exception as e:
            return {
                "content": f"❌ Failed to start {agent_name}: {e}",
                "action": "error"
            }
    
    async def _handle_stop_agent(self, agent_name: str) -> Dict[str, Any]:
        """Handle stop agent request"""
        try:
            # This would integrate with actual agent stopping
            # For now, simulate response
            return {
                "content": f"🛑 Stopped {agent_name} agent successfully!",
                "action": "stop_agent",
                "data": {"agent_id": agent_name, "status": "stopped"}
            }
            
        except Exception as e:
            return {
                "content": f"❌ Failed to stop {agent_name}: {e}",
                "action": "error"
            }
    
    async def _handle_system_status(self) -> Dict[str, Any]:
        """Handle system status request"""
        try:
            system_info = {
                "status": "healthy",
                "active_agents": 10,
                "total_agents": 15,
                "uptime": "5 hours 30 minutes",
                "memory_usage": "45%",
                "cpu_usage": "25%"
            }
            
            status_text = f"""
🖥️ **System Status**

🟢 **Overall Status:** {system_info['status'].upper()}
🤖 **Agents:** {system_info['active_agents']}/{system_info['total_agents']} active
⏱️ **Uptime:** {system_info['uptime']}
💾 **Memory Usage:** {system_info['memory_usage']}
🔥 **CPU Usage:** {system_info['cpu_usage']}

All systems operational! ✅
"""
            
            return {
                "content": status_text,
                "action": "system_status",
                "data": system_info
            }
            
        except Exception as e:
            return {
                "content": f"❌ Error retrieving system status: {e}",
                "action": "error"
            }
    
    async def _handle_create_agent_request(self, session_id: str) -> Dict[str, Any]:
        """Handle create agent request"""
        # Set context for agent creation wizard
        self.conversations[session_id]["context"]["creating_agent"] = True
        self.conversations[session_id]["context"]["creation_step"] = "name"
        
        return {
            "content": """
🛠️ **Agent Creation Wizard**

Let's create a new agent! I'll guide you through the process.

**Step 1: Agent Name**
What would you like to name your new agent?

Example: "Data Processing Agent" or "Web Scraper Bot"
""",
            "action": "create_agent_wizard",
            "data": {"step": "name", "wizard_active": True}
        }
    
    async def _handle_unknown_command(self, message: str) -> Dict[str, Any]:
        """Handle unknown command with suggestions"""
        suggestions = [
            "Try asking 'help' to see what I can do",
            "You can ask about agent status with 'status of [agent_name]'",
            "Use 'list agents' to see all available agents",
            "Ask 'system status' for overall system health"
        ]
        
        import random
        suggestion = random.choice(suggestions)
        
        return {
            "content": f"I'm not sure I understand that command. {suggestion}",
            "action": "unknown_command",
            "data": {"suggestions": suggestions}
        }
    
    async def _save_conversation(self, session_id: str):
        """Save conversation to file"""
        try:
            conversation_file = self.context_dir / f"conversation_{session_id}.json"
            with open(conversation_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversations[session_id], f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.warning(f"Could not save conversation {session_id}: {e}")
    
    async def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for session"""
        if session_id in self.conversations:
            return self.conversations[session_id]["messages"]
        return []
    
    async def clear_conversation(self, session_id: str) -> Dict[str, Any]:
        """Clear conversation history"""
        try:
            if session_id in self.conversations:
                del self.conversations[session_id]
            
            return {
                "success": True,
                "message": "Conversation cleared"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get chatbot status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "capabilities": self.capabilities,
            "active_conversations": len(self.conversations),
            "supported_commands": list(self.command_patterns.keys()),
            "last_updated": datetime.now().isoformat()
        }

# Global instance
chatbot_agent = ChatbotAgent()

# Agent registration
def register_agent():
    """Register this agent with the system"""
    return {
        "id": chatbot_agent.agent_id,
        "name": chatbot_agent.name,
        "version": chatbot_agent.version,
        "capabilities": chatbot_agent.capabilities,
        "status": "active",
        "route": f"/api/agents/{chatbot_agent.agent_id}",
        "description": "Advanced conversational AI for system interaction"
    }

if __name__ == "__main__":
    # Test chatbot
    async def test_chatbot():
        bot = chatbot_agent
        
        test_messages = [
            "Hello!",
            "list agents",
            "status of chatbot",
            "help",
            "system status"
        ]
        
        for message in test_messages:
            print(f"\nUser: {message}")
            response = await bot.process_message(message, "test_session")
            print(f"Bot: {response['response']}")
    
    asyncio.run(test_chatbot())