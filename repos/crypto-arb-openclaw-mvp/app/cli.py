from __future__ import annotations

import json
from dataclasses import asdict

from app.config import load_strategy_config
from app.execution.pionex_dryrun import PionexDryRunExecution
from app.integrations.coingecko_mcp import snapshot_from_market_tool
from app.integrations.openclaw import build_agent_summary, build_openclaw_message
from app.integrations.pulse_mcp import pulse_signals_from_context
from app.models import OrderBookTop, PositionState
from app.quote_engine import build_quote_intents
from app.risk import derive_kill_switch
from app.simulator import run_simulation


MARKET_PAYLOAD = {
    "generated_at": "2026-03-13T00:00:00Z",
    "assets": [
        {
            "symbol": "btc",
            "current_price": 71500,
            "high_24h": 73000,
            "low_24h": 69000,
            "price_change_percentage_24h": 3.1,
            "total_volume": 48_000_000_000,
        },
        {
            "symbol": "eth",
            "current_price": 2110,
            "high_24h": 2200,
            "low_24h": 2000,
            "price_change_percentage_24h": 4.4,
            "total_volume": 29_000_000_000,
        },
    ],
}

PULSE_PAYLOAD = {
    "items": [
        {
            "task_title": "Crypto 指數：極度恐懼 (18)",
            "summary": "市場情緒偏弱，但波動上升。",
            "entropy_score": 0.667,
            "decision_signal_score": 0.597,
            "tags": ["crypto", "fear"],
        }
    ]
}


def main() -> None:
    config = load_strategy_config()
    snapshots = snapshot_from_market_tool(MARKET_PAYLOAD)
    pulse_signals = pulse_signals_from_context(PULSE_PAYLOAD)
    trades = run_simulation(snapshots, pulse_signals, config)
    summary = build_agent_summary(trades)
    book = OrderBookTop(
        symbol=config.trading_pair,
        bid=MARKET_PAYLOAD["assets"][0]["current_price"] - 20,
        ask=MARKET_PAYLOAD["assets"][0]["current_price"] + 20,
        timestamp=MARKET_PAYLOAD["generated_at"],
    )
    kill_switch = derive_kill_switch(pulse_signals, daily_drawdown_pct=0.0, entropy_threshold=config.stop_on_pulse_entropy)
    quotes = build_quote_intents(
        book=book,
        position=PositionState(symbol=config.trading_pair, base_qty=0.0, quote_value_usd=0.0, open_orders=0),
        kill_switch=kill_switch,
        max_notional_usd=config.max_notional_per_order_usd,
        quote_refresh_ms=config.quote_refresh_ms,
    )
    execution = PionexDryRunExecution()
    fills = [execution.place_order(quote, book) for quote in quotes]
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(json.dumps({"risk_mode": kill_switch.mode, "quotes": [asdict(quote) for quote in quotes], "fills": fills}, ensure_ascii=False, indent=2))
    print(build_openclaw_message(summary))


if __name__ == "__main__":
    main()
