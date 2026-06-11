# P0 Fixes - AI-MultiColony-Ecosystem

## Summary
All 8 P0 blockers fixed. 3623 tests passing.

## Fixes Applied

### 1. Kill Switch Hardcoded Approval Code (CRITICAL SECURITY)
- **File**: `ai_multicolony/finance/kill_switch.py`
- Removed hardcoded `LEVEL_3_APPROVAL_CODE = "CONFIRM_LEVEL3_DEACTIVATION_AFTER_REVIEW"`
- Added `_get_level3_approval_code()` static method reading from `os.environ.get("MULTICOLONY_LEVEL3_APPROVAL_CODE")`
- If env var not set: logs error and denies deactivation
- Removed approval code from all log messages — now just says "incorrect" or "not configured"
- Updated test to use `monkeypatch.setenv()` instead of referencing the removed class attribute

### 2. Event Bus Race Condition
- **File**: `ai_multicolony/core/event_bus.py`
- Wrapped `self._event_count += 1` with `async with self._lock:` in `publish_event()`
- Wrapped `self._message_count += 1` with `async with self._lock:` in `send_message()`

### 3. Silent Exception in Agent Loop
- **File**: `ai_multicolony/core/agent_loop.py`
- Changed `except Exception: pass` to `except Exception as exc: logger.warning("Memory condensation failed: %s", exc)`

### 4. Systemic datetime.utcnow() Deprecation
- Replaced 77+ instances of `datetime.utcnow()` → `datetime.now(timezone.utc)` across 24 files
- Added `timezone` to `from datetime import` where missing
- Fixed `time.strftime` → `datetime.now(timezone.utc).strftime` in `llm_provider.py`
- Files: permissions.py, server.py, client.py, knowledge_graph.py, manager.py, paging.py, session.py, knowledge.py, vector.py, memory.py, registry.py, channel.py, schemas.py, base.py, colony.py, browser.py, voice.py, security.py, researcher.py, graph.py, state.py, coder.py, manus.py, llm_provider.py, quant_nanggroe execution base.py

### 5. Market Source Returns Static Data
- **File**: `ai_multicolony/sources/market.py`
- Added `STALE_DATA_WARNING` constant logged on every `fetch()` and `scan()` call
- Added `is_live` property returning `False`
- Updated class docstring with warning about dev-mode only

### 6. Risk Guard Mutates TradeRequest
- **File**: `ai_multicolony/finance/risk_guard.py`
- Added `request = request.model_copy(deep=True)` at the start of `check_trade()` to avoid mutating the caller's request
- Updated test to verify original request is not mutated and result reflects the constraint

### 7. Audit File Default Path
- **File**: `ai_multicolony/security/audit.py`
- Added `_DEFAULT_AUDIT_PATH = os.path.expanduser("~/.multicolony/audit/audit.jsonl")`
- Updated both `FileAuditStorage.__init__()` and `AuditTrail.__init__()` defaults

### 8. Autoswitch Counter Never Resets
- **File**: `ai_multicolony/finance/autoswitch.py`
- Added `_last_switch_date` field initialized to current UTC date
- Added date-change check at the top of `evaluate_and_switch()` that resets `_switches_today` to 0 when the date changes

## Test Results
```
3623 passed in 24.28s
```
