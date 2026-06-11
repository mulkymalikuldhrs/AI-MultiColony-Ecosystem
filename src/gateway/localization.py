"""
Localization Manager - Multi-language support for the API gateway.
Port of Crucix localization patterns to Python with Pydantic v2.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger("ecosystem.gateway.localization")


class LocaleConfig(BaseModel):
    """Configuration for a locale."""
    code: str  # e.g., "en", "id", "zh"
    name: str  # e.g., "English", "Bahasa Indonesia", "Chinese"
    default: bool = False


class LocalizationManager:
    """Multi-language support for the API gateway.

    Features:
    - Multiple locale support
    - String key lookups with fallback to default locale
    - Dynamic locale registration
    - JSON-based string files
    """

    DEFAULT_LOCALE = "en"

    def __init__(self, default_locale: str = "en") -> None:
        self.default_locale = default_locale
        self.locales: dict[str, LocaleConfig] = {}
        self.strings: dict[str, dict[str, str]] = {}  # locale -> key -> value

        # Register default locale
        self.register_locale(LocaleConfig(
            code=default_locale, name="English", default=True
        ))

    def register_locale(self, config: LocaleConfig) -> None:
        """Register a locale."""
        self.locales[config.code] = config
        if config.code not in self.strings:
            self.strings[config.code] = {}
        logger.info("Registered locale: %s (%s)", config.code, config.name)

    def add_strings(self, locale: str, strings: dict[str, str]) -> None:
        """Add string translations for a locale.

        Args:
            locale: Locale code (e.g., "en", "id")
            strings: Dict mapping string keys to translations
        """
        if locale not in self.strings:
            self.strings[locale] = {}
        self.strings[locale].update(strings)

    def get(self, key: str, locale: str | None = None, **kwargs) -> str:
        """Get a localized string.

        Args:
            key: String key
            locale: Target locale (defaults to default_locale)
            **kwargs: Format parameters for string interpolation

        Returns:
            Localized string, with fallback to default locale if key not found.
        """
        target_locale = locale or self.default_locale

        # Try target locale first
        value = self.strings.get(target_locale, {}).get(key)
        if value is not None:
            if kwargs:
                try:
                    return value.format(**kwargs)
                except (KeyError, IndexError):
                    return value
            return value

        # Fallback to default locale
        if target_locale != self.default_locale:
            value = self.strings.get(self.default_locale, {}).get(key)
            if value is not None:
                if kwargs:
                    try:
                        return value.format(**kwargs)
                    except (KeyError, IndexError):
                        return value
                return value

        # Return key itself as last resort
        return key

    def get_available_locales(self) -> list[LocaleConfig]:
        """Get list of available locales."""
        return list(self.locales.values())

    def load_from_dict(self, data: dict[str, dict[str, str]]) -> None:
        """Load translations from a nested dict {locale: {key: value}}."""
        for locale, strings in data.items():
            if locale not in self.locales:
                self.register_locale(LocaleConfig(code=locale, name=locale))
            self.add_strings(locale, strings)

    def get_status(self) -> dict:
        """Get localization status."""
        return {
            "default_locale": self.default_locale,
            "available_locales": [lc.model_dump() for lc in self.locales.values()],
            "string_counts": {locale: len(strings) for locale, strings in self.strings.items()},
        }
