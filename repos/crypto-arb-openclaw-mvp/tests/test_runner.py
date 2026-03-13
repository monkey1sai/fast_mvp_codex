from __future__ import annotations

import json
import tempfile
import unittest

from app.config import load_live_trading_config
from app.models import OrderBookTop, PositionState, RunnerConfig
from app.runner import run_hft_cycles


class _FakeExecution:
    def __init__(self) -> None:
        self.order_ids: list[str] = []

    def get_position(self, symbol: str):
        return PositionState(symbol=symbol, base_qty=0.0, quote_value_usd=0.0, open_orders=0)

    def get_symbol_constraints(self, symbol: str):
        return {}

    def place_order(self, quote, book):
        order_id = f"ord-{len(self.order_ids) + 1}"
        self.order_ids.append(order_id)
        return {"code": "0", "data": [{"ordId": order_id, "state": "filled"}]}

    def cancel_order(self, symbol: str, order_id: str):
        return {"code": "0", "data": [{"ordId": order_id, "state": "canceled"}]}

    def get_order(self, symbol: str, order_id: str):
        return {"code": "0", "data": [{"ordId": order_id, "state": "filled"}]}


class _FakeOkxMarket:
    def __init__(self) -> None:
        self.calls = 0

    def get_book_ticker(self, symbol: str):
        self.calls += 1
        return OrderBookTop(symbol=symbol, bid=100.0, ask=100.2, timestamp=f"t-{self.calls}")


class _FakeCoinGeckoMarket:
    def get_reference_book(self, symbol: str, coin_id: str, vs_currency: str = "usd"):
        return OrderBookTop(symbol=symbol, bid=99.9, ask=100.1, timestamp="cg-1")


class RunnerTests(unittest.TestCase):
    def _live_config(self):
        config = load_live_trading_config()
        config.enabled = True
        config.exchange = "okx"
        config.symbol_allowlist = ["BTC_USDT"]
        config.require_explicit_confirmation = False
        return config

    def test_run_hft_cycles_writes_telemetry_and_cycles(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            telemetry_path = f"{tmpdir}/runner.jsonl"
            runner_config = RunnerConfig(
                symbol="BTC_USDT",
                price_source="okx",
                coingecko_coin_id="bitcoin",
                cycle_count=2,
                poll_interval_ms=1,
                telemetry_path=telemetry_path,
                explicit_confirmation=True,
            )
            records = run_hft_cycles(
                runner_config=runner_config,
                execution=_FakeExecution(),
                okx_market=_FakeOkxMarket(),
                coingecko_market=_FakeCoinGeckoMarket(),
                pulse_signals=[],
                live_config=self._live_config(),
                daily_loss_usd=0.0,
                sleep_fn=lambda _: None,
            )
            self.assertEqual(len(records), 2)
            self.assertEqual(records[-1]["result"]["placed_orders"], 1)
            with open(telemetry_path, "r", encoding="utf-8") as handle:
                rows = [json.loads(line) for line in handle.read().splitlines()]
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["symbol"], "BTC_USDT")
        self.assertIn("latency_ms", rows[0])

    def test_run_hft_cycles_uses_coingecko_reference_when_selected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            runner_config = RunnerConfig(
                symbol="BTC_USDT",
                price_source="coingecko",
                coingecko_coin_id="bitcoin",
                cycle_count=1,
                poll_interval_ms=1,
                telemetry_path=f"{tmpdir}/runner.jsonl",
                explicit_confirmation=True,
            )
            records = run_hft_cycles(
                runner_config=runner_config,
                execution=_FakeExecution(),
                okx_market=_FakeOkxMarket(),
                coingecko_market=_FakeCoinGeckoMarket(),
                pulse_signals=[],
                live_config=self._live_config(),
                daily_loss_usd=0.0,
                sleep_fn=lambda _: None,
            )
        self.assertEqual(records[0]["price_source"], "coingecko")
        self.assertEqual(records[0]["book"]["timestamp"], "cg-1")


if __name__ == "__main__":
    unittest.main()
