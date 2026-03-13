import unittest

from app.market_data.pionex_public import PionexPublicMarketData


class PionexMarketDataTests(unittest.TestCase):
    def test_get_book_ticker_uses_public_endpoint(self) -> None:
        calls = []

        def fake_transport(method: str, url: str, headers: dict[str, str]) -> dict:
            calls.append({"method": method, "url": url, "headers": headers})
            return {
                "result": True,
                "data": {
                    "tickers": [
                        {
                            "symbol": "BTC_USDT",
                            "bidPrice": "70000.1",
                            "askPrice": "70001.5",
                            "timestamp": 1773380000000,
                        }
                    ]
                },
            }

        client = PionexPublicMarketData(transport=fake_transport)
        book = client.get_book_ticker("BTC_USDT")

        self.assertEqual(book.symbol, "BTC_USDT")
        self.assertEqual(book.bid, 70000.1)
        self.assertEqual(book.ask, 70001.5)
        self.assertEqual(calls[0]["method"], "GET")
        self.assertIn("/api/v1/market/bookTickers?symbol=BTC_USDT&type=SPOT", calls[0]["url"])
        self.assertEqual(calls[0]["headers"]["User-Agent"], "SAGA-Brain/2.0")

    def test_get_book_ticker_falls_back_to_tickers(self) -> None:
        calls = []

        def fake_transport(method: str, url: str, headers: dict[str, str]) -> dict:
            calls.append({"method": method, "url": url, "headers": headers})
            if "bookTickers" in url:
                return {"result": True, "data": {"tickers": []}}
            return {
                "result": True,
                "data": {
                    "tickers": [
                        {
                            "symbol": "BTC_USDT",
                            "bid": "70010.1",
                            "ask": "70011.5",
                            "timestamp": 1773380000001,
                        }
                    ]
                },
            }

        client = PionexPublicMarketData(transport=fake_transport)
        book = client.get_book_ticker("BTC_USDT")

        self.assertEqual(book.bid, 70010.1)
        self.assertEqual(book.ask, 70011.5)
        self.assertEqual(len(calls), 2)
        self.assertIn("/api/v1/market/tickers?symbol=BTC_USDT", calls[1]["url"])


if __name__ == "__main__":
    unittest.main()
