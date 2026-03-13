import os
import unittest

from app.config import load_strategy_config


class HftConfigTests(unittest.TestCase):
    def test_hft_defaults_exist(self) -> None:
        original = os.environ.copy()
        try:
            for key in [
                "TRADING_PAIR",
                "MAX_NOTIONAL_PER_ORDER_USD",
                "MAX_OPEN_ORDERS",
                "MAX_NET_POSITION_USD",
                "QUOTE_REFRESH_MS",
                "STOP_ON_PULSE_ENTROPY",
            ]:
                os.environ.pop(key, None)

            config = load_strategy_config()
            self.assertEqual(config.trading_pair, "BTC_USDT")
            self.assertEqual(config.max_notional_per_order_usd, 5.0)
            self.assertEqual(config.max_open_orders, 2)
            self.assertEqual(config.max_net_position_usd, 10.0)
            self.assertEqual(config.quote_refresh_ms, 1200)
            self.assertEqual(config.stop_on_pulse_entropy, 0.75)
        finally:
            os.environ.clear()
            os.environ.update(original)


if __name__ == "__main__":
    unittest.main()
