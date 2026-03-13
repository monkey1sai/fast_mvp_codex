import json
import unittest

from app.execution.pionex_live import PionexLiveExecution, build_rest_signature
from app.models import OrderBookTop, QuoteIntent


class PionexLiveTests(unittest.TestCase):
    def test_build_rest_signature_matches_official_example(self) -> None:
        signature = build_rest_signature(
            method="GET",
            path="/api/v1/trade/allOrders",
            params={"symbol": "BTC_USDT", "limit": "1", "timestamp": "1655896754515"},
            body='{"symbol": "BTC_USDT"}',
            secret="NFqv4MB3hB0SOiEsJNDP9e0jDdKPWbDqS_Z1dbU4",
        )
        self.assertEqual(signature, "ec83d21e1237cbe7e0172f79c0e3a4741c86f6b201ba762f21149bf195519be1")

    def test_place_order_uses_transport(self) -> None:
        calls: list[dict] = []

        def fake_transport(method: str, url: str, headers: dict, body: str | None) -> dict:
            calls.append({"method": method, "url": url, "headers": headers, "body": body})
            if "/api/v1/common/symbols" in url:
                return {
                    "result": True,
                    "data": {"symbols": [{"symbol": "BTC_USDT", "basePrecision": 6, "quotePrecision": 2, "enable": True}]},
                }
            return {"result": True, "data": {"orderId": 12345}}

        adapter = PionexLiveExecution(
            api_key="demo-key",
            api_secret="demo-secret",
            transport=fake_transport,
        )
        quote = QuoteIntent(symbol="BTC_USDT", side="buy", price=100.0, size_usd=5.0, ttl_ms=1000, rationale="demo")
        book = OrderBookTop(symbol="BTC_USDT", bid=99.9, ask=100.1, timestamp="2026-03-13T00:00:00Z")

        result = adapter.place_order(quote, book)

        self.assertTrue(result["result"])
        self.assertEqual(result["data"]["orderId"], 12345)
        self.assertEqual(calls[0]["method"], "GET")
        self.assertIn("/api/v1/common/symbols", calls[0]["url"])
        self.assertEqual(calls[1]["method"], "POST")
        self.assertIn("/api/v1/trade/order?timestamp=", calls[1]["url"])
        self.assertEqual(calls[1]["headers"]["User-Agent"], "SAGA-Brain/2.0")
        body = json.loads(calls[1]["body"])
        self.assertEqual(body["symbol"], "BTC_USDT")
        self.assertEqual(body["type"], "LIMIT")
        self.assertEqual(body["size"], "0.050000")
        self.assertEqual(body["price"], "100.00")

    def test_cancel_order_sends_body_with_symbol(self) -> None:
        calls: list[dict] = []

        def fake_transport(method: str, url: str, headers: dict, body: str | None) -> dict:
            calls.append({"method": method, "url": url, "headers": headers, "body": body})
            return {"result": True, "data": {"orderId": 12345}}

        adapter = PionexLiveExecution(
            api_key="demo-key",
            api_secret="demo-secret",
            transport=fake_transport,
        )

        result = adapter.cancel_order("BTC_USDT", "12345")

        self.assertTrue(result["result"])
        self.assertEqual(calls[0]["method"], "DELETE")
        self.assertIn("/api/v1/trade/order?timestamp=", calls[0]["url"])
        self.assertEqual(json.loads(calls[0]["body"]), {"symbol": "BTC_USDT", "orderId": 12345})
        self.assertEqual(calls[0]["headers"]["User-Agent"], "SAGA-Brain/2.0")

    def test_auth_calls_balances_endpoint(self) -> None:
        calls: list[dict] = []

        def fake_transport(method: str, url: str, headers: dict, body: str | None) -> dict:
            calls.append({"method": method, "url": url, "headers": headers, "body": body})
            return {"result": True, "data": {"balances": []}}

        adapter = PionexLiveExecution(
            api_key="demo-key",
            api_secret="demo-secret",
            transport=fake_transport,
        )

        self.assertTrue(adapter.test_auth())
        self.assertEqual(calls[0]["method"], "GET")
        self.assertIn("/api/v1/account/balances?timestamp=", calls[0]["url"])

    def test_auth_returns_false_on_runtime_error(self) -> None:
        def fake_transport(method: str, url: str, headers: dict, body: str | None) -> dict:
            raise RuntimeError("Pionex API error 403: {'raw': ''}")

        adapter = PionexLiveExecution(
            api_key="demo-key",
            api_secret="demo-secret",
            transport=fake_transport,
        )

        self.assertFalse(adapter.test_auth())


if __name__ == "__main__":
    unittest.main()
