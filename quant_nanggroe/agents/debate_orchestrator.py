"""Multi-Agent Debate Protocol — Structured Bull/Bear Investment Debate.

Implements a structured debate protocol where Bull and Bear researchers
present opposing arguments, a Risk Analyst reviews both sides, and a
Portfolio Manager (Moderator) synthesizes the final decision with an
explicit reasoning chain.

Debate Flow
-----------
1. **Round 1**: Independent analysis from Bull and Bear researchers
2. **Round 2-N**: Rebuttal — each side sees opponent's arguments
3. **Risk Review**: Risk analyst reviews both sides for blind spots
4. **Moderation**: Portfolio Manager synthesizes with reasoning chain

Usage::

    from quant_nanggroe.agents.debate import DebateOrchestrator, DebateConfig

    orchestrator = DebateOrchestrator(llm_provider=my_llm)
    result = await orchestrator.debate("AAPL", context={"price": 175.0})
    print(result.final_decision, result.reasoning)
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol

from pydantic import BaseModel, Field, ConfigDict

logger = logging.getLogger(__name__)


# ── Enums ───────────────────────────────────────────────────────────────


class DebateDecision(str, Enum):
    """Final decision from the debate."""

    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"
    NO_TRADE = "NO_TRADE"


class DebateRole(str, Enum):
    """Roles in the debate protocol."""

    BULL_RESEARCHER = "bull_researcher"
    BEAR_RESEARCHER = "bear_researcher"
    RISK_ANALYST = "risk_analyst"
    PORTFOLIO_MANAGER = "portfolio_manager"


# ── LLM Provider Protocol ──────────────────────────────────────────────


class LLMProviderProto(Protocol):
    """Protocol for LLM provider integration.

    Any LLM provider that implements ``chat()`` can be used,
    including the ecosystem's ``LLMProvider`` or ``NIMProvider``.
    """

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        **kwargs: Any,
    ) -> Any:
        """Send messages and get a response."""
        ...


# ── Pydantic Models ─────────────────────────────────────────────────────


class DebateArgument(BaseModel):
    """A single argument in the debate.

    Attributes:
        role: The debater's role.
        round_number: Which debate round this argument belongs to.
        points: Key argument points.
        evidence: Supporting evidence for each point.
        confidence: Confidence score (0.0–1.0).
        counter_points: Points rebutting the opponent.
        risks_identified: Risks identified by this argument.
    """

    model_config = ConfigDict(frozen=False)

    role: DebateRole = DebateRole.BULL_RESEARCHER
    round_number: int = 1
    points: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    counter_points: List[str] = Field(default_factory=list)
    risks_identified: List[str] = Field(default_factory=list)


class DebateResult(BaseModel):
    """Final result from the debate protocol — fully serializable.

    Attributes:
        debate_id: Unique identifier for this debate.
        symbol: The asset being debated.
        bull_score: Aggregated bull case strength (0.0–1.0).
        bear_score: Aggregated bear case strength (0.0–1.0).
        risk_veto: Whether the risk analyst vetoed the trade.
        risk_concerns: List of risk concerns raised.
        final_decision: The synthesized decision.
        reasoning: Explicit reasoning chain from the moderator.
        bull_arguments: All bull arguments by round.
        bear_arguments: All bear arguments by round.
        risk_analysis: Risk analyst's review.
        n_rounds: Number of debate rounds completed.
        timestamp: UTC timestamp.
    """

    model_config = ConfigDict(frozen=False)

    debate_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    symbol: str = ""
    bull_score: float = Field(default=0.5, ge=0.0, le=1.0)
    bear_score: float = Field(default=0.5, ge=0.0, le=1.0)
    risk_veto: bool = False
    risk_concerns: List[str] = Field(default_factory=list)
    final_decision: DebateDecision = DebateDecision.HOLD
    reasoning: str = ""
    bull_arguments: List[DebateArgument] = Field(default_factory=list)
    bear_arguments: List[DebateArgument] = Field(default_factory=list)
    risk_analysis: Optional[DebateArgument] = None
    n_rounds: int = 0
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_api_dict(self) -> Dict[str, Any]:
        """Convert to API-safe dictionary."""
        return {
            "debate_id": self.debate_id,
            "symbol": self.symbol,
            "bull_score": round(self.bull_score, 4),
            "bear_score": round(self.bear_score, 4),
            "risk_veto": self.risk_veto,
            "risk_concerns": self.risk_concerns,
            "final_decision": self.final_decision.value,
            "reasoning": self.reasoning,
            "n_rounds": self.n_rounds,
            "timestamp": self.timestamp.isoformat(),
        }


class DebateConfig(BaseModel):
    """Configuration for the debate protocol.

    Attributes:
        max_rounds: Maximum number of debate rounds.
        min_confidence_gap: Minimum gap between bull/bear scores
            to declare a winner.  If gap < this, decision is HOLD.
        risk_veto_threshold: If risk analyst confidence < this,
            the trade is vetoed.
        require_rebuttal: Whether rebuttal rounds are mandatory.
    """

    model_config = ConfigDict(frozen=False)

    max_rounds: int = 3
    min_confidence_gap: float = 0.1
    risk_veto_threshold: float = 0.3
    require_rebuttal: bool = True


# ── System Prompts ──────────────────────────────────────────────────────

BULL_RESEARCHER_PROMPT = """You are a BULL RESEARCHER analyzing {symbol}.
Your role is to present compelling, evidence-based arguments FOR investing in this asset.

