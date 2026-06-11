# Task: Implement TIER 1 Modules for Quant-Nanggroe-AI

## Agent: Main Builder
## Status: COMPLETED ✅

## Summary
Implemented all 7 TIER 1 production-critical modules for the quant_nanggroe package. All modules compile, import, and pass functional tests.

## Files Created

### 1. `quant_nanggroe/engine/regime_detector.py` — Market Regime Detection (HMM-based)
- **Classes**: `HMMRegimeDetector`, `RegimeState`, `Regime`
- **Key Methods**:
  - `fit(returns, volumes)` — Fit HMM model on historical data
  - `predict(recent_returns, recent_volumes)` → `RegimeState` — Detect current regime
  - `_compute_regime_simple()` — ADX + ATR fallback when hmmlearn unavailable
- **4 Regimes**: BULL, BEAR, SIDEWAYS, CRISIS
- **Features**: daily returns, 20-day rolling volatility, volume change
- **Fallback**: Statistical heuristic using ADX + ATR when hmmlearn not installed
- **Serializable**: `RegimeState.to_api_dict()` for API responses

### 2. `quant_nanggroe/engine/backtest/cpcv.py` — Combinatorial Purged Cross-Validation
- **Classes**: `CombinatorialPurgedCV`, `CPCVEvaluationResult`, `CPCVSplitResult`
- **Key Methods**:
  - `split(timestamps)` → List of (train, test) index pairs
  - `split_detailed(timestamps)` → List of `CPCVSplitResult` with metadata
  - `evaluate_strategy(strategy_fn, data)` → `CPCVEvaluationResult` with mean Sharpe + CI
- **De Prado method**: Purge + Embargo to prevent information leakage
- **Configurable**: n_groups, n_test_groups, purge_gap, embargo params

### 3. `quant_nanggroe/agents/debate_orchestrator.py` — Multi-Agent Debate Protocol
- **Classes**: `DebateOrchestrator`, `DebateResult`, `DebateArgument`, `DebateConfig`, `DebateDecision`, `DebateRole`
- **Key Methods**:
  - `debate(symbol, context, max_rounds)` → `DebateResult`
  - 4 Roles: Bull Researcher, Bear Researcher, Risk Analyst, Portfolio Manager
  - Round 1: Independent analysis → Round 2-N: Rebuttal → Risk Review → Moderation
- **Returns**: bull_score, bear_score, risk_veto, final_decision, reasoning
- **Note**: Renamed from `debate.py` to `debate_orchestrator.py` due to existing `debate/` package

### 4. `quant_nanggroe/engine/grounding.py` — Grounding System (Prevent LLM Price Hallucination)
- **Classes**: `MarketGrounding`, `GroundingResult`, `ValidationResult`, `GroundedPrice`
- **Key Methods**:
  - `ground_prompt(system_prompt, symbols)` → `GroundingResult` with enhanced prompt
  - `validate_response(response, symbols)` → `ValidationResult` with hallucination detection
- **Pattern**: Pre-fetch OHLCV → Render markdown table → Inject with "ONLY prices you may cite"
- **Caching**: 5-minute TTL with cleanup
- **Validation**: Any price within 5% of grounded data or flagged as hallucinated

### 5. `quant_nanggroe/engine/worker.py` — Singleton Background Worker
- **Classes**: `BackgroundWorker`, `SingletonLock`, `WorkerTask`, `WorkerHealth`, `TaskMetrics`
- **Key Methods**:
  - `start()` → Acquire lock, start tasks
  - `stop()` → Graceful shutdown
  - `health_check()` → `WorkerHealth`
  - `register_task(task)` / `deregister_task(name)`
- **Features**: File-based singleton lock, SIGINT/SIGTERM handling, exponential backoff, configurable tasks

### 6. `quant_nanggroe/engine/nim_provider.py` — NVIDIA NIM Provider (Full Integration)
- **Classes**: `NIMProvider`, `NIMResponse`, `CircuitBreaker`, `TaskType`
- **Key Methods**:
  - `chat(prompt, task, model)` → `NIMResponse`
  - `health_check()` → Provider health status
- **5 Free Models**: deepseek-r1, llama-3.3-70b, nemotron-70b, mixtral-8x22b, gemma-3-27b
- **Task routing**: reasoning → deepseek-r1, analysis → nemotron, quick → mixtral, vision → gemma
- **Circuit breaker**: 3 failures → 5 min cooldown
- **Fallback chain**: NIM → Ollama → Mock with [MOCK] prefix
- **Async**: aiohttp-based, no SDK dependency

### 7. `quant_nanggroe/engine/model_registry.py` — Model Registry
- **Functions**: `register_model()`, `get_model()`, `list_models()`, `has_model()`, `unregister_model()`
- **ABC**: `QuantModel` with `fit()`, `predict()`, `explain()`
- **Registered Models**:
  - `linear` → `LinearModel` (OLS regression, no sklearn needed)
  - `xgboost` → `XGBoostModel` (gradient boosted trees with fallback)
  - `transformer` → `TransformerModel` (attention-based stub with PyTorch support)

## Verification Results
- ✅ All 7 files pass `python3 -m py_compile`
- ✅ All 7 modules import successfully
- ✅ All functional tests pass:
  - Regime detection correctly identifies CRISIS regime (91% confidence)
  - CPCV generates 12/15 valid splits with purging and embargo
  - Grounding enhances prompts with real/mock price data
  - Worker initializes with default tasks and health check
  - NIM Provider correctly routes to mock without API key
  - Model Registry: Linear R²=0.965, XGBoost/Transformer stubs work

## Design Decisions
- **Pydantic models** throughout for serialization (consistent with codebase)
- **Graceful fallbacks** for all optional dependencies (hmmlearn, xgboost, torch, aiohttp, yfinance)
- **Async/await** for all I/O operations
- **`if __name__ == "__main__"`** demo sections in every module
- Renamed `debate.py` → `debate_orchestrator.py` to avoid conflict with existing `debate/` package
