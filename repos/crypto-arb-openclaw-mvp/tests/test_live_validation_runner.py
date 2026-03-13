import unittest
from unittest.mock import patch

from app.live_guard import evaluate_live_order
from app.live_validation_runner import run_live_validation_cycle
from app.models import KillSwitchState, LiveTradingConfig, OrderBookTop, PositionState


class _FakeExecution:
    def __init__(self, place_result: dict) -> None:
        self.place_result = place_result
        self.placed = []
        self.cancelled = []

    def place_order(self, quote, book):
        self.placed.append((quote, book))
        return self.place_result

    def cancel_order(self, symbol: str, order_id: str):
        self.cancelled.append((symbol, order_id))
        return {"cancelled": True, "symbol": symbol, "order_id": order_id}

    def get_position(self, symbol: str):
        return PositionState(
            symbol=symbol,
            base_qty=1.0,
            quote_value_usd=0.0,
            open_orders=0,
            available_quote_usd=100.0,
        )

    def get_symbol_constraints(self, symbol: str):
        return {}

    def get_order(self, symbol: str, order_id: str):
        return {"result": True, "data": {"orderId": order_id, "status": "resting"}}


class LiveValidationRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = LiveTradingConfig(
            enabled=True,
            exchange="pionex",
            api_base_url="https://api.pionex.com",
            symbol_allowlist=["BTC_USDT"],
            max_notional_per_order_usd=5.0,
            max_daily_loss_usd=1.0,
            auto_cancel_after_ms=3000,
            require_explicit_confirmation=True,
        )
        self.book = OrderBookTop(symbol="BTC_USDT", bid=99.8, ask=100.0, timestamp="2026-03-13T00:00:00Z")
        self.kill = KillSwitchState(mode="normal", triggered=False, reason="")

    def test_places_only_one_order_when_guard_passes(self) -> None:
        execution = _FakeExecution({"result": True, "data": {"orderId": "abc"}, "status": "filled"})
        result = run_live_validation_cycle(
            book=self.book,
            kill_switch=self.kill,
            execution=execution,
            live_config=self.config,
            explicit_confirmation=True,
            daily_loss_usd=0.0,
        )
        self.assertEqual(result["placed_orders"], 1)
        self.assertEqual(len(execution.placed), 1)
        self.assertTrue(any(event["stage"] == "place_order_request" for event in result["events"]))

    def test_does_not_place_when_halt(self) -> None:
        execution = _FakeExecution({"result": True, "data": {"orderId": "abc"}, "status": "filled"})
        result = run_live_validation_cycle(
            book=self.book,
            kill_switch=KillSwitchState(mode="halt", triggered=True, reason="risk"),
            execution=execution,
            live_config=self.config,
            explicit_confirmation=True,
            daily_loss_usd=0.0,
        )
        self.assertEqual(result["placed_orders"], 0)
        self.assertEqual(result["mode"], "halt")

    def test_resting_order_is_cancelled(self) -> None:
        execution = _FakeExecution({"result": True, "data": {"orderId": "abc"}, "status": "resting"})
        result = run_live_validation_cycle(
            book=self.book,
            kill_switch=self.kill,
            execution=execution,
            live_config=self.config,
            explicit_confirmation=True,
            daily_loss_usd=0.0,
        )
        self.assertEqual(result["cancelled_orders"], 1)
        self.assertEqual(execution.cancelled, [("BTC_USDT", "abc")])
        self.assertEqual(result["cancel_after_ms"], 3000)
        self.assertTrue(any(event["stage"] == "cancel_order_result" for event in result["events"]))

    def test_okx_style_result_payload_is_supported(self) -> None:
        execution = _FakeExecution({"code": "0", "data": [{"ordId": "okx-1", "state": "resting"}]})
        with patch("app.live_validation_runner.time.sleep") as _sleep:
            result = run_live_validation_cycle(
                book=self.book,
                kill_switch=self.kill,
                execution=execution,
                live_config=self.config,
                explicit_confirmation=True,
                daily_loss_usd=0.0,
            )
        self.assertEqual(result["cancelled_orders"], 1)
        self.assertEqual(execution.cancelled, [("BTC_USDT", "okx-1")])

    def test_waits_then_checks_order_before_cancel(self) -> None:
        class _CheckingExecution(_FakeExecution):
            def get_order(self, symbol: str, order_id: str):
                return {"code": "0", "data": [{"ordId": order_id, "state": "live"}]}

        execution = _CheckingExecution({"code": "0", "data": [{"ordId": "okx-1", "state": "live"}]})
        with patch("app.live_validation_runner.time.sleep") as mocked_sleep:
            result = run_live_validation_cycle(
                book=self.book,
                kill_switch=self.kill,
                execution=execution,
                live_config=self.config,
                explicit_confirmation=True,
                daily_loss_usd=0.0,
            )
        mocked_sleep.assert_called_once()
        self.assertEqual(result["cancelled_orders"], 1)

    def test_okx_place_result_without_state_still_checks_and_cancels(self) -> None:
        class _OkxExecution(_FakeExecution):
            def get_order(self, symbol: str, order_id: str):
                return {"code": "0", "data": [{"ordId": order_id, "state": "live"}]}

        execution = _OkxExecution({"code": "0", "data": [{"ordId": "okx-2", "sCode": "0", "sMsg": "Order placed"}]})
        with patch("app.live_validation_runner.time.sleep") as mocked_sleep:
            result = run_live_validation_cycle(
                book=self.book,
                kill_switch=self.kill,
                execution=execution,
                live_config=self.config,
                explicit_confirmation=True,
                daily_loss_usd=0.0,
            )
        mocked_sleep.assert_called_once()
        self.assertEqual(result["cancelled_orders"], 1)
        self.assertEqual(execution.cancelled, [("BTC_USDT", "okx-2")])

    def test_returns_guard_failure_when_below_exchange_minimum(self) -> None:
        class _ConstrainedExecution(_FakeExecution):
            def get_symbol_constraints(self, symbol: str):
                return {"minAmount": 10.0}

        execution = _ConstrainedExecution({"result": True, "data": {"orderId": "abc"}, "status": "filled"})
        result = run_live_validation_cycle(
            book=self.book,
            kill_switch=self.kill,
            execution=execution,
            live_config=self.config,
            explicit_confirmation=True,
            daily_loss_usd=0.0,
        )
        self.assertEqual(result["placed_orders"], 0)
        self.assertEqual(result["reason"], "no quote passed live guard")
        self.assertEqual(result["min_notional_usd"], 10.0)

    def test_returns_guard_failure_when_available_quote_balance_insufficient(self) -> None:
        class _LowBalanceExecution(_FakeExecution):
            def get_position(self, symbol: str):
                return PositionState(
                    symbol=symbol,
                    base_qty=0.0,
                    quote_value_usd=0.0,
                    open_orders=0,
                    available_quote_usd=2.0,
                )

        execution = _LowBalanceExecution({"result": True, "data": {"orderId": "abc"}, "status": "filled"})
        result = run_live_validation_cycle(
            book=self.book,
            kill_switch=self.kill,
            execution=execution,
            live_config=self.config,
            explicit_confirmation=True,
            daily_loss_usd=0.0,
        )
        self.assertEqual(result["placed_orders"], 0)
        self.assertEqual(result["reason"], "no quote passed live guard")
        guard_events = [event for event in result["events"] if event["stage"] == "guard_decision"]
        self.assertTrue(any("insufficient available quote balance" in event["reasons"] for event in guard_events))
        self.assertTrue(any("insufficient available base balance" in event["reasons"] for event in guard_events))


if __name__ == "__main__":
    unittest.main()
