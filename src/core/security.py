"""
Security middleware module for the Agentic AI System.

Provides in-memory rate limiting, HTTP security header injection,
secrets scanning, and input sanitization utilities.

All classes use Pydantic v2 models for configuration and validation,
and require no external dependencies beyond the Python standard library
and pydantic.

Made with love by Mulky Malikul Dhaher in Indonesia
"""

from __future__ import annotations

import html
import math
import re
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Pydantic v2 Configuration Models
# ---------------------------------------------------------------------------

class RateLimiterConfig(BaseModel):
    """Configuration for the token-bucket rate limiter.

    Attributes:
        rate: Number of tokens added per second (the refill rate).
        capacity: Maximum number of tokens the bucket can hold.
        per_key: If True, each distinct key gets its own bucket.
    """

    rate: float = Field(
        default=10.0,
        gt=0,
        description="Token refill rate per second.",
    )
    capacity: int = Field(
        default=60,
        gt=0,
        description="Maximum burst capacity (bucket size).",
    )
    per_key: bool = Field(
        default=True,
        description="Maintain a separate bucket per key (e.g. per IP).",
    )

    @field_validator("capacity")
    @classmethod
    def capacity_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("capacity must be a positive integer")
        return v


class SecurityHeadersConfig(BaseModel):
    """Configuration for HTTP security headers.

    Attributes:
        x_content_type_options: Value for X-Content-Type-Options header.
        x_frame_options: Value for X-Frame-Options header.
        x_xss_protection: Value for X-XSS-Protection header.
        content_security_policy: Value for Content-Security-Policy header.
        strict_transport_security: Value for Strict-Transport-Security header.
        referrer_policy: Value for Referrer-Policy header.
        enabled: Master switch to enable/disable header injection.
    """

    x_content_type_options: str = Field(
        default="nosniff",
        description="Prevents MIME-type sniffing.",
    )
    x_frame_options: str = Field(
        default="DENY",
        description="Prevents clickjacking via iframe embedding.",
    )
    x_xss_protection: str = Field(
        default="1; mode=block",
        description="Enables browser XSS filter.",
    )
    content_security_policy: str = Field(
        default="default-src 'self'",
        description="Restricts resource loading origins.",
    )
    strict_transport_security: str = Field(
        default="max-age=31536000; includeSubDomains",
        description="Enforces HTTPS connections.",
    )
    referrer_policy: str = Field(
        default="strict-origin-when-cross-origin",
        description="Controls referrer information sent with requests.",
    )
    enabled: bool = Field(
        default=True,
        description="Master switch for header injection.",
    )


class SecretsScannerConfig(BaseModel):
    """Configuration for the secrets scanner.

    Attributes:
        custom_patterns: Additional regex patterns to detect (list of
            raw pattern strings).  Each is compiled with re.IGNORECASE.
        max_line_length: Skip lines longer than this to avoid pathological
            regex back-tracking on minified files.
    """

    custom_patterns: List[str] = Field(
        default_factory=list,
        description="Additional regex patterns for secret detection.",
    )
    max_line_length: int = Field(
        default=10_000,
        gt=0,
        description="Skip lines longer than this many characters.",
    )


class SanitizeConfig(BaseModel):
    """Configuration for input sanitization.

    Attributes:
        max_length: Truncate input to this many characters.
        strip_html: If True, HTML-escape angle brackets and ampersands.
        strip_control_chars: If True, remove ASCII control characters
            (except newline and tab).
        allowed_schemes: URL schemes permitted after sanitization.
    """

    max_length: int = Field(
        default=10_000,
        gt=0,
        description="Maximum allowed input length.",
    )
    strip_html: bool = Field(
        default=True,
        description="HTML-escape special characters.",
    )
    strip_control_chars: bool = Field(
        default=True,
        description="Remove ASCII control characters.",
    )
    allowed_schemes: Set[str] = Field(
        default_factory=lambda: {"http", "https", "mailto"},
        description="Permitted URL schemes after sanitization.",
    )


