import unittest

from app.market_data.coingecko_public import CoinGeckoReferenceMarketData


class CoinGeckoMarketDataTests(unittest.TestCase):
    def test_get_reference_book_from_simple_price(self) -> None:
        calls = []

        def fake_transport(method: str, url: str, headers: dict[str, str]) -> dict:
            calls.append({"method": method, "url": url, "headers": headers})
            return {
                "bitcoin": {
                    "usd": 71234.5,
                    "last_updated_at": 1773389900,
                }
            }

        client = CoinGeckoReferenceMarketData(api_key="demo-key", transport=fake_transport)
        book = client.get_reference_book(symbol="BTC_USDT", coin_id="bitcoin")

        self.assertEqual(book.symbol, "BTC_USDT")
        self.assertGreater(book.ask, book.bid)
        self.assertEqual(calls[0]["method"], "GET")
        self.assertIn("/simple/price?ids=bitcoin&vs_currencies=usd&include_last_updated_at=true", calls[0]["url"])


if __name__ == "__main__":
    unittest.main()
