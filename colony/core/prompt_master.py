"""
🧠 Prompt Master Agent - Central AI Intelligence Hub
Advanced prompt processing and AI coordination system

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import re

# Import our LLM client
try:
    from .llm_client import llm_client, LLMResponse
except ImportError:
    # Fallback if module can't be imported
    llm_client = None
    LLMResponse = None

class PromptMasterAgent:
    """
    Prompt Master Agent: Central AI intelligence coordinator
    
    Capabilities:
    - 🧠 Multi-provider LLM integration
    - 🎯 Intelligent task routing
    - 🤖 Agent selection and coordination
    - 📊 Performance monitoring
    - 🔄 Automatic fallback handling
    - 💬 Conversation management
    - 🎨 Prompt optimization
    """
    
    def __init__(self):
        self.agent_id = "prompt_master"
        self.name = "Prompt Master Agent"
        self.status = "initializing"
        self.version = "2.0.0"
        self.start_time = None
        
        # Core capabilities
        self.capabilities = [
            "prompt_processing",
            "task_routing",
            "agent_coordination",
            "llm_integration",
            "conversation_management",
            "performance_monitoring"
        ]
        
        # Performance tracking
        self.processed_prompts = 0
        self.successful_prompts = 0
        self.failed_prompts = 0
        self.total_response_time = 0
        
        # Conversation tracking
        self.active_conversations = {}
        self.conversation_history = []
        
        # Task routing patterns
        self.task_patterns = {
            r"create.*web.*app|build.*website|make.*landing.*page": "fullstack_dev",
            r"design.*ui|create.*component|ui.*design": "ui_designer",
            r"write.*code|program|coding|script": "dev_engine",
            r"deploy|deployment|hosting|server": "deploy_manager",
            r"database|data.*sync|backup": "data_sync",
            r"test|debug|bug|error": "bug_hunter",
            r"security|auth|login|password": "authentication",
            r"marketing|promote|seo|content": "marketing",
            r"shell|terminal|command|execute": "cybershell",
            r"agent|bot|ai.*assistant": "agent_maker"
        }
        
        # Initialize logging
        self.setup_logging()
        
        # Initialize if LLM client is available
        if llm_client:
            self.llm_available = True
            self.logger.info("LLM client available")
        else:
            self.llm_available = False
            self.logger.warning("LLM client not available - running in offline mode")
        
        self.status = "ready"
        self.logger.info("Prompt Master Agent initialized successfully")
    
    def setup_logging(self):
        """Setup logging for Prompt Master"""
        log_dir = Path("data/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "prompt_master.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("PromptMaster")
    
    async def process_prompt(
        self, 
        prompt: str, 
        input_type: str = "text", 
        metadata: Dict = None,
        conversation_id: str = None
    ) -> Dict[str, Any]:
        """
        Process prompt using AI with intelligent routing
        """
        start_time = time.time()
        self.processed_prompts += 1
        
        if not prompt or not prompt.strip():
            return self._create_error_response("Empty prompt provided")
        
        metadata = metadata or {}
        conversation_id = conversation_id or f"conv_{int(time.time())}"
        
        try:
            self.logger.info(f"Processing prompt: {prompt[:50]}...")
            
            # Analyze prompt intent
            analysis = await self._analyze_prompt_intent(prompt)
            
            # Select best agent for the task
            selected_agent = self._select_best_agent(prompt, analysis)
            
            # Process with AI if available
            if self.llm_available and llm_client:
                ai_response = await self._process_with_ai(prompt, metadata, analysis)
                
                if ai_response.success:
                    # Create comprehensive response
                    response = {
                        "success": True,
                        "response": ai_response.content,
                        "agent": self.agent_id,
                        "ai_provider": ai_response.provider,
                        "ai_model": ai_response.model,
                        "selected_agent": selected_agent,
                        "intent_analysis": analysis,
                        "conversation_id": conversation_id,
                        "response_time": time.time() - start_time,
                        "timestamp": datetime.now().isoformat(),
                        "usage": ai_response.usage
                    }
                    
                    # Store conversation
                    self._store_conversation(conversation_id, prompt, response)
                    
                    self.successful_prompts += 1
                    self.total_response_time += response["response_time"]
                    
                    return response
                else:
                    self.logger.error(f"AI processing failed: {ai_response.error}")
                    return self._create_fallback_response(prompt, selected_agent, ai_response.error)
            else:
                # Fallback mode without AI
                return self._create_fallback_response(prompt, selected_agent, "AI not available")
                
        except Exception as e:
            self.logger.error(f"Prompt processing error: {e}")
            self.failed_prompts += 1
            return self._create_error_response(str(e))
    
    async def _analyze_prompt_intent(self, prompt: str) -> Dict[str, Any]:
        """Analyze prompt to understand user intent"""
        analysis = {
            "length": len(prompt),
            "word_count": len(prompt.split()),
            "complexity": "simple",
            "intent": "general",
            "requires_coding": False,
            "requires_deployment": False,
            "urgency": "normal"
        }
        
        prompt_lower = prompt.lower()
        
        # Detect complexity
        if analysis["word_count"] > 50:
            analysis["complexity"] = "complex"
        elif analysis["word_count"] > 20:
            analysis["complexity"] = "medium"
        
        # Detect coding requirements
        coding_keywords = ["code", "program", "script", "function", "class", "algorithm", "api"]
        if any(keyword in prompt_lower for keyword in coding_keywords):
            analysis["requires_coding"] = True
        
        # Detect deployment requirements
        deploy_keywords = ["deploy", "hosting", "server", "production", "cloud", "docker"]
        if any(keyword in prompt_lower for keyword in deploy_keywords):
            analysis["requires_deployment"] = True
        
        # Detect urgency
        urgent_keywords = ["urgent", "asap", "quickly", "fast", "immediate", "now"]
        if any(keyword in prompt_lower for keyword in urgent_keywords):
            analysis["urgency"] = "high"
        
        # Detect intent based on patterns
        for pattern, intent in self.task_patterns.items():
            if re.search(pattern, prompt_lower):
                analysis["intent"] = intent
                break
        
        return analysis
    
    def _select_best_agent(self, prompt: str, analysis: Dict[str, Any]) -> str:
        """Select the best agent for the task"""
        
        # Use intent analysis first
        if analysis.get("intent") != "general":
            return analysis["intent"]
        
        # Pattern-based selection
        prompt_lower = prompt.lower()
        
        for pattern, agent_id in self.task_patterns.items():
            if re.search(pattern, prompt_lower):
                return agent_id
        
        # Default selections based on keywords
        if analysis.get("requires_coding"):
            return "dev_engine"
        elif analysis.get("requires_deployment"):
            return "deploy_manager"
        else:
            return "agent_maker"  # Default fallback
    
    async def _process_with_ai(
        self, 
        prompt: str, 
        metadata: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> LLMResponse:
        """Process prompt using AI providers"""
        
        # Enhance prompt with context
        enhanced_prompt = self._enhance_prompt(prompt, analysis, metadata)
        
        # Create messages for chat completion
        messages = [
            {
                "role": "system",
                "content": self._get_system_prompt(analysis)
            },
            {
                "role": "user", 
                "content": enhanced_prompt
            }
        ]
        
        # Get AI response
        response = await llm_client.chat_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )
        
        return response
    
    def _enhance_prompt(
        self, 
        prompt: str, 
        analysis: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> str:
        """Enhance prompt with context and instructions"""
        
        enhanced = f"""Task Analysis:
