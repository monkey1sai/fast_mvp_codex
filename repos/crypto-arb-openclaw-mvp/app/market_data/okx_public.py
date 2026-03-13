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


def to_okx_inst_id(symbol: str) -> str:
    return symbol.replace("_", "-").upper()


class OkxPublicMarketData:
    def __init__(
        self,
        api_base_url: str = "https://www.okx.com",
        transport: Callable[[str, str, dict[str, str]], dict] | None = None,
    ) -> None:
        self.api_base_url = api_base_url.rstrip("/")
        self.transport = transport or _default_transport

    def get_book_ticker(self, symbol: str) -> OrderBookTop:
        inst_id = to_okx_inst_id(symbol)
        path = "/api/v5/market/ticker"
        query = urllib.parse.urlencode({"instId": inst_id})
        url = f"{self.api_base_url}{path}?{query}"
        payload = self.transport("GET", url, {"User-Agent": "SAGA-Brain/2.0"})
        rows = payload.get("data", [])
        if not rows:
            raise RuntimeError(f"no market data returned for {symbol}")
        row = rows[0]
        return OrderBookTop(
            symbol=symbol,
            bid=float(row["bidPx"]),
            ask=float(row["askPx"]),
            timestamp=str(row.get("ts", "")),
        )
