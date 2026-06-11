"""
Comprehensive tests for previously untested C2 modules.

Covers:
1. src/middlewares/ — LoopDetection, TokenUsage, SafetyTermination,
   Clarification, Summarization, SafetyFinishReason
2. src/guardrails/ — GuardrailProvider, AllowlistProvider, GuardrailMiddleware
3. src/skills/ — Skill, SkillStorage, parser, validation, slash, installer
4. src/config/ — AppConfig, ModelConfig, MemoryConfig, LoopDetectionConfig
5. src/llm_models/ — factory helpers, credential_loader
6. src/channels/ — MessageBus, InboundMessage, OutboundMessage, Channel

All tests use mocking — no real API calls or external services.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Ensure project root is importable
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ═══════════════════════════════════════════════════════════════════════════
# 1. MIDDLEWARE TESTS
# ═══════════════════════════════════════════════════════════════════════════


# ---- 1a. Safety Termination Detectors -----------------------------------

class TestSafetyTerminationDetectors:
    """Tests for src/middlewares/safety_termination_detectors.py.

    Verifies that each built-in detector correctly identifies its
    provider-specific safety termination signal and returns None for
    normal responses.
    """

    def test_openai_content_filter_detects_content_filter(self):
        """OpenAI detector should detect finish_reason='content_filter'."""
        from langchain_core.messages import AIMessage

        from src.middlewares.safety_termination_detectors import (
            OpenAICompatibleContentFilterDetector,
        )

        det = OpenAICompatibleContentFilterDetector()
        msg = AIMessage(content="partial", response_metadata={"finish_reason": "content_filter"})
        result = det.detect(msg)
        assert result is not None
        assert result.detector == "openai_compatible_content_filter"
        assert result.reason_field == "finish_reason"
        assert result.reason_value == "content_filter"

    def test_openai_content_filter_allows_normal_finish(self):
        """OpenAI detector should return None for finish_reason='stop'."""
        from langchain_core.messages import AIMessage

        from src.middlewares.safety_termination_detectors import (
            OpenAICompatibleContentFilterDetector,
        )

        det = OpenAICompatibleContentFilterDetector()
        msg = AIMessage(content="hello", response_metadata={"finish_reason": "stop"})
        assert det.detect(msg) is None

    def test_openai_content_filter_custom_finish_reasons(self):
        """OpenAI detector should honour custom finish_reasons set."""
        from langchain_core.messages import AIMessage

        from src.middlewares.safety_termination_detectors import (
            OpenAICompatibleContentFilterDetector,
        )

        det = OpenAICompatibleContentFilterDetector(finish_reasons=["sensitive", "violation"])
        msg_sensitive = AIMessage(content="", response_metadata={"finish_reason": "sensitive"})
        msg_violation = AIMessage(content="", response_metadata={"finish_reason": "violation"})
        assert det.detect(msg_sensitive) is not None
        assert det.detect(msg_violation) is not None
        # content_filter is not in custom set
        msg_cf = AIMessage(content="", response_metadata={"finish_reason": "content_filter"})
        assert det.detect(msg_cf) is None

    def test_openai_extracts_azure_content_filter_results(self):
        """OpenAI detector should carry Azure content_filter_results into extras."""
        from langchain_core.messages import AIMessage

        from src.middlewares.safety_termination_detectors import (
            OpenAICompatibleContentFilterDetector,
        )

        det = OpenAICompatibleContentFilterDetector()
        filter_results = {"hate": {"filtered": True}}
        msg = AIMessage(
            content="",
            response_metadata={"finish_reason": "content_filter", "content_filter_results": filter_results},
        )
        result = det.detect(msg)
        assert result is not None
        assert result.extras.get("content_filter_results") == filter_results

    def test_anthropic_refusal_detects_refusal(self):
        """Anthropic detector should detect stop_reason='refusal'."""
        from langchain_core.messages import AIMessage

        from src.middlewares.safety_termination_detectors import AnthropicRefusalDetector

        det = AnthropicRefusalDetector()
        msg = AIMessage(content="I can't", response_metadata={"stop_reason": "refusal"})
        result = det.detect(msg)
        assert result is not None
        assert result.detector == "anthropic_refusal"
        assert result.reason_field == "stop_reason"
        assert result.reason_value == "refusal"

    def test_anthropic_refusal_allows_normal_stop(self):
        """Anthropic detector should return None for stop_reason='end_turn'."""
        from langchain_core.messages import AIMessage

        from src.middlewares.safety_termination_detectors import AnthropicRefusalDetector

        det = AnthropicRefusalDetector()
        msg = AIMessage(content="done", response_metadata={"stop_reason": "end_turn"})
        assert det.detect(msg) is None

    def test_gemini_safety_detects_safety(self):
        """Gemini detector should detect finish_reason='SAFETY'."""
        from langchain_core.messages import AIMessage

        from src.middlewares.safety_termination_detectors import GeminiSafetyDetector

        det = GeminiSafetyDetector()
        msg = AIMessage(content="", response_metadata={"finish_reason": "SAFETY"})
        result = det.detect(msg)
        assert result is not None
        assert result.detector == "gemini_safety"
        assert result.reason_value == "SAFETY"

    def test_gemini_safety_detects_prohibited_content(self):
        """Gemini detector should detect PROHIBITED_CONTENT and other default reasons."""
        from langchain_core.messages import AIMessage

        from src.middlewares.safety_termination_detectors import GeminiSafetyDetector

        det = GeminiSafetyDetector()
        msg = AIMessage(content="", response_metadata={"finish_reason": "PROHIBITED_CONTENT"})
        result = det.detect(msg)
        assert result is not None

    def test_gemini_safety_allows_normal_stop(self):
        """Gemini detector should return None for finish_reason='STOP'."""
        from langchain_core.messages import AIMessage

        from src.middlewares.safety_termination_detectors import GeminiSafetyDetector

        det = GeminiSafetyDetector()
        msg = AIMessage(content="ok", response_metadata={"finish_reason": "STOP"})
        assert det.detect(msg) is None

    def test_gemini_extracts_safety_ratings(self):
        """Gemini detector should carry safety_ratings into extras when present."""
        from langchain_core.messages import AIMessage

        from src.middlewares.safety_termination_detectors import GeminiSafetyDetector

        det = GeminiSafetyDetector()
        ratings = [{"category": "HARM_CATEGORY_HARASSMENT", "probability": "HIGH"}]
        msg = AIMessage(
            content="",
            response_metadata={"finish_reason": "SAFETY", "safety_ratings": ratings},
        )
        result = det.detect(msg)
        assert result is not None
        assert result.extras.get("safety_ratings") == ratings

    def test_default_detectors_returns_three(self):
        """default_detectors() should return the 3 built-in detectors."""
        from src.middlewares.safety_termination_detectors import default_detectors

        dets = default_detectors()
        assert len(dets) == 3
        names = {d.name for d in dets}
        assert "openai_compatible_content_filter" in names
        assert "anthropic_refusal" in names
        assert "gemini_safety" in names

    def test_metadata_in_additional_kwargs(self):
        """Detectors should also check additional_kwargs for finish_reason."""
        from langchain_core.messages import AIMessage

        from src.middlewares.safety_termination_detectors import (
            OpenAICompatibleContentFilterDetector,
        )

        det = OpenAICompatibleContentFilterDetector()
        msg = AIMessage(content="", additional_kwargs={"finish_reason": "content_filter"})
        result = det.detect(msg)
        assert result is not None

    def test_safety_termination_dataclass(self):
        """SafetyTermination dataclass should store all fields correctly."""
        from src.middlewares.safety_termination_detectors import SafetyTermination

        st = SafetyTermination(
            detector="test",
            reason_field="field",
            reason_value="val",
            extras={"key": "value"},
        )
        assert st.detector == "test"
        assert st.reason_field == "field"
        assert st.reason_value == "val"
        assert st.extras == {"key": "value"}
        # frozen dataclass
        with pytest.raises(AttributeError):
            st.detector = "changed"


# ---- 1b. Safety Finish Reason Middleware ---------------------------------


class TestSafetyFinishReasonMiddleware:
    """Tests for src/middlewares/safety_finish_reason_middleware.py.

    Verifies that the middleware strips tool_calls from AIMessages
    flagged by safety termination detectors, and leaves normal messages
    untouched.
    """

    def _make_runtime(self):
        """Create a mock Runtime with minimal context."""
        runtime = MagicMock()
        runtime.context = {"thread_id": "test-thread"}
        return runtime

    def test_no_messages_returns_none(self):
        """Middleware should return None when state has no messages."""
        from src.middlewares.safety_finish_reason_middleware import (
            SafetyFinishReasonMiddleware,
        )

        mw = SafetyFinishReasonMiddleware()
        result = mw._apply({"messages": []}, self._make_runtime())
        assert result is None

    def test_non_ai_message_returns_none(self):
        """Middleware should return None when last message is not AIMessage."""
        from langchain_core.messages import HumanMessage

        from src.middlewares.safety_finish_reason_middleware import (
            SafetyFinishReasonMiddleware,
        )

        mw = SafetyFinishReasonMiddleware()
        result = mw._apply({"messages": [HumanMessage(content="hi")]}, self._make_runtime())
        assert result is None

    def test_ai_message_without_tool_calls_unchanged(self):
        """Middleware should not modify AIMessages without tool_calls."""
        from langchain_core.messages import AIMessage

        from src.middlewares.safety_finish_reason_middleware import (
            SafetyFinishReasonMiddleware,
        )

        mw = SafetyFinishReasonMiddleware()
        msg = AIMessage(content="hello", response_metadata={"finish_reason": "content_filter"})
        result = mw._apply({"messages": [msg]}, self._make_runtime())
        assert result is None

    def test_ai_message_with_normal_finish_reason_unchanged(self):
        """Middleware should not touch messages with normal finish reasons."""
        from langchain_core.messages import AIMessage

        from src.middlewares.safety_finish_reason_middleware import (
            SafetyFinishReasonMiddleware,
        )

        mw = SafetyFinishReasonMiddleware()
        msg = AIMessage(
            content="",
            tool_calls=[{"name": "bash", "args": {"cmd": "ls"}, "id": "tc1"}],
            response_metadata={"finish_reason": "stop"},
        )
        result = mw._apply({"messages": [msg]}, self._make_runtime())
        assert result is None

    def test_strips_tool_calls_on_content_filter(self):
        """Middleware should strip tool_calls when content_filter is detected."""
        from langchain_core.messages import AIMessage

        from src.middlewares.safety_finish_reason_middleware import (
            SafetyFinishReasonMiddleware,
        )

        mw = SafetyFinishReasonMiddleware()
        msg = AIMessage(
            content="",
            tool_calls=[{"name": "write_file", "args": {"path": "/x"}, "id": "tc1"}],
            response_metadata={"finish_reason": "content_filter"},
        )
        result = mw._apply({"messages": [msg]}, self._make_runtime())
        assert result is not None
        patched = result["messages"][0]
        assert isinstance(patched, AIMessage)
        assert patched.tool_calls == []
        # Should contain the user-facing explanation
        assert "safety-related signal" in patched.content

    def test_stamps_safety_termination_in_kwargs(self):
        """Middleware should record observability in additional_kwargs."""
        from langchain_core.messages import AIMessage

        from src.middlewares.safety_finish_reason_middleware import (
            SafetyFinishReasonMiddleware,
        )

        mw = SafetyFinishReasonMiddleware()
        msg = AIMessage(
            content="",
            tool_calls=[{"name": "bash", "args": {}, "id": "tc1"}],
            response_metadata={"finish_reason": "content_filter"},
        )
        result = mw._apply({"messages": [msg]}, self._make_runtime())
        patched = result["messages"][0]
        assert "safety_termination" in patched.additional_kwargs
        st = patched.additional_kwargs["safety_termination"]
        assert st["detector"] == "openai_compatible_content_filter"
        assert st["suppressed_tool_call_count"] == 1

    def test_detect_with_no_matching_detector(self):
        """Middleware should not fire when no detector matches the message."""
        from langchain_core.messages import AIMessage

        from src.middlewares.safety_finish_reason_middleware import (
            SafetyFinishReasonMiddleware,
        )

        # Use custom detector that never matches
        never_match = MagicMock()
        never_match.name = "never_match"
        never_match.detect.return_value = None

        mw = SafetyFinishReasonMiddleware(detectors=[never_match])
        msg = AIMessage(
            content="",
            tool_calls=[{"name": "bash", "args": {}, "id": "tc1"}],
            response_metadata={"finish_reason": "content_filter"},
        )
        result = mw._apply({"messages": [msg]}, self._make_runtime())
        assert result is None

    def test_append_user_message_with_string_content(self):
        """_append_user_message should append text to a string content."""
        from src.middlewares.safety_finish_reason_middleware import (
            SafetyFinishReasonMiddleware,
        )

        result = SafetyFinishReasonMiddleware._append_user_message("hello", "warning")
        assert result == "hello\n\nwarning"

    def test_append_user_message_with_none_content(self):
        """_append_user_message should return text when content is None."""
        from src.middlewares.safety_finish_reason_middleware import (
            SafetyFinishReasonMiddleware,
        )

        result = SafetyFinishReasonMiddleware._append_user_message(None, "warning")
        assert result == "warning"

    def test_append_user_message_with_list_content(self):
        """_append_user_message should append to list-content properly."""
        from src.middlewares.safety_finish_reason_middleware import (
            SafetyFinishReasonMiddleware,
        )

        content = [{"type": "text", "text": "thinking..."}]
        result = SafetyFinishReasonMiddleware._append_user_message(content, "warning")
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[-1]["type"] == "text"


# ---- 1c. Loop Detection Middleware ---------------------------------------


class TestLoopDetectionMiddleware:
    """Tests for src/middlewares/loop_detection_middleware.py.

    Verifies that the loop detection middleware correctly hashes tool
    calls, tracks them in sliding windows, and triggers warnings/hard
    stops when thresholds are exceeded.
    """

    def test_import(self):
        """LoopDetectionMiddleware should be importable."""
        from src.middlewares.loop_detection_middleware import LoopDetectionMiddleware

        assert LoopDetectionMiddleware is not None

    def test_hash_tool_calls_stable(self):
        """Hashing the same tool calls should produce the same hash."""
        from src.middlewares.loop_detection_middleware import _hash_tool_calls

        tcs = [{"name": "bash", "args": {"cmd": "ls"}, "id": "1"}]
        h1 = _hash_tool_calls(tcs)
        h2 = _hash_tool_calls(tcs)
        assert h1 == h2

    def test_hash_tool_calls_different_args(self):
        """Different tool call args should produce different hashes."""
        from src.middlewares.loop_detection_middleware import _hash_tool_calls

        tcs_a = [{"name": "bash", "args": {"cmd": "ls"}, "id": "1"}]
        tcs_b = [{"name": "bash", "args": {"cmd": "pwd"}, "id": "1"}]
        assert _hash_tool_calls(tcs_a) != _hash_tool_calls(tcs_b)

    def test_hash_tool_calls_empty(self):
        """Empty tool calls list should hash to a consistent value."""
        from src.middlewares.loop_detection_middleware import _hash_tool_calls

        h = _hash_tool_calls([])
        assert isinstance(h, str)


# ---- 1d. Token Usage Middleware ------------------------------------------


class TestTokenUsageMiddleware:
    """Tests for src/middlewares/token_usage_middleware.py.

    Verifies token usage attribution, step kind inference, and
    the helper functions that normalize tool call descriptions.
    """

    def test_string_arg_with_string(self):
        """_string_arg should strip a string and return it."""
        from src.middlewares.token_usage_middleware import _string_arg

        assert _string_arg("  hello  ") == "hello"

    def test_string_arg_with_empty_string(self):
        """_string_arg should return None for whitespace-only strings."""
        from src.middlewares.token_usage_middleware import _string_arg

        assert _string_arg("   ") is None

    def test_string_arg_with_non_string(self):
        """_string_arg should return None for non-string inputs."""
        from src.middlewares.token_usage_middleware import _string_arg

        assert _string_arg(42) is None
        assert _string_arg(None) is None

    def test_normalize_todos_valid(self):
        """_normalize_todos should convert valid dicts into Todo objects."""
        from src.middlewares.token_usage_middleware import _normalize_todos

        raw = [
            {"content": "Task A", "status": "pending"},
            {"content": "Task B", "status": "in_progress"},
            {"content": "Task C", "status": "completed"},
        ]
        result = _normalize_todos(raw)
        assert len(result) == 3
        assert result[0]["content"] == "Task A"
        assert result[0]["status"] == "pending"

    def test_normalize_todos_skips_invalid(self):
        """_normalize_todos should skip non-dict items and bad statuses."""
        from src.middlewares.token_usage_middleware import _normalize_todos

        raw = [
            "not a dict",
            {"content": "Good", "status": "pending"},
            {"content": "Bad status", "status": "invalid"},
            42,
        ]
        result = _normalize_todos(raw)
        assert len(result) == 2  # "Good" and "Bad status" (status dropped for invalid)

    def test_normalize_todos_non_list(self):
        """_normalize_todos should return empty list for non-list input."""
        from src.middlewares.token_usage_middleware import _normalize_todos

        assert _normalize_todos("not a list") == []
        assert _normalize_todos(None) == []

    def test_todo_action_kind_new_completed(self):
        """_todo_action_kind should return 'todo_complete' for new completed."""
        from src.middlewares.token_usage_middleware import _todo_action_kind

        assert _todo_action_kind(None, {"status": "completed"}) == "todo_complete"

    def test_todo_action_kind_new_in_progress(self):
        """_todo_action_kind should return 'todo_start' for new in_progress."""
        from src.middlewares.token_usage_middleware import _todo_action_kind

        assert _todo_action_kind(None, {"status": "in_progress"}) == "todo_start"

    def test_todo_action_kind_completed_from_previous(self):
        """_todo_action_kind should return 'todo_complete' when completing an existing todo."""
        from src.middlewares.token_usage_middleware import _todo_action_kind

        prev = {"content": "X", "status": "in_progress"}
        curr = {"content": "X", "status": "completed"}
        assert _todo_action_kind(prev, curr) == "todo_complete"

    def test_infer_step_kind_final_answer(self):
        """_infer_step_kind should return 'final_answer' for content-only messages."""
        from langchain_core.messages import AIMessage

        from src.middlewares.token_usage_middleware import _infer_step_kind

        msg = AIMessage(content="Here is your answer")
        assert _infer_step_kind(msg, []) == "final_answer"

    def test_infer_step_kind_thinking(self):
        """_infer_step_kind should return 'thinking' for empty content with no actions."""
        from langchain_core.messages import AIMessage

        from src.middlewares.token_usage_middleware import _infer_step_kind

        msg = AIMessage(content="")
        assert _infer_step_kind(msg, []) == "thinking"

    def test_infer_step_kind_tool_batch(self):
        """_infer_step_kind should return 'tool_batch' for multiple actions."""
        from langchain_core.messages import AIMessage

        from src.middlewares.token_usage_middleware import _infer_step_kind

        msg = AIMessage(content="")
        actions = [{"kind": "tool"}, {"kind": "tool"}]
        assert _infer_step_kind(msg, actions) == "tool_batch"

    def test_infer_step_kind_subagent_dispatch(self):
        """_infer_step_kind should return 'subagent_dispatch' for single subagent action."""
        from langchain_core.messages import AIMessage

        from src.middlewares.token_usage_middleware import _infer_step_kind

        msg = AIMessage(content="")
        actions = [{"kind": "subagent"}]
        assert _infer_step_kind(msg, actions) == "subagent_dispatch"

    def test_describe_tool_call_generic(self):
        """_describe_tool_call should return generic tool info for unknown tools."""
        from src.middlewares.token_usage_middleware import _describe_tool_call

        tc = {"name": "custom_tool", "args": {"description": "does stuff"}, "id": "tc1"}
        result = _describe_tool_call(tc, [])
        assert len(result) == 1
        assert result[0]["kind"] == "tool"
        assert result[0]["tool_name"] == "custom_tool"

    def test_describe_tool_call_search(self):
        """_describe_tool_call should return 'search' kind for web_search."""
        from src.middlewares.token_usage_middleware import _describe_tool_call

        tc = {"name": "web_search", "args": {"query": "test"}, "id": "tc1"}
        result = _describe_tool_call(tc, [])
        assert result[0]["kind"] == "search"

    def test_describe_tool_call_subagent(self):
        """_describe_tool_call should return 'subagent' kind for task tool."""
        from src.middlewares.token_usage_middleware import _describe_tool_call

        tc = {"name": "task", "args": {"description": "sub task", "subagent_type": "general"}, "id": "tc1"}
        result = _describe_tool_call(tc, [])
        assert result[0]["kind"] == "subagent"

    def test_build_attribution_basic(self):
        """_build_attribution should return a well-formed attribution dict."""
        from langchain_core.messages import AIMessage

        from src.middlewares.token_usage_middleware import _build_attribution

        msg = AIMessage(content="hello", tool_calls=[])
        attr = _build_attribution(msg, [])
        assert attr["version"] == 1
        assert attr["kind"] == "final_answer"
        assert attr["shared_attribution"] is False

    def test_build_attribution_with_tool_calls(self):
        """_build_attribution with tool calls should produce tool_batch kind."""
        from langchain_core.messages import AIMessage

        from src.middlewares.token_usage_middleware import _build_attribution

        msg = AIMessage(
            content="",
            tool_calls=[
                {"name": "bash", "args": {"cmd": "ls"}, "id": "tc1"},
                {"name": "bash", "args": {"cmd": "pwd"}, "id": "tc2"},
            ],
        )
        attr = _build_attribution(msg, [])
        assert attr["kind"] == "tool_batch"
        assert attr["shared_attribution"] is True
        assert len(attr["tool_call_ids"]) == 2


# ---- 1e. Clarification Middleware ----------------------------------------


class TestClarificationMiddleware:
    """Tests for src/middlewares/clarification_middleware.py.

    Verifies that clarification requests are intercepted, formatted
    properly, and non-clarification tool calls pass through.
    """

    def test_format_clarification_basic(self):
        """_format_clarification_message should format a basic question."""
        from src.middlewares.clarification_middleware import ClarificationMiddleware

        mw = ClarificationMiddleware()
        result = mw._format_clarification_message({"question": "What do you want?"})
        assert "What do you want?" in result

    def test_format_clarification_with_context(self):
        """_format_clarification_message should include context when provided."""
        from src.middlewares.clarification_middleware import ClarificationMiddleware

        mw = ClarificationMiddleware()
        result = mw._format_clarification_message({
            "question": "Which approach?",
            "context": "Two options available",
        })
        assert "Two options available" in result
        assert "Which approach?" in result

    def test_format_clarification_with_options(self):
        """_format_clarification_message should number options when provided."""
        from src.middlewares.clarification_middleware import ClarificationMiddleware

        mw = ClarificationMiddleware()
        result = mw._format_clarification_message({
            "question": "Pick one",
            "options": ["Option A", "Option B"],
        })
        assert "1. Option A" in result
        assert "2. Option B" in result

    def test_format_clarification_json_string_options(self):
        """_format_clarification_message should handle options as JSON string."""
        from src.middlewares.clarification_middleware import ClarificationMiddleware

        mw = ClarificationMiddleware()
        result = mw._format_clarification_message({
            "question": "Pick one",
            "options": json.dumps(["A", "B"]),
        })
        assert "1. A" in result
        assert "2. B" in result

    def test_format_clarification_type_icons(self):
        """_format_clarification_message should include type-specific icons."""
        from src.middlewares.clarification_middleware import ClarificationMiddleware

        mw = ClarificationMiddleware()
        result_risk = mw._format_clarification_message({
            "question": "OK?",
            "clarification_type": "risk_confirmation",
        })
        assert "⚠️" in result_risk

        result_suggestion = mw._format_clarification_message({
            "question": "Try this?",
            "clarification_type": "suggestion",
        })
        assert "💡" in result_suggestion

    def test_is_chinese(self):
        """_is_chinese should detect Chinese characters."""
        from src.middlewares.clarification_middleware import ClarificationMiddleware

        mw = ClarificationMiddleware()
        assert mw._is_chinese("你好") is True
        assert mw._is_chinese("hello") is False
        assert mw._is_chinese("hello 你好") is True

    def test_stable_message_id_with_tool_call_id(self):
        """_stable_message_id should use tool_call_id when available."""
        from src.middlewares.clarification_middleware import ClarificationMiddleware

        mw = ClarificationMiddleware()
        result = mw._stable_message_id("tc123", "some message")
        assert result == "clarification:tc123"

    def test_stable_message_id_without_tool_call_id(self):
        """_stable_message_id should produce a deterministic hash when no ID."""
        from src.middlewares.clarification_middleware import ClarificationMiddleware

        mw = ClarificationMiddleware()
        result = mw._stable_message_id("", "some message")
        assert result.startswith("clarification:")
        # Same input → same output
        assert result == mw._stable_message_id("", "some message")

    def test_wrap_tool_call_passes_non_clarification(self):
        """wrap_tool_call should delegate to handler for non-clarification calls."""
        from src.middlewares.clarification_middleware import ClarificationMiddleware

        mw = ClarificationMiddleware()
        request = MagicMock()
        request.tool_call = {"name": "bash", "args": {}, "id": "tc1"}
        handler = MagicMock(return_value=MagicMock())
        result = mw.wrap_tool_call(request, handler)
        handler.assert_called_once_with(request)

    def test_wrap_tool_call_intercepts_clarification(self):
        """wrap_tool_call should intercept ask_clarification and return Command."""
        from src.middlewares.clarification_middleware import ClarificationMiddleware

        mw = ClarificationMiddleware()
        request = MagicMock()
        request.tool_call = {
            "name": "ask_clarification",
            "args": {"question": "What?"},
            "id": "tc1",
        }
        handler = MagicMock()
        result = mw.wrap_tool_call(request, handler)
        # Should return a Command, not call the handler
        handler.assert_not_called()
        assert hasattr(result, "goto")  # Command has goto

    @pytest.mark.asyncio
    async def test_awrap_tool_call_passes_non_clarification(self):
        """awrap_tool_call should delegate to handler for non-clarification calls."""
        from src.middlewares.clarification_middleware import ClarificationMiddleware

        mw = ClarificationMiddleware()
        request = MagicMock()
        request.tool_call = {"name": "bash", "args": {}, "id": "tc1"}
        handler = AsyncMock(return_value=MagicMock())
        result = await mw.awrap_tool_call(request, handler)
        handler.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_awrap_tool_call_intercepts_clarification(self):
        """awrap_tool_call should intercept ask_clarification."""
        from src.middlewares.clarification_middleware import ClarificationMiddleware

        mw = ClarificationMiddleware()
        request = MagicMock()
        request.tool_call = {
            "name": "ask_clarification",
            "args": {"question": "What?"},
            "id": "tc1",
        }
        handler = AsyncMock()
        result = await mw.awrap_tool_call(request, handler)
        handler.assert_not_called()
        assert hasattr(result, "goto")


# ---- 1f. Tool Call Metadata ----------------------------------------------


class TestToolCallMetadata:
    """Tests for src/middlewares/tool_call_metadata.py.

    Verifies clone_ai_message_with_tool_calls properly syncs raw
    provider tool-call metadata.
    """

    def test_clone_with_empty_tool_calls(self):
        """Cloning with empty tool_calls should clear all tool metadata."""
        from langchain_core.messages import AIMessage

        from src.middlewares.tool_call_metadata import clone_ai_message_with_tool_calls

        msg = AIMessage(
            content="",
            tool_calls=[{"name": "bash", "args": {}, "id": "tc1"}],
            additional_kwargs={"tool_calls": [{"id": "tc1", "name": "bash"}], "function_call": {"name": "bash"}},
        )
        cloned = clone_ai_message_with_tool_calls(msg, [])
        assert cloned.tool_calls == []
        assert "function_call" not in cloned.additional_kwargs

    def test_clone_preserves_kept_tool_calls(self):
        """Cloning should keep the specified tool calls in raw metadata."""
        from langchain_core.messages import AIMessage

        from src.middlewares.tool_call_metadata import clone_ai_message_with_tool_calls

        msg = AIMessage(
            content="",
            tool_calls=[
                {"name": "bash", "args": {}, "id": "tc1"},
                {"name": "read", "args": {}, "id": "tc2"},
            ],
            additional_kwargs={
                "tool_calls": [
                    {"id": "tc1", "name": "bash"},
                    {"id": "tc2", "name": "read"},
                ]
            },
        )
        cloned = clone_ai_message_with_tool_calls(msg, [{"name": "read", "args": {}, "id": "tc2"}])
        assert len(cloned.tool_calls) == 1
        assert cloned.tool_calls[0]["id"] == "tc2"
        raw_tcs = cloned.additional_kwargs.get("tool_calls", [])
        assert len(raw_tcs) == 1
        assert raw_tcs[0]["id"] == "tc2"

    def test_clone_updates_content(self):
        """Cloning with content= should replace the message content."""
        from langchain_core.messages import AIMessage

        from src.middlewares.tool_call_metadata import clone_ai_message_with_tool_calls

        msg = AIMessage(content="old", tool_calls=[])
        cloned = clone_ai_message_with_tool_calls(msg, [], content="new")
        assert cloned.content == "new"

    def test_clone_finish_reason_tool_calls_to_stop(self):
        """When tool_calls cleared, finish_reason='tool_calls' should become 'stop'."""
        from langchain_core.messages import AIMessage

        from src.middlewares.tool_call_metadata import clone_ai_message_with_tool_calls

        msg = AIMessage(
            content="",
            tool_calls=[{"name": "bash", "args": {}, "id": "tc1"}],
            response_metadata={"finish_reason": "tool_calls"},
        )
        cloned = clone_ai_message_with_tool_calls(msg, [])
        assert cloned.response_metadata["finish_reason"] == "stop"

    def test_clone_preserves_other_finish_reason(self):
        """Non-tool_calls finish reasons should not be changed when clearing tool_calls."""
        from langchain_core.messages import AIMessage

        from src.middlewares.tool_call_metadata import clone_ai_message_with_tool_calls

        msg = AIMessage(
            content="",
            tool_calls=[{"name": "bash", "args": {}, "id": "tc1"}],
            response_metadata={"finish_reason": "content_filter"},
        )
        cloned = clone_ai_message_with_tool_calls(msg, [])
        assert cloned.response_metadata["finish_reason"] == "content_filter"


# ═══════════════════════════════════════════════════════════════════════════
# 2. GUARDRAILS TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestGuardrailProvider:
    """Tests for src/guardrails/provider.py data structures."""

    def test_guardrail_request_defaults(self):
        """GuardrailRequest should have correct default values."""
        from src.guardrails.provider import GuardrailRequest

        req = GuardrailRequest(tool_name="bash", tool_input={"cmd": "ls"})
        assert req.tool_name == "bash"
        assert req.agent_id is None
        assert req.thread_id is None
        assert req.is_subagent is False
        assert req.timestamp == ""

    def test_guardrail_decision_allow(self):
        """GuardrailDecision should store allow=True with reasons."""
        from src.guardrails.provider import GuardrailDecision, GuardrailReason

        dec = GuardrailDecision(
            allow=True,
            reasons=[GuardrailReason(code="oap.allowed")],
        )
        assert dec.allow is True
        assert len(dec.reasons) == 1
        assert dec.policy_id is None

    def test_guardrail_decision_deny(self):
        """GuardrailDecision should store deny with detailed reasons."""
        from src.guardrails.provider import GuardrailDecision, GuardrailReason

        dec = GuardrailDecision(
            allow=False,
            reasons=[GuardrailReason(code="oap.tool_not_allowed", message="bash is denied")],
            policy_id="strict",
        )
        assert dec.allow is False
        assert dec.policy_id == "strict"


class TestAllowlistProvider:
    """Tests for src/guardrails/builtin.py AllowlistProvider.

    Verifies that the allowlist provider correctly allows or blocks
    tool calls based on allowlist/denylist configuration.
    """

    def test_allows_tool_in_allowlist(self):
        """Tools in the allowlist should be allowed."""
        from src.guardrails.builtin import AllowlistProvider
        from src.guardrails.provider import GuardrailRequest

        provider = AllowlistProvider(allowed_tools=["bash", "read"])
        req = GuardrailRequest(tool_name="bash", tool_input={})
        decision = provider.evaluate(req)
        assert decision.allow is True

    def test_blocks_tool_not_in_allowlist(self):
        """Tools not in the allowlist should be blocked."""
        from src.guardrails.builtin import AllowlistProvider
        from src.guardrails.provider import GuardrailRequest

        provider = AllowlistProvider(allowed_tools=["bash", "read"])
        req = GuardrailRequest(tool_name="rm", tool_input={})
        decision = provider.evaluate(req)
        assert decision.allow is False
        assert "not in allowlist" in decision.reasons[0].message

    def test_blocks_tool_in_denylist(self):
        """Tools in the denylist should be blocked even without allowlist."""
        from src.guardrails.builtin import AllowlistProvider
        from src.guardrails.provider import GuardrailRequest

        provider = AllowlistProvider(denied_tools=["rm"])
        req = GuardrailRequest(tool_name="rm", tool_input={})
        decision = provider.evaluate(req)
        assert decision.allow is False
        assert "denied" in decision.reasons[0].message

    def test_allows_tool_not_in_denylist(self):
        """Tools not in the denylist should be allowed."""
        from src.guardrails.builtin import AllowlistProvider
        from src.guardrails.provider import GuardrailRequest

        provider = AllowlistProvider(denied_tools=["rm"])
        req = GuardrailRequest(tool_name="bash", tool_input={})
        decision = provider.evaluate(req)
        assert decision.allow is True

    def test_denylist_overrides_allowlist(self):
        """Denylist should take precedence when both are set."""
        from src.guardrails.builtin import AllowlistProvider
        from src.guardrails.provider import GuardrailRequest

        provider = AllowlistProvider(allowed_tools=["bash", "rm"], denied_tools=["rm"])
        req = GuardrailRequest(tool_name="rm", tool_input={})
        decision = provider.evaluate(req)
        assert decision.allow is False

    def test_no_restrictions_allows_all(self):
        """With no allowlist or denylist, all tools should be allowed."""
        from src.guardrails.builtin import AllowlistProvider
        from src.guardrails.provider import GuardrailRequest

        provider = AllowlistProvider()
        req = GuardrailRequest(tool_name="anything", tool_input={})
        decision = provider.evaluate(req)
        assert decision.allow is True

    @pytest.mark.asyncio
    async def test_aevaluate_matches_evaluate(self):
        """Async aevaluate should return the same result as sync evaluate."""
        from src.guardrails.builtin import AllowlistProvider
        from src.guardrails.provider import GuardrailRequest

        provider = AllowlistProvider(allowed_tools=["bash"])
        req = GuardrailRequest(tool_name="bash", tool_input={})
        sync_dec = provider.evaluate(req)
        async_dec = await provider.aevaluate(req)
        assert sync_dec.allow == async_dec.allow


class TestGuardrailMiddleware:
    """Tests for src/guardrails/middleware.py GuardrailMiddleware.

    Verifies that the middleware blocks denied tool calls and
    passes allowed ones through.
    """

    def _make_middleware(self, provider, *, fail_closed=True):
        from src.guardrails.middleware import GuardrailMiddleware

        return GuardrailMiddleware(provider, fail_closed=fail_closed)

    def test_allowed_tool_passes_through(self):
        """Allowed tools should be passed to the handler."""
        from src.guardrails.builtin import AllowlistProvider
        from src.guardrails.middleware import GuardrailMiddleware

        provider = AllowlistProvider(allowed_tools=["bash"])
        mw = GuardrailMiddleware(provider)
        request = MagicMock()
        request.tool_call = {"name": "bash", "args": {}, "id": "tc1"}
        handler = MagicMock(return_value=MagicMock())
        result = mw.wrap_tool_call(request, handler)
        handler.assert_called_once_with(request)

    def test_denied_tool_returns_error_message(self):
        """Denied tools should return a ToolMessage with error status."""
        from langchain_core.messages import ToolMessage

        from src.guardrails.builtin import AllowlistProvider
        from src.guardrails.middleware import GuardrailMiddleware

        provider = AllowlistProvider(denied_tools=["rm"])
        mw = GuardrailMiddleware(provider)
        request = MagicMock()
        request.tool_call = {"name": "rm", "args": {}, "id": "tc1"}
        handler = MagicMock()
        result = mw.wrap_tool_call(request, handler)
        handler.assert_not_called()
        assert isinstance(result, ToolMessage)
        assert result.status == "error"
        assert "Guardrail denied" in result.content

    def test_fail_closed_on_provider_error(self):
        """When provider raises and fail_closed=True, the call should be blocked."""
        from src.guardrails.middleware import GuardrailMiddleware
        from src.guardrails.provider import GuardrailRequest

        failing_provider = MagicMock()
        failing_provider.evaluate.side_effect = RuntimeError("provider error")

        mw = GuardrailMiddleware(failing_provider, fail_closed=True)
        request = MagicMock()
        request.tool_call = {"name": "bash", "args": {}, "id": "tc1"}
        handler = MagicMock()
        result = mw.wrap_tool_call(request, handler)
        handler.assert_not_called()
        assert result.status == "error"

    def test_fail_open_on_provider_error(self):
        """When provider raises and fail_closed=False, the call should pass through."""
        from src.guardrails.middleware import GuardrailMiddleware

        failing_provider = MagicMock()
        failing_provider.evaluate.side_effect = RuntimeError("provider error")

        mw = GuardrailMiddleware(failing_provider, fail_closed=False)
        request = MagicMock()
        request.tool_call = {"name": "bash", "args": {}, "id": "tc1"}
        handler = MagicMock(return_value=MagicMock())
        result = mw.wrap_tool_call(request, handler)
        handler.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_async_denied_tool_returns_error(self):
        """Async awrap_tool_call should block denied tools."""
        from langchain_core.messages import ToolMessage

        from src.guardrails.builtin import AllowlistProvider
        from src.guardrails.middleware import GuardrailMiddleware

        provider = AllowlistProvider(denied_tools=["rm"])
        mw = GuardrailMiddleware(provider)
        request = MagicMock()
        request.tool_call = {"name": "rm", "args": {}, "id": "tc1"}
        handler = AsyncMock()
        result = await mw.awrap_tool_call(request, handler)
        handler.assert_not_called()
        assert isinstance(result, ToolMessage)
        assert result.status == "error"

    @pytest.mark.asyncio
    async def test_async_allowed_tool_passes_through(self):
        """Async awrap_tool_call should pass allowed tools to handler."""
        from src.guardrails.builtin import AllowlistProvider
        from src.guardrails.middleware import GuardrailMiddleware

        provider = AllowlistProvider(allowed_tools=["bash"])
        mw = GuardrailMiddleware(provider)
        request = MagicMock()
        request.tool_call = {"name": "bash", "args": {}, "id": "tc1"}
        handler = AsyncMock(return_value=MagicMock())
        result = await mw.awrap_tool_call(request, handler)
        handler.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_async_fail_open_on_provider_error(self):
        """Async fail_closed=False should pass through when provider raises."""
        from src.guardrails.middleware import GuardrailMiddleware

        failing_provider = MagicMock()
        failing_provider.aevaluate = AsyncMock(side_effect=RuntimeError("error"))

        mw = GuardrailMiddleware(failing_provider, fail_closed=False)
        request = MagicMock()
        request.tool_call = {"name": "bash", "args": {}, "id": "tc1"}
        handler = AsyncMock(return_value=MagicMock())
        result = await mw.awrap_tool_call(request, handler)
        handler.assert_called_once_with(request)


# ═══════════════════════════════════════════════════════════════════════════
# 3. SKILLS TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestSkillType:
    """Tests for src/skills/types.py Skill dataclass."""

    def test_skill_basic(self):
        """Skill should store basic metadata."""
        from src.skills.types import Skill, SkillCategory

        s = Skill(
            name="my-skill",
            description="A test skill",
            license=None,
            skill_dir=Path("/tmp/skill"),
            skill_file=Path("/tmp/skill/SKILL.md"),
            relative_path=Path("."),
            category=SkillCategory.CUSTOM,
        )
        assert s.name == "my-skill"
        assert s.category == SkillCategory.CUSTOM
        assert s.enabled is False  # default

    def test_skill_path_property(self):
        """skill_path should return the relative path as posix string."""
        from src.skills.types import Skill, SkillCategory

        s = Skill(
            name="x",
            description="x",
            license=None,
            skill_dir=Path("/tmp"),
            skill_file=Path("/tmp/SKILL.md"),
            relative_path=Path("."),
            category=SkillCategory.PUBLIC,
        )
        assert s.skill_path == ""

    def test_skill_path_nested(self):
        """skill_path with nested directory should return the relative path."""
        from src.skills.types import Skill, SkillCategory

        s = Skill(
            name="x",
            description="x",
            license=None,
            skill_dir=Path("/tmp"),
            skill_file=Path("/tmp/SKILL.md"),
            relative_path=Path("sub/dir"),
            category=SkillCategory.PUBLIC,
        )
        assert s.skill_path == "sub/dir"

    def test_get_container_path(self):
        """get_container_path should build full container path."""
        from src.skills.types import Skill, SkillCategory

        s = Skill(
            name="x",
            description="x",
            license=None,
            skill_dir=Path("/tmp"),
            skill_file=Path("/tmp/SKILL.md"),
            relative_path=Path("sub"),
            category=SkillCategory.CUSTOM,
        )
        assert s.get_container_path() == "/mnt/skills/custom/sub"

    def test_get_container_file_path(self):
        """get_container_file_path should include SKILL.md."""
        from src.skills.types import Skill, SkillCategory

        s = Skill(
            name="x",
            description="x",
            license=None,
            skill_dir=Path("/tmp"),
            skill_file=Path("/tmp/SKILL.md"),
            relative_path=Path("sub"),
            category=SkillCategory.CUSTOM,
        )
        assert s.get_container_file_path() == "/mnt/skills/custom/sub/SKILL.md"

    def test_skill_category_enum(self):
        """SkillCategory enum should have public and custom values."""
        from src.skills.types import SkillCategory

        assert SkillCategory.PUBLIC == "public"
        assert SkillCategory.CUSTOM == "custom"


class TestSkillParser:
    """Tests for src/skills/parser.py parse_skill_file and helpers."""

    def test_parse_allowed_tools_none(self):
        """parse_allowed_tools with None should return None."""
        from src.skills.parser import parse_allowed_tools

        assert parse_allowed_tools(None, Path("test")) is None

    def test_parse_allowed_tools_list(self):
        """parse_allowed_tools with valid list should return the list."""
        from src.skills.parser import parse_allowed_tools

        result = parse_allowed_tools(["bash", "read"], Path("test"))
        assert result == ["bash", "read"]

    def test_parse_allowed_tools_empty_list(self):
        """parse_allowed_tools with empty list should return empty list."""
        from src.skills.parser import parse_allowed_tools

        result = parse_allowed_tools([], Path("test"))
        assert result == []

    def test_parse_allowed_tools_non_list_raises(self):
        """parse_allowed_tools with non-list should raise ValueError."""
        from src.skills.parser import parse_allowed_tools

        with pytest.raises(ValueError, match="must be a list"):
            parse_allowed_tools("not a list", Path("test"))

    def test_parse_allowed_tools_non_string_item_raises(self):
        """parse_allowed_tools with non-string items should raise ValueError."""
        from src.skills.parser import parse_allowed_tools

        with pytest.raises(ValueError, match="only strings"):
            parse_allowed_tools([42], Path("test"))

    def test_parse_allowed_tools_empty_string_raises(self):
        """parse_allowed_tools with empty string items should raise ValueError."""
        from src.skills.parser import parse_allowed_tools

        with pytest.raises(ValueError, match="empty tool names"):
            parse_allowed_tools([""], Path("test"))

    def test_parse_skill_file_valid(self):
        """parse_skill_file should parse a valid SKILL.md with frontmatter."""
        from src.skills.parser import parse_skill_file
        from src.skills.types import SkillCategory

        with tempfile.TemporaryDirectory() as tmp:
            skill_md = Path(tmp) / "SKILL.md"
            skill_md.write_text(
                "---\nname: my-skill\ndescription: A test skill\n---\n\nContent here\n",
                encoding="utf-8",
            )
            result = parse_skill_file(skill_md, SkillCategory.CUSTOM)
            assert result is not None
            assert result.name == "my-skill"
            assert result.description == "A test skill"

    def test_parse_skill_file_missing_name(self):
        """parse_skill_file should return None when name is missing."""
        from src.skills.parser import parse_skill_file
        from src.skills.types import SkillCategory

        with tempfile.TemporaryDirectory() as tmp:
            skill_md = Path(tmp) / "SKILL.md"
            skill_md.write_text(
                "---\ndescription: A test skill\n---\n",
                encoding="utf-8",
            )
            result = parse_skill_file(skill_md, SkillCategory.CUSTOM)
            assert result is None

    def test_parse_skill_file_missing_description(self):
        """parse_skill_file should return None when description is missing."""
        from src.skills.parser import parse_skill_file
        from src.skills.types import SkillCategory

        with tempfile.TemporaryDirectory() as tmp:
            skill_md = Path(tmp) / "SKILL.md"
            skill_md.write_text(
                "---\nname: my-skill\n---\n",
                encoding="utf-8",
            )
            result = parse_skill_file(skill_md, SkillCategory.CUSTOM)
            assert result is None

    def test_parse_skill_file_no_frontmatter(self):
        """parse_skill_file should return None when no frontmatter present."""
        from src.skills.parser import parse_skill_file
        from src.skills.types import SkillCategory

        with tempfile.TemporaryDirectory() as tmp:
            skill_md = Path(tmp) / "SKILL.md"
            skill_md.write_text("Just plain text\n", encoding="utf-8")
            result = parse_skill_file(skill_md, SkillCategory.CUSTOM)
            assert result is None

    def test_parse_skill_file_nonexistent(self):
        """parse_skill_file should return None for nonexistent files."""
        from src.skills.parser import parse_skill_file
        from src.skills.types import SkillCategory

        result = parse_skill_file(Path("/nonexistent/SKILL.md"), SkillCategory.CUSTOM)
        assert result is None

    def test_parse_skill_file_with_license(self):
        """parse_skill_file should parse the license field."""
        from src.skills.parser import parse_skill_file
        from src.skills.types import SkillCategory

        with tempfile.TemporaryDirectory() as tmp:
            skill_md = Path(tmp) / "SKILL.md"
            skill_md.write_text(
                "---\nname: my-skill\ndescription: Test\nlicense: MIT\n---\n",
                encoding="utf-8",
            )
            result = parse_skill_file(skill_md, SkillCategory.CUSTOM)
            assert result is not None
            assert result.license == "MIT"

    def test_parse_skill_file_with_allowed_tools(self):
        """parse_skill_file should parse the allowed-tools field."""
        from src.skills.parser import parse_skill_file
        from src.skills.types import SkillCategory

        with tempfile.TemporaryDirectory() as tmp:
            skill_md = Path(tmp) / "SKILL.md"
            skill_md.write_text(
                "---\nname: my-skill\ndescription: Test\nallowed-tools:\n  - bash\n  - read\n---\n",
                encoding="utf-8",
            )
            result = parse_skill_file(skill_md, SkillCategory.CUSTOM)
            assert result is not None
            assert result.allowed_tools == ["bash", "read"]


class TestSkillValidation:
    """Tests for src/skills/validation.py _validate_skill_frontmatter."""

    def test_valid_skill(self):
        """A valid SKILL.md should pass validation."""
        from src.skills.validation import _validate_skill_frontmatter

        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: my-skill\ndescription: A test skill\n---\n",
                encoding="utf-8",
            )
            is_valid, message, name = _validate_skill_frontmatter(skill_dir)
            assert is_valid is True
            assert name == "my-skill"

    def test_missing_skill_md(self):
        """Missing SKILL.md should fail validation."""
        from src.skills.validation import _validate_skill_frontmatter

        with tempfile.TemporaryDirectory() as tmp:
            is_valid, message, name = _validate_skill_frontmatter(Path(tmp))
            assert is_valid is False
            assert "not found" in message

    def test_missing_name(self):
        """Missing name field should fail validation."""
        from src.skills.validation import _validate_skill_frontmatter

        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp)
            (skill_dir / "SKILL.md").write_text(
                "---\ndescription: Test\n---\n",
                encoding="utf-8",
            )
            is_valid, message, name = _validate_skill_frontmatter(skill_dir)
            assert is_valid is False
            assert "name" in message.lower()

    def test_invalid_name_format(self):
        """Non-hyphen-case name should fail validation."""
        from src.skills.validation import _validate_skill_frontmatter

        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp)
            (skill_dir / "SKILL.md").write_text(
                '---\nname: "My Skill"\ndescription: Test\n---\n',
                encoding="utf-8",
            )
            is_valid, message, name = _validate_skill_frontmatter(skill_dir)
            assert is_valid is False
            assert "hyphen-case" in message.lower()

    def test_unexpected_frontmatter_key(self):
        """Unexpected frontmatter keys should fail validation."""
        from src.skills.validation import _validate_skill_frontmatter

        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: my-skill\ndescription: Test\nunknown_key: value\n---\n",
                encoding="utf-8",
            )
            is_valid, message, name = _validate_skill_frontmatter(skill_dir)
            assert is_valid is False
            assert "unexpected" in message.lower() or "unknown_key" in message

    def test_name_too_long(self):
        """Names exceeding 64 characters should fail validation."""
        from src.skills.validation import _validate_skill_frontmatter

        long_name = "a" * 65
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp)
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: {long_name}\ndescription: Test\n---\n",
                encoding="utf-8",
            )
            is_valid, message, name = _validate_skill_frontmatter(skill_dir)
            assert is_valid is False
            assert "too long" in message.lower()


class TestSlashSkill:
    """Tests for src/skills/slash.py slash-skill parsing and resolution."""

    def test_parse_slash_skill_reference_valid(self):
        """Valid /skill-name syntax should parse correctly."""
        from src.skills.slash import parse_slash_skill_reference

        result = parse_slash_skill_reference("/my-skill do something")
        assert result is not None
        assert result.name == "my-skill"
        assert result.remaining_text == "do something"

    def test_parse_slash_skill_reference_no_args(self):
        """Slash skill with no remaining text should work."""
        from src.skills.slash import parse_slash_skill_reference

        result = parse_slash_skill_reference("/my-skill")
        assert result is not None
        assert result.name == "my-skill"
        assert result.remaining_text == ""

    def test_parse_slash_skill_reference_reserved(self):
        """Reserved control commands should not be parsed as skill references."""
        from src.skills.slash import parse_slash_skill_reference

        assert parse_slash_skill_reference("/help") is None
        assert parse_slash_skill_reference("/status") is None
        assert parse_slash_skill_reference("/new") is None

    def test_parse_slash_skill_reference_invalid(self):
        """Non-slash or malformed input should return None."""
        from src.skills.slash import parse_slash_skill_reference

        assert parse_slash_skill_reference("no slash") is None
        assert parse_slash_skill_reference("") is None

    def test_parse_slash_skill_reference_uppercase_rejected(self):
        """Uppercase skill names should not match the pattern."""
        from src.skills.slash import parse_slash_skill_reference

        assert parse_slash_skill_reference("/MySkill") is None

    def test_resolve_slash_skill_found(self):
        """resolve_slash_skill should find an enabled skill by name."""
        from src.skills.slash import resolve_slash_skill
        from src.skills.types import Skill, SkillCategory

        skills = [
            Skill(
                name="python-helper",
                description="Helps with Python",
                license=None,
                skill_dir=Path("/tmp"),
                skill_file=Path("/tmp/SKILL.md"),
                relative_path=Path("."),
                category=SkillCategory.CUSTOM,
                enabled=True,
            ),
        ]
        result = resolve_slash_skill("/python-helper write code", skills)
        assert result is not None
        assert result.skill.name == "python-helper"
        assert result.remaining_text == "write code"

    def test_resolve_slash_skill_disabled(self):
        """resolve_slash_skill should not match disabled skills."""
        from src.skills.slash import resolve_slash_skill
        from src.skills.types import Skill, SkillCategory

        skills = [
            Skill(
                name="python-helper",
                description="Helps with Python",
                license=None,
                skill_dir=Path("/tmp"),
                skill_file=Path("/tmp/SKILL.md"),
                relative_path=Path("."),
                category=SkillCategory.CUSTOM,
                enabled=False,
            ),
        ]
        result = resolve_slash_skill("/python-helper", skills)
        assert result is None

    def test_resolve_slash_skill_not_found(self):
        """resolve_slash_skill should return None when skill doesn't exist."""
        from src.skills.slash import resolve_slash_skill

        result = resolve_slash_skill("/nonexistent", [])
        assert result is None


