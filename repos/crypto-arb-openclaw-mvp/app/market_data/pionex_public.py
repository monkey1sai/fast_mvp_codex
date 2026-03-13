from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Callable

from app.models import OrderBookTop


def _default_transport(method: str, url: str, headers: dict[str, str]) -> dict:
    request = urllib.request.Request(url=url, headers=headers, method=method.upper())
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


class PionexPublicMarketData:
    def __init__(
        self,
        api_base_url: str = "https://api.pionex.com",
        transport: Callable[[str, str, dict[str, str]], dict] | None = None,
    ) -> None:
        self.api_base_url = api_base_url.rstrip("/")
        self.transport = transport or _default_transport

    def _request(self, path: str, params: dict[str, str]) -> dict:
        query = urllib.parse.urlencode(params)
        url = f"{self.api_base_url}{path}"
        if query:
            url += f"?{query}"
        return self.transport("GET", url, {"User-Agent": "SAGA-Brain/2.0"})

    def get_book_ticker(self, symbol: str) -> OrderBookTop:
        payload = self._request("/api/v1/market/bookTickers", {"symbol": symbol, "type": "SPOT"})
        tickers = payload.get("data", {}).get("tickers", [])
        if not tickers:
            payload = self._request("/api/v1/market/tickers", {"symbol": symbol})
            tickers = payload.get("data", {}).get("tickers", [])
        if not tickers:
            raise RuntimeError(f"no market data returned for {symbol}")
        ticker = tickers[0]
        return OrderBookTop(
            symbol=str(ticker.get("symbol", symbol)),
            bid=float(ticker.get("bidPrice", ticker.get("bid", 0.0))),
            ask=float(ticker.get("askPrice", ticker.get("ask", 0.0))),
            timestamp=str(ticker.get("timestamp", "")),
        )
