from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class MarketSnapshot:
    symbol: str
    venue_bid: float
    venue_ask: float
    reference_price: float
    volatility_24h_pct: float
    liquidity_score: float
    timestamp: str


@dataclass(slots=True)
class PulseSignal:
    task_title: str
    summary: str
    entropy_score: float
    decision_signal_score: float
    tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class StrategyConfig:
    trading_pair: str
    min_edge_bps: float
    backtest_profit_target_bps: float
    backtest_window_seconds: int
    cooldown_seconds: int
    taker_fee_bps: float
    slippage_bps: float
    max_position_usd: float
    max_daily_drawdown_pct: float
    max_notional_per_order_usd: float
    max_open_orders: int
    max_net_position_usd: float
    quote_refresh_ms: int
    stop_on_pulse_entropy: float
    dry_run: bool = True


@dataclass(slots=True)
class OrderBookTop:
    symbol: str
    bid: float
    ask: float
    timestamp: str

    @property
    def mid_price(self) -> float:
        return (self.bid + self.ask) / 2

    @property
    def spread_bps(self) -> float:
        if self.mid_price == 0:
            return 0.0
        return ((self.ask - self.bid) / self.mid_price) * 10_000


@dataclass(slots=True)
class QuoteIntent:
    symbol: str
    side: str
    price: float
    size_usd: float
    ttl_ms: int
    rationale: str

    @property
    def notional_usd(self) -> float:
        return self.size_usd


@dataclass(slots=True)
class PositionState:
    symbol: str
    base_qty: float
    quote_value_usd: float
    open_orders: int

    @property
    def net_exposure_usd(self) -> float:
        return self.quote_value_usd


@dataclass(slots=True)
class KillSwitchState:
    mode: str
    triggered: bool
    reason: str


@dataclass(slots=True)
class LiveTradingConfig:
    enabled: bool
    exchange: str
    api_base_url: str
    symbol_allowlist: list[str]
    max_notional_per_order_usd: float
    max_daily_loss_usd: float
    auto_cancel_after_ms: int
    require_explicit_confirmation: bool


@dataclass(slots=True)
class LiveGuardDecision:
    approved: bool
    reasons: list[str]
    capped_notional_usd: float


@dataclass(slots=True)
class RunnerConfig:
    symbol: str
    price_source: str
    coingecko_coin_id: str
    cycle_count: int
    poll_interval_ms: int
    telemetry_path: str
    explicit_confirmation: bool


@dataclass(slots=True)
class CycleDecision:
    action: str
    estimated_net_profit_bps: float
    cooldown_seconds: int
    reason: str


@dataclass(slots=True)
class Opportunity:
    symbol: str
    gross_edge_bps: float
    net_edge_bps: float
    size_usd: float
    expected_pnl_usd: float
    rationale: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RiskDecision:
    approved: bool
    reasons: list[str]
    capped_size_usd: float


@dataclass(slots=True)
class SimulatedTrade:
    opportunity: Opportunity
    risk: RiskDecision
    realized_pnl_usd: float
    capital_after_usd: float