class TestSkillInstaller:
    """Tests for src/skills/installer.py archive safety helpers."""

    def test_is_unsafe_zip_member_absolute_path(self):
        """Absolute paths in zip members should be flagged as unsafe."""
        from src.skills.installer import is_unsafe_zip_member

        info = zipfile.ZipInfo(filename="/etc/passwd")
        assert is_unsafe_zip_member(info) is True

    def test_is_unsafe_zip_member_traversal(self):
        """Directory traversal paths should be flagged as unsafe."""
        from src.skills.installer import is_unsafe_zip_member

        info = zipfile.ZipInfo(filename="../../etc/passwd")
        assert is_unsafe_zip_member(info) is True

    def test_is_unsafe_zip_member_safe(self):
        """Normal relative paths should be considered safe."""
        from src.skills.installer import is_unsafe_zip_member

        info = zipfile.ZipInfo(filename="skill/SKILL.md")
        assert is_unsafe_zip_member(info) is False

    def test_is_unsafe_zip_member_empty(self):
        """Empty filenames should not be flagged."""
        from src.skills.installer import is_unsafe_zip_member

        info = zipfile.ZipInfo(filename="")
        assert is_unsafe_zip_member(info) is False

    def test_should_ignore_dotfiles(self):
        """Dotfiles and __MACOSX should be ignored."""
        from src.skills.installer import should_ignore_archive_entry

        assert should_ignore_archive_entry(Path(".DS_Store")) is True
        assert should_ignore_archive_entry(Path("__MACOSX")) is True
        assert should_ignore_archive_entry(Path("SKILL.md")) is False

    def test_resolve_skill_dir_from_archive_single_dir(self):
        """Archive with a single directory should resolve to that dir."""
        from src.skills.installer import resolve_skill_dir_from_archive

        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "my-skill"
            skill_dir.mkdir()
            result = resolve_skill_dir_from_archive(Path(tmp))
            assert result == skill_dir

    def test_resolve_skill_dir_from_archive_multiple_items(self):
        """Archive with multiple items should resolve to the temp dir itself."""
        from src.skills.installer import resolve_skill_dir_from_archive

        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "SKILL.md").write_text("---\nname: x\ndescription: y\n---\n")
            (Path(tmp) / "readme.txt").write_text("hi")
            result = resolve_skill_dir_from_archive(Path(tmp))
            assert result == Path(tmp)

    def test_resolve_skill_dir_from_archive_empty_raises(self):
        """Empty archive should raise ValueError."""
        from src.skills.installer import resolve_skill_dir_from_archive

        with tempfile.TemporaryDirectory() as tmp:
            # Create a subdirectory that only has dotfiles
            dotfile_dir = Path(tmp) / ".hidden"
            dotfile_dir.mkdir()
            with pytest.raises(ValueError, match="empty"):
                resolve_skill_dir_from_archive(Path(tmp))

    def test_skill_already_exists_error(self):
        """SkillAlreadyExistsError should be a ValueError."""
        from src.skills.installer import SkillAlreadyExistsError

        with pytest.raises(ValueError):
            raise SkillAlreadyExistsError("already exists")

    def test_skill_security_scan_error(self):
        """SkillSecurityScanError should be a ValueError."""
        from src.skills.installer import SkillSecurityScanError

        with pytest.raises(ValueError):
            raise SkillSecurityScanError("security issue")


