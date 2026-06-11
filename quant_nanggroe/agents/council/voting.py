"""
Weighted Voting Mechanism for Quant Nanggroe AI Trading Framework.

Implements a weighted voting system where each agent's vote is weighted
by their historical accuracy. Produces a final council decision based
on the aggregate weighted votes.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from quant_nanggroe.agents.state import (
    AgentOutput,
    AgentRole,
    AgentState,
    CouncilResult,
    TradeAction,
    VoteResult,
)


logger = logging.getLogger(__name__)


# Default weights based on historical accuracy (can be updated)
DEFAULT_VOTER_WEIGHTS: Dict[str, float] = {
    "researcher": 1.2,
    "macro": 1.0,
    "crypto": 0.9,
    "forex": 0.9,
    "strategist": 1.5,
    "risk": 2.0,       # Risk agent has highest weight for safety
    "portfolio": 1.0,
    "trader": 1.3,
    "execution": 0.5,  # Execution doesn't vote on direction
}

COUNCIL_VOTE_PROMPT = """You are participating in a council vote for the Quant Nanggroe AI Trading Framework.

Based on all available analysis and debate results, cast your vote.

## Available Analysis:
{analysis_summary}

## Debate Results:
{debate_summary}

## Your Role: {role}
## Your Weight: {weight}

Cast your vote as one of: BUY, SELL, HOLD, CLOSE, EMERGENCY_EXIT

Provide:
1. Your vote
2. Your confidence level (0.0 - 1.0)
3. Brief reasoning

Format: VOTE: **BUY/SELL/HOLD** (Confidence: X%) - Reasoning"""

COUNCIL_SUMMARY_PROMPT = """Summarize the following council vote results and determine the final decision.

## Votes:
{votes_summary}

## Weighted Scores:
{weighted_scores}

Provide:
1. Summary of the council discussion
2. Final decision based on weighted votes
3. Consensus level (0.0 - 1.0)
4. Whether human review is needed (if consensus < 0.4)

