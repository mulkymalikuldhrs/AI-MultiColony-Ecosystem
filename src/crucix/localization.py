"""
Crucix Localization Manager — i18n system with JSON locale files.

Port of lib/i18n.mjs to Python. Supports:
- Dot-path key lookup (e.g., "dashboard.title")
- Parameter interpolation with {param} syntax
- Fallback to default locale
- Loading from JSON files or dicts
- Locale caching

Integrates with the existing src/gateway/localization.py but adds
Crucix-specific features like deep nested key traversal and
the original file-based locale loading from contrib/crucix/locales/.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional

import structlog
from pydantic import BaseModel

logger = structlog.get_logger("crucix.localization")

# Pattern for {param} interpolation
_INTERPOLATE_RE = re.compile(r"\{(\w+)\}")


class LocaleInfo(BaseModel):
    """Metadata about a locale."""

    code: str
    name: str
    native_name: str


class LocalizationManager:
    """Crucix i18n/localization manager.

    Loads locale JSON files, caches them, and provides translation
    lookups with parameter interpolation and fallback.

    Args:
        locales_dir: Path to directory containing {lang}.json locale files.
        default_locale: Fallback locale code (default: "en").
    """

    DEFAULT_LOCALE = "en"
    SUPPORTED_LOCALES = ["en", "fr"]

    def __init__(
        self,
        locales_dir: str | Path | None = None,
        default_locale: str = "en",
    ) -> None:
        self.default_locale = default_locale[:2].lower()
        if self.default_locale not in self.SUPPORTED_LOCALES:
            self.default_locale = self.DEFAULT_LOCALE

        self.locales_dir = Path(locales_dir) if locales_dir else None
        self._cache: dict[str, dict[str, Any]] = {}
        self._current_locale: Optional[str] = None

        logger.info(
            "localization_initialized",
            default_locale=self.default_locale,
            locales_dir=str(self.locales_dir) if self.locales_dir else None,
        )

    # ── Locale Loading ─────────────────────────────────────────────────

    def _load_locale_file(self, lang: str) -> dict[str, Any]:
        """Load a locale JSON file from disk."""
        if lang in self._cache:
            return self._cache[lang]

        if not self.locales_dir:
            logger.warning("no_locales_dir", lang=lang)
            return self._load_builtin_fallback(lang)

        locale_path = self.locales_dir / f"{lang}.json"
        if not locale_path.exists():
            logger.warning("locale_file_not_found", path=str(locale_path), fallback=self.default_locale)
            if lang != self.default_locale:
                return self._load_locale_file(self.default_locale)
            return {}

        try:
            data = json.loads(locale_path.read_text(encoding="utf-8"))
            self._cache[lang] = data
            logger.debug("locale_loaded", lang=lang, keys=len(data))
            return data
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("locale_load_failed", lang=lang, error=str(exc))
            if lang != self.default_locale:
                return self._load_locale_file(self.default_locale)
            return {}

    def _load_builtin_fallback(self, lang: str) -> dict[str, Any]:
        """Minimal built-in locale for when no files are available."""
        if lang == "fr":
            return {
                "meta": {"code": "fr", "name": "French", "nativeName": "Fran\u00e7ais"},
                "dashboard": {"title": "CRUCIX \u2014 Terminal de Renseignement"},
            }
        return {
            "meta": {"code": "en", "name": "English", "nativeName": "English"},
            "dashboard": {"title": "CRUCIX \u2014 Intelligence Terminal"},
        }

    def load_locale(self, lang: str) -> dict[str, Any]:
        """Load and cache a locale. Public API."""
        return self._load_locale_file(lang)

    def register_locale_data(self, lang: str, data: dict[str, Any]) -> None:
        """Register locale data directly (e.g., from a dict or API)."""
        self._cache[lang] = data
        if lang not in self.SUPPORTED_LOCALES:
            self.SUPPORTED_LOCALES.append(lang)

    # ── Translation ────────────────────────────────────────────────────

    def _resolve_path(self, data: dict[str, Any], key_path: str) -> Any:
        """Resolve a dot-separated key path through nested dicts."""
        current = data
        for key in key_path.split("."):
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current

    def _interpolate(self, template: str, params: dict[str, str | int | float]) -> str:
        """Interpolate {param} placeholders in a template string."""
        def _replace(match: re.Match) -> str:
            key = match.group(1)
            if key in params:
                return str(params[key])
            return match.group(0)  # leave {key} as-is if not provided

        return _INTERPOLATE_RE.sub(_replace, template)

    def t(self, key_path: str, locale: str | None = None, **params: str | int | float) -> str:
        """Translate a key path with optional parameter interpolation.

        Args:
            key_path: Dot-separated key (e.g., "dashboard.title").
            locale: Target locale (defaults to current or default).
            **params: Interpolation parameters.

        Returns:
            Translated string, or the key_path if not found.
        """
        lang = (locale or self._current_locale or self.default_locale)[:2].lower()
        if lang not in self.SUPPORTED_LOCALES:
            lang = self.default_locale

        data = self._load_locale_file(lang)
        value = self._resolve_path(data, key_path)

        if value is not None and isinstance(value, str):
            if params:
                return self._interpolate(value, params)
            return value

        # Fallback to default locale
        if lang != self.default_locale:
            fallback_data = self._load_locale_file(self.default_locale)
            value = self._resolve_path(fallback_data, key_path)
            if value is not None and isinstance(value, str):
                if params:
                    return self._interpolate(value, params)
                return value

        logger.warning("missing_translation", key=key_path, locale=lang)
        return key_path

    # ── Locale Info ────────────────────────────────────────────────────

    def get_current_locale(self) -> str:
        """Get the current effective locale code."""
        return self._current_locale or self.default_locale

    def set_locale(self, locale: str) -> None:
        """Set the current locale."""
        lang = locale[:2].lower()
        if lang in self.SUPPORTED_LOCALES:
            self._current_locale = lang
        else:
            logger.warning("unsupported_locale", locale=locale, fallback=self.default_locale)
            self._current_locale = self.default_locale

    def get_supported_locales(self) -> list[LocaleInfo]:
        """Get metadata for all supported locales."""
        result = []
        for code in self.SUPPORTED_LOCALES:
            data = self._load_locale_file(code)
            meta = data.get("meta", {})
            result.append(LocaleInfo(
                code=code,
                name=meta.get("name", code),
                native_name=meta.get("nativeName", code),
            ))
        return result

    def get_llm_system_prompt(self, locale: str | None = None) -> str:
        """Get the LLM system prompt from locale data.

        Port of lib/i18n.mjs getLLMPrompt().
        """
        lang = (locale or self._current_locale or self.default_locale)[:2].lower()
        data = self._load_locale_file(lang)
        prompt = self._resolve_path(data, "llm.systemPrompt")
        if prompt and isinstance(prompt, str):
            return prompt
        # Fallback to English
        if lang != self.DEFAULT_LOCALE:
            fallback_data = self._load_locale_file(self.DEFAULT_LOCALE)
            prompt = self._resolve_path(fallback_data, "llm.systemPrompt")
            if prompt and isinstance(prompt, str):
                return prompt
        return ""

    def is_supported(self, lang: str) -> bool:
        """Check if a language code is supported."""
        return lang[:2].lower() in self.SUPPORTED_LOCALES

    def clear_cache(self) -> None:
        """Clear the locale cache (useful for development)."""
        self._cache.clear()
