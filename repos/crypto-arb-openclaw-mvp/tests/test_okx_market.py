import unittest

from app.market_data.okx_public import OkxPublicMarketData


class OkxMarketDataTests(unittest.TestCase):
    def test_get_ticker_uses_okx_public_endpoint(self) -> None:
        calls = []

        def fake_transport(method: str, url: str, headers: dict[str, str]) -> dict:
            calls.append({"method": method, "url": url, "headers": headers})
            return {
                "code": "0",
                "msg": "",
                "data": [
                    {
                        "instId": "BTC-USDT",
                        "bidPx": "71800.1",
                        "askPx": "71800.2",
                        "ts": "1773393000000",
                    }
                ],
            }

        client = OkxPublicMarketData(transport=fake_transport)
        book = client.get_book_ticker("BTC_USDT")

        self.assertEqual(book.symbol, "BTC_USDT")
        self.assertEqual(book.bid, 71800.1)
        self.assertEqual(book.ask, 71800.2)
        self.assertEqual(calls[0]["method"], "GET")
        self.assertIn("/api/v5/market/ticker?instId=BTC-USDT", calls[0]["url"])
        self.assertEqual(calls[0]["headers"]["User-Agent"], "SAGA-Brain/2.0")


if __name__ == "__main__":
    unittest.main()