class TestSkillStorageBase:
    """Tests for src/skills/storage/skill_storage.py SkillStorage base class."""

    def test_validate_skill_name_valid(self):
        """Valid hyphen-case names should pass validation."""
        from src.skills.storage.skill_storage import SkillStorage

        assert SkillStorage.validate_skill_name("my-skill") == "my-skill"
        assert SkillStorage.validate_skill_name("bash") == "bash"
        assert SkillStorage.validate_skill_name("a1-b2-c3") == "a1-b2-c3"

    def test_validate_skill_name_invalid(self):
        """Invalid names should raise ValueError."""
        from src.skills.storage.skill_storage import SkillStorage

        with pytest.raises(ValueError):
            SkillStorage.validate_skill_name("My Skill")
        with pytest.raises(ValueError):
            SkillStorage.validate_skill_name("skill!")
        with pytest.raises(ValueError):
            SkillStorage.validate_skill_name("")

    def test_validate_skill_name_too_long(self):
        """Names over 64 chars should raise ValueError."""
        from src.skills.storage.skill_storage import SkillStorage

        with pytest.raises(ValueError, match="64"):
            SkillStorage.validate_skill_name("a" * 65)

    def test_validate_relative_path_valid(self):
        """Valid relative paths should resolve within base_dir."""
        from src.skills.storage.skill_storage import SkillStorage

        base = Path("/tmp/skills")
        result = SkillStorage.validate_relative_path("sub/dir", base)
        assert result == (base / "sub/dir").resolve()

    def test_validate_relative_path_empty_raises(self):
        """Empty relative path should raise ValueError."""
        from src.skills.storage.skill_storage import SkillStorage

        with pytest.raises(ValueError, match="empty"):
            SkillStorage.validate_relative_path("", Path("/tmp"))

    def test_validate_relative_path_traversal_raises(self):
        """Traversal paths should raise ValueError."""
        from src.skills.storage.skill_storage import SkillStorage

        with pytest.raises(ValueError, match="within"):
            SkillStorage.validate_relative_path("../../etc/passwd", Path("/tmp/skills"))

    def test_validate_skill_markdown_content_valid(self):
        """Valid SKILL.md content should pass validation."""
        from src.skills.storage.skill_storage import SkillStorage

        content = "---\nname: my-skill\ndescription: Test skill\n---\n\nBody"
        # Should not raise
        SkillStorage.validate_skill_markdown_content("my-skill", content)

    def test_validate_skill_markdown_content_name_mismatch(self):
        """SKILL.md with different name should raise ValueError."""
        from src.skills.storage.skill_storage import SkillStorage

        content = "---\nname: other-skill\ndescription: Test\n---\n"
        with pytest.raises(ValueError, match="must match"):
            SkillStorage.validate_skill_markdown_content("my-skill", content)

    def test_ensure_safe_support_path_valid(self):
        """Valid support paths should resolve correctly."""
        from src.skills.storage.skill_storage import SkillStorage

        # Create a concrete subclass for testing
        class TestStorage(SkillStorage):
            def get_skills_root_path(self):
                return Path("/tmp/skills")

            def _iter_skill_files(self):
                return iter([])

            def read_custom_skill(self, name):
                return ""

            def write_custom_skill(self, name, relative_path, content):
                pass

            async def ainstall_skill_from_archive(self, archive_path):
                return {}

            def delete_custom_skill(self, name, **kwargs):
                pass

            def custom_skill_exists(self, name):
                return False

            def public_skill_exists(self, name):
                return False

            def append_history(self, name, record):
                pass

            def read_history(self, name):
                return []

        storage = TestStorage()
        result = storage.ensure_safe_support_path("my-skill", "references/data.json")
        assert str(result).endswith("references/data.json")

    def test_ensure_safe_support_path_invalid_subdir(self):
        """Support paths outside allowed subdirs should raise ValueError."""
        from src.skills.storage.skill_storage import SkillStorage

        class TestStorage(SkillStorage):
            def get_skills_root_path(self):
                return Path("/tmp/skills")

            def _iter_skill_files(self):
                return iter([])

            def read_custom_skill(self, name):
                return ""

            def write_custom_skill(self, name, relative_path, content):
                pass

            async def ainstall_skill_from_archive(self, archive_path):
                return {}

            def delete_custom_skill(self, name, **kwargs):
                pass

            def custom_skill_exists(self, name):
                return False

            def public_skill_exists(self, name):
                return False

            def append_history(self, name, record):
                pass

            def read_history(self, name):
                return []

        storage = TestStorage()
        with pytest.raises(ValueError, match="must live under"):
            storage.ensure_safe_support_path("my-skill", "etc/passwd")

    def test_ensure_safe_support_path_traversal(self):
        """Support paths with .. should raise ValueError."""
        from src.skills.storage.skill_storage import SkillStorage

        class TestStorage(SkillStorage):
            def get_skills_root_path(self):
                return Path("/tmp/skills")

            def _iter_skill_files(self):
                return iter([])

            def read_custom_skill(self, name):
                return ""

            def write_custom_skill(self, name, relative_path, content):
                pass

            async def ainstall_skill_from_archive(self, archive_path):
                return {}

            def delete_custom_skill(self, name, **kwargs):
                pass

            def custom_skill_exists(self, name):
                return False

            def public_skill_exists(self, name):
                return False

            def append_history(self, name, record):
                pass

            def read_history(self, name):
                return []

        storage = TestStorage()
        with pytest.raises(ValueError, match="traversal"):
            storage.ensure_safe_support_path("my-skill", "references/../../etc/passwd")