Context:
{context}

Round {round_number} — {round_type}

Focus on:
1. Strong fundamentals and growth prospects
2. Positive technical indicators and momentum
3. Favorable market conditions and catalysts
4. Competitive advantages and market position
5. Upside potential and favorable risk/reward

{rebuttal_instruction}

Provide your analysis as structured arguments with:
- Key points (3-5 bullet points)
- Supporting evidence
- Confidence score (0.0-1.0)
- Any risks you acknowledge but believe are outweighed
"""

BEAR_RESEARCHER_PROMPT = """You are a BEAR RESEARCHER analyzing {symbol}.
Your role is to present compelling, evidence-based arguments AGAINST investing in this asset.

Context:
{context}

Round {round_number} — {round_type}

Focus on:
1. Fundamental weaknesses and declining metrics
2. Negative technical signals and bearish patterns
3. Unfavorable market conditions and headwinds
4. Competitive threats and market risks
5. Downside risks and unfavorable risk/reward

{rebuttal_instruction}

Provide your analysis as structured arguments with:
- Key points (3-5 bullet points)
- Supporting evidence
- Confidence score (0.0-1.0)
- Any bull points you acknowledge but believe are outweighed
"""

RISK_ANALYST_PROMPT = """You are a RISK ANALYST reviewing the debate about {symbol}.

Context:
{context}

Bull Arguments:
{bull_args}

Bear Arguments:
{bear_args}

Your job is to:
1. Identify blind spots in both bull and bear cases
2. Assess tail risks not covered by either side
3. Evaluate position sizing implications
4. Determine if any risk factors warrant a VETO (blocking the trade)
5. Provide an overall risk assessment with confidence

If any of these "circuit breaker" conditions are met, you MUST veto:
- Potential loss exceeds 10% of portfolio
- Liquidity risk is extreme
- Correlation risk with existing positions is too high
- Geopolitical/event risk is elevated and unaccounted for

Provide:
- Key risk concerns (list)
- Risk confidence (0.0-1.0) — below {veto_threshold} = VETO
- Whether to veto the trade
- Recommended position size adjustment (0.0-1.0 of original)
"""

MODERATOR_PROMPT = """You are a PORTFOLIO MANAGER moderating the debate about {symbol}.

Context:
{context}

Bull Score: {bull_score:.2f} | Bear Score: {bear_score:.2f}
Risk Veto: {risk_veto}
Risk Concerns: {risk_concerns}

Bull Arguments Summary:
{bull_summary}

Bear Arguments Summary:
{bear_summary}

Risk Analysis:
{risk_summary}

