from __future__ import annotations

from app.models import LiveGuardDecision, LiveTradingConfig, QuoteIntent


def evaluate_live_order(
    quote: QuoteIntent,
    config: LiveTradingConfig,
    daily_loss_usd: float,
    explicit_confirmation: bool,
    min_notional_usd: float = 0.0,
) -> LiveGuardDecision:
    reasons: list[str] = []

    if not config.enabled:
        reasons.append("live trading disabled")

    if config.require_explicit_confirmation and not explicit_confirmation:
        reasons.append("explicit confirmation required")

    if quote.symbol not in config.symbol_allowlist:
        reasons.append("symbol not allowlisted")

    if quote.notional_usd > config.max_notional_per_order_usd:
        reasons.append("order notional exceeds cap")

    if min_notional_usd > 0 and quote.notional_usd < min_notional_usd:
        reasons.append("order notional below exchange minimum")

    if daily_loss_usd >= config.max_daily_loss_usd:
        reasons.append("daily loss limit reached")

    return LiveGuardDecision(
        approved=not reasons,
        reasons=reasons,
        capped_notional_usd=min(quote.notional_usd, config.max_notional_per_order_usd),
    )