# ---------------------------------------------------------------------------
# RateLimiter — Token Bucket Algorithm (in-memory, no Redis)
# ---------------------------------------------------------------------------

@dataclass
class _Bucket:
    """Internal token-bucket state for a single key."""

    tokens: float
    last_refill: float


class RateLimiter:
    """In-memory token-bucket rate limiter.

    The token bucket algorithm allows short bursts up to *capacity* while
    sustaining a long-term average of *rate* requests per second.  Each
    call to :meth:`allow` consumes one token; when the bucket is empty
    the request is rejected.

    This implementation is **thread-safe** for CPython due to the GIL,
    and uses no external dependencies (no Redis, no memcached).

    Example::

        limiter = RateLimiter(RateLimiterConfig(rate=5, capacity=20))
        if limiter.allow("192.168.1.1"):
            handle_request()
        else:
            return "Too Many Requests", 429
    """

    def __init__(self, config: Optional[RateLimiterConfig] = None) -> None:
        self._config = config or RateLimiterConfig()
        self._buckets: Dict[str, _Bucket] = defaultdict(
            lambda: _Bucket(tokens=float(self._config.capacity), last_refill=time.monotonic())
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def allow(self, key: str = "global", tokens: int = 1) -> bool:
        """Check whether *key* is allowed to proceed.

        Args:
            key: Identifier for the client/resource (e.g. IP address).
            tokens: Number of tokens to consume for this request.

        Returns:
            True if the request is allowed, False if rate-limited.
        """
        if not self._config.per_key:
            key = "global"

        now = time.monotonic()
        bucket = self._buckets[key]

        # Refill tokens based on elapsed time
        elapsed = now - bucket.last_refill
        refill = elapsed * self._config.rate
        bucket.tokens = min(float(self._config.capacity), bucket.tokens + refill)
        bucket.last_refill = now

        if bucket.tokens >= tokens:
            bucket.tokens -= tokens
            return True

        return False

    def reset(self, key: str = "global") -> None:
        """Reset the bucket for *key* to full capacity."""
        self._buckets[key] = _Bucket(
            tokens=float(self._config.capacity),
            last_refill=time.monotonic(),
        )

    def get_tokens(self, key: str = "global") -> float:
        """Return the current number of available tokens for *key*.

        The return value is a float because fractional tokens accumulate
        over time.
        """
        now = time.monotonic()
        bucket = self._buckets[key]
        elapsed = now - bucket.last_refill
        refill = elapsed * self._config.rate
        return min(float(self._config.capacity), bucket.tokens + refill)

    def cleanup(self, max_age: float = 300.0) -> int:
        """Remove buckets that have been idle for more than *max_age* seconds.

        Returns the number of buckets removed.
        """
        now = time.monotonic()
        stale_keys = [
            k
            for k, b in self._buckets.items()
            if (now - b.last_refill) > max_age
            and b.tokens >= self._config.capacity * 0.99
        ]
        for k in stale_keys:
            del self._buckets[k]
        return len(stale_keys)


# ---------------------------------------------------------------------------
# SecurityHeaders — Middleware Helper for Flask / FastAPI
# ---------------------------------------------------------------------------

class SecurityHeaders:
    """Inject OWASP-recommended security headers into HTTP responses.

    Works as a WSGI/ASGI middleware helper.  For Flask, use the
    ``flask_after_request`` class method.  For FastAPI / Starlette,
    use the ``asgi_middleware`` method.

    Example (Flask)::

        headers = SecurityHeaders()
        app.after_request(headers.flask_after_request)

    Example (FastAPI)::

        headers = SecurityHeaders()
        app.middleware("http")(headers.starlette_middleware)
    """

    def __init__(self, config: Optional[SecurityHeadersConfig] = None) -> None:
        self._config = config or SecurityHeadersConfig()

    @property
    def headers(self) -> Dict[str, str]:
        """Return the header dictionary based on current configuration."""
        if not self._config.enabled:
            return {}
        return {
            "X-Content-Type-Options": self._config.x_content_type_options,
            "X-Frame-Options": self._config.x_frame_options,
            "X-XSS-Protection": self._config.x_xss_protection,
            "Content-Security-Policy": self._config.content_security_policy,
            "Strict-Transport-Security": self._config.strict_transport_security,
            "Referrer-Policy": self._config.referrer_policy,
        }

    def flask_after_request(self, response: Any) -> Any:
        """Flask ``after_request`` handler.

        Args:
            response: Flask Response object.

        Returns:
            The same Response object with security headers set.
        """
        for header_name, header_value in self.headers.items():
            response.headers[header_name] = header_value
        return response

    async def starlette_middleware(self, request: Any, call_next: Any) -> Any:
        """ASGI middleware for Starlette / FastAPI.

        Args:
            request: The incoming Starlette Request.
            call_next: The next middleware/endpoint callable.

        Returns:
            Response with security headers attached.
        """
        response = await call_next(request)
        for header_name, header_value in self.headers.items():
            response.headers[header_name] = header_value
        return response


# ---------------------------------------------------------------------------
# SecretsScanner — Detect Hardcoded API Keys / Secrets in Strings
# ---------------------------------------------------------------------------

# Built-in patterns compiled once at module load.
_BUILTIN_SECRET_PATTERNS: List[Tuple[str, re.Pattern[str]]] = [
    ("AWS Access Key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("AWS Secret Key", re.compile(r"aws.{0,20}[0-9a-zA-Z/+]{40}", re.IGNORECASE)),
    ("GitHub Token", re.compile(r"gh[pousr]_[0-9a-zA-Z]{36}")),
    ("GitLab Token", re.compile(r"glpat-[0-9a-zA-Z\-]{20}")),
    ("Slack Token", re.compile(r"xox[baprs]-[0-9a-zA-Z\-]{10,}")),
    ("Stripe Key", re.compile(r"(?i)sk_live_[0-9a-zA-Z]{24,}")),
    ("Private Key Block", re.compile(r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----")),
    ("Google API Key", re.compile(r"AIza[0-9A-Za-z\-_]{35}")),
    ("Generic API Key", re.compile(r"(?i)(?:api[_-]?key|apikey|secret[_-]?key|access[_-]?key|token)\s*[:=]\s*['\"]?[0-9a-zA-Z\-_]{20,}['\"]?")),
    ("Bearer Token", re.compile(r"(?i)bearer\s+[0-9a-zA-Z\-._~+/]+=*")),
]


class SecretMatch(BaseModel):
    """A single secret detection match.

    Attributes:
        pattern_name: Human-readable name of the matched pattern.
        match_text: The portion of text that matched (may be partially
            masked for safety).
        line_number: 1-based line number where the match was found.
        column: 0-based column offset within the line.
    """

    pattern_name: str
    match_text: str
    line_number: int = -1
    column: int = -1


class ScanResult(BaseModel):
    """Result of a secrets scan operation.

    Attributes:
        has_secrets: True if at least one secret was detected.
        matches: List of individual matches.
        lines_scanned: Number of lines examined.
    """

    has_secrets: bool
    matches: List[SecretMatch] = Field(default_factory=list)
    lines_scanned: int = 0


class SecretsScanner:
    """Scan strings and source code for hardcoded API keys and secrets.

    Uses a curated set of regex patterns for common cloud/service
    credentials (AWS, GitHub, Stripe, Slack, etc.) and allows custom
    patterns to be added via configuration.

    Example::

        scanner = SecretsScanner()
        result = scanner.scan("api_key = 'EXAMPLE_SECRET_KEY_REPLACE_ME'")
        if result.has_secrets:
            for m in result.matches:
                print(f"Found {m.pattern_name} at line {m.line_number}")
    """

    def __init__(self, config: Optional[SecretsScannerConfig] = None) -> None:
        self._config = config or SecretsScannerConfig()
        self._patterns: List[Tuple[str, re.Pattern[str]]] = list(_BUILTIN_SECRET_PATTERNS)

        # Compile and append user-supplied patterns.
        for raw in self._config.custom_patterns:
            compiled = re.compile(raw, re.IGNORECASE)
            self._patterns.append(("Custom: " + raw[:40], compiled))

    def scan(self, text: str) -> ScanResult:
        """Scan *text* for hardcoded secrets.

        Args:
            text: The source string or file content to scan.

        Returns:
            A :class:`ScanResult` with match details.
        """
        matches: List[SecretMatch] = []
        lines = text.splitlines()
        lines_scanned = 0

        for line_idx, line in enumerate(lines):
            if len(line) > self._config.max_line_length:
                continue  # Skip extremely long lines (e.g. minified JS)

            lines_scanned += 1

            for name, pattern in self._patterns:
                for m in pattern.finditer(line):
                    # Mask the match for safety — show first 4 chars + ***
                    raw = m.group(0)
                    masked = raw[:4] + "***" if len(raw) > 4 else raw
                    matches.append(
                        SecretMatch(
                            pattern_name=name,
                            match_text=masked,
                            line_number=line_idx + 1,
                            column=m.start(),
                        )
                    )

        return ScanResult(
            has_secrets=len(matches) > 0,
            matches=matches,
            lines_scanned=lines_scanned,
        )

    def scan_file(self, path: str) -> ScanResult:
        """Convenience method to scan a file by path.

        Args:
            path: Filesystem path to the file to scan.

        Returns:
            A :class:`ScanResult`.
        """
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                content = fh.read()
        except OSError:
            return ScanResult(has_secrets=False, lines_scanned=0)
        return self.scan(content)


# ---------------------------------------------------------------------------
# sanitize_input — Basic Input Sanitization
# ---------------------------------------------------------------------------

# Characters that are stripped when strip_control_chars is enabled.
_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

# Pattern for detecting javascript: and other dangerous URL schemes
_DANGEROUS_SCHEME_RE = re.compile(
    r"(?i)\b(javascript|vbscript|data|blob)\s*:"
)


def sanitize_input(
    value: str,
    config: Optional[SanitizeConfig] = None,
) -> str:
    """Sanitize a user-supplied string.

    Performs the following transformations based on *config*:

    1. **Length truncation** — Truncates to ``max_length`` characters.
    2. **Control character stripping** — Removes ASCII control characters
       except newline (``\\n``) and tab (``\\t``).
    3. **HTML escaping** — Escapes ``<``, ``>``, ``&``, ``"``, and ``'``
       using :func:`html.escape`.
    4. **Dangerous URL scheme removal** — Replaces ``javascript:``,
       ``vbscript:``, ``data:``, and ``blob:`` schemes with ``removed:``.

    Args:
        value: The raw user input.
        config: Sanitization configuration.  Uses defaults if not provided.

    Returns:
        The sanitized string.

    Example::

        safe = sanitize_input("<script>alert('xss')</script>")
        # '&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;'
    """
    cfg = config or SanitizeConfig()

    # 1. Truncate to max length
    result = value[: cfg.max_length]

    # 2. Strip control characters (preserve \n and \t)
    if cfg.strip_control_chars:
        result = _CONTROL_CHAR_RE.sub("", result)

    # 3. HTML-escape
    if cfg.strip_html:
        result = html.escape(result, quote=True)

    # 4. Neutralize dangerous URL schemes
    result = _DANGEROUS_SCHEME_RE.sub("removed:", result)

    return result


# ---------------------------------------------------------------------------
# Module-level convenience instances
# ---------------------------------------------------------------------------

#: Default rate limiter (10 req/s, burst 60).
default_rate_limiter = RateLimiter()

#: Default security headers middleware.
default_security_headers = SecurityHeaders()

#: Default secrets scanner.
default_secrets_scanner = SecretsScanner()