Synthesize the debate into a final decision:
1. Weigh bull vs bear arguments by evidence quality
2. Factor in risk analyst's assessment
3. If risk veto is active, the decision MUST be NO_TRADE
4. Provide explicit reasoning chain showing how you reached the decision

Decision options: STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL, NO_TRADE

Output your decision with a clear reasoning chain.
"""


# ── Debate Orchestrator ─────────────────────────────────────────────────


class DebateOrchestrator:
    """Orchestrates the multi-agent debate protocol.

    Manages the structured debate between Bull and Bear researchers,
    with Risk Analyst review and Portfolio Manager moderation.

    Args:
        llm_provider: LLM provider implementing the chat() interface.
            Uses the ecosystem's LLM provider.  If None, generates
            structured mock responses.
        config: Debate configuration.

    Usage::

        orchestrator = DebateOrchestrator(llm_provider=my_llm)
        result = await orchestrator.debate("AAPL", context={"price": 175})
        print(result.final_decision)
    """

    def __init__(
        self,
        llm_provider: Optional[LLMProviderProto] = None,
        config: Optional[DebateConfig] = None,
    ) -> None:
        self.llm = llm_provider
        self.config = config or DebateConfig()
        self._debate_history: List[DebateResult] = []

    async def debate(
        self,
        symbol: str,
        context: Optional[Dict[str, Any]] = None,
        max_rounds: Optional[int] = None,
    ) -> DebateResult:
        """Run the full debate protocol for a symbol.

        Args:
            symbol: Trading symbol (e.g., "AAPL", "BTC-USD").
            context: Additional context data (price, fundamentals, etc.).
            max_rounds: Override max rounds from config.

        Returns:
            DebateResult with the final decision and reasoning.
        """
        context = context or {}
        rounds = max_rounds or self.config.max_rounds

        bull_arguments: List[DebateArgument] = []
        bear_arguments: List[DebateArgument] = []
        context_str = self._format_context(context)

        # ── Round 1: Independent Analysis ─────────────────────────────

        round_type = "Opening Statements"
        rebuttal_instruction = "This is your opening statement. Present your strongest independent analysis."

        bull_arg = await self._generate_argument(
            symbol=symbol,
            role=DebateRole.BULL_RESEARCHER,
            round_number=1,
            round_type=round_type,
            context_str=context_str,
            rebuttal_instruction=rebuttal_instruction,
            opponent_args=None,
        )
        bear_arg = await self._generate_argument(
            symbol=symbol,
            role=DebateRole.BEAR_RESEARCHER,
            round_number=1,
            round_type=round_type,
            context_str=context_str,
            rebuttal_instruction=rebuttal_instruction,
            opponent_args=None,
        )

        bull_arguments.append(bull_arg)
        bear_arguments.append(bear_arg)

        # ── Round 2-N: Rebuttal Rounds ────────────────────────────────

        for round_num in range(2, rounds + 1):
            round_type = "Rebuttal"
            rebuttal = (
                "You now see your opponent's arguments. "
                "Directly address and counter their key points while "
                "strengthening your own case."
            )

            bull_arg = await self._generate_argument(
                symbol=symbol,
                role=DebateRole.BULL_RESEARCHER,
                round_number=round_num,
                round_type=round_type,
                context_str=context_str,
                rebuttal_instruction=rebuttal,
                opponent_args=bear_arguments[-1:],
            )
            bear_arg = await self._generate_argument(
                symbol=symbol,
                role=DebateRole.BEAR_RESEARCHER,
                round_number=round_num,
                round_type=round_type,
                context_str=context_str,
                rebuttal_instruction=rebuttal,
                opponent_args=bull_arguments[-1:],
            )

            bull_arguments.append(bull_arg)
            bear_arguments.append(bear_arg)

        # ── Risk Analyst Review ───────────────────────────────────────

        risk_analysis = await self._risk_review(
            symbol, context_str, bull_arguments, bear_arguments
        )

        # ── Calculate Scores ──────────────────────────────────────────

        bull_score = self._aggregate_scores(bull_arguments)
        bear_score = self._aggregate_scores(bear_arguments)

        # Determine risk veto
        risk_veto = False
        risk_concerns: List[str] = []
        if risk_analysis:
            risk_concerns = risk_analysis.risks_identified
            if risk_analysis.confidence < self.config.risk_veto_threshold:
                risk_veto = True

        # ── Portfolio Manager Synthesis ───────────────────────────────

        decision, reasoning = await self._moderate(
            symbol=symbol,
            context_str=context_str,
            bull_score=bull_score,
            bear_score=bear_score,
            bull_arguments=bull_arguments,
            bear_arguments=bear_arguments,
            risk_veto=risk_veto,
            risk_concerns=risk_concerns,
            risk_analysis=risk_analysis,
        )

        result = DebateResult(
            symbol=symbol,
            bull_score=bull_score,
            bear_score=bear_score,
            risk_veto=risk_veto,
            risk_concerns=risk_concerns,
            final_decision=decision,
            reasoning=reasoning,
            bull_arguments=bull_arguments,
            bear_arguments=bear_arguments,
            risk_analysis=risk_analysis,
            n_rounds=rounds,
        )

        self._debate_history.append(result)
        return result

    # ── Argument Generation ──────────────────────────────────────────

    async def _generate_argument(
        self,
        symbol: str,
        role: DebateRole,
        round_number: int,
        round_type: str,
        context_str: str,
        rebuttal_instruction: str,
        opponent_args: Optional[List[DebateArgument]] = None,
    ) -> DebateArgument:
        """Generate a debate argument using the LLM or fallback.

        Args:
            symbol: Trading symbol.
            role: Debater role.
            round_number: Current round number.
            round_type: Type of round (opening/rebuttal).
            context_str: Formatted context string.
            rebuttal_instruction: Instructions for rebuttal.
            opponent_args: Opponent's previous arguments.

        Returns:
            DebateArgument with the generated argument.
        """
        # Select prompt template
        if role == DebateRole.BULL_RESEARCHER:
            template = BULL_RESEARCHER_PROMPT
        else:
            template = BEAR_RESEARCHER_PROMPT

        # Build opponent arguments string
        opponent_str = ""
        if opponent_args:
            parts = []
            for arg in opponent_args:
                parts.append(
                    f"Round {arg.round_number}: "
                    f"Points: {'; '.join(arg.points[:3])} "
                    f"(confidence: {arg.confidence:.2f})"
                )
            opponent_str = f"\nOpponent's arguments:\n" + "\n".join(parts)
            rebuttal_instruction += opponent_str

        prompt = template.format(
            symbol=symbol,
            context=context_str,
            round_number=round_number,
            round_type=round_type,
            rebuttal_instruction=rebuttal_instruction,
        )

        # Call LLM or use fallback
        if self.llm is not None:
            try:
                response = await self.llm.chat(
                    messages=[{"role": "user", "content": prompt}]
                )
                content = self._extract_content(response)
                return self._parse_argument(content, role, round_number)
            except Exception as exc:
                logger.warning(
                    "debate_llm_failed_using_fallback",
                    extra={"role": role.value, "error": str(exc)},
                )

        # Fallback: structured mock argument
        return self._generate_fallback_argument(
            symbol, role, round_number, context_str, opponent_args
        )

    async def _risk_review(
        self,
        symbol: str,
        context_str: str,
        bull_arguments: List[DebateArgument],
        bear_arguments: List[DebateArgument],
    ) -> DebateArgument:
        """Run risk analyst review of the debate.

        Args:
            symbol: Trading symbol.
            context_str: Formatted context.
            bull_arguments: All bull arguments.
            bear_arguments: All bear arguments.

        Returns:
            DebateArgument from the risk analyst.
        """
        bull_summary = self._summarize_arguments(bull_arguments)
        bear_summary = self._summarize_arguments(bear_arguments)

        prompt = RISK_ANALYST_PROMPT.format(
            symbol=symbol,
            context=context_str,
            bull_args=bull_summary,
            bear_args=bear_summary,
            veto_threshold=self.config.risk_veto_threshold,
        )

        if self.llm is not None:
            try:
                response = await self.llm.chat(
                    messages=[{"role": "user", "content": prompt}]
                )
                content = self._extract_content(response)
                return self._parse_risk_analysis(content)
            except Exception as exc:
                logger.warning(
                    "risk_review_llm_failed_using_fallback",
                    extra={"error": str(exc)},
                )

        # Fallback risk analysis
        return self._generate_fallback_risk_analysis(
            symbol, bull_arguments, bear_arguments
        )

    async def _moderate(
        self,
        symbol: str,
        context_str: str,
        bull_score: float,
        bear_score: float,
        bull_arguments: List[DebateArgument],
        bear_arguments: List[DebateArgument],
        risk_veto: bool,
        risk_concerns: List[str],
        risk_analysis: Optional[DebateArgument],
    ) -> tuple[DebateDecision, str]:
        """Portfolio Manager synthesizes the final decision.

        Args:
            symbol: Trading symbol.
            context_str: Formatted context.
            bull_score: Aggregated bull score.
            bear_score: Aggregated bear score.
            bull_arguments: All bull arguments.
            bear_arguments: All bear arguments.
            risk_veto: Whether risk analyst vetoed.
            risk_concerns: Risk concerns identified.
            risk_analysis: Risk analyst's argument.

        Returns:
            Tuple of (final_decision, reasoning_chain).
        """
        # If risk veto, decision is automatically NO_TRADE
        if risk_veto:
            return DebateDecision.NO_TRADE, (
                f"Risk analyst vetoed the trade. "
                f"Concerns: {'; '.join(risk_concerns[:3])}. "
                f"Even though bull score ({bull_score:.2f}) vs bear score "
                f"({bear_score:.2f}), risk concerns override."
            )

        bull_summary = self._summarize_arguments(bull_arguments)
        bear_summary = self._summarize_arguments(bear_arguments)
        risk_summary = ""
        if risk_analysis:
            risk_summary = self._summarize_arguments([risk_analysis])

        prompt = MODERATOR_PROMPT.format(
            symbol=symbol,
            context=context_str,
            bull_score=bull_score,
            bear_score=bear_score,
            risk_veto=risk_veto,
            risk_concerns="; ".join(risk_concerns[:5]) if risk_concerns else "None",
            bull_summary=bull_summary,
            bear_summary=bear_summary,
            risk_summary=risk_summary,
        )

        if self.llm is not None:
            try:
                response = await self.llm.chat(
                    messages=[{"role": "user", "content": prompt}]
                )
                content = self._extract_content(response)
                return self._parse_moderator_decision(content, bull_score, bear_score)
            except Exception as exc:
                logger.warning(
                    "moderator_llm_failed_using_fallback",
                    extra={"error": str(exc)},
                )

        # Fallback: deterministic decision from scores
        return self._fallback_moderate(bull_score, bear_score, risk_concerns)

    # ── Fallback Methods (no LLM) ───────────────────────────────────

    def _generate_fallback_argument(
        self,
        symbol: str,
        role: DebateRole,
        round_number: int,
        context_str: str,
        opponent_args: Optional[List[DebateArgument]] = None,
    ) -> DebateArgument:
        """Generate a structured fallback argument without LLM.

        Uses context data and opponent arguments to create a
        plausible structured argument.
        """
        import re

        # Extract numeric values from context
        price_match = re.search(r"price['\"]?\s*[:=]\s*([\d.]+)", context_str, re.IGNORECASE)
        change_match = re.search(r"change(?:_pct)?['\"]?\s*[:=]\s*([-\d.]+)", context_str, re.IGNORECASE)

        price = float(price_match.group(1)) if price_match else 0.0
        change = float(change_match.group(1)) if change_match else 0.0

        counter_points: List[str] = []
        if opponent_args:
            for arg in opponent_args:
                for point in arg.points[:2]:
                    counter_points.append(
                        f"Counter to {arg.role.value}: {point} — "
                        f"{'bullish' if role == DebateRole.BULL_RESEARCHER else 'bearish'} context applies"
                    )

        if role == DebateRole.BULL_RESEARCHER:
            points = [
                f"Strong market positioning for {symbol}",
                f"Favorable technical momentum" + (f" (+{change:.1f}% recent gain)" if change > 0 else ""),
                "Positive sector tailwinds and catalysts",
                "Supportive macro environment",
            ]
            evidence = [
                "Sector outperformance relative to benchmark",
                "Key resistance levels broken",
                "Institutional accumulation signals",
                "Central bank policy support",
            ]
            risks = [
                "Potential overbought conditions",
                "Macro uncertainty could reverse gains",
            ]
            # Higher confidence if positive change
            confidence = min(0.9, 0.6 + abs(change) * 0.02) if change > 0 else 0.55
        else:
            points = [
                f"Overvaluation risk for {symbol}",
                f"Unfavorable technical signals" + (f" ({change:.1f}% recent decline)" if change < 0 else ""),
                "Macro headwinds possible",
                "Competitive threats increasing",
            ]
            evidence = [
                "Elevated P/E ratio vs sector",
                "Rising interest rate expectations",
                "Technical indicators showing weakness",
                "Insider selling signals",
            ]
            risks = [
                "Short squeeze potential",
                "Earnings could surprise positively",
            ]
            confidence = min(0.9, 0.6 + abs(change) * 0.02) if change < 0 else 0.50

        return DebateArgument(
            role=role,
            round_number=round_number,
            points=points,
            evidence=evidence,
            confidence=confidence,
            counter_points=counter_points,
            risks_identified=risks,
        )

    def _generate_fallback_risk_analysis(
        self,
        symbol: str,
        bull_arguments: List[DebateArgument],
        bear_arguments: List[DebateArgument],
    ) -> DebateArgument:
        """Generate fallback risk analysis without LLM."""
        bull_conf = max((a.confidence for a in bull_arguments), default=0.5)
        bear_conf = max((a.confidence for a in bear_arguments), default=0.5)

        concerns: List[str] = []
        if abs(bull_conf - bear_conf) < 0.2:
            concerns.append("Low conviction signal — bull/bear scores close")
        if bear_conf > 0.7:
            concerns.append("High bear confidence — significant downside risk")
        concerns.extend([
            "Tail risk not fully quantified",
            "Position sizing should be conservative",
            "Consider stop-loss at key support levels",
        ])

        risk_confidence = 0.5 + abs(bull_conf - bear_conf) * 0.3

        return DebateArgument(
            role=DebateRole.RISK_ANALYST,
            round_number=0,
            points=concerns[:5],
            evidence=["Historical backtesting", "Correlation analysis", "Drawdown simulation"],
            confidence=min(1.0, risk_confidence),
            counter_points=[],
            risks_identified=concerns,
        )

    def _fallback_moderate(
        self,
        bull_score: float,
        bear_score: float,
        risk_concerns: List[str],
    ) -> tuple[DebateDecision, str]:
        """Deterministic moderation fallback based on scores."""
        gap = bull_score - bear_score

        if abs(gap) < self.config.min_confidence_gap:
            decision = DebateDecision.HOLD
            reasoning = (
                f"Bull ({bull_score:.2f}) and Bear ({bear_score:.2f}) "
                f"scores too close (gap={gap:.2f} < {self.config.min_confidence_gap}). "
                f"Insufficient conviction for directional trade."
            )
        elif gap > 0.4:
            decision = DebateDecision.STRONG_BUY
            reasoning = (
                f"Strong bull case ({bull_score:.2f}) significantly "
                f"outweighs bear case ({bear_score:.2f}). "
                f"Gap of {gap:.2f} indicates high conviction buy."
            )
        elif gap > 0.15:
            decision = DebateDecision.BUY
            reasoning = (
                f"Bull case ({bull_score:.2f}) moderately outweighs "
                f"bear case ({bear_score:.2f}). Gap of {gap:.2f} "
                f"supports a cautious long position."
            )
        elif gap < -0.4:
            decision = DebateDecision.STRONG_SELL
            reasoning = (
                f"Strong bear case ({bear_score:.2f}) significantly "
                f"outweighs bull case ({bull_score:.2f}). "
                f"Gap of {gap:.2f} indicates high conviction sell."
            )
        elif gap < -0.15:
            decision = DebateDecision.SELL
            reasoning = (
                f"Bear case ({bear_score:.2f}) moderately outweighs "
                f"bull case ({bull_score:.2f}). Gap of {gap:.2f} "
                f"supports a cautious short position."
            )
        else:
            decision = DebateDecision.HOLD
            reasoning = (
                f"Neutral signal — bull ({bull_score:.2f}) vs bear "
                f"({bear_score:.2f}). No clear edge for directional trade."
            )

        if risk_concerns:
            reasoning += f" Risk concerns noted: {'; '.join(risk_concerns[:2])}."

        return decision, reasoning

    # ── Helper Methods ───────────────────────────────────────────────

    @staticmethod
    def _format_context(context: Dict[str, Any]) -> str:
        """Format context dict into readable string."""
        if not context:
            return "No additional context provided."
        lines = []
        for key, value in context.items():
            if isinstance(value, dict):
                lines.append(f"{key}:")
                for k, v in value.items():
                    lines.append(f"  {k}: {v}")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)

    @staticmethod
    def _extract_content(response: Any) -> str:
        """Extract text content from LLM response.

        Handles various response formats from different providers.
        """
        if isinstance(response, str):
            return response
        if hasattr(response, "content"):
            return str(response.content)
        if isinstance(response, dict):
            return response.get("content", str(response))
        return str(response)

    @staticmethod
    def _parse_argument(
        content: str, role: DebateRole, round_number: int
    ) -> DebateArgument:
        """Parse LLM response into a DebateArgument.

        Extracts structured data from free-text LLM output.
        Falls back to putting the whole response as a single point.
        """
        points: List[str] = []
        evidence: List[str] = []
        confidence = 0.5
        counter_points: List[str] = []
        risks: List[str] = []

        for line in content.split("\n"):
            line = line.strip()
            if not line:
                continue

            lower = line.lower()

            # Extract confidence
            if "confidence" in lower:
                import re
                match = re.search(r"(\d+\.?\d*)", line)
                if match:
                    confidence = min(1.0, max(0.0, float(match.group(1))))
                    if confidence > 1.0:
                        confidence /= 100.0

            # Extract points (bullet-like lines)
            elif line.startswith(("-", "*", "•")) or line.startswith(tuple(f"{i}." for i in range(1, 10))):
                clean = line.lstrip("-*•0123456789. ").strip()
                if "counter" in lower or "rebut" in lower:
                    counter_points.append(clean)
                elif "risk" in lower:
                    risks.append(clean)
                elif "evidence" in lower or "support" in lower:
                    evidence.append(clean)
                else:
                    points.append(clean)

        # If no structured points found, use the whole content
        if not points:
            points = [content[:200]]

        return DebateArgument(
            role=role,
            round_number=round_number,
            points=points[:5],
            evidence=evidence[:5],
            confidence=confidence,
            counter_points=counter_points[:5],
            risks_identified=risks[:5],
        )

    @staticmethod
    def _parse_risk_analysis(content: str) -> DebateArgument:
        """Parse risk analysis from LLM response."""
        concerns: List[str] = []
        confidence = 0.5
        has_veto = False

        for line in content.split("\n"):
            line = line.strip()
            lower = line.lower()

            if "veto" in lower and ("yes" in lower or "true" in lower or "must" in lower):
                has_veto = True
            if "confidence" in lower:
                import re
                match = re.search(r"(\d+\.?\d*)", line)
                if match:
                    confidence = min(1.0, max(0.0, float(match.group(1))))
                    if confidence > 1.0:
                        confidence /= 100.0
            if line.startswith(("-", "*", "•")) or line.startswith(tuple(f"{i}." for i in range(1, 10))):
                clean = line.lstrip("-*•0123456789. ").strip()
                if "veto" not in lower and "confidence" not in lower:
                    concerns.append(clean)

        if not concerns:
            concerns = [content[:200]]

        return DebateArgument(
            role=DebateRole.RISK_ANALYST,
            round_number=0,
            points=concerns[:5],
            evidence=[],
            confidence=confidence,
            risks_identified=concerns[:5],
        )

    @staticmethod
    def _parse_moderator_decision(
        content: str, bull_score: float, bear_score: float
    ) -> tuple[DebateDecision, str]:
        """Parse moderator decision from LLM response."""
        upper = content.upper()
        decision = DebateDecision.HOLD

        # Try to find a decision keyword
        for dec in DebateDecision:
            if dec.value in upper:
                decision = dec
                break

        return decision, content

    @staticmethod
    def _aggregate_scores(arguments: List[DebateArgument]) -> float:
        """Aggregate confidence scores across all arguments.

        Uses weighted average, giving more weight to later rounds
        (rebuttals should be more informed).
        """
        if not arguments:
            return 0.5

        total_weight = 0.0
        weighted_sum = 0.0

        for arg in arguments:
            # Weight later rounds more heavily
            weight = 1.0 + (arg.round_number - 1) * 0.3
            weighted_sum += arg.confidence * weight
            total_weight += weight

        return min(1.0, weighted_sum / total_weight) if total_weight > 0 else 0.5

    @staticmethod
    def _summarize_arguments(arguments: List[DebateArgument]) -> str:
        """Summarize arguments into a readable string."""
        if not arguments:
            return "No arguments provided."

        lines = []
        for arg in arguments:
            lines.append(
                f"Round {arg.round_number} ({arg.role.value}, "
                f"conf={arg.confidence:.2f}): "
                f"{'; '.join(arg.points[:3])}"
            )
        return "\n".join(lines)

    # ── Properties ───────────────────────────────────────────────────

    @property
    def debate_history(self) -> List[DebateResult]:
        """Get all past debate results."""
        return list(self._debate_history)

    @property
    def stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics."""
        decisions: Dict[str, int] = {}
        for result in self._debate_history:
            key = result.final_decision.value
            decisions[key] = decisions.get(key, 0) + 1

        return {
            "total_debates": len(self._debate_history),
            "decision_distribution": decisions,
            "config": self.config.model_dump(),
        }


