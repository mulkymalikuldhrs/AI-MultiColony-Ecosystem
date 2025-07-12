"""
🤖 Enhanced Agent Creator
Advanced AI agent for creating custom agents dynamically

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import asyncio
import json
import os
import re
import ast
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import importlib.util
import inspect

class EnhancedAgentCreator:
    """
    Enhanced Agent Creator
    
    Capabilities:
    - Dynamic agent creation from specifications
    - Custom agent template generation
    - Agent capability analysis and enhancement
    - Auto-registration of new agents
    - Agent testing and validation
    - Agent documentation generation
    """
    
    def __init__(self):
        self.agent_id = "enhanced_agent_creator"
        self.name = "Enhanced Agent Creator"
        self.version = "2.0.0"
        self.status = "active"
        self.capabilities = [
            "dynamic_agent_creation",
            "custom_template_generation",
            "capability_analysis",
            "auto_registration",
            "agent_testing",
            "documentation_generation",
            "code_optimization",
            "dependency_management"
        ]
        
        # Initialize logging
        self.logger = logging.getLogger("EnhancedAgentCreator")
        self.logger.setLevel(logging.INFO)
        
        # Directories
        self.base_dir = Path(__file__).parent.parent.parent
        self.agents_dir = self.base_dir / "colony" / "agents"
        self.templates_dir = self.base_dir / "data" / "agent_templates"
        self.created_agents_dir = self.base_dir / "data" / "created_agents"
        
        # Create directories
        for dir_path in [self.templates_dir, self.created_agents_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Agent templates
        self.agent_templates = {
            "basic": self._get_basic_template(),
            "advanced": self._get_advanced_template(),
            "autonomous": self._get_autonomous_template(),
            "specialized": self._get_specialized_template(),
            "interactive": self._get_interactive_template()
        }
        
        # Created agents registry
        self.created_agents = []
        self.agent_registry = {}
        
        self.logger.info(f"🤖 {self.name} v{self.version} initialized")
    
    async def create_agent(self, specification: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new agent from specification"""
        try:
            self.logger.info(f"🔨 Creating agent: {specification.get('name', 'Unknown')}")
            
            # Validate specification
            validation_result = await self._validate_specification(specification)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": f"Invalid specification: {validation_result['errors']}"
                }
            
            # Generate agent code
            agent_code = await self._generate_agent_code(specification)
            
            # Create agent file
            agent_file = await self._create_agent_file(specification, agent_code)
            
            # Test agent
            test_result = await self._test_agent(agent_file)
            if not test_result["success"]:
                return {
                    "success": False,
                    "error": f"Agent test failed: {test_result['error']}"
                }
            
            # Register agent
            registration_result = await self._register_agent(agent_file, specification)
            
            # Generate documentation
            await self._generate_agent_documentation(agent_file, specification)
            
            # Add to created agents registry
            agent_info = {
                "id": specification["id"],
                "name": specification["name"],
                "file": str(agent_file),
                "created_at": datetime.now().isoformat(),
                "specification": specification,
                "status": "active"
            }
            self.created_agents.append(agent_info)
            
            self.logger.info(f"✅ Successfully created agent: {specification['name']}")
            
            return {
                "success": True,
                "agent_id": specification["id"],
                "agent_file": str(agent_file),
                "registration": registration_result
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error creating agent: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _validate_specification(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Validate agent specification"""
        errors = []
        
        # Required fields
        required_fields = ["id", "name", "description", "capabilities"]
        for field in required_fields:
            if field not in spec:
                errors.append(f"Missing required field: {field}")
        
        # Validate ID format
        if "id" in spec:
            if not re.match(r'^[a-z_][a-z0-9_]*$', spec["id"]):
                errors.append("Agent ID must be lowercase with underscores only")
        
        # Validate capabilities
        if "capabilities" in spec and not isinstance(spec["capabilities"], list):
            errors.append("Capabilities must be a list")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    async def _generate_agent_code(self, spec: Dict[str, Any]) -> str:
        """Generate agent code from specification"""
        template_type = spec.get("template", "basic")
        template = self.agent_templates.get(template_type, self.agent_templates["basic"])
        
        # Replace placeholders
        agent_code = template.format(
            agent_id=spec["id"],
            agent_name=spec["name"],
            agent_description=spec["description"],
            agent_capabilities=json.dumps(spec["capabilities"], indent=8),
            agent_version=spec.get("version", "1.0.0"),
            custom_methods=self._generate_custom_methods(spec),
            custom_imports=self._generate_custom_imports(spec)
        )
        
        return agent_code
    
    def _generate_custom_methods(self, spec: Dict[str, Any]) -> str:
        """Generate custom methods based on capabilities"""
        methods = []
        
        for capability in spec.get("capabilities", []):
            method_name = f"execute_{capability}"
            method_code = f'''
    async def {method_name}(self, *args, **kwargs):
        """Execute {capability} capability"""
        self.logger.info(f"🔄 Executing {capability}...")
        
        try:
            # Custom implementation for {capability}
            result = await self._handle_{capability}(*args, **kwargs)
            
            self.logger.info(f"✅ {capability} completed successfully")
            return {{
                "success": True,
                "result": result,
                "capability": "{capability}"
            }}
            
        except Exception as e:
            self.logger.error(f"❌ Error in {capability}: {{e}}")
            return {{
                "success": False,
                "error": str(e),
                "capability": "{capability}"
            }}
    
    async def _handle_{capability}(self, *args, **kwargs):
        """Handle {capability} implementation"""
        # TODO: Implement {capability} logic
        return f"{capability} executed with args: {{args}}, kwargs: {{kwargs}}"
'''
            methods.append(method_code)
        
        return "\n".join(methods)
    
    def _generate_custom_imports(self, spec: Dict[str, Any]) -> str:
        """Generate custom imports based on requirements"""
        imports = []
        
        # Add imports based on capabilities
        capability_imports = {
            "web_scraping": "import requests\nfrom bs4 import BeautifulSoup",
            "data_analysis": "import pandas as pd\nimport numpy as np",
            "machine_learning": "import sklearn\nimport tensorflow as tf",
            "database": "import sqlite3\nimport sqlalchemy",
            "api_integration": "import requests\nimport aiohttp",
            "file_processing": "import csv\nimport openpyxl",
            "image_processing": "from PIL import Image\nimport cv2",
            "natural_language": "import nltk\nimport spacy"
        }
        
        for capability in spec.get("capabilities", []):
            if capability in capability_imports:
                imports.append(capability_imports[capability])
        
        return "\n".join(imports)
    
    async def _create_agent_file(self, spec: Dict[str, Any], agent_code: str) -> Path:
        """Create agent file"""
        agent_filename = f"{spec['id']}.py"
        agent_file = self.agents_dir / agent_filename
        
        # Write agent code to file
        with open(agent_file, 'w', encoding='utf-8') as f:
            f.write(agent_code)
        
        return agent_file
    
    async def _test_agent(self, agent_file: Path) -> Dict[str, Any]:
        """Test the created agent"""
        try:
            # Test syntax
            with open(agent_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            ast.parse(content)
            
            # Test import
            spec = importlib.util.spec_from_file_location("test_agent", agent_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Test agent instantiation
            if hasattr(module, 'register_agent'):
                agent_info = module.register_agent()
                return {
                    "success": True,
                    "agent_info": agent_info
                }
            
            return {
                "success": False,
                "error": "Agent does not have register_agent function"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _register_agent(self, agent_file: Path, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Register the agent with the system"""
        try:
            # Import the agent
            spec_obj = importlib.util.spec_from_file_location(spec["id"], agent_file)
            module = importlib.util.module_from_spec(spec_obj)
            spec_obj.loader.exec_module(module)
            
            # Get registration info
            if hasattr(module, 'register_agent'):
                agent_info = module.register_agent()
                
                # Add to registry
                self.agent_registry[spec["id"]] = {
                    "module": module,
                    "info": agent_info,
                    "file": str(agent_file)
                }
                
                return {
                    "success": True,
                    "agent_info": agent_info
                }
            
            return {
                "success": False,
                "error": "No register_agent function found"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _generate_agent_documentation(self, agent_file: Path, spec: Dict[str, Any]):
        """Generate documentation for the agent"""
        doc_content = f"""# {spec['name']} Documentation

## Overview
{spec['description']}

## Agent Information
- **ID**: {spec['id']}
- **Version**: {spec.get('version', '1.0.0')}
- **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **File**: {agent_file.name}

## Capabilities
{chr(10).join(f"- {cap}" for cap in spec.get('capabilities', []))}

## Usage
```python
from colony.agents.{spec['id']} import {spec['id']}_agent

# Initialize agent
agent = {spec['id']}_agent

# Get agent status
status = agent.get_status()

# Execute capabilities
for capability in agent.capabilities:
    result = await agent.execute_{{capability}}()
```

## API Endpoints
- GET `/api/agents/{spec['id']}/status` - Get agent status
- POST `/api/agents/{spec['id']}/execute` - Execute agent capability

## Configuration
```yaml
{spec['id']}:
  enabled: true
  auto_start: false
  capabilities: {spec.get('capabilities', [])}
```

---
*Generated automatically by Enhanced Agent Creator*
"""
        
        doc_file = self.created_agents_dir / f"{spec['id']}_documentation.md"
        with open(doc_file, 'w', encoding='utf-8') as f:
            f.write(doc_content)
    
    def _get_basic_template(self) -> str:
        """Get basic agent template"""
        return '''"""
{agent_description}

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
{custom_imports}

class {agent_name.replace(' ', '')}Agent:
    """
    {agent_name}
    
    {agent_description}
    """
    
    def __init__(self):
        self.agent_id = "{agent_id}"
        self.name = "{agent_name}"
        self.version = "{agent_version}"
        self.status = "active"
        self.capabilities = {agent_capabilities}
        
        # Initialize logging
        self.logger = logging.getLogger(self.name.replace(' ', ''))
        self.logger.setLevel(logging.INFO)
        
        self.logger.info(f"🤖 {{self.name}} v{{self.version}} initialized")
    
    async def execute(self, capability: str, *args, **kwargs) -> Dict[str, Any]:
        """Execute a specific capability"""
        if capability not in self.capabilities:
            return {{
                "success": False,
                "error": f"Capability '{{capability}}' not supported"
            }}
        
        method_name = f"execute_{{capability}}"
        if hasattr(self, method_name):
            return await getattr(self, method_name)(*args, **kwargs)
        
        return {{
            "success": False,
            "error": f"Method '{{method_name}}' not implemented"
        }}
    {custom_methods}
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {{
            "agent_id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "capabilities": self.capabilities,
            "last_updated": datetime.now().isoformat()
        }}

# Global instance
{agent_id}_agent = {agent_name.replace(' ', '')}Agent()

# Agent registration
def register_agent():
    """Register this agent with the system"""
    return {{
        "id": {agent_id}_agent.agent_id,
        "name": {agent_id}_agent.name,
        "version": {agent_id}_agent.version,
        "capabilities": {agent_id}_agent.capabilities,
        "status": "active",
        "route": f"/api/agents/{{{{agent_id}_agent.agent_id}}}}",
        "description": "{agent_description}"
    }}

if __name__ == "__main__":
    # Test the agent
    agent = {agent_id}_agent
    print(f"Agent {{agent.name}} is ready!")
    print(f"Capabilities: {{agent.capabilities}}")
'''
    
    def _get_advanced_template(self) -> str:
        """Get advanced agent template with more features"""
        return '''"""
{agent_description}

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
{custom_imports}

class {agent_name.replace(' ', '')}Agent:
    """
    {agent_name}
    
    {agent_description}
    """
    
    def __init__(self):
        self.agent_id = "{agent_id}"
        self.name = "{agent_name}"
        self.version = "{agent_version}"
        self.status = "active"
        self.capabilities = {agent_capabilities}
        
        # Initialize logging
        self.logger = logging.getLogger(self.name.replace(' ', ''))
        self.logger.setLevel(logging.INFO)
        
        # State management
        self.state = {{
            "initialized_at": datetime.now().isoformat(),
            "execution_count": 0,
            "last_execution": None,
            "errors": []
        }}
        
        # Configuration
        self.config = {{
            "auto_retry": True,
            "max_retries": 3,
            "timeout": 30,
            "log_level": "INFO"
        }}
        
        # Data storage
        self.data_dir = Path(__file__).parent.parent.parent / "data" / self.agent_id
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"🤖 {{self.name}} v{{self.version}} initialized")
    
    async def execute(self, capability: str, *args, **kwargs) -> Dict[str, Any]:
        """Execute a specific capability with error handling and retry logic"""
        if capability not in self.capabilities:
            return {{
                "success": False,
                "error": f"Capability '{{capability}}' not supported",
                "available_capabilities": self.capabilities
            }}
        
        self.state["execution_count"] += 1
        self.state["last_execution"] = datetime.now().isoformat()
        
        method_name = f"execute_{{capability}}"
        if not hasattr(self, method_name):
            return {{
                "success": False,
                "error": f"Method '{{method_name}}' not implemented"
            }}
        
        # Execute with retry logic
        for attempt in range(self.config["max_retries"]):
            try:
                result = await asyncio.wait_for(
                    getattr(self, method_name)(*args, **kwargs),
                    timeout=self.config["timeout"]
                )
                
                # Log successful execution
                await self._log_execution(capability, "success", result)
                return result
                
            except asyncio.TimeoutError:
                error_msg = f"Execution timeout for {{capability}} (attempt {{attempt + 1}})"
                self.logger.warning(error_msg)
                if attempt == self.config["max_retries"] - 1:
                    await self._log_execution(capability, "timeout", {{"error": error_msg}})
                    return {{
                        "success": False,
                        "error": error_msg
                    }}
                    
            except Exception as e:
                error_msg = f"Error in {{capability}}: {{str(e)}} (attempt {{attempt + 1}})"
                self.logger.error(error_msg)
                self.state["errors"].append({{
                    "capability": capability,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                    "attempt": attempt + 1
                }})
                
                if attempt == self.config["max_retries"] - 1:
                    await self._log_execution(capability, "error", {{"error": str(e)}})
                    return {{
                        "success": False,
                        "error": str(e),
                        "attempts": attempt + 1
                    }}
                
                # Wait before retry
                await asyncio.sleep(2 ** attempt)
        
        return {{
            "success": False,
            "error": "Max retries exceeded"
        }}
    
    async def _log_execution(self, capability: str, status: str, result: Dict[str, Any]):
        """Log execution details"""
        log_entry = {{
            "timestamp": datetime.now().isoformat(),
            "capability": capability,
            "status": status,
            "result": result,
            "execution_count": self.state["execution_count"]
        }}
        
        log_file = self.data_dir / f"execution_log_{{int(time.time())}}.json"
        with open(log_file, 'w') as f:
            json.dump(log_entry, f, indent=2)
    {custom_methods}
    
    async def configure(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update agent configuration"""
        try:
            self.config.update(config)
            self.logger.info(f"Configuration updated: {{config}}")
            return {{
                "success": True,
                "config": self.config
            }}
        except Exception as e:
            return {{
                "success": False,
                "error": str(e)
            }}
    
    async def reset_state(self) -> Dict[str, Any]:
        """Reset agent state"""
        try:
            self.state = {{
                "initialized_at": datetime.now().isoformat(),
                "execution_count": 0,
                "last_execution": None,
                "errors": []
            }}
            self.logger.info("Agent state reset")
            return {{
                "success": True,
                "state": self.state
            }}
        except Exception as e:
            return {{
                "success": False,
                "error": str(e)
            }}
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status"""
        return {{
            "agent_id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "capabilities": self.capabilities,
            "state": self.state,
            "config": self.config,
            "last_updated": datetime.now().isoformat()
        }}
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get execution history"""
        history = []
        for log_file in self.data_dir.glob("execution_log_*.json"):
            try:
                with open(log_file, 'r') as f:
                    log_entry = json.load(f)
                    history.append(log_entry)
            except Exception as e:
                self.logger.warning(f"Could not read log file {{log_file}}: {{e}}")
        
        return sorted(history, key=lambda x: x["timestamp"], reverse=True)

# Global instance
{agent_id}_agent = {agent_name.replace(' ', '')}Agent()

# Agent registration
def register_agent():
    """Register this agent with the system"""
    return {{
        "id": {agent_id}_agent.agent_id,
        "name": {agent_id}_agent.name,
        "version": {agent_id}_agent.version,
        "capabilities": {agent_id}_agent.capabilities,
        "status": "active",
        "route": f"/api/agents/{{{{agent_id}_agent.agent_id}}}}",
        "description": "{agent_description}",
        "features": ["error_handling", "retry_logic", "state_management", "logging"]
    }}

if __name__ == "__main__":
    # Test the agent
    agent = {agent_id}_agent
    print(f"Agent {{agent.name}} is ready!")
    print(f"Capabilities: {{agent.capabilities}}")
    print(f"Status: {{agent.get_status()}}")
'''
    
    def _get_autonomous_template(self) -> str:
        """Get autonomous agent template"""
        return self._get_advanced_template()  # For now, use advanced template
    
    def _get_specialized_template(self) -> str:
        """Get specialized agent template"""
        return self._get_advanced_template()  # For now, use advanced template
    
    def _get_interactive_template(self) -> str:
        """Get interactive agent template"""
        return self._get_advanced_template()  # For now, use advanced template
    
    async def list_created_agents(self) -> List[Dict[str, Any]]:
        """List all created agents"""
        return self.created_agents
    
    async def get_agent_templates(self) -> Dict[str, str]:
        """Get available agent templates"""
        return {
            "basic": "Simple agent with basic functionality",
            "advanced": "Advanced agent with error handling and state management",
            "autonomous": "Autonomous agent with self-management capabilities",
            "specialized": "Specialized agent for specific domain tasks",
            "interactive": "Interactive agent with user interface capabilities"
        }
    
    async def delete_agent(self, agent_id: str) -> Dict[str, Any]:
        """Delete a created agent"""
        try:
            # Find agent in registry
            agent_info = None
            for agent in self.created_agents:
                if agent["id"] == agent_id:
                    agent_info = agent
                    break
            
            if not agent_info:
                return {
                    "success": False,
                    "error": f"Agent {agent_id} not found"
                }
            
            # Remove agent file
            agent_file = Path(agent_info["file"])
            if agent_file.exists():
                agent_file.unlink()
            
            # Remove from registry
            self.created_agents = [a for a in self.created_agents if a["id"] != agent_id]
            if agent_id in self.agent_registry:
                del self.agent_registry[agent_id]
            
            self.logger.info(f"🗑️ Deleted agent: {agent_id}")
            
            return {
                "success": True,
                "message": f"Agent {agent_id} deleted successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent creator status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "capabilities": self.capabilities,
            "created_agents_count": len(self.created_agents),
            "available_templates": list(self.agent_templates.keys()),
            "last_updated": datetime.now().isoformat()
        }

# Global instance
enhanced_agent_creator = EnhancedAgentCreator()

# Agent registration
def register_agent():
    """Register this agent with the system"""
    return {
        "id": enhanced_agent_creator.agent_id,
        "name": enhanced_agent_creator.name,
        "version": enhanced_agent_creator.version,
        "capabilities": enhanced_agent_creator.capabilities,
        "status": "active",
        "route": f"/api/agents/{enhanced_agent_creator.agent_id}",
        "description": "Advanced AI agent for creating custom agents dynamically"
    }

if __name__ == "__main__":
    # Test agent creation
    test_spec = {
        "id": "test_agent",
        "name": "Test Agent",
        "description": "A test agent for demonstration",
        "capabilities": ["data_processing", "file_handling"],
        "template": "advanced"
    }
    
    creator = enhanced_agent_creator
    result = asyncio.run(creator.create_agent(test_spec))
    print(f"Agent creation result: {result}")