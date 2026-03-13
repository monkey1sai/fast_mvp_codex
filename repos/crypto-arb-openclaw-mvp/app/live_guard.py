from __future__ import annotations

from app.models import LiveGuardDecision, LiveTradingConfig, QuoteIntent


def evaluate_live_order(
    quote: QuoteIntent,
    config: LiveTradingConfig,
    daily_loss_usd: float,
    explicit_confirmation: bool,
    min_notional_usd: float = 0.0,
    available_quote_usd: float | None = None,
    available_base_qty: float | None = None,
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

    if quote.side.lower() == "buy" and available_quote_usd is not None and quote.notional_usd > available_quote_usd:
        reasons.append("insufficient available quote balance")
    if quote.side.lower() == "sell" and available_base_qty is not None:
        required_base_qty = quote.notional_usd / max(quote.price, 1e-9)
        if required_base_qty > available_base_qty:
            reasons.append("insufficient available base balance")

    return LiveGuardDecision(
        approved=not reasons,
        reasons=reasons,
        capped_notional_usd=min(quote.notional_usd, config.max_notional_per_order_usd),
    )
