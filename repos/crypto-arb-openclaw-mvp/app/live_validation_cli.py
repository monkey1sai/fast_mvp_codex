from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path

from app.config import load_live_trading_config
from app.execution.okx_live import OkxLiveExecution
from app.execution.pionex_live import PionexLiveExecution
from app.live_validation_runner import run_live_validation_cycle
from app.market_data.coingecko_public import CoinGeckoReferenceMarketData
from app.market_data.okx_public import OkxPublicMarketData
from app.market_data.pionex_public import PionexPublicMarketData
from app.models import KillSwitchState, OrderBookTop


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if not os.getenv(key):
            os.environ[key] = value


def main() -> None:
    workspace_env = Path(__file__).resolve().parents[3] / ".env"
    load_env_file(workspace_env)

    parser = argparse.ArgumentParser(description="Run one guarded live validation cycle on Pionex or OKX.")
    parser.add_argument("--bid", type=float)
    parser.add_argument("--ask", type=float)
    parser.add_argument("--symbol", default="BTC_USDT")
    parser.add_argument("--exchange", choices=["pionex", "okx"], default="pionex")
    parser.add_argument("--price-source", choices=["pionex", "coingecko"], default="pionex")
    parser.add_argument("--coingecko-coin-id", default="bitcoin")
    parser.add_argument("--confirm-live", action="store_true")
    parser.add_argument("--daily-loss-usd", type=float, default=0.0)
    args = parser.parse_args()

    config = load_live_trading_config()
    if args.exchange == "okx":
        api_key = os.getenv("OKX_API_KEY", "")
        api_secret = os.getenv("OKX_API_SECRET", "")
        passphrase = os.getenv("OKX_API_PASSPHRASE", "")
        if not api_key or not api_secret or not passphrase:
            raise SystemExit("OKX_API_KEY, OKX_API_SECRET, OKX_API_PASSPHRASE are required")
        execution = OkxLiveExecution(
            api_key=api_key,
            api_secret=api_secret,
            passphrase=passphrase,
            api_base_url=os.getenv("OKX_API_BASE_URL", "https://www.okx.com"),
            demo_trading=os.getenv("OKX_DEMO_TRADING", "true").lower() in {"1", "true", "yes", "on"},
        )
    else:
        api_key = os.getenv("PIONEX_API_KEY", "")
        api_secret = os.getenv("PIONEX_API_SECRET", "")
        if not api_key or not api_secret:
            raise SystemExit("PIONEX_API_KEY and PIONEX_API_SECRET are required")
        execution = PionexLiveExecution(
            api_key=api_key,
            api_secret=api_secret,
            api_base_url=config.api_base_url,
        )

    if args.bid is None or args.ask is None:
        if args.price_source == "coingecko":
            cg_api_key = os.getenv("COINGECKO_PRO_API_KEY", "")
            if not cg_api_key:
                raise SystemExit("COINGECKO_PRO_API_KEY is required for --price-source coingecko")
            market = CoinGeckoReferenceMarketData(api_key=cg_api_key)
            book = asyncio.run(
                market.get_reference_book_via_websocket(
                    symbol=args.symbol,
                    coin_id=args.coingecko_coin_id,
                )
            )
        else:
            if args.exchange == "okx":
                market = OkxPublicMarketData(api_base_url=os.getenv("OKX_API_BASE_URL", "https://www.okx.com"))
            else:
                market = PionexPublicMarketData(api_base_url=config.api_base_url)
            book = market.get_book_ticker(args.symbol)
    else:
        book = OrderBookTop(symbol=args.symbol, bid=args.bid, ask=args.ask, timestamp="manual")

    result = run_live_validation_cycle(
        book=book,
        kill_switch=KillSwitchState(mode="normal", triggered=False, reason=""),
        execution=execution,
        live_config=config,
        explicit_confirmation=args.confirm_live,
        daily_loss_usd=args.daily_loss_usd,
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
