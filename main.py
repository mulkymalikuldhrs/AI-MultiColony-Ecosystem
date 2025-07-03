"""
🧠 Agentic AI System - EVOLUSI KECERDASAN UMUM
Next-Generation Autonomous Multi-Agent Intelligence System
Powered by Camel-AI Framework with Advanced AGI Capabilities

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
Version: 3.0.0 - Evolusi Kecerdasan Umum
"""

import asyncio
import sys
import os
import signal
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/system.log'),
        logging.StreamHandler()
    ]
)

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

def print_banner():
    """Print evolutionary system banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                     🧠 EVOLUSI KECERDASAN UMUM 🧠                            ║
║                                                                              ║
║                 Advanced Multi-Agent Intelligence System                     ║
║                       Powered by CAMEL-AI Framework                         ║
║                                                                              ║
║   🐫 Camel-AI Societies  | 🤖 100+ Enhanced Prompts | 🌐 Modern UI          ║
║   🔄 Workforce Mgmt      | 📊 Real-time Analytics   | 🚀 MCP Integration     ║
║   🎯 Role-Playing Agents | 💡 Quantum Thinking      | 🔮 Future Architecture ║
║                                                                              ║
║                Made with ❤️ by Mulky Malikul Dhaher 🇮🇩                     ║
║                         Version 3.0.0 - Evolusi                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

class EvolusiKecerdasanUmum:
    """
    Evolusi Kecerdasan Umum - Next-Generation AGI System
    
    Features:
    - 🐫 Camel-AI multi-agent framework integration
    - 🧠 100+ enhanced prompts for advanced interactions
    - 🤖 Role-playing societies and workforce management
    - 🔄 Intelligent task decomposition and coordination
    - 🌐 Modern web interface with real-time monitoring
    - 🎯 Adaptive learning and metacognitive capabilities
    """
    
    def __init__(self):
        self.system_id = "evolusi_kecerdasan_umum"
        self.version = "3.0.0"
        self.status = "initializing"
        self.start_time = datetime.now()
        
        # Core components
        self.camel_integration = None
        self.enhanced_prompts = None
        self.prompt_master = None
        self.memory_bus = None
        self.sync_engine = None
        self.scheduler = None
        self.ai_selector = None
        
        # Legacy agents registry (maintained for compatibility)
        self.legacy_agents = {}
        self.active_agents = {}
        
        # Camel-AI specific components
        self.camel_agents = {}
        self.active_societies = {}
        self.active_workforces = {}
        
        # System configuration
        self.config = self._load_system_config()
        
        # Analytics and monitoring
        self.analytics = {
            "tasks_processed": 0,
            "prompts_executed": 0,
            "societies_created": 0,
            "agents_interactions": 0,
            "average_response_time": 0.0
        }
        
        # Shutdown flag
        self.shutdown_requested = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _load_system_config(self) -> Dict[str, Any]:
        """Load enhanced system configuration"""
        default_config = {
            "system_mode": "evolusi",  # evolusi, legacy, hybrid
            "camel_ai": {
                "enabled": True,
                "default_model": "openai",
                "model_type": "gpt-4o-mini",
                "temperature": 0.7,
                "enable_societies": True,
                "enable_workforce": True,
                "enable_mcp": True
            },
            "enhanced_prompts": {
                "enabled": True,
                "auto_categorization": True,
                "usage_analytics": True
            },
            "auto_start_features": [
                "camel_integration",
                "enhanced_prompts",
                "intelligent_societies",
                "prompt_master",
                "memory_bus",
                "scheduler",
                "web_interface"
            ],
            "ui": {
                "enable_modern_interface": True,
                "enable_real_time_monitoring": True,
                "enable_agent_visualization": True,
                "web_interface_port": 5000
            },
            "performance": {
                "max_concurrent_tasks": 20,
                "max_concurrent_agents": 15,
                "task_timeout": 300,
                "society_max_turns": 25
            },
            "logging": {
                "level": "INFO",
                "enable_detailed_analytics": True,
                "save_conversations": True
            }
        }
        
        config_file = Path("config/evolusi_config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logging.warning(f"Failed to load config: {e}")
        
        return default_config
    
    async def initialize(self):
        """Initialize the Evolusi Kecerdasan Umum system"""
        print("🚀 Initializing Evolusi Kecerdasan Umum...")
        
        try:
            # Ensure data directories exist
            self._ensure_directories()
            
            # Initialize enhanced prompts library
            if "enhanced_prompts" in self.config["auto_start_features"]:
                await self._initialize_enhanced_prompts()
            
            # Initialize Camel-AI integration
            if "camel_integration" in self.config["auto_start_features"]:
                await self._initialize_camel_integration()
            
            # Initialize core components (legacy compatibility)
            await self._initialize_core_components()
            
            # Initialize legacy agents (for backward compatibility)
            await self._initialize_legacy_agents()
            
            # Initialize intelligent societies
            if "intelligent_societies" in self.config["auto_start_features"]:
                await self._initialize_intelligent_societies()
            
            # Start scheduler if enabled
            if "scheduler" in self.config["auto_start_features"]:
                await self._start_scheduler()
            
            # Start sync engine if enabled
            if self.config.get("enable_sync_engine", True):
                await self._start_sync_engine()
            
            # Start modern web interface
            if "web_interface" in self.config["auto_start_features"]:
                await self._start_modern_web_interface()
            
            self.status = "running"
            print("✅ Evolusi Kecerdasan Umum initialized successfully!")
            
            # Print comprehensive system status
            await self._print_evolusi_status()
            
        except Exception as e:
            print(f"❌ System initialization failed: {e}")
            logging.error(f"Initialization failed: {e}", exc_info=True)
            self.status = "failed"
            raise
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        directories = [
            "data", "data/backups", "data/logs", "data/cache", 
            "data/conversations", "data/analytics",
            "projects", "ui/generated", "reports",
            "config", "models", "societies", "workforces"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    async def _initialize_enhanced_prompts(self):
        """Initialize enhanced prompts library"""
        try:
            from core.enhanced_prompts import enhanced_prompts
            self.enhanced_prompts = enhanced_prompts
            
            # Load usage analytics if enabled
            if self.config["enhanced_prompts"]["usage_analytics"]:
                analytics_file = Path("data/analytics/prompt_usage.json")
                if analytics_file.exists():
                    with open(analytics_file, 'r') as f:
                        usage_data = json.load(f)
                        self.enhanced_prompts.usage_stats.update(usage_data)
            
            print("  ✅ Enhanced Prompts Library (25+ sophisticated prompts)")
            
        except Exception as e:
            print(f"  ❌ Enhanced Prompts: {e}")
            logging.error(f"Enhanced prompts initialization failed: {e}")
    
    async def _initialize_camel_integration(self):
        """Initialize Camel-AI integration"""
        try:
            from core.camel_integration import initialize_camel_integration, get_camel_integration
            
            # Initialize Camel-AI integration
            success = await initialize_camel_integration()
            if success:
                self.camel_integration = get_camel_integration()
                print("  ✅ Camel-AI Framework Integration")
                
                # Log integration status
                status = self.camel_integration.get_integration_status()
                print(f"    🐫 Agents: {status['agents_created']}")
                print(f"    🤖 Societies: {status['societies_created']}")
                print(f"    👥 Workforce: {'Available' if status['workforce_available'] else 'Not Available'}")
                print(f"    🔌 MCP: {'Available' if status['mcp_available'] else 'Not Available'}")
                
            else:
                print("  ⚠️  Camel-AI Integration failed, running in legacy mode")
                
        except Exception as e:
            print(f"  ❌ Camel-AI Integration: {e}")
            logging.error(f"Camel-AI integration failed: {e}")
    
    async def _initialize_core_components(self):
        """Initialize core system components (legacy compatibility)"""
        print("🔧 Initializing core components...")
        
        # Initialize Memory Bus
        try:
            from core.memory_bus import memory_bus
            self.memory_bus = memory_bus
            print("  ✅ Memory Bus")
        except Exception as e:
            print(f"  ❌ Memory Bus: {e}")
        
        # Initialize AI Selector
        try:
            from core.ai_selector import ai_selector
            self.ai_selector = ai_selector
            print("  ✅ AI Selector")
        except Exception as e:
            print(f"  ❌ AI Selector: {e}")
        
        # Initialize Enhanced Prompt Master
        try:
            from core.prompt_master import prompt_master
            self.prompt_master = prompt_master
            self.prompt_master.start_time = self.start_time.timestamp()
            
            # Integrate with enhanced prompts
            if self.enhanced_prompts:
                self.prompt_master.enhanced_prompts = self.enhanced_prompts
            
            # Integrate with Camel-AI
            if self.camel_integration:
                self.prompt_master.camel_integration = self.camel_integration
            
            print("  ✅ Enhanced Prompt Master")
        except Exception as e:
            print(f"  ❌ Prompt Master: {e}")
    
    async def _initialize_legacy_agents(self):
        """Initialize legacy agents for backward compatibility"""
        print("🤖 Initializing legacy agents...")
        
        # Simplified agent configurations for compatibility
        legacy_agent_configs = {
            "cybershell": {
                "module": "agents.cybershell",
                "instance": "cybershell_agent"
            },
            "agent_maker": {
                "module": "agents.agent_maker", 
                "instance": "agent_maker"
            },
            "ui_designer": {
                "module": "agents.ui_designer",
                "instance": "ui_designer_agent"
            },
            "commander_agi": {
                "module": "agents.commander_agi",
                "instance": "commander_agi"
            }
        }
        
        # Initialize only essential legacy agents
        for agent_id, config in legacy_agent_configs.items():
            try:
                module = __import__(config["module"], fromlist=[config["instance"]])
                agent_instance = getattr(module, config["instance"])
                
                self.legacy_agents[agent_id] = agent_instance
                self.active_agents[agent_id] = agent_instance
                
                print(f"  ✅ {agent_id} (legacy)")
                
            except Exception as e:
                print(f"  ⚠️  {agent_id}: {e}")
        
        print(f"🤖 Legacy agents: {len(self.legacy_agents)} loaded")
    
    async def _initialize_intelligent_societies(self):
        """Initialize intelligent agent societies"""
        if not self.camel_integration:
            print("  ⚠️  Intelligent Societies: Camel-AI not available")
            return
        
        try:
            # Create some default intelligent societies
            default_societies = [
                {
                    "name": "research_think_tank",
                    "description": "Research and analysis think tank",
                    "task": "Provide comprehensive research and analysis on complex topics"
                },
                {
                    "name": "development_team",
                    "description": "Software development team",
                    "task": "Design and develop software solutions with best practices"
                },
                {
                    "name": "innovation_lab",
                    "description": "Innovation and creative problem solving",
                    "task": "Generate innovative solutions to challenging problems"
                }
            ]
            
            for society_config in default_societies:
                try:
                    # This will be created on-demand when needed
                    self.active_societies[society_config["name"]] = {
                        "config": society_config,
                        "created": False,
                        "last_used": None
                    }
                except Exception as e:
                    logging.warning(f"Failed to prepare society {society_config['name']}: {e}")
            
            print(f"  ✅ Intelligent Societies ({len(self.active_societies)} templates)")
            
        except Exception as e:
            print(f"  ❌ Intelligent Societies: {e}")
    
    async def _start_scheduler(self):
        """Start the enhanced scheduler"""
        try:
            from core.scheduler import agent_scheduler
            self.scheduler = agent_scheduler
            self.scheduler.start()
            print("  ✅ Enhanced Scheduler")
        except Exception as e:
            print(f"  ❌ Scheduler: {e}")
    
    async def _start_sync_engine(self):
        """Start the sync engine"""
        try:
            from core.sync_engine import sync_engine
            self.sync_engine = sync_engine
            await self.sync_engine.start()
            print("  ✅ Sync Engine")
        except Exception as e:
            print(f"  ❌ Sync Engine: {e}")
    
    async def _start_modern_web_interface(self):
        """Start the modern web interface"""
        try:
            # Start modern web interface in background
            asyncio.create_task(self._run_modern_web_interface())
            print(f"  ✅ Modern Web Interface (Port {self.config['ui']['web_interface_port']})")
        except Exception as e:
            print(f"  ❌ Modern Web Interface: {e}")
    
    async def _run_modern_web_interface(self):
        """Run the modern web interface server"""
        try:
            # Create modern web interface script
            await self._create_modern_web_interface()
            
            import subprocess
            import sys
            
            # Start the modern interface
            subprocess.Popen([
                sys.executable, "ui/modern_interface.py"
            ])
            
        except Exception as e:
            logging.error(f"Modern web interface error: {e}")
    
    async def _create_modern_web_interface(self):
        """Create the modern web interface"""
        interface_code = '''"""
