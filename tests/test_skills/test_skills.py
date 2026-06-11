"""Tests for Skill System."""

import pytest

from ai_multicolony_ecosystem.skills import (
    SkillCategory,
    SkillDefinition,
    SkillPermission,
    SkillRegistry,
    parse_skill_md,
)


# ======================================================================
# Skill Definition Tests
# ======================================================================

class TestSkillDefinition:
    def test_defaults(self):
        skill = SkillDefinition(name="test")
        assert skill.name == "test"
        assert skill.version == "1.0.0"
        assert skill.category == SkillCategory.UTILITY
        assert SkillPermission.SAFE in skill.permissions

    def test_custom(self):
        skill = SkillDefinition(
            name="deep-research",
            description="Research skill",
            category=SkillCategory.RESEARCH,
            permissions=[SkillPermission.SAFE, SkillPermission.MODERATE],
            tools=["web_search", "file_write"],
            tags=["research", "analysis"],
        )
        assert skill.category == SkillCategory.RESEARCH
        assert len(skill.tools) == 2
        assert "research" in skill.tags


class TestSkillCategory:
    def test_values(self):
        assert SkillCategory.ANALYSIS == "analysis"
        assert SkillCategory.RESEARCH == "research"
        assert SkillCategory.TRADING == "trading"
        assert SkillCategory.GENERATION == "generation"


class TestSkillPermission:
    def test_values(self):
        assert SkillPermission.SAFE == "safe"
        assert SkillPermission.MODERATE == "moderate"
        assert SkillPermission.DANGEROUS == "dangerous"


# ======================================================================
# Skill Registry Tests
# ======================================================================

class TestSkillRegistry:
    def test_list_skills(self):
        skills = SkillRegistry.list_skills()
        assert "deep-research" in skills
        assert "data-analysis" in skills
        assert "chart-visualization" in skills
        assert "frontend-design" in skills
        assert "trading-signal" in skills
        assert len(skills) >= 5

    def test_get_skill(self):
        skill = SkillRegistry.get("deep-research")
        assert skill is not None
        assert skill.name == "deep-research"
        assert skill.category == SkillCategory.RESEARCH

    def test_get_nonexistent(self):
        skill = SkillRegistry.get("nonexistent_skill")
        assert skill is None

    def test_count(self):
        assert SkillRegistry.count() >= 5

    def test_all_skills(self):
        all_skills = SkillRegistry.all_skills()
        assert isinstance(all_skills, dict)
        assert len(all_skills) >= 5


# ======================================================================
# SKILL.md Parser Tests
# ======================================================================

class TestParseSkillMd:
    def test_valid_skill_md(self):
        content = """---
name: test-skill
description: A test skill
category: analysis
permissions: [safe]
tools: [web_search]
---

Execute the test with {{param1}} and {{param2}}."""
        skill = parse_skill_md(content)
        assert skill is not None
        assert skill.name == "test-skill"
        assert skill.description == "A test skill"
        assert skill.category == SkillCategory.ANALYSIS
        assert skill.prompt_template.startswith("Execute the test")

    def test_no_frontmatter(self):
        content = "Just some markdown without frontmatter"
        skill = parse_skill_md(content)
        assert skill is None

    def test_minimal_skill_md(self):
        content = """---
name: minimal
---

Do something."""
        skill = parse_skill_md(content)
        assert skill is not None
        assert skill.name == "minimal"

    def test_with_tools(self):
        content = """---
name: tool-skill
tools: [search, code_execute, file_write]
---

Use tools."""
        skill = parse_skill_md(content)
        assert skill is not None
        assert len(skill.tools) == 3
        assert "search" in skill.tools

    def test_with_permissions(self):
        content = """---
name: perm-skill
permissions: [safe, moderate]
---

Be careful."""
        skill = parse_skill_md(content)
        assert skill is not None
        assert len(skill.permissions) == 2


# ======================================================================
# Bundled Skills Tests
# ======================================================================

class TestBundledSkills:
    def test_deep_research(self):
        skill = SkillRegistry.get("deep-research")
        assert skill is not None
        assert skill.category == SkillCategory.RESEARCH
        assert "web_search" in skill.tools

    def test_data_analysis(self):
        skill = SkillRegistry.get("data-analysis")
        assert skill is not None
        assert skill.category == SkillCategory.ANALYSIS

    def test_chart_visualization(self):
        skill = SkillRegistry.get("chart-visualization")
        assert skill is not None
        assert skill.category == SkillCategory.GENERATION

    def test_trading_signal(self):
        skill = SkillRegistry.get("trading-signal")
        assert skill is not None
        assert skill.category == SkillCategory.TRADING
        assert SkillPermission.DANGEROUS in skill.permissions

    def test_frontend_design(self):
        skill = SkillRegistry.get("frontend-design")
        assert skill is not None
        assert SkillPermission.MODERATE in skill.permissions
