from __future__ import annotations

from app.models import KillSwitchState, Opportunity, PulseSignal, RiskDecision, StrategyConfig


def derive_kill_switch(
    pulse_signals: list[PulseSignal],
    daily_drawdown_pct: float,
    entropy_threshold: float,
) -> KillSwitchState:
    if daily_drawdown_pct >= 0.05:
        return KillSwitchState(mode="halt", triggered=True, reason="daily drawdown limit reached")

    if any(signal.entropy_score >= entropy_threshold for signal in pulse_signals):
        return KillSwitchState(mode="halt", triggered=True, reason="high-entropy pulse active")

    if any(
        tag.lower() in {"exchange", "exploit", "withdrawal", "incident"}
        for signal in pulse_signals
        for tag in signal.tags
    ):
        return KillSwitchState(mode="halt", triggered=True, reason="exchange risk pulse active")

    if any(signal.entropy_score >= max(0.6, entropy_threshold - 0.15) for signal in pulse_signals):
        return KillSwitchState(mode="caution", triggered=False, reason="elevated macro uncertainty")

    return KillSwitchState(mode="normal", triggered=False, reason="")


def evaluate_risk(
    opportunity: Opportunity,
    pulse_signals: list[PulseSignal],
    config: StrategyConfig,
    capital_usd: float,
    daily_drawdown_pct: float,
) -> RiskDecision:
    reasons: list[str] = []
    capped_size = min(opportunity.size_usd, capital_usd, config.max_position_usd)
    kill_switch = derive_kill_switch(
        pulse_signals=pulse_signals,
        daily_drawdown_pct=daily_drawdown_pct,
        entropy_threshold=config.stop_on_pulse_entropy,
    )

    if daily_drawdown_pct >= config.max_daily_drawdown_pct:
        reasons.append("daily drawdown limit reached")

    if kill_switch.triggered:
        reasons.append(kill_switch.reason)

    if capped_size <= 0:
        reasons.append("no capital available")

    if opportunity.net_edge_bps < config.min_edge_bps:
        reasons.append("edge below threshold")

    approved = not reasons
    return RiskDecision(approved=approved, reasons=reasons, capped_size_usd=round(capped_size, 2))