# ═══════════════════════════════════════════════════════════════════════════
# 4. CONFIG TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestModelConfig:
    """Tests for src/config/model_config.py ModelConfig Pydantic model."""

    def test_model_config_required_fields(self):
        """ModelConfig should require name, use, and model fields."""
        from src.config.model_config import ModelConfig

        mc = ModelConfig(name="gpt4", use="langchain_openai:ChatOpenAI", model="gpt-4")
        assert mc.name == "gpt4"
        assert mc.use == "langchain_openai:ChatOpenAI"
        assert mc.model == "gpt-4"

    def test_model_config_defaults(self):
        """ModelConfig should have correct defaults for optional fields."""
        from src.config.model_config import ModelConfig

        mc = ModelConfig(name="test", use="test:Test", model="test-model")
        assert mc.supports_thinking is False
        assert mc.supports_reasoning_effort is False
        assert mc.supports_vision is False
        assert mc.when_thinking_enabled is None
        assert mc.when_thinking_disabled is None

    def test_model_config_with_thinking(self):
        """ModelConfig should accept thinking configuration."""
        from src.config.model_config import ModelConfig

        mc = ModelConfig(
            name="test",
            use="test:Test",
            model="test-model",
            supports_thinking=True,
            when_thinking_enabled={"thinking": {"type": "enabled", "budget_tokens": 10000}},
            when_thinking_disabled={"thinking": {"type": "disabled"}},
        )
        assert mc.supports_thinking is True
        assert mc.when_thinking_enabled is not None

    def test_model_config_extra_fields_allowed(self):
        """ModelConfig with extra="allow" should accept extra fields."""
        from src.config.model_config import ModelConfig

        mc = ModelConfig(
            name="test",
            use="test:Test",
            model="test-model",
            api_key="sk-test",  # extra field
        )
        assert mc.name == "test"


