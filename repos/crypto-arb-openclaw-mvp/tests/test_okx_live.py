import json
import unittest

from app.execution.okx_live import OkxLiveExecution
from app.models import OrderBookTop, QuoteIntent


class OkxLiveTests(unittest.TestCase):
    def test_place_order_uses_trade_order_endpoint(self) -> None:
        calls: list[dict] = []

        def fake_transport(method: str, url: str, headers: dict[str, str], body: str | None) -> dict:
            calls.append({"method": method, "url": url, "headers": headers, "body": body})
            return {"code": "0", "data": [{"ordId": "12345", "sCode": "0", "sMsg": ""}]}

        adapter = OkxLiveExecution(
            api_key="demo-key",
            api_secret="demo-secret",
            passphrase="demo-passphrase",
            transport=fake_transport,
        )
        quote = QuoteIntent(symbol="BTC_USDT", side="buy", price=71800.12, size_usd=10.0, ttl_ms=3000, rationale="demo")
        book = OrderBookTop(symbol="BTC_USDT", bid=71800.1, ask=71800.2, timestamp="2026-03-13T00:00:00Z")

        result = adapter.place_order(quote, book)

        self.assertEqual(calls[0]["method"], "POST")
        self.assertTrue(calls[0]["url"].endswith("/api/v5/trade/order"))
        self.assertEqual(calls[0]["headers"]["OK-ACCESS-KEY"], "demo-key")
        self.assertEqual(calls[0]["headers"]["x-simulated-trading"], "1")
        body = json.loads(calls[0]["body"])
        self.assertEqual(body["instId"], "BTC-USDT")
        self.assertEqual(body["tdMode"], "cash")
        self.assertEqual(body["ordType"], "post_only")
        self.assertEqual(body["side"], "buy")
        self.assertEqual(result["code"], "0")

    def test_cancel_order_uses_cancel_order_endpoint(self) -> None:
        calls: list[dict] = []

        def fake_transport(method: str, url: str, headers: dict[str, str], body: str | None) -> dict:
            calls.append({"method": method, "url": url, "headers": headers, "body": body})
            return {"code": "0", "data": [{"ordId": "12345", "sCode": "0", "sMsg": ""}]}

        adapter = OkxLiveExecution(
            api_key="demo-key",
            api_secret="demo-secret",
            passphrase="demo-passphrase",
            transport=fake_transport,
        )

        result = adapter.cancel_order("BTC_USDT", "12345")

        self.assertEqual(calls[0]["method"], "POST")
        self.assertTrue(calls[0]["url"].endswith("/api/v5/trade/cancel-order"))
        self.assertEqual(json.loads(calls[0]["body"]), {"instId": "BTC-USDT", "ordId": "12345"})
        self.assertEqual(result["code"], "0")

    def test_get_order_uses_order_endpoint(self) -> None:
        calls: list[dict] = []

        def fake_transport(method: str, url: str, headers: dict[str, str], body: str | None) -> dict:
            calls.append({"method": method, "url": url, "headers": headers, "body": body})
            return {"code": "0", "data": [{"ordId": "12345", "state": "live"}]}

        adapter = OkxLiveExecution(
            api_key="demo-key",
            api_secret="demo-secret",
            passphrase="demo-passphrase",
            transport=fake_transport,
        )

        result = adapter.get_order("BTC_USDT", "12345")

        self.assertEqual(calls[0]["method"], "GET")
        self.assertIn("/api/v5/trade/order?instId=BTC-USDT&ordId=12345", calls[0]["url"])
        self.assertIsNone(calls[0]["body"])
        self.assertEqual(result["data"][0]["state"], "live")


if __name__ == "__main__":
    unittest.main()
