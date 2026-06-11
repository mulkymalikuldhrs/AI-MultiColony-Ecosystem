"""NVIDIA NIM (Inference Microservice) LLM provider.

NIM exposes an OpenAI-compatible API, so this provider re-uses the
standard ``/v1/chat/completions`` and ``/v1/embeddings`` endpoints.
All I/O is fully async via ``httpx.AsyncClient`` with structured
request/response logging through *structlog*.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx
import structlog
from pydantic import BaseModel, Field

from ai_multicolony.exceptions import (
    LLMError,
    LLMRateLimitError,
    ProviderError,
)
from ai_multicolony.core.llm_providers.circuit_breaker import CircuitBreaker

logger = structlog.get_logger(__name__)


# ── Pydantic response models ─────────────────────────────────────────────────


class NIMUsage(BaseModel):
    """Token usage returned by NIM."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class NIMChoice(BaseModel):
    """A single completion choice."""

    index: int = 0
    content: str = ""
    finish_reason: str | None = None


class NIMChatResponse(BaseModel):
    """Normalised chat completion response."""

    id: str = ""
    model: str = ""
    choices: list[NIMChoice] = Field(default_factory=list)
    usage: NIMUsage = Field(default_factory=NIMUsage)


class NIMEmbedResponse(BaseModel):
    """Embedding response."""

    model: str = ""
    embeddings: list[list[float]] = Field(default_factory=list)
    usage: NIMUsage = Field(default_factory=NIMUsage)


# ── Provider ─────────────────────────────────────────────────────────────────


