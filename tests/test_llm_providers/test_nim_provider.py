"""Tests for NIMProvider — fully mocked HTTP, no real API keys required."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from ai_multicolony.core.llm_providers.nim_provider import (
    NIMProvider,
    NIMChatResponse,
    NIMEmbedResponse,
    NIMChoice,
    NIMUsage,
)
from ai_multicolony.exceptions import LLMRateLimitError, ProviderError


# ======================================================================
# Fixtures
# ======================================================================


@pytest.fixture
def provider() -> NIMProvider:
    """NIMProvider with a dummy API key."""
    return NIMProvider(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key="test-key-123",
        model="meta/llama-3.1-70b-instruct",
        timeout=10.0,
        max_retries=2,
    )


def _mock_response(
    status_code: int = 200,
    json_body: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> httpx.Response:
    """Build an httpx.Response with a JSON body."""
    body = json_body or {}
    request = MagicMock(spec=httpx.Request)
    return httpx.Response(
        status_code=status_code,
        request=request,
        json=body,
        headers=headers or {},
    )


CHAT_OK_BODY: dict[str, Any] = {
    "id": "chatcmpl-test",
    "model": "meta/llama-3.1-70b-instruct",
    "choices": [
        {
            "index": 0,
            "message": {"role": "assistant", "content": "Hello from NIM!"},
            "finish_reason": "stop",
        }
    ],
    "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
}

EMBED_OK_BODY: dict[str, Any] = {
    "model": "nvidia/nv-embedqa-e5-v5",
    "data": [
        {"index": 0, "embedding": [0.1, 0.2, 0.3]},
    ],
    "usage": {"prompt_tokens": 3, "total_tokens": 3},
}


# ======================================================================
# Chat completion
# ======================================================================


class TestComplete:
    @pytest.mark.asyncio
    async def test_complete_returns_text(self, provider: NIMProvider) -> None:
        mock_resp = _mock_response(200, CHAT_OK_BODY)

        with patch.object(provider, "_request", new_callable=AsyncMock, return_value=mock_resp):
            result = await provider.complete(
                [{"role": "user", "content": "Hello"}],
            )
        assert result == "Hello from NIM!"

    @pytest.mark.asyncio
    async def test_complete_passes_model(self, provider: NIMProvider) -> None:
        mock_resp = _mock_response(200, CHAT_OK_BODY)

        with patch.object(provider, "_request", new_callable=AsyncMock, return_value=mock_resp) as m:
            await provider.complete(
                [{"role": "user", "content": "Hi"}],
                model="custom-model",
                temperature=0.5,
            )
            call_kwargs = m.call_args
            payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
            assert payload["model"] == "custom-model"
            assert payload["temperature"] == 0.5

    @pytest.mark.asyncio
    async def test_complete_rate_limit_raises(self, provider: NIMProvider) -> None:
        with patch.object(
            provider,
            "_request",
            new_callable=AsyncMock,
            side_effect=LLMRateLimitError(provider="nim", retry_after=30),
        ):
            with pytest.raises(LLMRateLimitError):
                await provider.complete([{"role": "user", "content": "Hi"}])

    @pytest.mark.asyncio
    async def test_complete_retries_on_server_error(self) -> None:
        """Should retry up to max_retries on server errors."""
        # Use max_retries=3 so we have room for 2 failures + 1 success
        provider = NIMProvider(api_key="test", max_retries=3)
        call_count = 0

        async def flaky_request(*args: Any, **kwargs: Any) -> httpx.Response:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ProviderError(provider="nim", message="500 Server Error")
            return _mock_response(200, CHAT_OK_BODY)

        with patch.object(provider, "_request", new_callable=AsyncMock, side_effect=flaky_request):
            result = await provider.complete([{"role": "user", "content": "Hi"}])
        assert result == "Hello from NIM!"
        assert call_count == 3  # 2 failures + 1 success

    @pytest.mark.asyncio
    async def test_complete_exhausted_retries_raises(self, provider: NIMProvider) -> None:
        with patch.object(
            provider,
            "_request",
            new_callable=AsyncMock,
            side_effect=ProviderError(provider="nim", message="500"),
        ):
            with pytest.raises(ProviderError, match="failed after"):
                await provider.complete([{"role": "user", "content": "Hi"}])

    @pytest.mark.asyncio
    async def test_complete_with_empty_choices(self, provider: NIMProvider) -> None:
        empty_body = {
            "id": "chatcmpl-empty",
            "model": "meta/llama-3.1-70b-instruct",
            "choices": [],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }
        mock_resp = _mock_response(200, empty_body)
        with patch.object(provider, "_request", new_callable=AsyncMock, return_value=mock_resp):
            result = await provider.complete([{"role": "user", "content": "Hi"}])
        assert result == ""


# ======================================================================
# Embedding
# ======================================================================


class TestEmbed:
    @pytest.mark.asyncio
    async def test_embed_returns_vector(self, provider: NIMProvider) -> None:
        mock_resp = _mock_response(200, EMBED_OK_BODY)
        with patch.object(provider, "_request", new_callable=AsyncMock, return_value=mock_resp):
            vec = await provider.embed("Hello world")
        assert vec == [0.1, 0.2, 0.3]

    @pytest.mark.asyncio
    async def test_embed_empty_response(self, provider: NIMProvider) -> None:
        empty_body = {
            "model": "nvidia/nv-embedqa-e5-v5",
            "data": [],
            "usage": {"prompt_tokens": 0, "total_tokens": 0},
        }
        mock_resp = _mock_response(200, empty_body)
        with patch.object(provider, "_request", new_callable=AsyncMock, return_value=mock_resp):
            vec = await provider.embed("Hello world")
        assert vec == []

    @pytest.mark.asyncio
    async def test_embed_rate_limit_raises(self, provider: NIMProvider) -> None:
        with patch.object(
            provider,
            "_request",
            new_callable=AsyncMock,
            side_effect=LLMRateLimitError(provider="nim", retry_after=60),
        ):
            with pytest.raises(LLMRateLimitError):
                await provider.embed("test")


# ======================================================================
# Health check
# ======================================================================


class TestHealthCheck:
    @pytest.mark.asyncio
    async def test_health_check_ok(self, provider: NIMProvider) -> None:
        mock_resp = _mock_response(200)
        with patch.object(
            provider, "_get_client", new_callable=AsyncMock
        ) as mock_client_factory:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_resp)
            mock_client_factory.return_value = mock_client

            result = await provider.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, provider: NIMProvider) -> None:
        with patch.object(
            provider, "_get_client", new_callable=AsyncMock
        ) as mock_client_factory:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=httpx.ConnectError("refused"))
            mock_client_factory.return_value = mock_client

            result = await provider.health_check()
        assert result is False


# ======================================================================
# Request error handling
# ======================================================================


class TestRequestErrors:
    @pytest.mark.asyncio
    async def test_429_raises_rate_limit(self, provider: NIMProvider) -> None:
        mock_resp = _mock_response(429, headers={"retry-after": "30"})
        with patch.object(provider, "_get_client", new_callable=AsyncMock) as fac:
            client = AsyncMock()
            client.request = AsyncMock(return_value=mock_resp)
            fac.return_value = client
            with pytest.raises(LLMRateLimitError):
                await provider._request("POST", "/chat/completions", json={})

    @pytest.mark.asyncio
    async def test_500_raises_provider_error(self, provider: NIMProvider) -> None:
        mock_resp = _mock_response(500, json_body={"error": "Internal Server Error"})
        with patch.object(provider, "_get_client", new_callable=AsyncMock) as fac:
            client = AsyncMock()
            client.request = AsyncMock(return_value=mock_resp)
            fac.return_value = client
            with pytest.raises(ProviderError, match="500"):
                await provider._request("POST", "/chat/completions", json={})

    @pytest.mark.asyncio
    async def test_401_raises_provider_error(self, provider: NIMProvider) -> None:
        mock_resp = _mock_response(401, json_body={"error": "Unauthorized"})
        with patch.object(provider, "_get_client", new_callable=AsyncMock) as fac:
            client = AsyncMock()
            client.request = AsyncMock(return_value=mock_resp)
            fac.return_value = client
            with pytest.raises(ProviderError, match="401"):
                await provider._request("POST", "/chat/completions", json={})


# ======================================================================
# Response parsing
# ======================================================================


class TestResponseParsing:
    def test_parse_chat_response(self) -> None:
        resp = _mock_response(200, CHAT_OK_BODY)
        parsed = NIMProvider._parse_chat_response(resp)
        assert isinstance(parsed, NIMChatResponse)
        assert parsed.model == "meta/llama-3.1-70b-instruct"
        assert len(parsed.choices) == 1
        assert parsed.choices[0].content == "Hello from NIM!"
        assert parsed.usage.total_tokens == 15

    def test_parse_embed_response(self) -> None:
        resp = _mock_response(200, EMBED_OK_BODY)
        parsed = NIMProvider._parse_embed_response(resp)
        assert isinstance(parsed, NIMEmbedResponse)
        assert len(parsed.embeddings) == 1
        assert parsed.embeddings[0] == [0.1, 0.2, 0.3]


# ======================================================================
# Client lifecycle
# ======================================================================


class TestClientLifecycle:
    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        async with NIMProvider(api_key="test") as p:
            assert p._client is None  # not created until first use
        # After exiting, client should be cleaned up
        assert p._client is None

    @pytest.mark.asyncio
    async def test_close_idempotent(self, provider: NIMProvider) -> None:
        await provider.close()
        await provider.close()  # should not raise
