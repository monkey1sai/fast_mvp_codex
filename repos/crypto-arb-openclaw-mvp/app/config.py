from __future__ import annotations

import os

from app.models import LiveTradingConfig, StrategyConfig


def _float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return float(value)


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return int(value)


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def load_strategy_config() -> StrategyConfig:
    return StrategyConfig(
        trading_pair=os.getenv("TRADING_PAIR", "BTC_USDT"),
        min_edge_bps=_float_env("MIN_EDGE_BPS", 25.0),
        backtest_profit_target_bps=_float_env("BACKTEST_PROFIT_TARGET_BPS", 25.0),
        backtest_window_seconds=_int_env("BACKTEST_WINDOW_SECONDS", 300),
        cooldown_seconds=_int_env("COOLDOWN_SECONDS", 150),
        taker_fee_bps=_float_env("TAKER_FEE_BPS", 10.0),
        slippage_bps=_float_env("SLIPPAGE_BPS", 5.0),
        max_position_usd=_float_env("MAX_POSITION_USD", 50.0),
        max_daily_drawdown_pct=_float_env("MAX_DAILY_DRAWDOWN_PCT", 0.10),
        max_notional_per_order_usd=_float_env("MAX_NOTIONAL_PER_ORDER_USD", 5.0),
        max_open_orders=_int_env("MAX_OPEN_ORDERS", 2),
        max_net_position_usd=_float_env("MAX_NET_POSITION_USD", 10.0),
        quote_refresh_ms=_int_env("QUOTE_REFRESH_MS", 1200),
        stop_on_pulse_entropy=_float_env("STOP_ON_PULSE_ENTROPY", 0.75),
        dry_run=_bool_env("DRY_RUN", True),
    )


def load_live_market_config() -> dict[str, str | int]:
    return {
        "coingecko_ws_url": os.getenv("COINGECKO_WS_URL", "wss://stream.coingecko.com/v1"),
        "coingecko_ws_channel": os.getenv("COINGECKO_WS_CHANNEL", "CGSimplePrice"),
        "coingecko_ws_coin_ids": os.getenv("COINGECKO_WS_COIN_IDS", "bitcoin,ethereum"),
        "coingecko_ws_duration_seconds": _int_env("COINGECKO_WS_DURATION_SECONDS", 300),
    }


def load_live_trading_config() -> LiveTradingConfig:
    allowlist = [item.strip() for item in os.getenv("LIVE_SYMBOL_ALLOWLIST", "BTC_USDT").split(",") if item.strip()]
    return LiveTradingConfig(
        enabled=_bool_env("LIVE_TRADING_ENABLED", False),
        exchange=os.getenv("LIVE_EXCHANGE", "pionex"),
        api_base_url=os.getenv("PIONEX_API_BASE_URL", "https://api.pionex.com"),
        symbol_allowlist=allowlist,
        max_notional_per_order_usd=_float_env("MAX_NOTIONAL_PER_ORDER_USD", 5.0),
        max_daily_loss_usd=_float_env("MAX_DAILY_LOSS_USD", 1.0),
        auto_cancel_after_ms=_int_env("AUTO_CANCEL_AFTER_MS", 3000),
        require_explicit_confirmation=_bool_env("REQUIRE_EXPLICIT_CONFIRMATION", True),
    )
