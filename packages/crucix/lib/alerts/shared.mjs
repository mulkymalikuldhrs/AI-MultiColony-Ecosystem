// Shared alert utilities — TIER_CONFIG, rule-based evaluation, parseJSON
// Extracted from telegram.mjs and discord.mjs to eliminate duplication

// ─── Alert Tiers ────────────────────────────────────────────────────────────
// FLASH:    Immediate action required — market-moving, time-critical
// PRIORITY: Important signal cluster — act within hours
// ROUTINE:  Noteworthy change — FYI, no urgency

export const TIER_CONFIG = {
  FLASH:    { emoji: '🔴', color: 0xFF0000, label: 'FLASH',    cooldownMs: 5 * 60 * 1000,  maxPerHour: 6 },
  PRIORITY: { emoji: '🟡', color: 0xFFAA00, label: 'PRIORITY', cooldownMs: 30 * 60 * 1000, maxPerHour: 4 },
  ROUTINE:  { emoji: '🔵', color: 0x3498DB, label: 'ROUTINE',  cooldownMs: 60 * 60 * 1000, maxPerHour: 2 },
};

// ─── Rule-Based Alert Fallback ────────────────────────────────────────────

/**
 * Deterministic alert evaluation when LLM is unavailable.
 * Uses signal counts, severity, and cross-domain correlation.
 */
export function ruleBasedEvaluation(signals, delta) {
  const criticals = signals.filter(s => s.severity === 'critical');
  const highs = signals.filter(s => s.severity === 'high');
  const nukeSignal = signals.find(s => s.key === 'nuke_anomaly');
  const osintNew = signals.filter(s => s.key?.startsWith('tg_urgent'));
  const marketSignals = signals.filter(s => ['vix', 'hy_spread', 'wti', 'brent', 'natgas', 'gold', 'silver', '10y2y'].includes(s.key));
  const conflictSignals = signals.filter(s => ['conflict_events', 'conflict_fatalities', 'thermal_total'].includes(s.key));

  // FLASH: nuclear anomaly, or ≥3 critical signals across domains
  if (nukeSignal) {
    return {
      shouldAlert: true, tier: 'FLASH', confidence: 'HIGH',
      headline: 'Nuclear Anomaly Detected',
      reason: 'Safecast radiation monitors have flagged an anomaly. This requires immediate attention.',
      actionable: 'Check dashboard for affected sites. Monitor confirmation from secondary sources.',
      signals: ['nuke_anomaly'],
      crossCorrelation: 'radiation monitors',
    };
  }

  // FLASH: ≥2 critical signals AND they span multiple domains
  const hasCriticalMarket = criticals.some(s => marketSignals.includes(s));
  const hasCriticalConflict = criticals.some(s => conflictSignals.includes(s) || osintNew.includes(s));
  if (criticals.length >= 2 && hasCriticalMarket && hasCriticalConflict) {
    return {
      shouldAlert: true, tier: 'FLASH', confidence: 'HIGH',
      headline: `${criticals.length} Critical Cross-Domain Signals`,
      reason: `${criticals.length} critical signals detected across market and conflict domains. Multi-domain correlation suggests systemic event.`,
      actionable: 'Review dashboard immediately. Assess portfolio exposure.',
      signals: criticals.map(s => s.label || s.key).slice(0, 5),
      crossCorrelation: 'market + conflict',
    };
  }

  // PRIORITY: ≥2 high/critical signals in same direction
  const escalatedHighs = [...criticals, ...highs].filter(s => s.direction === 'up');
  if (escalatedHighs.length >= 2) {
    return {
      shouldAlert: true, tier: 'PRIORITY', confidence: 'MEDIUM',
      headline: `${escalatedHighs.length} Escalating Signals`,
      reason: `Multiple indicators escalating simultaneously: ${escalatedHighs.map(s => s.label || s.key).slice(0, 3).join(', ')}.`,
      actionable: 'Monitor for continuation. Check if trend persists in next sweep.',
      signals: escalatedHighs.map(s => s.label || s.key).slice(0, 5),
      crossCorrelation: 'multi-indicator',
    };
  }

  // PRIORITY: ≥5 new OSINT posts (surge in conflict reporting)
  if (osintNew.length >= 5) {
    return {
      shouldAlert: true, tier: 'PRIORITY', confidence: 'MEDIUM',
      headline: `OSINT Surge: ${osintNew.length} New Urgent Posts`,
      reason: `${osintNew.length} new urgent OSINT signals detected. Elevated conflict reporting tempo.`,
      actionable: 'Review OSINT stream for pattern. Cross-check with satellite and ACLED data.',
      signals: osintNew.map(s => s.text || s.label || s.key).slice(0, 5),
      crossCorrelation: 'telegram OSINT',
    };
  }

  // ROUTINE: any critical signal OR ≥3 high signals
  if (criticals.length >= 1 || highs.length >= 3) {
    const topSignal = criticals[0] || highs[0];
    return {
      shouldAlert: true, tier: 'ROUTINE', confidence: 'LOW',
      headline: topSignal.label || topSignal.reason || 'Signal Change Detected',
      reason: `${criticals.length} critical, ${highs.length} high-severity signals. ${delta.summary.direction} bias.`,
      actionable: 'Monitor',
      signals: [...criticals, ...highs].map(s => s.label || s.key).slice(0, 4),
      crossCorrelation: 'single-domain',
    };
  }

  // No alert
  return {
    shouldAlert: false,
    reason: `${signals.length} signals, but none meet alert threshold (${criticals.length} critical, ${highs.length} high).`,
  };
}

// ─── JSON Parser ───────────────────────────────────────────────────────────

export function parseJSON(text) {
  if (!text) return null;
  let cleaned = text.trim();
  if (cleaned.startsWith('```')) {
    cleaned = cleaned.replace(/^```(?:json)?\n?/, '').replace(/\n?```$/, '');
  }
  try {
    return JSON.parse(cleaned);
  } catch {
    const match = cleaned.match(/\{[\s\S]*\}/);
    if (match) {
      try { return JSON.parse(match[0]); } catch { /* give up */ }
    }
    return null;
  }
}
