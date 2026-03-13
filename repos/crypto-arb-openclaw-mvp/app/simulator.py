from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.models import MarketSnapshot, PulseSignal, SimulatedTrade, StrategyConfig
from app.risk import evaluate_risk
from app.strategy import evaluate_cycle_decision, scan_opportunity


def _parse_timestamp(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def run_simulation(
    snapshots: list[MarketSnapshot],
    pulse_signals: list[PulseSignal],
    config: StrategyConfig,
    initial_capital_usd: float = 30.0,
) -> list[SimulatedTrade]:
    capital = initial_capital_usd
    peak_capital = initial_capital_usd
    trades: list[SimulatedTrade] = []
    next_allowed_at: datetime | None = None

    for index, snapshot in enumerate(snapshots):
        current_at = _parse_timestamp(snapshot.timestamp)
        if next_allowed_at is not None and current_at < next_allowed_at:
            continue

        window_start = current_at - timedelta(seconds=config.backtest_window_seconds)
        recent_snapshots = [
            item
            for item in snapshots[: index + 1]
            if item.symbol == snapshot.symbol and _parse_timestamp(item.timestamp) >= window_start
        ]
        cycle_decision = evaluate_cycle_decision(recent_snapshots, config)
        if cycle_decision.action != "trade":
            next_allowed_at = current_at + timedelta(seconds=cycle_decision.cooldown_seconds)
            continue

        opportunity = scan_opportunity(snapshot, config)
        if opportunity is None:
            continue

        drawdown_pct = 0.0 if peak_capital == 0 else max(0.0, (peak_capital - capital) / peak_capital)
        risk = evaluate_risk(opportunity, pulse_signals, config, capital_usd=capital, daily_drawdown_pct=drawdown_pct)
        realized = opportunity.expected_pnl_usd if risk.approved else 0.0
        capital = round(capital + realized, 4)
        peak_capital = max(peak_capital, capital)
        trades.append(
            SimulatedTrade(
                opportunity=opportunity,
                risk=risk,
                realized_pnl_usd=round(realized, 4),
                capital_after_usd=capital,
            )
        )

    return trades