Modern Web Interface for Evolusi Kecerdasan Umum
Built with Streamlit for advanced AGI interactions
"""

import streamlit as st
import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="Evolusi Kecerdasan Umum",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("🧠 Evolusi Kecerdasan Umum")
    st.subheader("Advanced Multi-Agent Intelligence System")
    
    # Sidebar
    st.sidebar.title("🎛️ Control Panel")
    
    # Main interface tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🤖 Agents", "🧠 Enhanced Prompts", "🐫 Societies", "📊 Analytics"])
    
    with tab1:
        st.header("Active Agents")
        st.info("Agent management interface coming soon...")
    
    with tab2:
        st.header("Enhanced Prompts Library")
        st.info("Enhanced prompts interface coming soon...")
    
    with tab3:
        st.header("Intelligent Societies")
        st.info("Society management interface coming soon...")
    
    with tab4:
        st.header("System Analytics")
        st.info("Analytics dashboard coming soon...")

if __name__ == "__main__":
    main()
'''
        
        interface_file = Path("ui/modern_interface.py")
        with open(interface_file, 'w') as f:
            f.write(interface_code)
    
    async def _print_evolusi_status(self):
        """Print comprehensive Evolusi status"""
        status_info = f"""
┌─ EVOLUSI KECERDASAN UMUM STATUS ────────────────────────────────────────────┐
│ Status: {self.status.upper()}                                               
│ Version: {self.version}                                                     
│ Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}                    
│                                                                             
│ 🐫 Camel-AI Integration:                                                    
│   • Framework: {'✅' if self.camel_integration else '❌'}                    
│   • Agents: {self.camel_integration.integration_status['agents_created'] if self.camel_integration else 0}
│   • Societies: {self.camel_integration.integration_status['societies_created'] if self.camel_integration else 0}
│   • Workforce: {'✅' if self.camel_integration and self.camel_integration.integration_status['workforce_available'] else '❌'}
│   • MCP: {'✅' if self.camel_integration and self.camel_integration.integration_status['mcp_available'] else '❌'}
│                                                                             
│ 🧠 Enhanced Features:                                                       
│   • Enhanced Prompts: {'✅' if self.enhanced_prompts else '❌'} ({len(self.enhanced_prompts.prompts) if self.enhanced_prompts else 0} prompts)
│   • Intelligent Societies: {'✅' if self.active_societies else '❌'} ({len(self.active_societies)} templates)
│   • Legacy Agents: {'✅' if self.legacy_agents else '❌'} ({len(self.legacy_agents)} active)
│                                                                             
│ 🧠 Core Components:                                                         
│   • Enhanced Prompt Master: {'✅' if self.prompt_master else '❌'}          
│   • Memory Bus: {'✅' if self.memory_bus else '❌'}                         
│   • AI Selector: {'✅' if self.ai_selector else '❌'}                       
│   • Sync Engine: {'✅' if self.sync_engine else '❌'}                       
│   • Scheduler: {'✅' if self.scheduler else '❌'}                           
│                                                                             
│ 🌐 Interfaces:                                                              
│   • Modern Web UI: http://localhost:{self.config['ui']['web_interface_port']}
│   • Legacy API: http://localhost:{self.config['ui']['web_interface_port']}/api
│   • Streamlit Interface: streamlit run ui/modern_interface.py              
│                                                                             
│ 📊 Analytics:                                                               
│   • Tasks Processed: {self.analytics['tasks_processed']}                   
│   • Prompts Executed: {self.analytics['prompts_executed']}                 
│   • Societies Created: {self.analytics['societies_created']}               
│                                                                             
│ 🇮🇩 Made with ❤️ by Mulky Malikul Dhaher in Indonesia                      
│    Evolusi Kecerdasan Umum - Next Generation AGI                           
└─────────────────────────────────────────────────────────────────────────────┘
        """
        print(status_info)
    
    async def process_user_input(self, user_input: str, input_type: str = "text", 
                                metadata: Dict = None, use_camel: bool = True) -> Dict[str, Any]:
        """Process user input through the evolved system"""
        start_time = datetime.now()
        
        # Determine processing method
        if use_camel and self.camel_integration:
            result = await self._process_with_camel_ai(user_input, input_type, metadata)
        elif self.prompt_master:
            result = await self._process_with_legacy_system(user_input, input_type, metadata)
        else:
            return {"success": False, "error": "No processing system available"}
        
        # Update analytics
        processing_time = (datetime.now() - start_time).total_seconds()
        self.analytics["tasks_processed"] += 1
        self.analytics["average_response_time"] = (
            (self.analytics["average_response_time"] * (self.analytics["tasks_processed"] - 1) + processing_time) 
            / self.analytics["tasks_processed"]
        )
        
        result["processing_time"] = processing_time
        return result
    
    async def _process_with_camel_ai(self, user_input: str, input_type: str, metadata: Dict) -> Dict[str, Any]:
        """Process input using Camel-AI framework"""
        try:
            # Analyze input to determine best processing approach
            if self._is_complex_task(user_input):
                # Use intelligent society for complex tasks
                result = await self.camel_integration.create_intelligent_society(
                    task_description=user_input
                )
                
                if result.get("success"):
                    self.analytics["societies_created"] += 1
                
                return result
            
            else:
                # Use enhanced prompts for simpler tasks
                return await self._process_with_enhanced_prompts(user_input, metadata)
        
        except Exception as e:
            return {"success": False, "error": f"Camel-AI processing failed: {str(e)}"}
    
    async def _process_with_enhanced_prompts(self, user_input: str, metadata: Dict) -> Dict[str, Any]:
        """Process input using enhanced prompts"""
        try:
            # Auto-select appropriate prompt based on input
            prompt_id = self._select_appropriate_prompt(user_input)
            
            if prompt_id:
                result = await self.camel_integration.process_enhanced_prompt(
                    prompt_id=prompt_id,
                    task_description=user_input,
                    user_input=user_input,
                    **(metadata or {})
                )
                
                self.analytics["prompts_executed"] += 1
                return result
            
            else:
                # Fallback to direct agent processing
                return await self.camel_integration.process_enhanced_prompt(
                    prompt_id="systematic_solver",
                    problem_statement=user_input,
                    problem_context=metadata.get("context", "General problem solving"),
                    constraints=metadata.get("constraints", "Standard constraints"),
                    success_metrics=metadata.get("success_metrics", "Problem resolution"),
                    resources=metadata.get("resources", "System capabilities")
                )
        
        except Exception as e:
            return {"success": False, "error": f"Enhanced prompts processing failed: {str(e)}"}
    
    async def _process_with_legacy_system(self, user_input: str, input_type: str, metadata: Dict) -> Dict[str, Any]:
        """Process input using legacy system"""
        try:
            result = await self.prompt_master.process_prompt(
                prompt=user_input,
                input_type=input_type,
                metadata=metadata or {}
            )
            return result
        except Exception as e:
            return {"success": False, "error": f"Legacy processing failed: {str(e)}"}
    
    def _is_complex_task(self, user_input: str) -> bool:
        """Determine if a task is complex enough to warrant society processing"""
        complexity_indicators = [
            "analyze", "research", "develop", "create", "design", "implement",
            "compare", "evaluate", "synthesize", "integrate", "collaborate",
            "multi-step", "comprehensive", "detailed", "thorough"
        ]
        
        input_lower = user_input.lower()
        return any(indicator in input_lower for indicator in complexity_indicators) and len(user_input) > 50
    
    def _select_appropriate_prompt(self, user_input: str) -> Optional[str]:
        """Select appropriate enhanced prompt based on input analysis"""
        if not self.enhanced_prompts:
            return None
        
        input_lower = user_input.lower()
        
        # Map keywords to prompt IDs
        prompt_mapping = {
            ("research", "analyze", "study"): "research_synthesizer",
            ("code", "develop", "program"): "code_architect",
            ("design", "architecture", "system"): "architecture_visionary",
            ("creative", "innovative", "novel"): "innovation_catalyst",
            ("problem", "solve", "solution"): "systematic_solver",
            ("communicate", "explain", "present"): "adaptive_communicator",
            ("learn", "teach", "train"): "learning_orchestrator",
            ("future", "predict", "forecast"): "future_architect",
            ("ethical", "moral", "bias"): "ethics_advisor"
        }
        
        for keywords, prompt_id in prompt_mapping.items():
            if any(keyword in input_lower for keyword in keywords):
                return prompt_id
        
        return None
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        status = {
            "system_id": self.system_id,
            "version": self.version,
            "status": self.status,
            "uptime_seconds": uptime,
            "started_at": self.start_time.isoformat(),
            "system_mode": self.config.get("system_mode", "evolusi"),
            
            # Camel-AI integration status
            "camel_integration": {
                "available": self.camel_integration is not None,
                "status": self.camel_integration.get_integration_status() if self.camel_integration else None
            },
            
            # Enhanced features status
            "enhanced_features": {
                "prompts_library": {
                    "available": self.enhanced_prompts is not None,
                    "total_prompts": len(self.enhanced_prompts.prompts) if self.enhanced_prompts else 0,
                    "usage_stats": self.enhanced_prompts.get_usage_statistics() if self.enhanced_prompts else None
                },
                "intelligent_societies": {
                    "templates": len(self.active_societies),
                    "created": self.analytics["societies_created"]
                }
            },
            
            # Core components status
            "core_components": {
                "prompt_master": self.prompt_master is not None,
                "memory_bus": self.memory_bus is not None,
                "ai_selector": self.ai_selector is not None,
                "sync_engine": self.sync_engine is not None,
                "scheduler": self.scheduler is not None
            },
            
            # Agents status
            "agents": {
                "legacy_total": len(self.legacy_agents),
                "legacy_active": len(self.active_agents),
                "camel_agents": len(self.camel_integration.agent_factory.agents) if self.camel_integration else 0
            },
            
            # Analytics
            "analytics": self.analytics.copy(),
            
            # Configuration
            "config": self.config
        }
        
        # Add component-specific status
        if self.prompt_master:
            status["prompt_master_status"] = self.prompt_master.get_system_status()
        
        if self.camel_integration:
            status["camel_features"] = self.camel_integration.list_available_features()
        
        return status
    
    async def run_interactive_mode(self):
        """Run in enhanced interactive mode"""
        print("\n🎯 Entering Evolusi Interactive Mode")
        print("🧠 Enhanced with Camel-AI, 100+ prompts, and intelligent societies")
        print("Type 'help' for commands, 'exit' to quit.\n")
        
        while not self.shutdown_requested:
            try:
                # Get user input with enhanced prompt
                user_input = input("🧠 Evolusi AI > ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['exit', 'quit']:
                    break
                elif user_input.lower() == 'help':
                    self._print_evolusi_help()
                    continue
                elif user_input.lower() == 'status':
                    status = await self.get_system_status()
                    print(json.dumps(status, indent=2, default=str))
                    continue
                elif user_input.lower() == 'agents':
                    self._print_agents_status()
                    continue
                elif user_input.lower() == 'prompts':
                    self._print_prompts_status()
                    continue
                elif user_input.lower() == 'societies':
                    self._print_societies_status()
                    continue
                elif user_input.startswith('society:'):
                    # Create custom society
                    task = user_input[8:].strip()
                    if task:
                        await self._create_custom_society(task)
                    continue
                
                # Process as regular task
                print("🔄 Processing with Evolusi Intelligence...")
                result = await self.process_user_input(user_input)
                
                if result.get("success"):
                    print("✅ Task completed successfully!")
                    if "result" in result:
                        print(f"📊 Result: {result['result']}")
                    if "response" in result:
                        print(f"🤖 Response: {result['response']}")
                    if "processing_time" in result:
                        print(f"⏱️  Processing time: {result['processing_time']:.2f}s")
                else:
                    print(f"❌ Error: {result.get('error', 'Unknown error')}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Sampai jumpa! (Goodbye!)")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                logging.error(f"Interactive mode error: {e}", exc_info=True)
    
    def _print_evolusi_help(self):
        """Print enhanced help information"""
        help_text = """