# ═══════════════════════════════════════════════════════════════════════
# Demo
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import asyncio

    async def demo():
        # Run debate without LLM (uses fallback)
        orchestrator = DebateOrchestrator(
            config=DebateConfig(max_rounds=2)
        )

        result = await orchestrator.debate(
            symbol="AAPL",
            context={
                "price": 175.50,
                "change_pct": 2.3,
                "volume_trend": "increasing",
                "sector": "Technology",
                "pe_ratio": 28.5,
            },
        )

        print("=" * 60)
        print(f"DEBATE RESULT: {result.symbol}")
        print("=" * 60)
        print(f"Bull Score: {result.bull_score:.2f}")
        print(f"Bear Score: {result.bear_score:.2f}")
        print(f"Risk Veto: {result.risk_veto}")
        print(f"Final Decision: {result.final_decision.value}")
        print(f"Reasoning: {result.reasoning[:200]}...")
        print(f"Rounds: {result.n_rounds}")

        print("\n--- Bull Arguments ---")
        for arg in result.bull_arguments:
            print(f"  Round {arg.round_number} (conf={arg.confidence:.2f}):")
            for p in arg.points[:3]:
                print(f"    • {p}")

        print("\n--- Bear Arguments ---")
        for arg in result.bear_arguments:
            print(f"  Round {arg.round_number} (conf={arg.confidence:.2f}):")
            for p in arg.points[:3]:
                print(f"    • {p}")

        if result.risk_analysis:
            print(f"\n--- Risk Analysis (conf={result.risk_analysis.confidence:.2f}) ---")
            for c in result.risk_analysis.risks_identified[:3]:
                print(f"  ⚠ {c}")

        print(f"\nAPI dict: {result.to_api_dict()}")
        print(f"\nOrchestrator stats: {orchestrator.stats}")

    asyncio.run(demo())
