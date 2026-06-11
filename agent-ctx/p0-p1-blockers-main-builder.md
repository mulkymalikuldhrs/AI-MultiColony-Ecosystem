# Task: P0/P1 Blocker Fixes — Quant-Nanggroe-AI

## Agent: Main Builder
## Date: 2026-06-11

## Summary

All P0 (critical) and P1 (high-priority) blockers have been fixed in the Quant-Nanggroe-AI sub-package within the AI-MultiColony-Ecosystem repo.

## Files Modified

### P0-1: Constitutional Risk Limits Override via Environment Variables
- **`quant_nanggroe/config/settings.py`** (full rewrite)
  - Removed ALL risk limit fields from Settings class (risk_max_per_trade, risk_max_daily_loss, risk_max_weekly_loss, risk_max_drawdown)
  - Added `_CONSTITUTIONAL_ENV_VARS` list of forbidden env var names
  - Added `_check_no_constitutional_overrides()` function that detects override attempts
  - `get_settings()` now raises RuntimeError if any QNAI_RISK_* env vars are set
  - Added docstring pointing to constants.py as SINGLE SOURCE OF TRUTH

### P0-2: Live Trading Safeguards
- **`quant_nanggroe/cli.py`** (full rewrite)
  - Added `_verify_live_trading_safety()` function with 3 mandatory checks:
    1. `QNAI_ENABLE_LIVE_TRADING=CONFIRMED` env var required
    2. User must type "I UNDERSTAND THE RISKS" as explicit confirmation
    3. Risk guardian must be importable and kill switch must be inactive
  - Added bonus check: constitutional override detection
  - Added 10-second cooldown before first live trade
  - If any check fails, live mode is refused and falls back to PAPER mode

### P0-3: Duplicate Constitutional Constants
- **`quant_nanggroe/engine/risk/constants.py`** (full rewrite)
  - Added `from typing import Final`
  - All constants marked as `Final[...]` (immutable at type-check level)
  - Added KILL_SWITCH_DAILY_PNL = -0.008 (early warning at 0.8% before 1% hard limit)
  - Changed KILL_SWITCH_WEEKLY_PNL from -0.05 to -0.025 (early warning at 2.5% before 3% hard limit)
  - Added comprehensive docstring explaining single-source-of-truth status

- **`quant_nanggroe/agents/state.py`** (full rewrite)
  - REMOVED all hardcoded duplicate constants (MAX_RISK_PER_TRADE, etc.)
  - Now imports ALL constitutional limits from `quant_nanggroe.engine.risk.constants`
  - `create_initial_state()` now includes kill_switch thresholds in metadata

- **`ai_multicolony/finance/risk_guard.py`** (full rewrite)
  - REMOVED hardcoded duplicate constants
  - Now imports from `quant_nanggroe.engine.risk.constants`
  - Converted fraction-based constants to percentage-based for backward compatibility

### P0-4: Missing Critical Dependencies
- **`requirements.txt`** (updated)
  - Added: pydantic-settings>=2.0, scipy>=1.11, click>=8.0, ccxt>=4.0, alpaca-py>=0.20, yfinance>=0.2, polygon-api-client>=1.12, twelvedata>=0.5, langgraph>=0.2, langchain>=0.3, langchain-openai>=0.2, langchain-anthropic>=0.2, langchain-google-genai>=2.0, langchain-core>=0.3, fastapi>=0.100, uvicorn>=0.24, scikit-learn>=1.3

- **`requirements-full.txt`** (NEW file)
  - Includes all base requirements plus optional deps: ib_insync, MetaTrader5, langchain-community, xgboost, torch, lightgbm, catboost, chromadb, faiss-cpu, solana, solders, docker, selenium, arxiv, asyncpg

### P1-1: README Documents Fictional TypeScript APIs
- **`README.md`** (multiple edits)
  - Replaced TypeScript/React badges with Python/LangGraph badges
  - Replaced "React 19" UI claim with "Dashboard UI (FastAPI + REST)"
  - Updated prerequisites from Node.js/npm to Python/pip
  - Updated installation commands from `npm install` to `pip install`
  - Replaced ALL TypeScript API examples with actual Python examples from quant_nanggroe
  - Updated env var section with QNAI_ prefix and constitutional immutability note
  - Updated dev setup from npm commands to pip/mypy/ruff/pytest
  - Changed "TypeScript strict" to "Python strict"
  - Changed Schema.org programmingLanguage from TypeScript to Python

### P1-2: Kill Switch Is In-Memory Only
- **`quant_nanggroe/engine/risk/kill_switch.py`** (full rewrite)
  - Added file-based persistence to `data/kill_switch_state.json`
  - Added `_persist_state()` method (atomic write via temp file)
  - Added `_load_persisted_state()` method called at init
  - If kill switch was active before restart, it remains active and logs CRITICAL warning
  - Trading is REFUSED until manually reset with explicit confirmation
  - `check_auto_trigger()` now uses KILL_SWITCH thresholds (early warning) plus hard limits
  - `reset()` method already required explicit confirmation (unchanged)

### P1-4: LLM Mock Fallback Creates Silent Failure
- **`quant_nanggroe/cli.py`** (included in P0-2 rewrite)
  - Added `--allow-simulated` flag (required for simulated mode)
  - Without --allow-simulated, simulated mode is BLOCKED with clear error
  - Added `_SIMULATED_BANNER` with large yellow warning box
  - All simulated outputs prefixed with `[SIMULATED]`
  - Simulated pipeline panel shows bold warning about no real analysis
  - Import errors and pipeline errors also require --allow-simulated to fall back

## Verification

All modified files pass `python3 -m py_compile`:
- quant_nanggroe/config/settings.py ✓
- quant_nanggroe/engine/risk/constants.py ✓
- quant_nanggroe/engine/risk/kill_switch.py ✓
- quant_nanggroe/cli.py ✓
- quant_nanggroe/agents/state.py ✓
- ai_multicolony/finance/risk_guard.py ✓

Runtime tests passed:
- Constitutional override detection works (env var set → violation detected)
- Kill switch persistence works (activate → reload → still active → reset with confirmation)
- Constants values verified (KILL_SWITCH_DAILY_PNL = -0.008 triggers before MAX_DAILY_LOSS = 0.01)
- risk_guard.py imports from constants.py produce correct percentage values
