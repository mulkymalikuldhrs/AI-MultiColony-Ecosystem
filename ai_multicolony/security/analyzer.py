"""Security analysis engine.

Provides LLM-based, pattern-based, and rule-based security analysis
for code, commands, and agent actions.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from ai_multicolony.config.logging_config import get_logger

logger = get_logger(__name__)


class Severity(str, Enum):
    """Security finding severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AnalysisMode(str, Enum):
    """Analysis modes."""

    PATTERN = "pattern"
    RULE = "rule"
    LLM = "llm"
    HYBRID = "hybrid"


@dataclass
class SecurityFinding:
    """A security finding from analysis."""

    title: str
    description: str
    severity: Severity = Severity.MEDIUM
    category: str = "general"
    location: str = ""
    remediation: str = ""
    confidence: float = 1.0
    source: str = "pattern"  # pattern, rule, llm
    metadata: dict[str, Any] = field(default_factory=dict)


class SecurityAnalyzer:
    """Security analysis engine with multiple analysis modes.

    Features:
    - Pattern-based analysis (regex)
    - Rule-based analysis (custom rules)
    - LLM-based analysis (using configured LLM provider)
    - Hybrid analysis (combining all modes)
    - Code security analysis
    - Command injection detection
    - Path traversal detection
    - XSS detection
    - Secret detection
    - Custom rule support
    """

    def __init__(self, llm_provider: Optional[Any] = None) -> None:
        self._llm_provider = llm_provider
        self._patterns = self._default_patterns()
        self._rules: list[dict[str, Any]] = []
        self._custom_checks: list[Any] = []

    def _default_patterns(self) -> dict[str, list[dict[str, Any]]]:
        """Default pattern-based detection rules."""
        return {
            "command_injection": [
                {"pattern": r"eval\s*\(", "severity": Severity.HIGH, "description": "Use of eval() can lead to code injection"},
                {"pattern": r"exec\s*\(", "severity": Severity.HIGH, "description": "Use of exec() can lead to code injection"},
                {"pattern": r"subprocess\.call\s*\(.*shell\s*=\s*True", "severity": Severity.HIGH, "description": "Shell=True in subprocess can lead to command injection"},
                {"pattern": r"os\.system\s*\(", "severity": Severity.HIGH, "description": "os.system() can lead to command injection"},
                {"pattern": r"os\.popen\s*\(", "severity": Severity.HIGH, "description": "os.popen() can lead to command injection"},
            ],
            "path_traversal": [
                {"pattern": r"\.\./", "severity": Severity.HIGH, "description": "Path traversal pattern detected"},
                {"pattern": r"\.\.\\", "severity": Severity.HIGH, "description": "Windows path traversal pattern detected"},
                {"pattern": r"open\s*\(.*\+\s*", "severity": Severity.MEDIUM, "description": "Dynamic file path construction"},
            ],
            "xss": [
                {"pattern": r"innerHTML\s*=", "severity": Severity.MEDIUM, "description": "Direct innerHTML assignment can lead to XSS"},
                {"pattern": r"document\.write\s*\(", "severity": Severity.MEDIUM, "description": "document.write() can lead to XSS"},
                {"pattern": r"v-html\s*=", "severity": Severity.MEDIUM, "description": "Vue v-html directive can lead to XSS"},
            ],
            "secrets": [
                {"pattern": r"(?i)password\s*=\s*['\"][^'\"]+['\"]", "severity": Severity.CRITICAL, "description": "Hardcoded password detected"},
                {"pattern": r"(?i)api_key\s*=\s*['\"][^'\"]+['\"]", "severity": Severity.CRITICAL, "description": "Hardcoded API key detected"},
                {"pattern": r"(?i)secret\s*=\s*['\"][^'\"]+['\"]", "severity": Severity.CRITICAL, "description": "Hardcoded secret detected"},
                {"pattern": r"(?i)token\s*=\s*['\"][a-zA-Z0-9]{20,}['\"]", "severity": Severity.HIGH, "description": "Possible hardcoded token detected"},
            ],
            "unsafe_deserialization": [
                {"pattern": r"pickle\.loads?\s*\(", "severity": Severity.HIGH, "description": "Pickle deserialization can execute arbitrary code"},
                {"pattern": r"yaml\.load\s*\([^)]*\)(?!.*Loader)", "severity": Severity.HIGH, "description": "Unsafe YAML loading without Loader"},
            ],
            "sql_injection": [
                {"pattern": r"execute\s*\(\s*[\"'].*%s.*[\"']\s*%", "severity": Severity.HIGH, "description": "Potential SQL injection via string formatting"},
                {"pattern": r"raw\s*\(\s*[\"'].*\+.*[\"']", "severity": Severity.HIGH, "description": "Potential SQL injection via string concatenation"},
            ],
        }

    def add_rule(self, rule: dict[str, Any]) -> None:
        """Add a custom security rule.

        Args:
            rule: Rule dictionary with 'name', 'check' (callable), 'severity', 'description'.
        """
        self._rules.append(rule)

    def add_custom_check(self, check_fn: Any) -> None:
        """Add a custom check function.

        Args:
            check_fn: Callable that takes (code, language) and returns list[SecurityFinding].
        """
        self._custom_checks.append(check_fn)

    def analyze_code(
        self,
        code: str,
        language: str = "python",
        mode: AnalysisMode = AnalysisMode.PATTERN,
    ) -> list[SecurityFinding]:
        """Analyze code for security issues.

        Args:
            code: The code to analyze.
            language: Programming language.
            mode: Analysis mode.

        Returns:
            List of security findings.
        """
        findings: list[SecurityFinding] = []

        if mode in (AnalysisMode.PATTERN, AnalysisMode.HYBRID):
            findings.extend(self._pattern_analysis(code, language))

        if mode in (AnalysisMode.RULE, AnalysisMode.HYBRID):
            findings.extend(self._rule_analysis(code, language))

        if mode in (AnalysisMode.LLM, AnalysisMode.HYBRID):
            # LLM analysis is async, skip in sync mode
            pass

        # Custom checks
        for check_fn in self._custom_checks:
            try:
                custom_findings = check_fn(code, language)
                if custom_findings:
                    findings.extend(custom_findings)
            except Exception as e:
                logger.warning("custom_check_error", error=str(e))

        return findings

    async def analyze_code_async(
        self,
        code: str,
        language: str = "python",
        mode: AnalysisMode = AnalysisMode.HYBRID,
    ) -> list[SecurityFinding]:
        """Async version of code analysis with LLM support.

        Args:
            code: The code to analyze.
            language: Programming language.
            mode: Analysis mode.

        Returns:
            List of security findings.
        """
        findings = self.analyze_code(code, language, mode)

        if mode in (AnalysisMode.LLM, AnalysisMode.HYBRID) and self._llm_provider:
            llm_findings = await self._llm_analysis(code, language)
            findings.extend(llm_findings)

        # Deduplicate findings
        seen = set()
        unique_findings = []
        for f in findings:
            key = (f.title, f.location, f.category)
            if key not in seen:
                seen.add(key)
                unique_findings.append(f)

        return unique_findings

    def analyze_command(self, command: str) -> list[SecurityFinding]:
        """Analyze a shell command for security issues.

        Args:
            command: The shell command.

        Returns:
            List of security findings.
        """
        findings: list[SecurityFinding] = []

        dangerous_patterns = [
            (r"rm\s+-rf\s+/", Severity.CRITICAL, "Recursive force delete from root"),
            (r"mkfs", Severity.CRITICAL, "Filesystem format command"),
            (r"dd\s+if=", Severity.HIGH, "Disk dump command"),
            (r":\(\)\{\s*:\|:\s*&\s*\}", Severity.CRITICAL, "Fork bomb detected"),
            (r"curl\s+.*\|\s*sh", Severity.CRITICAL, "Piping curl output to shell"),
            (r"wget\s+.*\|\s*sh", Severity.CRITICAL, "Piping wget output to shell"),
            (r"chmod\s+777", Severity.MEDIUM, "Overly permissive file mode"),
            (r"sudo\s+rm", Severity.HIGH, "Sudo remove command"),
            (r">\s*/dev/sd", Severity.CRITICAL, "Direct write to block device"),
            (r"iptables\s+-F", Severity.HIGH, "Flush firewall rules"),
        ]

        for pattern, severity, description in dangerous_patterns:
            if re.search(pattern, command):
                findings.append(SecurityFinding(
                    title="Dangerous Command Detected",
                    description=description,
                    severity=severity,
                    category="dangerous_command",
                    remediation="Review and restrict this command",
                    source="pattern",
                ))

        return findings

    def _pattern_analysis(self, code: str, language: str) -> list[SecurityFinding]:
        """Pattern-based security analysis."""
        findings: list[SecurityFinding] = []

        for category, patterns in self._patterns.items():
            for pattern_info in patterns:
                matches = re.finditer(pattern_info["pattern"], code, re.MULTILINE)
                for match in matches:
                    finding = SecurityFinding(
                        title=f"{category.replace('_', ' ').title()} Detection",
                        description=pattern_info["description"],
                        severity=pattern_info["severity"],
                        category=category,
                        location=f"Line {code[:match.start()].count(chr(10)) + 1}",
                        remediation=self._get_remediation(category),
                        confidence=0.8,
                        source="pattern",
                        metadata={"matched_text": match.group(0)[:50]},
                    )
                    findings.append(finding)

        return findings

    def _rule_analysis(self, code: str, language: str) -> list[SecurityFinding]:
        """Rule-based security analysis."""
        findings: list[SecurityFinding] = []

        for rule in self._rules:
            try:
                check_fn = rule.get("check")
                if check_fn and callable(check_fn):
                    result = check_fn(code, language)
                    if result:
                        findings.extend(result)
            except Exception as e:
                logger.warning("rule_check_error", rule=rule.get("name"), error=str(e))

        return findings

    async def _llm_analysis(self, code: str, language: str) -> list[SecurityFinding]:
        """LLM-based security analysis."""
        if not self._llm_provider:
            return []

        try:
            # Truncate code if too long
            truncated = code[:2000] if len(code) > 2000 else code

            response = await self._llm_provider.chat(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a security code reviewer. Analyze the following code for security vulnerabilities. "
                            "Return a JSON array of findings, each with: title, description, severity (critical/high/medium/low), "
                            "category, and remediation. If no issues found, return empty array."
                        ),
                    },
                    {"role": "user", "content": f"```{language}\n{truncated}\n```"},
                ],
                max_tokens=1000,
            )

            import json
            content = response.content if hasattr(response, 'content') else str(response)

            # Try to parse JSON from response
            try:
                # Find JSON array in response
                start = content.find("[")
                end = content.rfind("]") + 1
                if start >= 0 and end > start:
                    parsed = json.loads(content[start:end])
                    findings = []
                    for item in parsed:
                        severity_str = item.get("severity", "medium").lower()
                        try:
                            severity = Severity(severity_str)
                        except ValueError:
                            severity = Severity.MEDIUM

                        findings.append(SecurityFinding(
                            title=item.get("title", "LLM Security Finding"),
                            description=item.get("description", ""),
                            severity=severity,
                            category=item.get("category", "llm_analysis"),
                            remediation=item.get("remediation", ""),
                            confidence=0.7,
                            source="llm",
                        ))
                    return findings
            except json.JSONDecodeError:
                pass

            return []
        except Exception as e:
            logger.warning("llm_analysis_error", error=str(e))
            return []

    def _get_remediation(self, category: str) -> str:
        """Get remediation advice for a category."""
        remediations = {
            "command_injection": "Use parameterized commands and avoid shell=True",
            "path_traversal": "Validate and sanitize file paths, use os.path.abspath",
            "xss": "Use textContent instead of innerHTML, sanitize user input",
            "secrets": "Use environment variables or secret management tools",
            "unsafe_deserialization": "Use safe serialization formats (JSON) or specify loaders",
            "sql_injection": "Use parameterized queries and ORM frameworks",
        }
        return remediations.get(category, "Review and address the security concern")