The final decision should be the action with the highest weighted score."""


class CouncilVoting:
    """
    Weighted voting mechanism for the trading council.

    Each agent casts a vote weighted by their historical accuracy.
    The final decision is determined by the highest weighted score.
    """

    def __init__(
        self,
        llm: BaseChatModel,
        voter_weights: Optional[Dict[str, float]] = None,
        consensus_threshold: float = 0.5,
    ) -> None:
        """
        Initialize the council voting system.

        Args:
            llm: Language model for vote synthesis
            voter_weights: Custom voter weights (defaults to DEFAULT_VOTER_WEIGHTS)
            consensus_threshold: Minimum consensus level for automatic execution
        """
        self._llm = llm
        self._voter_weights = voter_weights or DEFAULT_VOTER_WEIGHTS
        self._consensus_threshold = consensus_threshold

    def collect_votes(self, state: AgentState) -> List[VoteResult]:
        """
        Collect votes from all agents based on their outputs.

        Args:
            state: Current agent state with all agent outputs

        Returns:
            List of VoteResult instances
        """
        votes: List[VoteResult] = []
        agent_outputs = state.get("agent_outputs", {})

        for agent_name, output in agent_outputs.items():
            if not isinstance(output, dict):
                continue

            weight = self._voter_weights.get(agent_name, 1.0)

            # Extract vote from agent output
            vote, confidence, reasoning = self._extract_vote(
                agent_name=agent_name,
                output=output,
                state=state,
            )

            if vote is not None:
                votes.append(VoteResult(
                    voter=agent_name,
                    vote=vote,
                    weight=weight,
                    reasoning=reasoning,
                    confidence=confidence,
                ))

        return votes

    def compute_weighted_scores(self, votes: List[VoteResult]) -> Dict[str, float]:
        """
        Compute weighted scores for each trade action.

        Args:
            votes: List of vote results

        Returns:
            Dictionary mapping action to weighted score
        """
        scores: Dict[str, float] = {action.value: 0.0 for action in TradeAction}

        for vote in votes:
            action = vote.vote.value if isinstance(vote.vote, TradeAction) else str(vote.vote)
            weight = vote.weight * vote.confidence  # Weight * confidence
            scores[action] = scores.get(action, 0.0) + weight

        return scores

    def determine_decision(self, scores: Dict[str, float]) -> TradeAction:
        """
        Determine the final council decision from weighted scores.

        Args:
            scores: Weighted scores by action

        Returns:
            Final TradeAction based on highest weighted score
        """
        if not scores:
            return TradeAction.HOLD

        best_action = max(scores, key=lambda k: scores[k])
        try:
            return TradeAction(best_action)
        except ValueError:
            return TradeAction.HOLD

    def compute_consensus(self, votes: List[VoteResult], scores: Dict[str, float]) -> float:
        """
        Compute the consensus level of the council.

        Args:
            votes: List of vote results
            scores: Weighted scores by action

        Returns:
            Consensus level between 0.0 and 1.0
        """
        if not votes:
            return 0.0

        total_weight = sum(v.weight for v in votes)
        if total_weight == 0:
            return 0.0

        max_score = max(scores.values()) if scores else 0
        consensus = max_score / total_weight

        return min(max(consensus, 0.0), 1.0)

    def run_council_vote(self, state: AgentState) -> CouncilResult:
        """
        Run the full council voting process.

        Args:
            state: Current agent state

        Returns:
            CouncilResult with final decision and all vote details
        """
        # Collect votes
        votes = self.collect_votes(state)

        # Compute weighted scores
        weighted_scores = self.compute_weighted_scores(votes)

        # Determine final decision
        final_decision = self.determine_decision(weighted_scores)

        # Compute consensus
        consensus_level = self.compute_consensus(votes, weighted_scores)

        # Get debate summary
        debate_state = state.get("debate_state", {})
        debate_summary = self._summarize_debate(debate_state)

        # Determine if human review is needed
        requires_human_review = consensus_level < self._consensus_threshold

        # Create the result
        result = CouncilResult(
            final_decision=final_decision,
            debate_summary=debate_summary,
            votes=votes,
            weighted_score=weighted_scores,
            consensus_level=consensus_level,
            requires_human_review=requires_human_review,
        )

        logger.info(
            f"Council vote completed: {final_decision.value} "
            f"(consensus={consensus_level:.2f}, "
            f"human_review={requires_human_review})"
        )

        return result

    def _extract_vote(
        self,
        agent_name: str,
        output: Dict[str, Any],
        state: AgentState,
    ) -> tuple[Optional[TradeAction], float, str]:
        """
        Extract a vote from an agent's output.

        Extraction strategy (in priority order):
        1. Try to parse the content as JSON (structured output from LLM).
        2. Fall back to regex pattern matching on the text.
        3. If neither works, default to HOLD.

        Args:
            agent_name: Name of the voting agent
            output: Agent output dictionary
            state: Current agent state

        Returns:
            Tuple of (vote_action, confidence, reasoning)
        """
        content = output.get("content", "")
        confidence = output.get("confidence", 0.5)

        # ── Step 1: Try structured JSON parsing ────────────────────────
        vote = self._try_json_vote(content)

        # ── Step 2: Regex fallback ─────────────────────────────────────
        if vote is None:
            vote = self._try_regex_vote(content)

        # ── Step 3: Default to HOLD if nothing matched ─────────────────
        if vote is None:
            vote = TradeAction.HOLD
            logger.warning(
                "Vote extraction: no JSON or regex match for agent '%s', "
                "defaulting to HOLD. Content preview: %.100s",
                agent_name,
                content,
            )

        # Special handling for risk agent
        if agent_name == "risk":
            risk_verdict = state.get("risk_verdict", "VETOED")
            if risk_verdict == "VETOED":
                vote = TradeAction.HOLD
                confidence = 1.0
            elif risk_verdict == "KILL_SWITCH":
                vote = TradeAction.EMERGENCY_EXIT
                confidence = 1.0

        # Extract confidence from content
        conf_match = re.search(r"confidence[:\s]+([0-9]*\.?[0-9]+)", content, re.IGNORECASE)
        if conf_match:
            try:
                confidence = min(max(float(conf_match.group(1)), 0.0), 1.0)
            except ValueError:
                pass

        reasoning = content[:200] if content else f"Vote based on {agent_name} analysis"

        return vote, confidence, reasoning

    # ── Vote extraction helpers ────────────────────────────────────────

    @staticmethod
    def _try_json_vote(content: str) -> Optional[TradeAction]:
        """Attempt to extract a vote from JSON-structured LLM output.

        Looks for keys like 'vote', 'action', or 'decision' in the
        parsed JSON and maps the value to a TradeAction enum member.

        Returns None if content is not valid JSON or no recognised key found.
        """
        # Quick check: if the content doesn't look like JSON at all, skip.
        stripped = content.strip()
        if not stripped.startswith(("{", "[")):
            return None

        try:
            data = json.loads(stripped)
        except (json.JSONDecodeError, TypeError):
            # The LLM may wrap JSON in markdown — try to extract it.
            json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                except (json.JSONDecodeError, TypeError):
                    return None
            else:
                return None

        if not isinstance(data, dict):
            return None

        # Check common key names for the vote/action
        for key in ("vote", "action", "decision", "trade_action"):
            value = data.get(key)
            if value is not None:
                try:
                    return TradeAction(str(value).upper())
                except ValueError:
                    continue
        return None

    @staticmethod
    def _try_regex_vote(content: str) -> Optional[TradeAction]:
        """Attempt to extract a vote using regex pattern matching.

        Returns None if no pattern matches.
        """
        action_patterns = [
            (r"\bBUY\b", TradeAction.BUY),
            (r"\bSELL\b", TradeAction.SELL),
            (r"\bHOLD\b", TradeAction.HOLD),
            (r"\bCLOSE\b", TradeAction.CLOSE),
            (r"\bEMERGENCY_EXIT\b", TradeAction.EMERGENCY_EXIT),
            (r"FINAL TRANSACTION PROPOSAL:\s*\*\*(\w+)\*\*", None),
        ]

        for pattern, action in action_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                if action:
                    return action
                else:
                    try:
                        return TradeAction(match.group(1).upper())
                    except ValueError:
                        return TradeAction.HOLD

        return None

    def _summarize_debate(self, debate_state: Dict[str, Any]) -> str:
        """
        Create a summary of the debate for the council result.

        Args:
            debate_state: Debate state dictionary

        Returns:
            Debate summary string
        """
        parts = []

        # Investment debate summary
        invest_debate = debate_state.get("investment_debate", {})
        if invest_debate and isinstance(invest_debate, dict):
            judge_decision = invest_debate.get("judge_decision", "")
            if judge_decision:
                parts.append(f"Investment Debate Judge: {judge_decision[:500]}")

        # Risk debate summary
        risk_debate = debate_state.get("risk_debate", {})
        if risk_debate and isinstance(risk_debate, dict):
            judge_decision = risk_debate.get("judge_decision", "")
            if judge_decision:
                parts.append(f"Risk Debate Judge: {judge_decision[:500]}")

        return "\n\n".join(parts) if parts else "No debate conducted"
