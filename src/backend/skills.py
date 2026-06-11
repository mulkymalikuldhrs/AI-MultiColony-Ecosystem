"""
Skill Manager - Deer-flow style skill management.
Provides skill registration, validation, and lifecycle management.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger("ecosystem.backend.skills")


class SkillDefinition(BaseModel):
    """Definition of a skill."""
    name: str
    description: str
    version: str = "1.0.0"
    category: str = "general"
    author: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    enabled: bool = True
    config: dict = Field(default_factory=dict)


class SkillManager:
    """Skill registration, validation, and lifecycle management.

    Inspired by deer-flow's skill system with:
    - Skill registration and discovery
    - Validation of skill definitions
    - Enable/disable skills
    - Category-based organization
    """

    def __init__(self) -> None:
        self._skills: dict[str, SkillDefinition] = {}

    def register(self, skill: SkillDefinition) -> None:
        """Register a skill.

        Args:
            skill: SkillDefinition to register

        Raises:
            ValueError: If skill name already registered
        """
        if skill.name in self._skills:
            raise ValueError(f"Skill '{skill.name}' already registered")
        self._skills[skill.name] = skill
        logger.info("Registered skill: %s v%s", skill.name, skill.version)

    def unregister(self, name: str) -> bool:
        """Unregister a skill."""
        if name in self._skills:
            del self._skills[name]
            logger.info("Unregistered skill: %s", name)
            return True
        return False

    def get(self, name: str) -> Optional[SkillDefinition]:
        """Get a skill by name."""
        return self._skills.get(name)

    def list_skills(self, category: str | None = None, enabled_only: bool = False) -> list[SkillDefinition]:
        """List skills, optionally filtered by category and enabled status."""
        skills = list(self._skills.values())
        if category:
            skills = [s for s in skills if s.category == category]
        if enabled_only:
            skills = [s for s in skills if s.enabled]
        return skills

    def enable(self, name: str) -> bool:
        """Enable a skill."""
        skill = self._skills.get(name)
        if skill:
            skill.enabled = True
            return True
        return False

    def disable(self, name: str) -> bool:
        """Disable a skill."""
        skill = self._skills.get(name)
        if skill:
            skill.enabled = False
            return True
        return False

    def validate(self, skill: SkillDefinition) -> list[str]:
        """Validate a skill definition.

        Returns:
            List of validation error messages (empty if valid).
        """
        errors: list[str] = []

        if not skill.name or not skill.name.strip():
            errors.append("Skill name is required")
        if not skill.description or not skill.description.strip():
            errors.append("Skill description is required")
        if not skill.version:
            errors.append("Skill version is required")
        if skill.name in self._skills:
            errors.append(f"Skill '{skill.name}' already registered")

        # Check name format
        if skill.name and not all(c.isalnum() or c in "-_" for c in skill.name):
            errors.append("Skill name must contain only alphanumeric characters, hyphens, and underscores")

        return errors

    def get_categories(self) -> list[str]:
        """Get list of unique skill categories."""
        return sorted(set(s.category for s in self._skills.values()))

    def get_status(self) -> dict:
        """Get skill manager status."""
        return {
            "total_skills": len(self._skills),
            "enabled_skills": sum(1 for s in self._skills.values() if s.enabled),
            "categories": self.get_categories(),
        }
