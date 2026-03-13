from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.config import load_runner_config
from app.runner import build_default_runner, run_hft_cycles


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key and key not in __import__("os").environ:
            __import__("os").environ[key] = value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run continuous HFT validation cycles.")
    parser.add_argument("--cycles", type=int, help="Override runner cycle count.")
    parser.add_argument("--symbol", help="Override trading pair symbol.")
    parser.add_argument("--price-source", choices=["okx", "coingecko"], help="Override price source.")
    parser.add_argument("--coingecko-coin-id", help="Override CoinGecko coin id.")
    parser.add_argument("--telemetry-path", help="Override JSONL telemetry output path.")
    parser.add_argument("--event-log-path", help="Override event JSONL log output path.")
    parser.add_argument("--confirm-live", action="store_true", help="Explicitly approve live order flow.")
    return parser


def main() -> None:
    root_env = Path(__file__).resolve().parents[3] / ".env"
    runtime_env = Path(__file__).resolve().parents[3] / ".env.runtime"
    load_env_file(root_env)
    load_env_file(runtime_env)

    parser = build_parser()
    args = parser.parse_args()
    runner_config = load_runner_config()
    if args.cycles is not None:
        runner_config.cycle_count = args.cycles
    if args.symbol:
        runner_config.symbol = args.symbol
    if args.price_source:
        runner_config.price_source = args.price_source
    if args.coingecko_coin_id:
        runner_config.coingecko_coin_id = args.coingecko_coin_id
    if args.telemetry_path:
        runner_config.telemetry_path = args.telemetry_path
    if args.event_log_path:
        runner_config.event_log_path = args.event_log_path
    if args.confirm_live:
        runner_config.explicit_confirmation = True

    _, execution, okx_market, coingecko_market = build_default_runner()
    records = run_hft_cycles(
        runner_config=runner_config,
        execution=execution,
        okx_market=okx_market,
        coingecko_market=coingecko_market,
        pulse_signals=[],
        daily_loss_usd=0.0,
    )
    print(
        json.dumps(
            {
                "cycles": len(records),
                "telemetry_path": runner_config.telemetry_path,
                "event_log_path": runner_config.event_log_path,
                "last_result": records[-1]["result"] if records else {},
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