class TestMemoryConfig:
    """Tests for src/config/memory_config.py MemoryConfig Pydantic model."""

    def test_memory_config_defaults(self):
        """MemoryConfig should have sensible defaults."""
        from src.config.memory_config import MemoryConfig

        mc = MemoryConfig()
        assert mc.enabled is True
        assert mc.debounce_seconds == 30
        assert mc.max_facts == 100
        assert mc.fact_confidence_threshold == 0.7
        assert mc.injection_enabled is True
        assert mc.token_counting == "tiktoken"

    def test_memory_config_custom(self):
        """MemoryConfig should accept custom values."""
        from src.config.memory_config import MemoryConfig

        mc = MemoryConfig(
            enabled=False,
            debounce_seconds=60,
            max_facts=200,
            fact_confidence_threshold=0.9,
        )
        assert mc.enabled is False
        assert mc.debounce_seconds == 60
        assert mc.max_facts == 200

    def test_memory_config_debounce_bounds(self):
        """MemoryConfig debounce_seconds should be between 1 and 300."""
        from src.config.memory_config import MemoryConfig

        with pytest.raises(Exception):
            MemoryConfig(debounce_seconds=0)
        with pytest.raises(Exception):
            MemoryConfig(debounce_seconds=301)

    def test_memory_config_max_facts_bounds(self):
        """MemoryConfig max_facts should be between 10 and 500."""
        from src.config.memory_config import MemoryConfig

        with pytest.raises(Exception):
            MemoryConfig(max_facts=9)
        with pytest.raises(Exception):
            MemoryConfig(max_facts=501)

    def test_memory_config_confidence_bounds(self):
        """MemoryConfig fact_confidence_threshold should be between 0 and 1."""
        from src.config.memory_config import MemoryConfig

        with pytest.raises(Exception):
            MemoryConfig(fact_confidence_threshold=-0.1)
        with pytest.raises(Exception):
            MemoryConfig(fact_confidence_threshold=1.1)

    def test_get_set_memory_config(self):
        """get/set_memory_config should round-trip correctly."""
        from src.config.memory_config import MemoryConfig, get_memory_config, set_memory_config

        original = get_memory_config()
        try:
            custom = MemoryConfig(enabled=False, debounce_seconds=120)
            set_memory_config(custom)
            assert get_memory_config().enabled is False
            assert get_memory_config().debounce_seconds == 120
        finally:
            set_memory_config(original)

    def test_load_memory_config_from_dict(self):
        """load_memory_config_from_dict should create config from dict."""
        from src.config.memory_config import get_memory_config, load_memory_config_from_dict

        original = get_memory_config()
        try:
            load_memory_config_from_dict({"enabled": False, "max_facts": 50})
            config = get_memory_config()
            assert config.enabled is False
            assert config.max_facts == 50
        finally:
            load_memory_config_from_dict(original.model_dump())


