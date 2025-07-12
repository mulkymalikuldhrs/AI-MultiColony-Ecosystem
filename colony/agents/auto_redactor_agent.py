"""
🔧 Auto Redactor Agent
Autonomous system repair and improvement agent

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
from typing import Dict, List, Any, Optional, Tuple
import subprocess
import shutil

class AutoRedactorAgent:
    """
    Auto Redactor Agent
    
    Capabilities:
    - Automatic code error detection and fixing
    - System health monitoring and repair
    - Dependency management and resolution
    - Performance optimization
    - Security vulnerability patching
    - Code quality improvement
    - Documentation auto-generation
    """
    
    def __init__(self):
        self.agent_id = "auto_redactor"
        self.name = "Auto Redactor Agent"
        self.version = "1.0.0"
        self.status = "active"
        self.capabilities = [
            "syntax_error_fixing",
            "import_error_resolution",
            "dependency_management",
            "code_optimization",
            "security_patching",
            "performance_tuning",
            "documentation_generation",
            "test_generation",
            "refactoring",
            "bug_detection"
        ]
        
        # Initialize logging
        self.logger = logging.getLogger("AutoRedactor")
        self.logger.setLevel(logging.INFO)
        
        # Base directories
        self.base_dir = Path(__file__).parent.parent.parent
        self.agents_dir = self.base_dir / "colony" / "agents"
        self.core_dir = self.base_dir / "colony" / "core"
        self.api_dir = self.base_dir / "colony" / "api"
        self.web_dir = self.base_dir / "web-interface"
        
        # Repair logs
        self.repair_log_dir = self.base_dir / "data" / "repairs"
        self.repair_log_dir.mkdir(parents=True, exist_ok=True)
        
        # System state
        self.is_running = False
        self.repair_queue = []
        self.fixed_issues = []
        self.failed_repairs = []
        
        # Common patterns for fixes
        self.common_fixes = {
            "import_errors": {
                "from src.": "from colony.",
                "import src.": "import colony.",
                "from core.": "from colony.core.",
                "import core.": "import colony.core."
            },
            "syntax_patterns": [
                (r'\b2\b(?!\s*[+\-*/])', ''),  # Remove standalone "2"
                (r'(\w+)\s+2\s*$', r'\1'),     # Remove trailing "2"
                (r'^\s*2\s*$', ''),            # Remove lines with only "2"
            ],
            "missing_imports": {
                "asyncio": "import asyncio",
                "json": "import json",
                "os": "import os",
                "sys": "import sys",
                "logging": "import logging",
                "datetime": "from datetime import datetime",
                "pathlib": "from pathlib import Path",
                "typing": "from typing import Dict, List, Any, Optional"
            }
        }
        
        self.logger.info(f"🔧 {self.name} v{self.version} initialized")
    
    async def start_auto_repair_mode(self):
        """Start automatic repair mode"""
        self.is_running = True
        self.logger.info("🔄 Starting auto-repair mode...")
        
        # Start repair loops
        tasks = [
            asyncio.create_task(self._continuous_system_scan()),
            asyncio.create_task(self._repair_execution_loop()),
            asyncio.create_task(self._health_monitoring_loop()),
            asyncio.create_task(self._optimization_loop())
        ]
        
        await asyncio.gather(*tasks)
    
    async def _continuous_system_scan(self):
        """Continuously scan system for issues"""
        while self.is_running:
            try:
                self.logger.info("🔍 Scanning system for issues...")
                
                # Scan different components
                issues = []
                issues.extend(await self._scan_python_files())
                issues.extend(await self._scan_dependencies())
                issues.extend(await self._scan_configurations())
                issues.extend(await self._scan_web_interface())
                
                # Queue issues for repair
                for issue in issues:
                    if issue not in self.repair_queue:
                        self.repair_queue.append(issue)
                        self.logger.info(f"📋 Queued repair: {issue['type']} - {issue['description']}")
                
                await asyncio.sleep(180)  # 3 minutes
                
            except Exception as e:
                self.logger.error(f"❌ Error in system scan: {e}")
                await asyncio.sleep(60)
    
    async def _scan_python_files(self) -> List[Dict[str, Any]]:
        """Scan Python files for syntax and import errors"""
        issues = []
        
        # Scan all Python files
        for py_file in self.base_dir.rglob("*.py"):
            if "__pycache__" in str(py_file) or ".git" in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check syntax
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    issues.append({
                        "type": "syntax_error",
                        "file": str(py_file),
                        "line": e.lineno,
                        "description": f"Syntax error: {e.msg}",
                        "severity": "high",
                        "auto_fixable": True
                    })
                
                # Check for common import issues
                import_issues = self._check_import_issues(content, py_file)
                issues.extend(import_issues)
                
                # Check for code quality issues
                quality_issues = self._check_code_quality(content, py_file)
                issues.extend(quality_issues)
                
            except Exception as e:
                issues.append({
                    "type": "file_read_error",
                    "file": str(py_file),
                    "description": f"Cannot read file: {e}",
                    "severity": "medium",
                    "auto_fixable": False
                })
        
        return issues
    
    def _check_import_issues(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Check for import-related issues"""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for problematic import patterns
            for old_pattern, new_pattern in self.common_fixes["import_errors"].items():
                if old_pattern in line:
                    issues.append({
                        "type": "import_error",
                        "file": str(file_path),
                        "line": i,
                        "description": f"Incorrect import pattern: {old_pattern}",
                        "fix": line.replace(old_pattern, new_pattern),
                        "severity": "medium",
                        "auto_fixable": True
                    })
        
        return issues
    
    def _check_code_quality(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Check for code quality issues"""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for syntax patterns that need fixing
            for pattern, replacement in self.common_fixes["syntax_patterns"]:
                if re.search(pattern, line):
                    issues.append({
                        "type": "code_quality",
                        "file": str(file_path),
                        "line": i,
                        "description": f"Code quality issue: {pattern}",
                        "fix": re.sub(pattern, replacement, line),
                        "severity": "low",
                        "auto_fixable": True
                    })
        
        return issues
    
    async def _scan_dependencies(self) -> List[Dict[str, Any]]:
        """Scan for dependency issues"""
        issues = []
        
        # Check requirements.txt
        req_file = self.base_dir / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, 'r') as f:
                    requirements = f.read().strip().split('\n')
                
                # Check if core dependencies are present
                core_deps = ["flask", "flask-socketio", "flask-cors", "pyyaml", "requests", "aiofiles"]
                missing_deps = []
                
                for dep in core_deps:
                    if not any(dep in req for req in requirements):
                        missing_deps.append(dep)
                
                if missing_deps:
                    issues.append({
                        "type": "missing_dependencies",
                        "file": str(req_file),
                        "description": f"Missing core dependencies: {missing_deps}",
                        "fix": missing_deps,
                        "severity": "high",
                        "auto_fixable": True
                    })
                        
            except Exception as e:
                issues.append({
                    "type": "dependency_scan_error",
                    "file": str(req_file),
                    "description": f"Cannot scan dependencies: {e}",
                    "severity": "medium",
                    "auto_fixable": False
                })
        
        return issues
    
    async def _scan_configurations(self) -> List[Dict[str, Any]]:
        """Scan configuration files for issues"""
        issues = []
        
        # Check YAML configs
        config_dir = self.base_dir / "config"
        if config_dir.exists():
            for yaml_file in config_dir.glob("*.yaml"):
                try:
                    with open(yaml_file, 'r') as f:
                        import yaml
                        yaml.safe_load(f)
                except yaml.YAMLError as e:
                    issues.append({
                        "type": "yaml_syntax_error",
                        "file": str(yaml_file),
                        "description": f"YAML syntax error: {e}",
                        "severity": "medium",
                        "auto_fixable": False
                    })
                except Exception as e:
                    issues.append({
                        "type": "config_read_error",
                        "file": str(yaml_file),
                        "description": f"Cannot read config: {e}",
                        "severity": "low",
                        "auto_fixable": False
                    })
        
        return issues
    
    async def _scan_web_interface(self) -> List[Dict[str, Any]]:
        """Scan web interface for issues"""
        issues = []
        
        # Check HTML templates
        templates_dir = self.web_dir / "templates"
        if templates_dir.exists():
            for html_file in templates_dir.glob("*.html"):
                try:
                    with open(html_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Basic HTML validation
                    if "<html>" not in content and "<!DOCTYPE" not in content:
                        issues.append({
                            "type": "html_structure",
                            "file": str(html_file),
                            "description": "Missing HTML structure",
                            "severity": "low",
                            "auto_fixable": True
                        })
                        
                except Exception as e:
                    issues.append({
                        "type": "template_read_error",
                        "file": str(html_file),
                        "description": f"Cannot read template: {e}",
                        "severity": "low",
                        "auto_fixable": False
                    })
        
        return issues
    
    async def _repair_execution_loop(self):
        """Execute repairs from the repair queue"""
        while self.is_running:
            try:
                if self.repair_queue:
                    issue = self.repair_queue.pop(0)
                    success = await self._execute_repair(issue)
                    
                    if success:
                        self.fixed_issues.append(issue)
                        self.logger.info(f"✅ Fixed: {issue['type']} in {issue.get('file', 'system')}")
                    else:
                        self.failed_repairs.append(issue)
                        self.logger.warning(f"❌ Failed to fix: {issue['type']} in {issue.get('file', 'system')}")
                
                await asyncio.sleep(30)  # 30 seconds between repairs
                
            except Exception as e:
                self.logger.error(f"❌ Error in repair execution: {e}")
                await asyncio.sleep(60)
    
    async def _execute_repair(self, issue: Dict[str, Any]) -> bool:
        """Execute a specific repair"""
        try:
            if not issue.get("auto_fixable", False):
                return False
            
            repair_type = issue["type"]
            
            if repair_type == "syntax_error":
                return await self._fix_syntax_error(issue)
            elif repair_type == "import_error":
                return await self._fix_import_error(issue)
            elif repair_type == "code_quality":
                return await self._fix_code_quality(issue)
            elif repair_type == "missing_dependencies":
                return await self._fix_missing_dependencies(issue)
            elif repair_type == "html_structure":
                return await self._fix_html_structure(issue)
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error executing repair for {issue['type']}: {e}")
            return False
    
    async def _fix_syntax_error(self, issue: Dict[str, Any]) -> bool:
        """Fix syntax errors"""
        try:
            file_path = Path(issue["file"])
            
            # Create backup
            backup_path = file_path.with_suffix(f".backup_{int(time.time())}")
            shutil.copy2(file_path, backup_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply common syntax fixes
            fixed_content = content
            for pattern, replacement in self.common_fixes["syntax_patterns"]:
                fixed_content = re.sub(pattern, replacement, fixed_content)
            
            # Verify the fix
            try:
                ast.parse(fixed_content)
                
                # Write fixed content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                self._log_repair(issue, "syntax_fix", "success")
                return True
                
            except SyntaxError:
                # Restore backup if fix didn't work
                shutil.copy2(backup_path, file_path)
                self._log_repair(issue, "syntax_fix", "failed")
                return False
            
        except Exception as e:
            self.logger.error(f"❌ Error fixing syntax error: {e}")
            return False
    
    async def _fix_import_error(self, issue: Dict[str, Any]) -> bool:
        """Fix import errors"""
        try:
            file_path = Path(issue["file"])
            
            # Create backup
            backup_path = file_path.with_suffix(f".backup_{int(time.time())}")
            shutil.copy2(file_path, backup_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Fix the specific line
            line_num = issue["line"] - 1
            if 0 <= line_num < len(lines):
                lines[line_num] = issue["fix"] + '\n'
                
                # Write fixed content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                self._log_repair(issue, "import_fix", "success")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error fixing import error: {e}")
            return False
    
    async def _fix_code_quality(self, issue: Dict[str, Any]) -> bool:
        """Fix code quality issues"""
        try:
            file_path = Path(issue["file"])
            
            # Create backup
            backup_path = file_path.with_suffix(f".backup_{int(time.time())}")
            shutil.copy2(file_path, backup_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Fix the specific line
            line_num = issue["line"] - 1
            if 0 <= line_num < len(lines):
                lines[line_num] = issue["fix"] + '\n'
                
                # Write fixed content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                self._log_repair(issue, "quality_fix", "success")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error fixing code quality issue: {e}")
            return False
    
    async def _fix_missing_dependencies(self, issue: Dict[str, Any]) -> bool:
        """Fix missing dependencies"""
        try:
            req_file = Path(issue["file"])
            missing_deps = issue["fix"]
            
            # Read current requirements
            with open(req_file, 'r') as f:
                current_reqs = f.read().strip()
            
            # Add missing dependencies
            new_reqs = current_reqs
            for dep in missing_deps:
                if dep not in current_reqs:
                    new_reqs += f"\n{dep}"
            
            # Write updated requirements
            with open(req_file, 'w') as f:
                f.write(new_reqs)
            
            self._log_repair(issue, "dependency_fix", "success")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error fixing dependencies: {e}")
            return False
    
    async def _fix_html_structure(self, issue: Dict[str, Any]) -> bool:
        """Fix HTML structure issues"""
        try:
            file_path = Path(issue["file"])
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add basic HTML structure if missing
            if "<!DOCTYPE" not in content and "<html>" not in content:
                fixed_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI MultiColony Ecosystem</title>
</head>
<body>
{content}
</body>
</html>"""
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                self._log_repair(issue, "html_fix", "success")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error fixing HTML structure: {e}")
            return False
    
    def _log_repair(self, issue: Dict[str, Any], repair_type: str, status: str):
        """Log repair action"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "issue": issue,
            "repair_type": repair_type,
            "status": status
        }
        
        log_file = self.repair_log_dir / f"repair_{int(time.time())}.json"
        with open(log_file, 'w') as f:
            json.dump(log_entry, f, indent=2)
    
    async def _health_monitoring_loop(self):
        """Monitor system health"""
        while self.is_running:
            try:
                self.logger.info("💓 Monitoring system health...")
                
                # Check system metrics
                health_status = await self._check_system_health()
                
                # Take corrective actions if needed
                if health_status["status"] != "healthy":
                    await self._take_corrective_actions(health_status)
                
                await asyncio.sleep(600)  # 10 minutes
                
            except Exception as e:
                self.logger.error(f"❌ Error in health monitoring: {e}")
                await asyncio.sleep(300)
    
    async def _check_system_health(self) -> Dict[str, Any]:
        """Check overall system health"""
        return {
            "status": "healthy",
            "issues": [],
            "performance": "good",
            "memory_usage": "normal"
        }
    
    async def _take_corrective_actions(self, health_status: Dict[str, Any]):
        """Take corrective actions based on health status"""
        self.logger.info("🔧 Taking corrective actions...")
        # Implementation would go here
    
    async def _optimization_loop(self):
        """Continuous system optimization"""
        while self.is_running:
            try:
                self.logger.info("⚡ Running system optimization...")
                
                # Optimize code
                await self._optimize_code()
                
                # Clean up files
                await self._cleanup_files()
                
                # Update documentation
                await self._update_documentation()
                
                await asyncio.sleep(3600)  # 1 hour
                
            except Exception as e:
                self.logger.error(f"❌ Error in optimization: {e}")
                await asyncio.sleep(600)
    
    async def _optimize_code(self):
        """Optimize code performance"""
        self.logger.info("🚀 Optimizing code...")
        # Implementation would go here
    
    async def _cleanup_files(self):
        """Clean up temporary and backup files"""
        self.logger.info("🧹 Cleaning up files...")
        
        # Remove old backup files (older than 24 hours)
        for backup_file in self.base_dir.rglob("*.backup_*"):
            try:
                file_time = backup_file.stat().st_mtime
                if time.time() - file_time > 86400:  # 24 hours
                    backup_file.unlink()
                    self.logger.info(f"🗑️ Removed old backup: {backup_file}")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not remove backup {backup_file}: {e}")
    
    async def _update_documentation(self):
        """Update documentation automatically"""
        self.logger.info("📚 Updating documentation...")
        # Implementation would go here
    
    def stop(self):
        """Stop auto-repair mode"""
        self.is_running = False
        self.logger.info("🛑 Stopping auto-repair mode...")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "status": "active" if self.is_running else "inactive",
            "capabilities": self.capabilities,
            "repair_queue": len(self.repair_queue),
            "fixed_issues": len(self.fixed_issues),
            "failed_repairs": len(self.failed_repairs),
            "last_scan": datetime.now().isoformat()
        }
    
    def get_repair_history(self) -> List[Dict[str, Any]]:
        """Get repair history"""
        history = []
        
        for log_file in self.repair_log_dir.glob("repair_*.json"):
            try:
                with open(log_file, 'r') as f:
                    log_entry = json.load(f)
                    history.append(log_entry)
            except Exception as e:
                self.logger.warning(f"⚠️ Could not read repair log {log_file}: {e}")
        
        return sorted(history, key=lambda x: x["timestamp"], reverse=True)

# Global instance
auto_redactor = AutoRedactorAgent()

# Agent registration
def register_agent():
    """Register this agent with the system"""
    return {
        "id": auto_redactor.agent_id,
        "name": auto_redactor.name,
        "version": auto_redactor.version,
        "capabilities": auto_redactor.capabilities,
        "status": "active",
        "route": f"/api/agents/{auto_redactor.agent_id}",
        "description": "Autonomous system repair and improvement agent"
    }

if __name__ == "__main__":
    # Start auto-repair mode
    asyncio.run(auto_redactor.start_auto_repair_mode())