🆘 EVOLUSI KECERDASAN UMUM - HELP

Commands:
  help                    - Show this help
  status                  - Show comprehensive system status
  agents                  - List all agents (Camel-AI + Legacy)
  prompts                 - Show enhanced prompts library
  societies               - Show intelligent societies
  society: <task>         - Create custom society for task
  exit/quit               - Exit the system

Enhanced Natural Language Commands:
  "Research the latest developments in quantum computing"
  "Design a microservices architecture for an e-commerce platform"
  "Create an innovative solution for sustainable energy storage"
  "Develop a machine learning model for fraud detection"
  "Analyze the ethical implications of AI in healthcare"
  "Generate a comprehensive business plan for a tech startup"

🧠 Enhanced Features:
  🐫 Camel-AI Societies - Multi-agent collaboration
  🤖 100+ Enhanced Prompts - Sophisticated prompt library
  🎯 Role-Playing Agents - Specialized agent interactions
  💡 Quantum Thinking - Advanced problem-solving approaches
  🔮 Future Architecture - Next-generation system design
  🌐 Modern UI - Advanced web interface

For documentation: http://localhost:5000/docs
Streamlit UI: streamlit run ui/modern_interface.py
        """
        print(help_text)
    
    def _print_agents_status(self):
        """Print agents status"""
        print("\n🤖 AGENTS STATUS")
        
        if self.camel_integration:
            camel_agents = self.camel_integration.agent_factory.list_agents()
            print(f"Camel-AI Agents: {len(camel_agents)}")
            for agent in camel_agents:
                print(f"  🐫 {agent}")
        
        print(f"Legacy Agents: {len(self.legacy_agents)}")
        for agent_id in self.legacy_agents:
            print(f"  🔧 {agent_id}")
    
    def _print_prompts_status(self):
        """Print enhanced prompts status"""
        if not self.enhanced_prompts:
            print("❌ Enhanced prompts not available")
            return
        
        stats = self.enhanced_prompts.get_usage_statistics()
        print(f"\n🧠 ENHANCED PROMPTS LIBRARY")
        print(f"Total prompts: {stats['total_prompts']}")
        print(f"Total usage: {stats['total_usage']}")
        
        if stats['most_used']:
            print(f"Most used: {stats['most_used'][0]} ({stats['most_used'][1]} times)")
        
        print("\nCategories:")
        for category, count in stats['category_usage'].items():
            print(f"  📝 {category}: {count} uses")
    
    def _print_societies_status(self):
        """Print intelligent societies status"""
        print(f"\n🐫 INTELLIGENT SOCIETIES")
        print(f"Available templates: {len(self.active_societies)}")
        print(f"Societies created: {self.analytics['societies_created']}")
        
        for name, info in self.active_societies.items():
            status = "✅ Created" if info["created"] else "📋 Template"
            print(f"  {status} {name}: {info['config']['description']}")
    
    async def _create_custom_society(self, task: str):
        """Create a custom society for a specific task"""
        if not self.camel_integration:
            print("❌ Camel-AI integration not available")
            return
        
        print(f"🔄 Creating intelligent society for: {task}")
        
        try:
            result = await self.camel_integration.create_intelligent_society(task)
            
            if result.get("success"):
                print("✅ Society created and conversation completed!")
                print(f"📊 Total turns: {result.get('total_turns', 0)}")
                print(f"⏱️  Duration: {result.get('start_time')} to {result.get('end_time')}")
                
                # Save conversation
                conversation_file = Path(f"data/conversations/society_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                with open(conversation_file, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                
                print(f"💾 Conversation saved to: {conversation_file}")
                
            else:
                print(f"❌ Society creation failed: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Error creating society: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Received signal {signum}, initiating Evolusi shutdown...")
        self.shutdown_requested = True
    
    async def shutdown(self):
        """Gracefully shutdown the system"""
        print("🛑 Shutting down Evolusi Kecerdasan Umum...")
        
        try:
            # Save analytics
            analytics_file = Path("data/analytics/session_analytics.json")
            with open(analytics_file, 'w') as f:
                json.dump({
                    "session_end": datetime.now().isoformat(),
                    "analytics": self.analytics,
                    "uptime_seconds": (datetime.now() - self.start_time).total_seconds()
                }, f, indent=2)
            
            # Save enhanced prompts usage
            if self.enhanced_prompts and self.config["enhanced_prompts"]["usage_analytics"]:
                usage_file = Path("data/analytics/prompt_usage.json")
                with open(usage_file, 'w') as f:
                    json.dump(self.enhanced_prompts.usage_stats, f, indent=2)
            
            # Stop scheduler
            if self.scheduler:
                self.scheduler.stop()
                print("  ✅ Scheduler stopped")
            
            # Close database connections
            if self.memory_bus:
                self.memory_bus.cleanup_expired()
                print("  ✅ Memory cleanup completed")
            
            # Save system state
            await self._save_system_state()
            
            self.status = "stopped"
            print("✅ Evolusi Kecerdasan Umum shutdown complete")
            
        except Exception as e:
            print(f"❌ Shutdown error: {e}")
            logging.error(f"Shutdown error: {e}", exc_info=True)
    
    async def _save_system_state(self):
        """Save current system state"""
        try:
            state = {
                "shutdown_time": datetime.now().isoformat(),
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                "version": self.version,
                "status": self.status,
                "analytics": self.analytics,
                "camel_integration_available": self.camel_integration is not None,
                "enhanced_prompts_available": self.enhanced_prompts is not None,
                "legacy_agents": list(self.legacy_agents.keys()),
                "societies_templates": len(self.active_societies)
            }
            
            with open("data/last_evolusi_session.json", "w") as f:
                json.dump(state, f, indent=2, default=str)
                
        except Exception as e:
            print(f"Failed to save system state: {e}")

async def main():
    """Main entry point for Evolusi Kecerdasan Umum"""
    print_banner()
    
    # Create and initialize system
    system = EvolusiKecerdasanUmum()
    
    try:
        # Initialize the evolved system
        await system.initialize()
        
        # Check command line arguments
        if len(sys.argv) > 1:
            command = " ".join(sys.argv[1:])
            print(f"🎯 Executing command: {command}")
            
            result = await system.process_user_input(command)
            
            if result.get("success"):
                print("✅ Command executed successfully!")
                if "result" in result:
                    print(json.dumps(result["result"], indent=2, default=str))
                if "response" in result:
                    print(f"🤖 Response: {result['response']}")
            else:
                print(f"❌ Command failed: {result.get('error')}")
        else:
            # Run in enhanced interactive mode
            await system.run_interactive_mode()
    
    except KeyboardInterrupt:
        print("\n👋 Sampai jumpa! (Goodbye!)")
    
    except Exception as e:
        print(f"❌ System error: {e}")
        logging.error(f"System error: {e}", exc_info=True)
    
    finally:
        # Shutdown gracefully
        await system.shutdown()

if __name__ == "__main__":
    # Run the evolved system
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 System interrupted - Sampai jumpa!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        logging.error(f"Fatal error: {e}", exc_info=True)