class NIMProvider:
    """NVIDIA NIM provider with circuit-breaker protection.

    Parameters
    ----------
    base_url:
        NIM API base URL (e.g. ``https://integrate.api.nvidia.com/v1``).
    api_key:
        NVIDIA API key.
    model:
        Default model identifier for chat completions.
    timeout:
        HTTP request timeout in seconds.
    max_retries:
        Maximum number of retry attempts per request.
    """

    # Default NIM models
    DEFAULT_CHAT_MODEL: str = "meta/llama-3.1-70b-instruct"
    DEFAULT_EMBED_MODEL: str = "nvidia/nv-embedqa-e5-v5"

    def __init__(
        self,
        base_url: str = "https://integrate.api.nvidia.com/v1",
        api_key: str = "",
        model: str | None = None,
        timeout: float = 60.0,
        max_retries: int = 3,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model or self.DEFAULT_CHAT_MODEL
        self.timeout = timeout
        self.max_retries = max_retries
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=30.0,
        )

        self._client: httpx.AsyncClient | None = None
        self._call_count: int = 0

    # ── HTTP client lifecycle ────────────────────────────────────

    async def _get_client(self) -> httpx.AsyncClient:
        """Lazily create (or return existing) async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                timeout=httpx.Timeout(self.timeout, connect=10.0),
            )
        return self._client

    async def close(self) -> None:
        """Gracefully close the HTTP client."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> NIMProvider:
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()

    # ── Public API ───────────────────────────────────────────────

    async def complete(
        self,
        messages: list[dict[str, Any]],
        **kwargs: Any,
    ) -> str:
        """Send a chat-completion request and return the assistant text.

        Parameters
        ----------
        messages:
            Chat messages in OpenAI format (``[{role, content}, …]``).
        **kwargs:
            Extra parameters forwarded to the NIM API (e.g. *temperature*,
            *max_tokens*, *model*).

        Returns
        -------
        str
            The assistant's completion text.

        Raises
        ------
        ProviderError
            On non-retryable API errors.
        LLMRateLimitError
            When rate-limited by the NIM API.
        """
        model = kwargs.pop("model", self.model)
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            **kwargs,
        }

        return await self.circuit_breaker.call(self._complete_with_retries, payload)

    async def embed(self, text: str, **kwargs: Any) -> list[float]:
        """Generate an embedding vector for *text*.

        Parameters
        ----------
        text:
            Input string to embed.
        **kwargs:
            Extra parameters (e.g. *model*, *input_type*).

        Returns
        -------
        list[float]
            The embedding vector.

        Raises
        ------
        ProviderError
            On non-retryable API errors.
        """
        model = kwargs.pop("model", self.DEFAULT_EMBED_MODEL)
        payload: dict[str, Any] = {
            "model": model,
            "input": [text],
            **kwargs,
        }

        return await self.circuit_breaker.call(self._embed_with_retries, payload)

    async def health_check(self) -> bool:
        """Check whether the NIM API is reachable.

        Returns ``True`` when the ``/models`` endpoint responds with HTTP 200,
        ``False`` otherwise.
        """
        try:
            client = await self._get_client()
            resp = await client.get("/models")
            ok = resp.status_code == 200
            logger.debug(
                "nim_health_check",
                status_code=resp.status_code,
                ok=ok,
            )
            return ok
        except Exception as exc:
            logger.warning("nim_health_check_failed", error=str(exc))
            return False

    # ── Internal helpers ─────────────────────────────────────────

    async def _complete_with_retries(self, payload: dict[str, Any]) -> str:
        """Execute chat completion with exponential-backoff retries."""
        last_exc: Exception | None = None

        for attempt in range(self.max_retries):
            try:
                start = time.monotonic()
                resp = await self._request("POST", "/chat/completions", json=payload)
                latency = time.monotonic() - start

                parsed = self._parse_chat_response(resp)
                self._call_count += 1

                logger.info(
                    "nim_chat_complete",
                    model=parsed.model,
                    tokens=parsed.usage.total_tokens,
                    latency_ms=round(latency * 1000, 1),
                    attempt=attempt,
                )
                return parsed.choices[0].content if parsed.choices else ""

            except LLMRateLimitError:
                raise  # don't retry rate limits inside the retry loop
            except ProviderError as exc:
                last_exc = exc
                backoff = min(0.5 * (2 ** attempt), 10.0)
                logger.warning(
                    "nim_chat_retry",
                    attempt=attempt,
                    backoff=backoff,
                    error=str(exc),
                )
                await asyncio.sleep(backoff)

        raise ProviderError(
            provider="nim",
            message=f"Chat completion failed after {self.max_retries} retries: {last_exc}",
        )

    async def _embed_with_retries(self, payload: dict[str, Any]) -> list[float]:
        """Execute embedding with exponential-backoff retries."""
        last_exc: Exception | None = None

        for attempt in range(self.max_retries):
            try:
                start = time.monotonic()
                resp = await self._request("POST", "/embeddings", json=payload)
                latency = time.monotonic() - start

                parsed = self._parse_embed_response(resp)

                logger.info(
                    "nim_embed_complete",
                    model=parsed.model,
                    latency_ms=round(latency * 1000, 1),
                    attempt=attempt,
                )
                return parsed.embeddings[0] if parsed.embeddings else []

            except LLMRateLimitError:
                raise
            except ProviderError as exc:
                last_exc = exc
                backoff = min(0.5 * (2 ** attempt), 10.0)
                logger.warning(
                    "nim_embed_retry",
                    attempt=attempt,
                    backoff=backoff,
                    error=str(exc),
                )
                await asyncio.sleep(backoff)

        raise ProviderError(
            provider="nim",
            message=f"Embedding failed after {self.max_retries} retries: {last_exc}",
        )

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Issue an HTTP request and translate error status codes.

        Raises
        ------
        LLMRateLimitError
            On HTTP 429.
        ProviderError
            On HTTP 4xx/5xx (other than 429).
        """
        client = await self._get_client()
        resp = await client.request(method, path, **kwargs)

        if resp.status_code == 429:
            retry_after = float(resp.headers.get("retry-after", 60))
            raise LLMRateLimitError(provider="nim", retry_after=retry_after)

        if resp.status_code >= 400:
            body = resp.text[:500]
            raise ProviderError(
                provider="nim",
                message=f"NIM API error {resp.status_code}: {body}",
            )

        return resp

    # ── Response parsing ─────────────────────────────────────────

    @staticmethod
    def _parse_chat_response(resp: httpx.Response) -> NIMChatResponse:
        """Parse an OpenAI-format chat completion response."""
        data = resp.json()
        choices: list[NIMChoice] = []
        for c in data.get("choices", []):
            msg = c.get("message", {})
            choices.append(
                NIMChoice(
                    index=c.get("index", 0),
                    content=msg.get("content", ""),
                    finish_reason=c.get("finish_reason"),
                )
            )
        usage_data = data.get("usage", {})
        usage = NIMUsage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
        )
        return NIMChatResponse(
            id=data.get("id", ""),
            model=data.get("model", ""),
            choices=choices,
            usage=usage,
        )

    @staticmethod
    def _parse_embed_response(resp: httpx.Response) -> NIMEmbedResponse:
        """Parse an OpenAI-format embeddings response."""
        data = resp.json()
        embeddings: list[list[float]] = []
        for item in data.get("data", []):
            embeddings.append(item.get("embedding", []))
        usage_data = data.get("usage", {})
        usage = NIMUsage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
        )
        return NIMEmbedResponse(
            model=data.get("model", ""),
            embeddings=embeddings,
            usage=usage,
        )