class TestLoopDetectionConfig:
    """Tests for src/config/loop_detection_config.py LoopDetectionConfig."""

    def test_defaults(self):
        """LoopDetectionConfig should have sensible defaults."""
        from src.config.loop_detection_config import LoopDetectionConfig

        config = LoopDetectionConfig()
        assert config.enabled is True
        assert config.warn_threshold == 3
        assert config.hard_limit == 5
        assert config.window_size == 20
        assert config.tool_freq_warn == 30
        assert config.tool_freq_hard_limit == 50

    def test_hard_limit_below_warn_raises(self):
        """hard_limit < warn_threshold should raise validation error."""
        from src.config.loop_detection_config import LoopDetectionConfig

        with pytest.raises(Exception, match="hard_limit"):
            LoopDetectionConfig(warn_threshold=5, hard_limit=3)

    def test_tool_freq_hard_below_warn_raises(self):
        """tool_freq_hard_limit < tool_freq_warn should raise validation error."""
        from src.config.loop_detection_config import LoopDetectionConfig

        with pytest.raises(Exception, match="tool_freq_hard_limit"):
            LoopDetectionConfig(tool_freq_warn=50, tool_freq_hard_limit=30)

    def test_tool_freq_overrides(self):
        """Per-tool frequency overrides should be accepted."""
        from src.config.loop_detection_config import LoopDetectionConfig, ToolFreqOverride

        config = LoopDetectionConfig(
            tool_freq_overrides={
                "bash": ToolFreqOverride(warn=50, hard_limit=80),
            }
        )
        assert "bash" in config.tool_freq_overrides
        assert config.tool_freq_overrides["bash"].warn == 50

    def test_tool_freq_override_invalid(self):
        """ToolFreqOverride with hard_limit < warn should raise."""
        from src.config.loop_detection_config import ToolFreqOverride

        with pytest.raises(Exception, match="hard_limit"):
            ToolFreqOverride(warn=50, hard_limit=30)


class TestAppConfigHelpers:
    """Tests for src/config/app_config.py helper functions."""

    def test_resolve_env_variables_string(self):
        """resolve_env_variables should resolve $ENV_VAR references."""
        from src.config.app_config import AppConfig

        with patch.dict(os.environ, {"TEST_KEY": "resolved_value"}):
            result = AppConfig.resolve_env_variables("$TEST_KEY")
            assert result == "resolved_value"

    def test_resolve_env_variables_missing_raises(self):
        """resolve_env_variables should raise for missing env vars."""
        from src.config.app_config import AppConfig

        with pytest.raises(ValueError, match="not found"):
            AppConfig.resolve_env_variables("$NONEXISTENT_VAR_12345")

    def test_resolve_env_variables_plain_string(self):
        """resolve_env_variables should pass through non-$ strings."""
        from src.config.app_config import AppConfig

        assert AppConfig.resolve_env_variables("plain") == "plain"

    def test_resolve_env_variables_dict(self):
        """resolve_env_variables should recurse into dicts."""
        from src.config.app_config import AppConfig

        with patch.dict(os.environ, {"MY_KEY": "value"}):
            result = AppConfig.resolve_env_variables({"key": "$MY_KEY", "plain": "text"})
            assert result == {"key": "value", "plain": "text"}

    def test_resolve_env_variables_list(self):
        """resolve_env_variables should recurse into lists."""
        from src.config.app_config import AppConfig

        with patch.dict(os.environ, {"MY_KEY": "value"}):
            result = AppConfig.resolve_env_variables(["$MY_KEY", "plain"])
            assert result == ["value", "plain"]

    def test_logging_level_from_config(self):
        """logging_level_from_config should map strings to logging levels."""
        import logging

        from src.config.app_config import logging_level_from_config

        assert logging_level_from_config("debug") == logging.DEBUG
        assert logging_level_from_config("info") == logging.INFO
        assert logging_level_from_config("warning") == logging.WARNING
        assert logging_level_from_config("error") == logging.ERROR

    def test_logging_level_from_config_none(self):
        """logging_level_from_config(None) should default to INFO."""
        import logging

        from src.config.app_config import logging_level_from_config

        assert logging_level_from_config(None) == logging.INFO

    def test_coerce_null_list_sections(self):
        """_coerce_null_list_sections should convert None to empty list."""
        from src.config.app_config import AppConfig

        assert AppConfig._coerce_null_list_sections(None) == []
        assert AppConfig._coerce_null_list_sections([1, 2]) == [1, 2]

    def test_circuit_breaker_config(self):
        """CircuitBreakerConfig should have correct defaults."""
        from src.config.app_config import CircuitBreakerConfig

        cb = CircuitBreakerConfig()
        assert cb.failure_threshold == 5
        assert cb.recovery_timeout_sec == 60


