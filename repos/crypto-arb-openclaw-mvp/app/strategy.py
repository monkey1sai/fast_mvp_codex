from __future__ import annotations

from app.models import CycleDecision, MarketSnapshot, Opportunity, StrategyConfig


def evaluate_cycle_decision(
    recent_snapshots: list[MarketSnapshot],
    config: StrategyConfig,
) -> CycleDecision:
    if not recent_snapshots:
        return CycleDecision(
            action="wait",
            estimated_net_profit_bps=0.0,
            cooldown_seconds=config.cooldown_seconds,
            reason="no recent history",
        )

    current = recent_snapshots[-1]
    min_ask = min(snapshot.venue_ask for snapshot in recent_snapshots)
    max_bid = max(snapshot.venue_bid for snapshot in recent_snapshots)
    gross_profit_bps = ((max_bid - min_ask) / max(current.reference_price, 1e-9)) * 10_000
    net_profit_bps = gross_profit_bps - config.taker_fee_bps - config.slippage_bps
    if net_profit_bps >= config.backtest_profit_target_bps:
        return CycleDecision(
            action="trade",
            estimated_net_profit_bps=round(net_profit_bps, 4),
            cooldown_seconds=0,
            reason="net edge above threshold",
        )

    return CycleDecision(
        action="wait",
        estimated_net_profit_bps=round(net_profit_bps, 4),
        cooldown_seconds=config.cooldown_seconds,
        reason="net edge below threshold",
    )


def scan_opportunity(snapshot: MarketSnapshot, config: StrategyConfig) -> Opportunity | None:
    gross_edge_bps = ((snapshot.venue_bid - snapshot.venue_ask) / snapshot.reference_price) * 10_000
    net_edge_bps = gross_edge_bps - config.taker_fee_bps - config.slippage_bps
    if net_edge_bps < config.min_edge_bps:
        return None

    size_usd = min(config.max_position_usd, snapshot.reference_price * max(snapshot.liquidity_score, 0.1) * 0.05)
    expected_pnl_usd = size_usd * (net_edge_bps / 10_000)
    rationale = (
        f"{snapshot.symbol} gross {gross_edge_bps:.2f}bps, net {net_edge_bps:.2f}bps, "
        f"volatility {snapshot.volatility_24h_pct:.2f}%."
    )
    return Opportunity(
        symbol=snapshot.symbol,
        gross_edge_bps=gross_edge_bps,
        net_edge_bps=net_edge_bps,
        size_usd=round(size_usd, 2),
        expected_pnl_usd=round(expected_pnl_usd, 4),
        rationale=rationale,
        metadata={
            "reference_price": snapshot.reference_price,
            "liquidity_score": snapshot.liquidity_score,
        },
    )