- Intent: {analysis.get('intent', 'general')}
- Complexity: {analysis.get('complexity', 'simple')}
- Requires coding: {analysis.get('requires_coding', False)}
- Urgency: {analysis.get('urgency', 'normal')}

User Request:
{prompt}

Please provide a comprehensive response that:
1. Addresses the user's request directly
2. Includes specific actionable steps if applicable
3. Suggests relevant tools or technologies
4. Provides code examples if coding is involved
5. Is clear and well-structured

Respond professionally and helpfully."""
        
        return enhanced
    
    def _get_system_prompt(self, analysis: Dict[str, Any]) -> str:
        """Get system prompt based on analysis"""
        
        base_prompt = """You are an intelligent AI assistant integrated into the Agentic AI System, a sophisticated multi-agent platform created by Mulky Malikul Dhaher in Indonesia 🇮🇩.

You have access to specialized agents for:
- 🚀 Full-stack development (React, FastAPI, databases)
- 🎨 UI/UX design (Tailwind, modern components)
- ⚙️ DevOps and deployment (Docker, cloud platforms)
- 🔄 Data synchronization and management
- 🤖 AI agent creation and coordination
- 🛡️ Security and authentication
- 📈 Marketing and content creation

Your role is to provide intelligent, actionable responses that leverage the system's capabilities."""
        
        # Add specific context based on intent
        intent = analysis.get("intent", "general")
        
        if intent == "fullstack_dev":
            base_prompt += "\n\nFocus on: Full-stack web application development, modern frameworks, and best practices."
        elif intent == "ui_designer":
            base_prompt += "\n\nFocus on: UI/UX design, React components, Tailwind CSS, and modern design patterns."
        elif intent == "dev_engine":
            base_prompt += "\n\nFocus on: Code generation, project setup, and development automation."
        elif intent == "cybershell":
            base_prompt += "\n\nFocus on: System administration, shell commands, and automation scripts."
        
        return base_prompt
    
    def _create_fallback_response(
        self, 
        prompt: str, 
        selected_agent: str, 
        error: str = None
    ) -> Dict[str, Any]:
        """Create fallback response when AI is not available"""
        
        response_content = f"""I understand you want: {prompt[:100]}...

I've analyzed your request and selected the '{selected_agent}' agent as the best fit for this task.

However, I'm currently running in offline mode. Here's what I can suggest:

1. **Task Type**: Based on your request, this appears to be a {selected_agent.replace('_', ' ')} task
2. **Next Steps**: The system would normally route this to the {selected_agent} agent
3. **Manual Action**: You may need to specify the agent directly or try again when AI services are available

Selected Agent: {selected_agent}
"""
        
        if error:
            response_content += f"\nError Details: {error}"
        
        self.failed_prompts += 1
        
        return {
            "success": False,
            "response": response_content,
            "agent": self.agent_id,
            "selected_agent": selected_agent,
            "mode": "fallback",
            "error": error or "AI service unavailable",
            "timestamp": datetime.now().isoformat()
        }
    
    def _create_error_response(self, error: str) -> Dict[str, Any]:
        """Create error response"""
        self.failed_prompts += 1
        
        return {
            "success": False,
            "error": error,
            "agent": self.agent_id,
            "timestamp": datetime.now().isoformat()
        }
    
    def _store_conversation(
        self, 
        conversation_id: str, 
        prompt: str, 
        response: Dict[str, Any]
    ):
        """Store conversation for history"""
        conversation_entry = {
            "conversation_id": conversation_id,
            "prompt": prompt,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to active conversations
        if conversation_id not in self.active_conversations:
            self.active_conversations[conversation_id] = []
        
        self.active_conversations[conversation_id].append(conversation_entry)
        
        # Add to history
        self.conversation_history.append(conversation_entry)
        
        # Limit history size
        if len(self.conversation_history) > 1000:
            self.conversation_history = self.conversation_history[-500:]
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        avg_response_time = (
            self.total_response_time / max(self.successful_prompts, 1)
            if self.successful_prompts > 0 else 0
        )
        
        success_rate = (
            (self.successful_prompts / max(self.processed_prompts, 1)) * 100
            if self.processed_prompts > 0 else 0
        )
        
        status = {
            "agent_id": self.agent_id,
            "status": self.status,
            "version": self.version,
            "llm_available": self.llm_available,
            "uptime": self._get_uptime(),
            "performance": {
                "processed_prompts": self.processed_prompts,
                "successful_prompts": self.successful_prompts,
                "failed_prompts": self.failed_prompts,
                "success_rate": round(success_rate, 2),
                "avg_response_time": round(avg_response_time, 2)
            },
            "conversations": {
                "active_conversations": len(self.active_conversations),
                "total_history": len(self.conversation_history)
            }
        }
        
        # Add LLM stats if available
        if self.llm_available and llm_client:
            try:
                status["llm_stats"] = llm_client.get_provider_stats()
            except:
                pass
        
        return status
    
    def _get_uptime(self) -> str:
        """Get uptime string"""
        if not self.start_time:
            return "0h 0m"
        
        uptime_seconds = (datetime.now() - datetime.fromtimestamp(self.start_time)).total_seconds()
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        return f"{hours}h {minutes}m"
    
    async def test_llm_connection(self) -> Dict[str, Any]:
        """Test LLM connection"""
        if not self.llm_available:
            return {"success": False, "error": "LLM client not available"}
        
        try:
            test_prompt = "Hello! Please respond with 'Connection test successful' to confirm you're working."
            response = await llm_client.simple_prompt(test_prompt)
            
            return {
                "success": True,
                "response": response,
                "provider": llm_client.current_provider,
                "available_models": llm_client.get_available_models()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

class SimplePromptMaster(PromptMasterAgent):
    """Backward compatibility class"""
    pass

# Global instance
prompt_master = PromptMasterAgent()

# Export for use by other modules
__all__ = ['PromptMasterAgent', 'prompt_master', 'SimplePromptMaster']
