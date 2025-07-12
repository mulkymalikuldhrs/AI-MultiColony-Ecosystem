#!/usr/bin/env python3
"""
AI-MultiColony-Ecosystem System Analyzer
Comprehensive analysis tool to ensure all components work together
Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import os
import sys
import importlib
import inspect
import ast
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import traceback

class SystemAnalyzer:
    """Comprehensive system analyzer for AI-MultiColony-Ecosystem"""
    
    def __init__(self):
        self.root_path = Path(__file__).parent
        self.analysis_results = {
            "overview": {},
            "agents": {},
            "core_modules": {},
            "web_interface": {},
            "configurations": {},
            "dependencies": {},
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
    
    def analyze_all(self) -> Dict[str, Any]:
        """Run comprehensive analysis of the entire system"""
        print("🔍 Starting comprehensive system analysis...")
        
        # 1. Analyze project structure
        self._analyze_project_structure()
        
        # 2. Analyze agents
        self._analyze_agents()
        
        # 3. Analyze core modules
        self._analyze_core_modules()
        
        # 4. Analyze web interface
        self._analyze_web_interface()
        
        # 5. Analyze configurations
        self._analyze_configurations()
        
        # 6. Analyze dependencies
        self._analyze_dependencies()
        
        # 7. Test imports
        self._test_imports()
        
        # 8. Generate recommendations
        self._generate_recommendations()
        
        return self.analysis_results
    
    def _analyze_project_structure(self):
        """Analyze overall project structure"""
        print("📁 Analyzing project structure...")
        
        structure = {}
        
        # Count files by type
        python_files = list(self.root_path.rglob("*.py"))
        html_files = list(self.root_path.rglob("*.html"))
        js_files = list(self.root_path.rglob("*.js"))
        yaml_files = list(self.root_path.rglob("*.yaml")) + list(self.root_path.rglob("*.yml"))
        json_files = list(self.root_path.rglob("*.json"))
        
        structure = {
            "total_python_files": len(python_files),
            "total_html_files": len(html_files),
            "total_js_files": len(js_files),
            "total_yaml_files": len(yaml_files),
            "total_json_files": len(json_files),
            "main_directories": [d.name for d in self.root_path.iterdir() if d.is_dir()],
            "key_files": [
                "main.py",
                "requirements.txt",
                "README.md",
                "docker-compose.yml",
                "Dockerfile"
            ]
        }
        
        # Check for key files
        missing_files = []
        for key_file in structure["key_files"]:
            if not (self.root_path / key_file).exists():
                missing_files.append(key_file)
        
        if missing_files:
            self.analysis_results["warnings"].append(f"Missing key files: {missing_files}")
        
        self.analysis_results["overview"]["structure"] = structure
    
    def _analyze_agents(self):
        """Analyze all agent modules"""
        print("🤖 Analyzing agent modules...")
        
        agents_dir = self.root_path / "colony" / "agents"
        if not agents_dir.exists():
            self.analysis_results["errors"].append("Agents directory not found")
            return
        
        agents_analysis = {
            "total_agents": 0,
            "working_agents": 0,
            "broken_agents": 0,
            "agent_details": {},
            "agent_categories": {}
        }
        
        for agent_file in agents_dir.glob("*.py"):
            if agent_file.name.startswith("__"):
                continue
                
            agent_name = agent_file.stem
            agents_analysis["total_agents"] += 1
            
            try:
                # Try to parse the file
                with open(agent_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse AST to extract information
                tree = ast.parse(content)
                
                classes = []
                functions = []
                imports = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        classes.append(node.name)
                    elif isinstance(node, ast.FunctionDef):
                        functions.append(node.name)
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module)
                
                agents_analysis["agent_details"][agent_name] = {
                    "status": "working",
                    "classes": classes,
                    "functions": len(functions),
                    "imports": len(imports),
                    "file_size": agent_file.stat().st_size,
                    "lines": len(content.splitlines())
                }
                
                agents_analysis["working_agents"] += 1
                
                # Categorize agent
                if "financial" in agent_name.lower() or "money" in agent_name.lower():
                    category = "financial"
                elif "security" in agent_name.lower() or "auth" in agent_name.lower():
                    category = "security"
                elif "deploy" in agent_name.lower() or "dev" in agent_name.lower():
                    category = "development"
                elif "ui" in agent_name.lower() or "design" in agent_name.lower():
                    category = "design"
                else:
                    category = "general"
                
                if category not in agents_analysis["agent_categories"]:
                    agents_analysis["agent_categories"][category] = 0
                agents_analysis["agent_categories"][category] += 1
                
            except Exception as e:
                agents_analysis["agent_details"][agent_name] = {
                    "status": "broken",
                    "error": str(e)
                }
                agents_analysis["broken_agents"] += 1
                self.analysis_results["errors"].append(f"Agent {agent_name}: {str(e)}")
        
        self.analysis_results["agents"] = agents_analysis
    
    def _analyze_core_modules(self):
        """Analyze core system modules"""
        print("⚙️ Analyzing core modules...")
        
        core_dir = self.root_path / "colony" / "core"
        if not core_dir.exists():
            self.analysis_results["errors"].append("Core directory not found")
            return
        
        core_analysis = {
            "total_modules": 0,
            "working_modules": 0,
            "broken_modules": 0,
            "module_details": {},
            "key_modules": [
                "agent_registry.py",
                "base_agent.py",
                "system_bootstrap.py",
                "web_ui_connector.py",
                "launcher_agent_connector.py",
                "autonomous_engine_connector.py"
            ]
        }
        
        for module_file in core_dir.glob("*.py"):
            if module_file.name.startswith("__"):
                continue
                
            module_name = module_file.stem
            core_analysis["total_modules"] += 1
            
            try:
                with open(module_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                classes = []
                functions = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        classes.append(node.name)
                    elif isinstance(node, ast.FunctionDef):
                        functions.append(node.name)
                
                core_analysis["module_details"][module_name] = {
                    "status": "working",
                    "classes": classes,
                    "functions": len(functions),
                    "file_size": module_file.stat().st_size,
                    "lines": len(content.splitlines()),
                    "is_key_module": module_file.name in core_analysis["key_modules"]
                }
                
                core_analysis["working_modules"] += 1
                
            except Exception as e:
                core_analysis["module_details"][module_name] = {
                    "status": "broken",
                    "error": str(e)
                }
                core_analysis["broken_modules"] += 1
                self.analysis_results["errors"].append(f"Core module {module_name}: {str(e)}")
        
        self.analysis_results["core_modules"] = core_analysis
    
    def _analyze_web_interface(self):
        """Analyze web interface components"""
        print("🌐 Analyzing web interface...")
        
        web_dir = self.root_path / "web-interface"
        api_dir = self.root_path / "colony" / "api"
        
        web_analysis = {
            "has_web_interface": web_dir.exists(),
            "has_api": api_dir.exists(),
            "templates": 0,
            "static_files": 0,
            "api_endpoints": 0
        }
        
        if web_dir.exists():
            # Count templates
            templates_dir = web_dir / "templates"
            if templates_dir.exists():
                web_analysis["templates"] = len(list(templates_dir.glob("*.html")))
            
            # Count static files
            static_dir = web_dir / "static"
            if static_dir.exists():
                web_analysis["static_files"] = len(list(static_dir.rglob("*")))
        
        if api_dir.exists():
            # Analyze API structure
            app_file = api_dir / "app.py"
            if app_file.exists():
                try:
                    with open(app_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Count route decorators
                    web_analysis["api_endpoints"] = content.count("@app.route") + content.count("@socketio.on")
                    
                except Exception as e:
                    self.analysis_results["errors"].append(f"API analysis error: {str(e)}")
        
        self.analysis_results["web_interface"] = web_analysis
    
    def _analyze_configurations(self):
        """Analyze configuration files"""
        print("⚙️ Analyzing configurations...")
        
        config_analysis = {
            "config_files": {},
            "has_launcher_config": False,
            "has_system_config": False,
            "has_agent_templates": False
        }
        
        config_dir = self.root_path / "config"
        if config_dir.exists():
            for config_file in config_dir.glob("*"):
                if config_file.is_file():
                    config_analysis["config_files"][config_file.name] = {
                        "size": config_file.stat().st_size,
                        "exists": True
                    }
        
        # Check for key config files
        key_configs = {
            "launcher_config.yaml": "has_launcher_config",
            "system_config.yaml": "has_system_config", 
            "agent_templates.yaml": "has_agent_templates"
        }
        
        for config_file, flag in key_configs.items():
            if (config_dir / config_file).exists():
                config_analysis[flag] = True
        
        self.analysis_results["configurations"] = config_analysis
    
    def _analyze_dependencies(self):
        """Analyze project dependencies"""
        print("📦 Analyzing dependencies...")
        
        deps_analysis = {
            "requirements_file_exists": False,
            "total_dependencies": 0,
            "core_dependencies": [],
            "optional_dependencies": [],
            "missing_dependencies": []
        }
        
        req_file = self.root_path / "requirements.txt"
        if req_file.exists():
            deps_analysis["requirements_file_exists"] = True
            
            try:
                with open(req_file, 'r') as f:
                    lines = f.readlines()
                
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        deps_analysis["total_dependencies"] += 1
                        
                        # Categorize dependencies
                        if any(core in line.lower() for core in ['flask', 'fastapi', 'requests', 'pyyaml']):
                            deps_analysis["core_dependencies"].append(line)
                        else:
                            deps_analysis["optional_dependencies"].append(line)
                
            except Exception as e:
                self.analysis_results["errors"].append(f"Requirements analysis error: {str(e)}")
        
        self.analysis_results["dependencies"] = deps_analysis
    
    def _test_imports(self):
        """Test critical imports"""
        print("🧪 Testing critical imports...")
        
        critical_imports = [
            "colony.core.agent_registry",
            "colony.core.base_agent",
            "colony.core.system_bootstrap",
            "colony.api.app"
        ]
        
        import_results = {}
        
        for module_name in critical_imports:
            try:
                importlib.import_module(module_name)
                import_results[module_name] = "success"
            except Exception as e:
                import_results[module_name] = f"failed: {str(e)}"
                self.analysis_results["errors"].append(f"Import failed for {module_name}: {str(e)}")
        
        self.analysis_results["import_tests"] = import_results
    
    def _generate_recommendations(self):
        """Generate recommendations based on analysis"""
        print("💡 Generating recommendations...")
        
        recommendations = []
        
        # Check agent health
        if self.analysis_results["agents"]["broken_agents"] > 0:
            recommendations.append({
                "priority": "high",
                "category": "agents",
                "issue": f"{self.analysis_results['agents']['broken_agents']} broken agents found",
                "solution": "Fix syntax errors and missing dependencies in agent files"
            })
        
        # Check core modules
        if self.analysis_results["core_modules"]["broken_modules"] > 0:
            recommendations.append({
                "priority": "critical",
                "category": "core",
                "issue": f"{self.analysis_results['core_modules']['broken_modules']} broken core modules",
                "solution": "Fix core module errors immediately as they affect system stability"
            })
        
        # Check configurations
        if not self.analysis_results["configurations"]["has_launcher_config"]:
            recommendations.append({
                "priority": "medium",
                "category": "config",
                "issue": "Missing launcher configuration",
                "solution": "Create config/launcher_config.yaml for proper system configuration"
            })
        
        # Check dependencies
        if not self.analysis_results["dependencies"]["requirements_file_exists"]:
            recommendations.append({
                "priority": "high",
                "category": "dependencies",
                "issue": "Missing requirements.txt",
                "solution": "Create proper requirements.txt with all necessary dependencies"
            })
        
        # Check web interface
        if not self.analysis_results["web_interface"]["has_web_interface"]:
            recommendations.append({
                "priority": "medium",
                "category": "web",
                "issue": "Web interface directory missing",
                "solution": "Ensure web-interface directory exists with proper structure"
            })
        
        self.analysis_results["recommendations"] = recommendations
    
    def generate_report(self) -> str:
        """Generate comprehensive analysis report"""
        report = []
        report.append("=" * 80)
        report.append("🚀 AI-MultiColony-Ecosystem System Analysis Report")
        report.append("=" * 80)
        report.append("")
        
        # Overview
        report.append("📊 SYSTEM OVERVIEW")
        report.append("-" * 40)
        overview = self.analysis_results["overview"]["structure"]
        report.append(f"📁 Total Python files: {overview['total_python_files']}")
        report.append(f"🌐 Total HTML files: {overview['total_html_files']}")
        report.append(f"⚙️ Total YAML files: {overview['total_yaml_files']}")
        report.append(f"📂 Main directories: {', '.join(overview['main_directories'])}")
        report.append("")
        
        # Agents
        report.append("🤖 AGENTS ANALYSIS")
        report.append("-" * 40)
        agents = self.analysis_results["agents"]
        report.append(f"📊 Total agents: {agents['total_agents']}")
        report.append(f"✅ Working agents: {agents['working_agents']}")
        report.append(f"❌ Broken agents: {agents['broken_agents']}")
        report.append(f"📈 Success rate: {(agents['working_agents']/agents['total_agents']*100):.1f}%")
        report.append("")
        
        # Core Modules
        report.append("⚙️ CORE MODULES ANALYSIS")
        report.append("-" * 40)
        core = self.analysis_results["core_modules"]
        report.append(f"📊 Total modules: {core['total_modules']}")
        report.append(f"✅ Working modules: {core['working_modules']}")
        report.append(f"❌ Broken modules: {core['broken_modules']}")
        report.append(f"📈 Success rate: {(core['working_modules']/core['total_modules']*100):.1f}%")
        report.append("")
        
        # Web Interface
        report.append("🌐 WEB INTERFACE ANALYSIS")
        report.append("-" * 40)
        web = self.analysis_results["web_interface"]
        report.append(f"🌐 Has web interface: {'✅' if web['has_web_interface'] else '❌'}")
        report.append(f"🔌 Has API: {'✅' if web['has_api'] else '❌'}")
        report.append(f"📄 Templates: {web['templates']}")
        report.append(f"🔗 API endpoints: {web['api_endpoints']}")
        report.append("")
        
        # Errors
        if self.analysis_results["errors"]:
            report.append("❌ ERRORS FOUND")
            report.append("-" * 40)
            for error in self.analysis_results["errors"][:10]:  # Show first 10 errors
                report.append(f"• {error}")
            if len(self.analysis_results["errors"]) > 10:
                report.append(f"... and {len(self.analysis_results['errors']) - 10} more errors")
            report.append("")
        
        # Recommendations
        if self.analysis_results["recommendations"]:
            report.append("💡 RECOMMENDATIONS")
            report.append("-" * 40)
            for rec in self.analysis_results["recommendations"]:
                priority_icon = "🔴" if rec["priority"] == "critical" else "🟡" if rec["priority"] == "high" else "🟢"
                report.append(f"{priority_icon} [{rec['priority'].upper()}] {rec['issue']}")
                report.append(f"   💡 Solution: {rec['solution']}")
                report.append("")
        
        report.append("=" * 80)
        report.append("Analysis completed successfully! 🎉")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_report(self, filename: str = "system_analysis_report.txt"):
        """Save analysis report to file"""
        report = self.generate_report()
        
        with open(self.root_path / filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Also save JSON data
        json_filename = filename.replace('.txt', '.json')
        with open(self.root_path / json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, default=str)
        
        print(f"📄 Report saved to: {filename}")
        print(f"📊 Data saved to: {json_filename}")

def main():
    """Main function to run system analysis"""
    analyzer = SystemAnalyzer()
    
    # Run analysis
    results = analyzer.analyze_all()
    
    # Generate and display report
    report = analyzer.generate_report()
    print(report)
    
    # Save report
    analyzer.save_report()
    
    return results

if __name__ == "__main__":
    main()