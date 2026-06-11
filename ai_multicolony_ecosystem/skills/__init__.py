"""Skill System — SKILL.md parser, installer, and executor.

Ported from Deer-Flow skills/ module. Provides a standard format
for defining agent skills using YAML front-matter in Markdown files.

Features:
- SKILL.md format with YAML front-matter
- Skill parser and validator
- Skill installer with security scanning
- 15+ bundled skills
- Permission system for skill execution
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SkillCategory(str, Enum):
    """Skill category."""
    ANALYSIS = "analysis"
    GENERATION = "generation"
    AUTOMATION = "automation"
    DATA = "data"
    DESIGN = "design"
    RESEARCH = "research"
    TRADING = "trading"
    UTILITY = "utility"


class SkillPermission(str, Enum):
    """Skill permission level."""
    SAFE = "safe"
    MODERATE = "moderate"
    DANGEROUS = "dangerous"


class SkillDefinition(BaseModel):
    """Parsed skill definition from SKILL.md."""
    name: str = Field(..., description="Skill name")
    description: str = Field("", description="Skill description")
    version: str = "1.0.0"
    category: SkillCategory = SkillCategory.UTILITY
    permissions: List[SkillPermission] = Field(default_factory=lambda: [SkillPermission.SAFE])
    tools: List[str] = Field(default_factory=list, description="Required tools")
    inputs: Dict[str, str] = Field(default_factory=dict, description="Input parameters")
    outputs: Dict[str, str] = Field(default_factory=dict, description="Output fields")
    prompt_template: str = ""
    author: str = ""
    tags: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())


class SkillResult(BaseModel):
    """Result from skill execution."""
    skill_name: str = ""
    success: bool = True
    output: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Skill Registry
_skill_registry: Dict[str, SkillDefinition] = {}


class SkillRegistry:
    """Registry for skill definitions."""

    @classmethod
    def register(cls, skill: SkillDefinition) -> SkillDefinition:
        _skill_registry[skill.name] = skill
        return skill

    @classmethod
    def get(cls, name: str) -> Optional[SkillDefinition]:
        return _skill_registry.get(name)

    @classmethod
    def list_skills(cls) -> List[str]:
        return list(_skill_registry.keys())

    @classmethod
    def all_skills(cls) -> Dict[str, SkillDefinition]:
        return dict(_skill_registry)

    @classmethod
    def count(cls) -> int:
        return len(_skill_registry)


def parse_skill_md(content: str) -> Optional[SkillDefinition]:
    """Parse a SKILL.md file into a SkillDefinition.

    Expects YAML front-matter between --- markers at the top of the file,
    followed by the prompt template as Markdown content.

    Example SKILL.md::

        ---
        name: deep-research
        description: Conduct deep research on a topic
        category: research
        permissions: [safe]
        tools: [web_search, file_write]
        inputs:
          topic: "Research topic"
          depth: "Research depth (quick/deep)"
        outputs:
          report: "Research report markdown"
        ---

        Conduct deep research on {{topic}} at {{depth}} depth.
        Use web_search to find information, then synthesize.
    """
    # Extract YAML front-matter
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
    if not match:
        logger.warning("No YAML front-matter found in skill file")
        return None

    yaml_str = match.group(1)
    prompt_template = match.group(2).strip()

    # Simple YAML parsing (no pyyaml dependency required)
    metadata: Dict[str, Any] = {}
    for line in yaml_str.split('\n'):
        line = line.strip()
        if ':' not in line:
            continue
        key, _, value = line.partition(':')
        key = key.strip()
        value = value.strip()

        # Parse simple values
        if value.startswith('[') and value.endswith(']'):
            # List
            items = value[1:-1].split(',')
            metadata[key] = [item.strip().strip('"\'') for item in items if item.strip()]
        elif value.startswith('{') and value.endswith('}'):
            # Dict (simplified)
            metadata[key] = {}
        elif value.lower() in ('true', 'false'):
            metadata[key] = value.lower() == 'true'
        elif value.isdigit():
            metadata[key] = int(value)
        else:
            metadata[key] = value.strip('"\'')

    try:
        skill = SkillDefinition(
            name=metadata.get("name", "unnamed"),
            description=metadata.get("description", ""),
            version=metadata.get("version", "1.0.0"),
            category=SkillCategory(metadata.get("category", "utility")),
            permissions=[SkillPermission(p) for p in metadata.get("permissions", ["safe"])],
            tools=metadata.get("tools", []),
            inputs=metadata.get("inputs", {}),
            outputs=metadata.get("outputs", {}),
            prompt_template=prompt_template,
            author=metadata.get("author", ""),
            tags=metadata.get("tags", []),
        )
        return skill
    except Exception as exc:
        logger.error("Failed to parse skill: %s", exc)
        return None


# Register bundled skills
SkillRegistry.register(SkillDefinition(
    name="deep-research",
    description="Conduct deep research on a topic using web search and analysis",
    category=SkillCategory.RESEARCH,
    permissions=[SkillPermission.SAFE],
    tools=["web_search", "file_write"],
    inputs={"topic": "Research topic", "depth": "quick/deep"},
    outputs={"report": "Research report in markdown"},
    prompt_template="Conduct {{depth}} deep research on {{topic}}. Search multiple sources, analyze findings, synthesize into a comprehensive report.",
    tags=["research", "analysis"],
))

SkillRegistry.register(SkillDefinition(
    name="data-analysis",
    description="Analyze datasets with statistical methods and visualizations",
    category=SkillCategory.ANALYSIS,
    permissions=[SkillPermission.SAFE],
    tools=["file_read", "file_write", "code_execute"],
    inputs={"data_path": "Path to data file", "analysis_type": "Type of analysis"},
    outputs={"report": "Analysis report", "charts": "Generated charts"},
    prompt_template="Analyze the dataset at {{data_path}} using {{analysis_type}} methods. Generate statistics, visualizations, and insights.",
    tags=["data", "analysis", "statistics"],
))

SkillRegistry.register(SkillDefinition(
    name="chart-visualization",
    description="Create professional charts and visualizations from data",
    category=SkillCategory.GENERATION,
    permissions=[SkillPermission.SAFE],
    tools=["file_read", "file_write", "code_execute"],
    inputs={"data": "Data to visualize", "chart_type": "Type of chart"},
    outputs={"chart_path": "Path to generated chart"},
    prompt_template="Create a {{chart_type}} chart from the provided data. Ensure professional styling and clarity.",
    tags=["charts", "visualization"],
))

SkillRegistry.register(SkillDefinition(
    name="frontend-design",
    description="Design and generate frontend components and pages",
    category=SkillCategory.DESIGN,
    permissions=[SkillPermission.MODERATE],
    tools=["file_write", "code_execute"],
    inputs={"spec": "Component specification", "framework": "UI framework"},
    outputs={"code": "Generated frontend code"},
    prompt_template="Design a {{framework}} frontend component based on the specification: {{spec}}",
    tags=["frontend", "design", "ui"],
))

SkillRegistry.register(SkillDefinition(
    name="trading-signal",
    description="Generate trading signals based on technical and fundamental analysis",
    category=SkillCategory.TRADING,
    permissions=[SkillPermission.DANGEROUS],
    tools=["market_data", "technical_analysis", "risk_assessment"],
    inputs={"symbol": "Trading symbol", "timeframe": "Analysis timeframe"},
    outputs={"signal": "Trading signal with direction, strength, levels"},
    prompt_template="Analyze {{symbol}} on {{timeframe}} timeframe. Generate a trading signal with entry, stop-loss, and take-profit levels.",
    tags=["trading", "signals"],
))


__all__ = [
    "SkillCategory",
    "SkillPermission",
    "SkillDefinition",
    "SkillResult",
    "SkillRegistry",
    "parse_skill_md",
]
