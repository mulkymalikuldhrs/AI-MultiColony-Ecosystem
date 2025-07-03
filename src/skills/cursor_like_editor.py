"""
Cursor-like Code Editor Skills
Internal implementation of Cursor.so features
"""

import os
import ast
import re
import asyncio
import subprocess
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import difflib
import json
from datetime import datetime

# Import for code analysis
import tokenize
import io

from ..utils.logger import get_logger

logger = get_logger(__name__)

class CursorLikeCodeEditor:
    """
    Cursor-like AI-powered code editor
    Provides intelligent code completion, refactoring, and background agents
    """
    
    def __init__(self):
        self.model_manager = None
        self.agent_manager = None
        
        # Code context
        self.project_context = {}
        self.file_contexts = {}
        self.code_history = []
        
        # Background agents
        self.background_agents = []
        self.active_suggestions = {}
        
        # Code templates and patterns
        self.code_templates = {
            "python": {
                "function": """def {name}({params}):
    \"\"\"{docstring}\"\"\"
    {body}
    return {return_value}""",
                "class": """class {name}({parent}):
    \"\"\"{docstring}\"\"\"
    
    def __init__(self{init_params}):
        {init_body}""",
                "api_endpoint": """@app.{method}("/{endpoint}")
async def {function_name}({params}):
    \"\"\"{docstring}\"\"\"
    try:
        {body}
        return {return_statement}
    except Exception as e:
        return {{"error": str(e)}}"""
            },
            "javascript": {
                "function": """function {name}({params}) {{
    // {docstring}
    {body}
    return {return_value};
}}""",
                "react_component": """import React from 'react';

const {name} = ({props}) => {{
    {body}
    
    return (
        {jsx}
    );
}};

export default {name};"""
            }
        }
        
        # Code analysis patterns
        self.code_patterns = {
            "todo_comments": r"#\s*(TODO|FIXME|HACK|NOTE).*",
            "unused_imports": r"^import\s+\w+.*$",
            "long_functions": r"def\s+\w+.*:",
            "duplicate_code": r".*",
            "security_issues": [
                r"eval\(",
                r"exec\(",
                r"subprocess\.call\(",
                r"os\.system\("
            ]
        }
    
    async def initialize(self):
        """Initialize the Cursor-like editor"""
        logger.info("Initializing Cursor-like Code Editor...")
        
        # Initialize background processing
        asyncio.create_task(self._background_code_analysis())
        asyncio.create_task(self._intelligent_suggestions())
        
        logger.info("✅ Cursor-like Code Editor initialized")
    
    async def ai_code_completion(self, file_path: str, code_context: str, cursor_position: int) -> Dict[str, Any]:
        """
        AI-powered code completion similar to Cursor.so
        """
        try:
            # Analyze current context
            context_analysis = await self._analyze_code_context(file_path, code_context, cursor_position)
            
            # Generate completions
            completions = await self._generate_intelligent_completions(context_analysis)
            
            # Rank and filter completions
            ranked_completions = await self._rank_completions(completions, context_analysis)
            
            return {
                "success": True,
                "completions": ranked_completions,
                "context": context_analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AI code completion failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "completions": []
            }
    
    async def _analyze_code_context(self, file_path: str, code_context: str, cursor_position: int) -> Dict[str, Any]:
        """Analyze the current code context"""
        try:
            # Get file extension and language
            file_ext = Path(file_path).suffix.lower()
            language = self._detect_language(file_ext)
            
            # Parse code structure
            code_structure = await self._parse_code_structure(code_context, language)
            
            # Find current scope
            current_scope = self._find_current_scope(code_context, cursor_position)
            
            # Get relevant imports and dependencies
            imports = self._extract_imports(code_context, language)
            
            # Analyze surrounding context
            before_cursor = code_context[:cursor_position]
            after_cursor = code_context[cursor_position:]
            current_line = self._get_current_line(code_context, cursor_position)
            
            return {
                "file_path": file_path,
                "language": language,
                "cursor_position": cursor_position,
                "current_line": current_line,
                "current_scope": current_scope,
                "code_structure": code_structure,
                "imports": imports,
                "before_cursor": before_cursor[-200:],  # Last 200 chars
                "after_cursor": after_cursor[:200],     # Next 200 chars
                "indent_level": self._get_indent_level(current_line)
            }
            
        except Exception as e:
            logger.warning(f"Context analysis failed: {e}")
            return {"error": str(e)}
    
    def _detect_language(self, file_ext: str) -> str:
        """Detect programming language from file extension"""
        language_map = {
            ".py": "python",
            ".js": "javascript", 
            ".ts": "typescript",
            ".jsx": "react",
            ".tsx": "react",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".go": "go",
            ".rs": "rust",
            ".php": "php",
            ".rb": "ruby",
            ".swift": "swift",
            ".kt": "kotlin"
        }
        return language_map.get(file_ext, "text")
    
    async def _parse_code_structure(self, code: str, language: str) -> Dict[str, Any]:
        """Parse code structure for intelligent completion"""
        structure = {
            "functions": [],
            "classes": [],
            "variables": [],
            "imports": []
        }
        
        try:
            if language == "python":
                structure = await self._parse_python_structure(code)
            elif language in ["javascript", "typescript"]:
                structure = await self._parse_js_structure(code)
            
        except Exception as e:
            logger.warning(f"Code structure parsing failed: {e}")
        
        return structure
    
    async def _parse_python_structure(self, code: str) -> Dict[str, Any]:
        """Parse Python code structure"""
        structure = {
            "functions": [],
            "classes": [],
            "variables": [],
            "imports": []
        }
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    structure["functions"].append({
                        "name": node.name,
                        "args": [arg.arg for arg in node.args.args],
                        "line": node.lineno,
                        "docstring": ast.get_docstring(node)
                    })
                elif isinstance(node, ast.ClassDef):
                    structure["classes"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        "docstring": ast.get_docstring(node)
                    })
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        structure["imports"].append({
                            "name": alias.name,
                            "alias": alias.asname,
                            "type": "import"
                        })
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        structure["imports"].append({
                            "module": node.module,
                            "name": alias.name,
                            "alias": alias.asname,
                            "type": "from_import"
                        })
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            structure["variables"].append({
                                "name": target.id,
                                "line": node.lineno,
                                "type": "assignment"
                            })
                            
        except Exception as e:
            logger.warning(f"Python AST parsing failed: {e}")
        
        return structure
    
    async def _parse_js_structure(self, code: str) -> Dict[str, Any]:
        """Parse JavaScript/TypeScript code structure (simplified)"""
        structure = {
            "functions": [],
            "classes": [],
            "variables": [],
            "imports": []
        }
        
        try:
            # Simple regex-based parsing for JavaScript
            function_pattern = r"(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s+)?\(|(\w+)\s*:\s*(?:async\s+)?\()"
            class_pattern = r"class\s+(\w+)"
            import_pattern = r"import\s+.*?from\s+['\"]([^'\"]+)['\"]"
            variable_pattern = r"(?:const|let|var)\s+(\w+)"
            
            # Find functions
            for match in re.finditer(function_pattern, code):
                func_name = match.group(1) or match.group(2) or match.group(3)
                if func_name:
                    structure["functions"].append({
                        "name": func_name,
                        "line": code[:match.start()].count('\n') + 1
                    })
            
            # Find classes
            for match in re.finditer(class_pattern, code):
                structure["classes"].append({
                    "name": match.group(1),
                    "line": code[:match.start()].count('\n') + 1
                })
            
            # Find imports
            for match in re.finditer(import_pattern, code):
                structure["imports"].append({
                    "module": match.group(1),
                    "type": "es6_import"
                })
            
            # Find variables
            for match in re.finditer(variable_pattern, code):
                structure["variables"].append({
                    "name": match.group(1),
                    "line": code[:match.start()].count('\n') + 1
                })
                
        except Exception as e:
            logger.warning(f"JavaScript parsing failed: {e}")
        
        return structure
    
    def _find_current_scope(self, code: str, cursor_position: int) -> Dict[str, Any]:
        """Find the current scope at cursor position"""
        lines_before = code[:cursor_position].split('\n')
        current_line_num = len(lines_before)
        
        # Find enclosing function or class
        scope = {"type": "global", "name": None, "indent": 0}
        
        for i, line in enumerate(lines_before):
            stripped = line.strip()
            if stripped.startswith('def ') or stripped.startswith('class '):
                indent = len(line) - len(line.lstrip())
                if indent >= scope["indent"]:
                    scope_type = "function" if stripped.startswith('def ') else "class"
                    name = stripped.split()[1].split('(')[0].split(':')[0]
                    scope = {"type": scope_type, "name": name, "indent": indent, "line": i + 1}
        
        return scope
    
    def _extract_imports(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Extract imports from code"""
        imports = []
        
        if language == "python":
            import_pattern = r"^(?:import\s+(.+)|from\s+(.+)\s+import\s+(.+))$"
            for line in code.split('\n'):
                match = re.match(import_pattern, line.strip())
                if match:
                    if match.group(1):  # import module
                        imports.append({"type": "import", "module": match.group(1)})
                    elif match.group(2) and match.group(3):  # from module import item
                        imports.append({
                            "type": "from_import",
                            "module": match.group(2),
                            "items": match.group(3)
                        })
        
        return imports
    
    def _get_current_line(self, code: str, cursor_position: int) -> str:
        """Get the current line at cursor position"""
        lines = code[:cursor_position].split('\n')
        return lines[-1] if lines else ""
    
    def _get_indent_level(self, line: str) -> int:
        """Get indentation level of a line"""
        return len(line) - len(line.lstrip())
    
    async def _generate_intelligent_completions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate intelligent code completions"""
        completions = []
        
        try:
            language = context.get("language", "python")
            current_line = context.get("current_line", "")
            current_scope = context.get("current_scope", {})
            code_structure = context.get("code_structure", {})
            
            # Template-based completions
            template_completions = await self._generate_template_completions(context)
            completions.extend(template_completions)
            
            # Context-aware completions
            context_completions = await self._generate_context_completions(context)
            completions.extend(context_completions)
            
            # AI-powered completions
            if self.model_manager:
                ai_completions = await self._generate_ai_completions(context)
                completions.extend(ai_completions)
            
        except Exception as e:
            logger.warning(f"Completion generation failed: {e}")
        
        return completions
    
    async def _generate_template_completions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate template-based completions"""
        completions = []
        language = context.get("language", "python")
        current_line = context.get("current_line", "").strip()
        
        templates = self.code_templates.get(language, {})
        
        for template_name, template in templates.items():
            if self._should_suggest_template(current_line, template_name):
                completion = {
                    "type": "template",
                    "text": template,
                    "label": f"{template_name} template",
                    "detail": f"Generate {template_name}",
                    "kind": "snippet",
                    "priority": 8
                }
                completions.append(completion)
        
        return completions
    
    def _should_suggest_template(self, current_line: str, template_name: str) -> bool:
        """Determine if a template should be suggested"""
        triggers = {
            "function": ["def", "function"],
            "class": ["class"],
            "api_endpoint": ["@app", "endpoint", "route"],
            "react_component": ["component", "const"]
        }
        
        template_triggers = triggers.get(template_name, [])
        return any(trigger in current_line.lower() for trigger in template_triggers)
    
    async def _generate_context_completions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate context-aware completions"""
        completions = []
        current_line = context.get("current_line", "")
        code_structure = context.get("code_structure", {})
        
        # Variable completions
        for var in code_structure.get("variables", []):
            if var["name"].startswith(current_line.split()[-1] if current_line.split() else ""):
                completions.append({
                    "type": "variable",
                    "text": var["name"],
                    "label": var["name"],
                    "detail": f"Variable (line {var.get('line', 'unknown')})",
                    "kind": "variable",
                    "priority": 9
                })
        
        # Function completions
        for func in code_structure.get("functions", []):
            if func["name"].startswith(current_line.split()[-1] if current_line.split() else ""):
                args_str = ", ".join(func.get("args", []))
                completions.append({
                    "type": "function",
                    "text": f"{func['name']}({args_str})",
                    "label": f"{func['name']}()",
                    "detail": f"Function - {func.get('docstring', 'No description')}",
                    "kind": "function",
                    "priority": 9
                })
        
        return completions
    
    async def _generate_ai_completions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate AI-powered completions using model manager"""
        completions = []
        
        try:
            prompt = f"""
            Generate intelligent code completions for this context:
            
            Language: {context.get('language')}
            Current line: {context.get('current_line')}
            Current scope: {context.get('current_scope', {}).get('name', 'global')}
            Before cursor: {context.get('before_cursor', '')}
            
            Provide 3-5 relevant code completions as JSON:
            [
                {{
                    "text": "completion code",
                    "label": "display label", 
                    "detail": "description",
                    "priority": 1-10
                }}
            ]
            """
            
            response = await self.model_manager.generate_response(
                prompt,
                task_type="coding",
                max_tokens=500
            )
            
            # Parse AI response (simplified)
            try:
                import json
                ai_completions = json.loads(response)
                for completion in ai_completions:
                    completion["type"] = "ai"
                    completion["kind"] = "ai_suggestion"
                    completions.append(completion)
            except:
                # Fallback if JSON parsing fails
                completions.append({
                    "type": "ai",
                    "text": response[:100],
                    "label": "AI suggestion",
                    "detail": "AI-generated completion",
                    "kind": "ai_suggestion",
                    "priority": 7
                })
                
        except Exception as e:
            logger.warning(f"AI completion generation failed: {e}")
        
        return completions
    
    async def _rank_completions(self, completions: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Rank and filter completions"""
        # Sort by priority (higher = better)
        ranked = sorted(completions, key=lambda x: x.get("priority", 5), reverse=True)
        
        # Remove duplicates
        seen = set()
        unique_completions = []
        for completion in ranked:
            key = completion.get("text", "")
            if key not in seen:
                seen.add(key)
                unique_completions.append(completion)
        
        # Limit to top 10
        return unique_completions[:10]
    
    async def intelligent_refactoring(self, file_path: str, code: str, refactor_type: str) -> Dict[str, Any]:
        """
        Intelligent code refactoring
        """
        try:
            if refactor_type == "extract_function":
                return await self._extract_function_refactoring(code)
            elif refactor_type == "optimize_imports":
                return await self._optimize_imports_refactoring(code, file_path)
            elif refactor_type == "add_type_hints":
                return await self._add_type_hints_refactoring(code)
            elif refactor_type == "improve_naming":
                return await self._improve_naming_refactoring(code)
            else:
                return {"success": False, "error": "Unknown refactoring type"}
                
        except Exception as e:
            logger.error(f"Refactoring failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _extract_function_refactoring(self, code: str) -> Dict[str, Any]:
        """Extract function refactoring"""
        # Analyze code for potential function extractions
        suggestions = []
        
        # Find repeated code blocks
        lines = code.split('\n')
        for i in range(len(lines) - 3):
            block = '\n'.join(lines[i:i+3])
            if len(block.strip()) > 50:  # Minimum complexity
                suggestions.append({
                    "type": "extract_function",
                    "start_line": i + 1,
                    "end_line": i + 3,
                    "suggested_name": f"extracted_function_{i+1}",
                    "code": block
                })
        
        return {
            "success": True,
            "refactoring_type": "extract_function",
            "suggestions": suggestions[:5]  # Limit suggestions
        }
    
    async def _optimize_imports_refactoring(self, code: str, file_path: str) -> Dict[str, Any]:
        """Optimize imports refactoring"""
        imports = self._extract_imports(code, "python")
        used_imports = set()
        
        # Simple usage detection
        for imp in imports:
            module_name = imp.get("module", imp.get("name", ""))
            if module_name and module_name in code:
                used_imports.add(module_name)
        
        # Find unused imports
        unused = [imp for imp in imports if imp.get("module", imp.get("name", "")) not in used_imports]
        
        return {
            "success": True,
            "refactoring_type": "optimize_imports",
            "unused_imports": unused,
            "suggestions": [f"Remove unused import: {imp}" for imp in unused]
        }
    
    async def _add_type_hints_refactoring(self, code: str) -> Dict[str, Any]:
        """Add type hints refactoring"""
        suggestions = []
        
        # Find functions without type hints
        function_pattern = r"def\s+(\w+)\s*\(([^)]*)\)\s*:"
        for match in re.finditer(function_pattern, code):
            func_name = match.group(1)
            params = match.group(2)
            
            if "->" not in match.group(0):  # No return type hint
                suggestions.append({
                    "type": "add_return_type",
                    "function": func_name,
                    "suggestion": f"Add return type hint to {func_name}"
                })
            
            if ":" not in params and params.strip():  # No parameter type hints
                suggestions.append({
                    "type": "add_param_types",
                    "function": func_name,
                    "suggestion": f"Add parameter type hints to {func_name}"
                })
        
        return {
            "success": True,
            "refactoring_type": "add_type_hints", 
            "suggestions": suggestions
        }
    
    async def _improve_naming_refactoring(self, code: str) -> Dict[str, Any]:
        """Improve variable/function naming"""
        suggestions = []
        
        # Find potential naming improvements
        poor_names = ["x", "y", "z", "temp", "tmp", "data", "item", "val", "var"]
        variable_pattern = r"(\w+)\s*="
        
        for match in re.finditer(variable_pattern, code):
            var_name = match.group(1)
            if var_name.lower() in poor_names:
                suggestions.append({
                    "type": "improve_variable_name",
                    "current": var_name,
                    "suggestion": f"Consider renaming '{var_name}' to something more descriptive"
                })
        
        return {
            "success": True,
            "refactoring_type": "improve_naming",
            "suggestions": suggestions[:10]  # Limit suggestions
        }
    
    async def _background_code_analysis(self):
        """Background code analysis agent"""
        while True:
            try:
                await asyncio.sleep(30)  # Run every 30 seconds
                
                # Analyze open files for issues
                for file_path, context in self.file_contexts.items():
                    await self._analyze_file_for_issues(file_path, context)
                
            except Exception as e:
                logger.error(f"Background analysis error: {e}")
                await asyncio.sleep(60)
    
    async def _analyze_file_for_issues(self, file_path: str, context: Dict[str, Any]):
        """Analyze file for potential issues"""
        try:
            code = context.get("content", "")
            issues = []
            
            # Check for TODO comments
            for i, line in enumerate(code.split('\n')):
                if re.search(self.code_patterns["todo_comments"], line):
                    issues.append({
                        "type": "todo",
                        "line": i + 1,
                        "message": line.strip(),
                        "severity": "info"
                    })
            
            # Check for security issues
            for pattern in self.code_patterns["security_issues"]:
                if re.search(pattern, code):
                    issues.append({
                        "type": "security",
                        "pattern": pattern,
                        "message": f"Potential security issue: {pattern}",
                        "severity": "warning"
                    })
            
            # Store issues for later display
            self.active_suggestions[file_path] = issues
            
        except Exception as e:
            logger.warning(f"File analysis failed for {file_path}: {e}")
    
    async def _intelligent_suggestions(self):
        """Generate intelligent suggestions in background"""
        while True:
            try:
                await asyncio.sleep(60)  # Run every minute
                
                # Generate suggestions for active files
                for file_path in self.file_contexts:
                    await self._generate_file_suggestions(file_path)
                
            except Exception as e:
                logger.error(f"Suggestion generation error: {e}")
                await asyncio.sleep(120)
    
    async def _generate_file_suggestions(self, file_path: str):
        """Generate suggestions for a specific file"""
        try:
            context = self.file_contexts.get(file_path, {})
            code = context.get("content", "")
            
            if not code:
                return
            
            # Generate refactoring suggestions
            refactoring_suggestions = await self.intelligent_refactoring(
                file_path, code, "extract_function"
            )
            
            # Store suggestions
            if file_path not in self.active_suggestions:
                self.active_suggestions[file_path] = []
            
            if refactoring_suggestions.get("success"):
                for suggestion in refactoring_suggestions.get("suggestions", []):
                    self.active_suggestions[file_path].append({
                        "type": "refactoring",
                        "data": suggestion,
                        "timestamp": datetime.now().isoformat()
                    })
            
        except Exception as e:
            logger.warning(f"Suggestion generation failed for {file_path}: {e}")
    
    def update_file_context(self, file_path: str, content: str):
        """Update file context for background analysis"""
        self.file_contexts[file_path] = {
            "content": content,
            "last_updated": datetime.now().isoformat()
        }
    
    def get_suggestions(self, file_path: str) -> List[Dict[str, Any]]:
        """Get active suggestions for a file"""
        return self.active_suggestions.get(file_path, [])
    
    def set_model_manager(self, model_manager):
        """Set model manager reference"""
        self.model_manager = model_manager
    
    def set_agent_manager(self, agent_manager):
        """Set agent manager reference"""
        self.agent_manager = agent_manager