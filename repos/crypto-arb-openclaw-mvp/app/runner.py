from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
import os
import time
from typing import Any, Callable

from app.config import load_live_trading_config, load_runner_config, load_strategy_config
from app.execution.okx_live import OkxLiveExecution
from app.live_validation_runner import run_live_validation_cycle
from app.market_data.coingecko_public import CoinGeckoReferenceMarketData
from app.market_data.okx_public import OkxPublicMarketData
from app.models import KillSwitchState, OrderBookTop, PulseSignal, RunnerConfig
from app.risk import derive_kill_switch
from app.telemetry import append_jsonl


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def resolve_book_top(
    config: RunnerConfig,
    okx_market: Any,
    coingecko_market: Any,
) -> OrderBookTop:
    if config.price_source == "okx":
        return okx_market.get_book_ticker(config.symbol)
    if config.price_source == "coingecko":
        return coingecko_market.get_reference_book(
            symbol=config.symbol,
            coin_id=config.coingecko_coin_id,
            vs_currency="usd",
        )
    raise ValueError(f"unsupported price source: {config.price_source}")


def run_hft_cycles(
    runner_config: RunnerConfig,
    execution: Any,
    okx_market: Any,
    coingecko_market: Any,
    pulse_signals: list[PulseSignal],
    live_config: Any | None = None,
    daily_loss_usd: float = 0.0,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> list[dict[str, Any]]:
    strategy_config = load_strategy_config()
    live_config = live_config or load_live_trading_config()
    records: list[dict[str, Any]] = []
    for cycle in range(1, runner_config.cycle_count + 1):
        started = time.perf_counter()
        book = resolve_book_top(runner_config, okx_market=okx_market, coingecko_market=coingecko_market)
        daily_drawdown_pct = 0.0
        kill_switch: KillSwitchState = derive_kill_switch(
            pulse_signals=pulse_signals,
            daily_drawdown_pct=daily_drawdown_pct,
            entropy_threshold=strategy_config.stop_on_pulse_entropy,
        )
        result = run_live_validation_cycle(
            book=book,
            kill_switch=kill_switch,
            execution=execution,
            live_config=live_config,
            explicit_confirmation=runner_config.explicit_confirmation,
            daily_loss_usd=daily_loss_usd,
        )
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        record = {
            "ts": _utc_now(),
            "cycle": cycle,
            "price_source": runner_config.price_source,
            "symbol": runner_config.symbol,
            "latency_ms": elapsed_ms,
            "kill_switch": asdict(kill_switch),
            "book": asdict(book),
            "result": result,
        }
        append_jsonl(runner_config.telemetry_path, record)
        records.append(record)
        if cycle < runner_config.cycle_count:
            sleep_fn(max(runner_config.poll_interval_ms, 0) / 1000)
    return records


def build_default_runner() -> tuple[RunnerConfig, Any, Any, Any]:
    runner_config = load_runner_config()
    live_config = load_live_trading_config()
    okx_market = OkxPublicMarketData()
    coingecko_market = CoinGeckoReferenceMarketData(
        api_key=os.getenv("COINGECKO_PRO_API_KEY", ""),
        api_base_url=os.getenv("COINGECKO_API_BASE_URL", "https://pro-api.coingecko.com/api/v3"),
    )
    execution = OkxLiveExecution(
        api_key=os.getenv("OKX_API_KEY", ""),
        api_secret=os.getenv("OKX_API_SECRET", ""),
        passphrase=os.getenv("OKX_API_PASSPHRASE", ""),
        api_base_url=os.getenv("OKX_API_BASE_URL", "https://www.okx.com"),
        demo_trading=os.getenv("OKX_DEMO_TRADING", "false").lower() in {"1", "true", "yes", "on"},
    )
    return runner_config, execution, okx_market, coingecko_market