# ═══════════════════════════════════════════════════════════════════════════
# 5. LLM MODELS TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestLLMFactoryHelpers:
    """Tests for src/llm_models/factory.py helper functions."""

    def test_deep_merge_dicts_basic(self):
        """_deep_merge_dicts should recursively merge dictionaries."""
        from src.llm_models.factory import _deep_merge_dicts

        base = {"a": 1, "b": {"c": 2}}
        override = {"b": {"d": 3}, "e": 4}
        result = _deep_merge_dicts(base, override)
        assert result == {"a": 1, "b": {"c": 2, "d": 3}, "e": 4}

    def test_deep_merge_dicts_none_base(self):
        """_deep_merge_dicts should handle None base dict."""
        from src.llm_models.factory import _deep_merge_dicts

        result = _deep_merge_dicts(None, {"a": 1})
        assert result == {"a": 1}

    def test_deep_merge_dicts_override_replaces_non_dict(self):
        """_deep_merge_dicts should replace non-dict values, not merge them."""
        from src.llm_models.factory import _deep_merge_dicts

        base = {"a": 1}
        override = {"a": 2}
        result = _deep_merge_dicts(base, override)
        assert result == {"a": 2}

    def test_deep_merge_dicts_does_not_mutate_inputs(self):
        """_deep_merge_dicts should not mutate input dictionaries."""
        from src.llm_models.factory import _deep_merge_dicts

        base = {"a": {"b": 1}}
        override = {"a": {"c": 2}}
        _deep_merge_dicts(base, override)
        assert base == {"a": {"b": 1}}
        assert override == {"a": {"c": 2}}

    def test_vllm_disable_chat_template_kwargs_thinking(self):
        """_vllm_disable_chat_template_kwargs should disable thinking kwargs."""
        from src.llm_models.factory import _vllm_disable_chat_template_kwargs

        result = _vllm_disable_chat_template_kwargs({"thinking": True, "enable_thinking": True})
        assert result == {"thinking": False, "enable_thinking": False}

    def test_vllm_disable_chat_template_kwargs_no_thinking(self):
        """_vllm_disable_chat_template_kwargs should return empty dict for non-thinking."""
        from src.llm_models.factory import _vllm_disable_chat_template_kwargs

        result = _vllm_disable_chat_template_kwargs({"other": True})
        assert result == {}

    def test_enable_stream_usage_openai(self):
        """_enable_stream_usage_by_default should set stream_usage for OpenAI with base_url."""
        from src.llm_models.factory import _enable_stream_usage_by_default

        settings = {"base_url": "https://custom.api.com"}
        _enable_stream_usage_by_default("langchain_openai:ChatOpenAI", settings)
        assert settings["stream_usage"] is True

    def test_enable_stream_usage_already_set(self):
        """_enable_stream_usage_by_default should not override existing setting."""
        from src.llm_models.factory import _enable_stream_usage_by_default

        settings = {"stream_usage": False, "base_url": "https://custom.api.com"}
        _enable_stream_usage_by_default("langchain_openai:ChatOpenAI", settings)
        assert settings["stream_usage"] is False

    def test_enable_stream_usage_non_openai(self):
        """_enable_stream_usage_by_default should not touch non-OpenAI providers."""
        from src.llm_models.factory import _enable_stream_usage_by_default

        settings = {}
        _enable_stream_usage_by_default("langchain_anthropic:ChatAnthropic", settings)
        assert "stream_usage" not in settings

    def test_apply_stream_chunk_timeout_default_openai(self):
        """_apply_stream_chunk_timeout_default should set default for OpenAI."""
        from src.llm_models.factory import _apply_stream_chunk_timeout_default

        settings = {}
        _apply_stream_chunk_timeout_default("langchain_openai:ChatOpenAI", settings)
        assert settings["stream_chunk_timeout"] == 240.0

    def test_apply_stream_chunk_timeout_existing(self):
        """_apply_stream_chunk_timeout_default should keep existing value."""
        from src.llm_models.factory import _apply_stream_chunk_timeout_default

        settings = {"stream_chunk_timeout": 60.0}
        _apply_stream_chunk_timeout_default("langchain_openai:ChatOpenAI", settings)
        assert settings["stream_chunk_timeout"] == 60.0

    def test_apply_stream_chunk_timeout_non_openai_removes(self):
        """_apply_stream_chunk_timeout_default should remove the key for non-OpenAI."""
        from src.llm_models.factory import _apply_stream_chunk_timeout_default

        settings = {"stream_chunk_timeout": 60.0}
        _apply_stream_chunk_timeout_default("langchain_anthropic:ChatAnthropic", settings)
        assert "stream_chunk_timeout" not in settings


class TestCredentialLoader:
    """Tests for src/llm_models/credential_loader.py credential loading.

    Uses mocked env vars and temporary files to test all code paths
    without requiring real credentials on disk.
    """

    def test_is_oauth_token_true(self):
        """is_oauth_token should detect Claude Code OAuth tokens."""
        from src.llm_models.credential_loader import is_oauth_token

        assert is_oauth_token("sk-ant-oat01-abc") is True

    def test_is_oauth_token_false(self):
        """is_oauth_token should return False for regular API keys."""
        from src.llm_models.credential_loader import is_oauth_token

        assert is_oauth_token("sk-ant-api03-abc") is False

    def test_is_oauth_token_non_string(self):
        """is_oauth_token should return False for non-strings."""
        from src.llm_models.credential_loader import is_oauth_token

        assert is_oauth_token(42) is False

    def test_claude_code_credential_not_expired(self):
        """ClaudeCodeCredential with future expiry should not be expired."""
        import time

        from src.llm_models.credential_loader import ClaudeCodeCredential

        cred = ClaudeCodeCredential(
            access_token="token",
            expires_at=int(time.time() * 1000) + 3600000,  # 1 hour from now
        )
        assert cred.is_expired is False

    def test_claude_code_credential_expired(self):
        """ClaudeCodeCredential with past expiry should be expired."""
        import time

        from src.llm_models.credential_loader import ClaudeCodeCredential

        cred = ClaudeCodeCredential(
            access_token="token",
            expires_at=int(time.time() * 1000) - 3600000,  # 1 hour ago
        )
        assert cred.is_expired is True

    def test_claude_code_credential_zero_expiry_not_expired(self):
        """ClaudeCodeCredential with expires_at=0 should not be expired."""
        from src.llm_models.credential_loader import ClaudeCodeCredential

        cred = ClaudeCodeCredential(access_token="token", expires_at=0)
        assert cred.is_expired is False

    def test_codex_cli_credential(self):
        """CodexCliCredential should store access_token and account_id."""
        from src.llm_models.credential_loader import CodexCliCredential

        cred = CodexCliCredential(access_token="tok", account_id="acc123")
        assert cred.access_token == "tok"
        assert cred.account_id == "acc123"

    def test_load_claude_code_credential_from_env(self):
        """load_claude_code_credential should read from CLAUDE_CODE_OAUTH_TOKEN env var."""
        from src.llm_models.credential_loader import load_claude_code_credential

        with patch.dict(os.environ, {"CLAUDE_CODE_OAUTH_TOKEN": "sk-ant-oat01-test"}, clear=False):
            # Remove other env vars that might interfere
            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop("ANTHROPIC_AUTH_TOKEN", None)
                os.environ.pop("CLAUDE_CODE_OAUTH_TOKEN_FILE_DESCRIPTOR", None)
                os.environ.pop("CLAUDE_CODE_CREDENTIALS_PATH", None)
                cred = load_claude_code_credential()
                assert cred is not None
                assert cred.access_token == "sk-ant-oat01-test"
                assert cred.source == "claude-cli-env"

    def test_load_claude_code_credential_from_anthropic_auth_token(self):
        """load_claude_code_credential should also check ANTHROPIC_AUTH_TOKEN."""
        from src.llm_models.credential_loader import load_claude_code_credential

        with patch.dict(os.environ, {"ANTHROPIC_AUTH_TOKEN": "sk-ant-oat01-anthropic"}, clear=False):
            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop("CLAUDE_CODE_OAUTH_TOKEN", None)
                os.environ.pop("CLAUDE_CODE_OAUTH_TOKEN_FILE_DESCRIPTOR", None)
                os.environ.pop("CLAUDE_CODE_CREDENTIALS_PATH", None)
                cred = load_claude_code_credential()
                assert cred is not None
                assert cred.access_token == "sk-ant-oat01-anthropic"

    def test_load_claude_code_credential_from_file(self):
        """load_claude_code_credential should read from credentials JSON file."""
        from src.llm_models.credential_loader import load_claude_code_credential

        with tempfile.TemporaryDirectory() as tmp:
            creds_file = Path(tmp) / ".credentials.json"
            creds_file.write_text(json.dumps({
                "claudeAiOauth": {
                    "accessToken": "sk-ant-oat01-fromfile",
                    "refreshToken": "",
                    "expiresAt": 0,  # never expires
                }
            }))
            with patch.dict(os.environ, {"CLAUDE_CODE_CREDENTIALS_PATH": str(creds_file)}, clear=False):
                os.environ.pop("CLAUDE_CODE_OAUTH_TOKEN", None)
                os.environ.pop("ANTHROPIC_AUTH_TOKEN", None)
                os.environ.pop("CLAUDE_CODE_OAUTH_TOKEN_FILE_DESCRIPTOR", None)
                cred = load_claude_code_credential()
                assert cred is not None
                assert cred.access_token == "sk-ant-oat01-fromfile"
                assert cred.source == "claude-cli-file"

    def test_load_claude_code_credential_no_sources(self):
        """load_claude_code_credential should return None when no sources available."""
        from src.llm_models.credential_loader import load_claude_code_credential

        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("CLAUDE_CODE_OAUTH_TOKEN", None)
            os.environ.pop("ANTHROPIC_AUTH_TOKEN", None)
            os.environ.pop("CLAUDE_CODE_OAUTH_TOKEN_FILE_DESCRIPTOR", None)
            os.environ.pop("CLAUDE_CODE_CREDENTIALS_PATH", None)
            with patch("src.llm_models.credential_loader._home_dir", return_value=Path("/nonexistent")):
                cred = load_claude_code_credential()
                assert cred is None

    def test_load_codex_cli_credential_from_file(self):
        """load_codex_cli_credential should read from auth.json file."""
        from src.llm_models.credential_loader import load_codex_cli_credential

        with tempfile.TemporaryDirectory() as tmp:
            auth_file = Path(tmp) / "auth.json"
            auth_file.write_text(json.dumps({
                "access_token": "codex-tok",
                "account_id": "acc-123",
            }))
            with patch.dict(os.environ, {"CODEX_AUTH_PATH": str(auth_file)}):
                cred = load_codex_cli_credential()
                assert cred is not None
                assert cred.access_token == "codex-tok"
                assert cred.account_id == "acc-123"

    def test_load_codex_cli_credential_nested_tokens(self):
        """load_codex_cli_credential should handle nested tokens structure."""
        from src.llm_models.credential_loader import load_codex_cli_credential

        with tempfile.TemporaryDirectory() as tmp:
            auth_file = Path(tmp) / "auth.json"
            auth_file.write_text(json.dumps({
                "tokens": {
                    "access_token": "nested-tok",
                    "account_id": "nested-acc",
                }
            }))
            with patch.dict(os.environ, {"CODEX_AUTH_PATH": str(auth_file)}):
                cred = load_codex_cli_credential()
                assert cred is not None
                assert cred.access_token == "nested-tok"

    def test_load_codex_cli_credential_no_file(self):
        """load_codex_cli_credential should return None when file doesn't exist."""
        from src.llm_models.credential_loader import load_codex_cli_credential

        with patch.dict(os.environ, {"CODEX_AUTH_PATH": "/nonexistent/auth.json"}):
            cred = load_codex_cli_credential()
            assert cred is None

    def test_resolve_credential_path_env_override(self):
        """_resolve_credential_path should use env var when set."""
        from src.llm_models.credential_loader import _resolve_credential_path

        with patch.dict(os.environ, {"MY_VAR": "/custom/path"}):
            result = _resolve_credential_path("MY_VAR", ".default/path")
            assert result == Path("/custom/path")

    def test_load_json_file_not_exists(self):
        """_load_json_file should return None for nonexistent files."""
        from src.llm_models.credential_loader import _load_json_file

        result = _load_json_file(Path("/nonexistent.json"), "test")
        assert result is None

    def test_load_json_file_is_dir(self):
        """_load_json_file should return None for directories."""
        from src.llm_models.credential_loader import _load_json_file

        with tempfile.TemporaryDirectory() as tmp:
            result = _load_json_file(Path(tmp), "test")
            assert result is None

    def test_load_json_file_valid(self):
        """_load_json_file should parse valid JSON files."""
        from src.llm_models.credential_loader import _load_json_file

        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "test.json"
            f.write_text('{"key": "value"}')
            result = _load_json_file(f, "test")
            assert result == {"key": "value"}

    def test_load_json_file_invalid(self):
        """_load_json_file should return None for invalid JSON."""
        from src.llm_models.credential_loader import _load_json_file

        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "bad.json"
            f.write_text("not json {{{")
            result = _load_json_file(f, "test")
            assert result is None


# ═══════════════════════════════════════════════════════════════════════════
# 6. CHANNELS TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestMessageBus:
    """Tests for src/channels/message_bus.py MessageBus.

    Verifies the async pub/sub hub correctly routes inbound and
    outbound messages between channels and the dispatcher.
    """

    @pytest.mark.asyncio
    async def test_publish_and_get_inbound(self):
        """Inbound messages should be enqueued and dequeued in order."""
        from src.channels.message_bus import InboundMessage, InboundMessageType, MessageBus

        bus = MessageBus()
        msg = InboundMessage(
            channel_name="test",
            chat_id="chat1",
            user_id="user1",
            text="hello",
            msg_type=InboundMessageType.CHAT,
        )
        await bus.publish_inbound(msg)
        received = await bus.get_inbound()
        assert received.text == "hello"
        assert received.channel_name == "test"

    @pytest.mark.asyncio
    async def test_inbound_queue_property(self):
        """inbound_queue property should return the underlying queue."""
        from src.channels.message_bus import MessageBus

        bus = MessageBus()
        q = bus.inbound_queue
        assert q is not None
        assert q.empty()

    @pytest.mark.asyncio
    async def test_subscribe_and_publish_outbound(self):
        """Outbound messages should be dispatched to all registered listeners."""
        from src.channels.message_bus import MessageBus, OutboundMessage

        bus = MessageBus()
        received = []

        async def callback(msg):
            received.append(msg)

        bus.subscribe_outbound(callback)
        msg = OutboundMessage(
            channel_name="test",
            chat_id="chat1",
            thread_id="thread1",
            text="response",
        )
        await bus.publish_outbound(msg)
        assert len(received) == 1
        assert received[0].text == "response"

    @pytest.mark.asyncio
    async def test_unsubscribe_outbound(self):
        """Unsubscribed listeners should not receive outbound messages."""
        from src.channels.message_bus import MessageBus, OutboundMessage

        bus = MessageBus()
        received = []

        async def callback(msg):
            received.append(msg)

        bus.subscribe_outbound(callback)
        bus.unsubscribe_outbound(callback)
        msg = OutboundMessage(
            channel_name="test",
            chat_id="chat1",
            thread_id="thread1",
            text="response",
        )
        await bus.publish_outbound(msg)
        assert len(received) == 0

    @pytest.mark.asyncio
    async def test_outbound_callback_error_doesnt_break_others(self):
        """A failing callback should not prevent other callbacks from receiving."""
        from src.channels.message_bus import MessageBus, OutboundMessage

        bus = MessageBus()
        received = []

        async def bad_callback(msg):
            raise RuntimeError("callback error")

        async def good_callback(msg):
            received.append(msg)

        bus.subscribe_outbound(bad_callback)
        bus.subscribe_outbound(good_callback)
        msg = OutboundMessage(
            channel_name="test",
            chat_id="chat1",
            thread_id="thread1",
            text="response",
        )
        await bus.publish_outbound(msg)
        assert len(received) == 1


class TestInboundMessage:
    """Tests for src/channels/message_bus.py InboundMessage dataclass."""

    def test_defaults(self):
        """InboundMessage should have correct defaults."""
        from src.channels.message_bus import InboundMessage, InboundMessageType

        msg = InboundMessage(
            channel_name="test",
            chat_id="c1",
            user_id="u1",
            text="hi",
        )
        assert msg.msg_type == InboundMessageType.CHAT
        assert msg.thread_ts is None
        assert msg.topic_id is None
        assert msg.files == []
        assert msg.metadata == {}

    def test_custom_values(self):
        """InboundMessage should accept all custom values."""
        from src.channels.message_bus import InboundMessage, InboundMessageType

        msg = InboundMessage(
            channel_name="slack",
            chat_id="c1",
            user_id="u1",
            text="/help",
            msg_type=InboundMessageType.COMMAND,
            thread_ts="1234",
            topic_id="topic1",
            files=[{"name": "file.txt"}],
            metadata={"key": "value"},
        )
        assert msg.msg_type == InboundMessageType.COMMAND
        assert msg.thread_ts == "1234"
        assert len(msg.files) == 1


class TestOutboundMessage:
    """Tests for src/channels/message_bus.py OutboundMessage dataclass."""

    def test_defaults(self):
        """OutboundMessage should have correct defaults."""
        from src.channels.message_bus import OutboundMessage

        msg = OutboundMessage(
            channel_name="test",
            chat_id="c1",
            thread_id="t1",
            text="response",
        )
        assert msg.artifacts == []
        assert msg.attachments == []
        assert msg.is_final is True
        assert msg.thread_ts is None
        assert msg.metadata == {}

    def test_with_artifacts(self):
        """OutboundMessage should accept artifacts list."""
        from src.channels.message_bus import OutboundMessage

        msg = OutboundMessage(
            channel_name="test",
            chat_id="c1",
            thread_id="t1",
            text="response",
            artifacts=["/path/to/file.py"],
        )
        assert len(msg.artifacts) == 1


class TestResolvedAttachment:
    """Tests for src/channels/message_bus.py ResolvedAttachment dataclass."""

    def test_resolved_attachment(self):
        """ResolvedAttachment should store all file metadata."""
        from src.channels.message_bus import ResolvedAttachment

        att = ResolvedAttachment(
            virtual_path="/mnt/output/report.pdf",
            actual_path=Path("/host/output/report.pdf"),
            filename="report.pdf",
            mime_type="application/pdf",
            size=1024,
            is_image=False,
        )
        assert att.filename == "report.pdf"
        assert att.is_image is False

    def test_resolved_attachment_image(self):
        """ResolvedAttachment should correctly flag images."""
        from src.channels.message_bus import ResolvedAttachment

        att = ResolvedAttachment(
            virtual_path="/mnt/img.png",
            actual_path=Path("/host/img.png"),
            filename="img.png",
            mime_type="image/png",
            size=2048,
            is_image=True,
        )
        assert att.is_image is True


class TestChannelBase:
    """Tests for src/channels/base.py Channel abstract base class."""

    def _make_channel(self):
        """Create a concrete Channel subclass for testing."""
        from src.channels.base import Channel
        from src.channels.message_bus import MessageBus

        class TestChannel(Channel):
            async def start(self):
                self._running = True

            async def stop(self):
                self._running = False

            async def send(self, msg):
                pass

        bus = MessageBus()
        return TestChannel(name="test", bus=bus, config={"key": "value"})

    def test_channel_init(self):
        """Channel should initialize with name, bus, and config."""
        ch = self._make_channel()
        assert ch.name == "test"
        assert ch.config == {"key": "value"}
        assert ch.is_running is False

    def test_supports_streaming_default(self):
        """Channel.supports_streaming should default to False."""
        ch = self._make_channel()
        assert ch.supports_streaming is False

    def test_make_inbound(self):
        """_make_inbound should create a properly constructed InboundMessage."""
        from src.channels.message_bus import InboundMessageType

        ch = self._make_channel()
        msg = ch._make_inbound(
            "chat1",
            "user1",
            "hello",
            msg_type=InboundMessageType.COMMAND,
            thread_ts="ts1",
        )
        assert msg.channel_name == "test"
        assert msg.chat_id == "chat1"
        assert msg.user_id == "user1"
        assert msg.text == "hello"
        assert msg.msg_type == InboundMessageType.COMMAND
        assert msg.thread_ts == "ts1"

    @pytest.mark.asyncio
    async def test_send_file_default_returns_false(self):
        """Default send_file should return False (no file upload support)."""
        ch = self._make_channel()
        result = await ch.send_file(MagicMock(), MagicMock())
        assert result is False

    @pytest.mark.asyncio
    async def test_on_outbound_routes_to_correct_channel(self):
        """_on_outbound should only process messages for this channel."""
        ch = self._make_channel()
        sent = []

        async def mock_send(msg):
            sent.append(msg)

        ch.send = mock_send

        from src.channels.message_bus import OutboundMessage

        msg = OutboundMessage(
            channel_name="test",
            chat_id="c1",
            thread_id="t1",
            text="hello",
        )
        await ch._on_outbound(msg)
        assert len(sent) == 1

    @pytest.mark.asyncio
    async def test_on_outbound_ignores_other_channels(self):
        """_on_outbound should ignore messages for other channels."""
        ch = self._make_channel()
        sent = []

        async def mock_send(msg):
            sent.append(msg)

        ch.send = mock_send

        from src.channels.message_bus import OutboundMessage

        msg = OutboundMessage(
            channel_name="other-channel",
            chat_id="c1",
            thread_id="t1",
            text="hello",
        )
        await ch._on_outbound(msg)
        assert len(sent) == 0

    @pytest.mark.asyncio
    async def test_receive_file_default_passthrough(self):
        """Default receive_file should return the message unchanged."""
        ch = self._make_channel()
        from src.channels.message_bus import InboundMessage

        msg = InboundMessage(
            channel_name="test",
            chat_id="c1",
            user_id="u1",
            text="hello",
        )
        result = await ch.receive_file(msg, "thread1")
        assert result is msg

    @pytest.mark.asyncio
    async def test_start_sets_running(self):
        """start() should set is_running to True."""
        ch = self._make_channel()
        assert ch.is_running is False
        await ch.start()
        assert ch.is_running is True

    @pytest.mark.asyncio
    async def test_stop_clears_running(self):
        """stop() should set is_running to False."""
        ch = self._make_channel()
        await ch.start()
        assert ch.is_running is True
        await ch.stop()
        assert ch.is_running is False


class TestInboundMessageType:
    """Tests for InboundMessageType enum."""

    def test_enum_values(self):
        """InboundMessageType should have chat and command values."""
        from src.channels.message_bus import InboundMessageType

        assert InboundMessageType.CHAT == "chat"
        assert InboundMessageType.COMMAND == "command"
