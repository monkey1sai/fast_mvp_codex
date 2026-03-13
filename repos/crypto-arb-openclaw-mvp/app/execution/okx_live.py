from __future__ import annotations

import json
import urllib.parse
from typing import Callable

from app.execution.base import ExecutionAdapter
from app.execution.okx_auth import OkxAuthClient
from app.market_data.okx_public import to_okx_inst_id
from app.models import OrderBookTop, PositionState, QuoteIntent


class OkxLiveExecution(ExecutionAdapter):
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        passphrase: str,
        api_base_url: str = "https://www.okx.com",
        demo_trading: bool = True,
        transport: Callable[[str, str, dict[str, str], str | None], dict] | None = None,
    ) -> None:
        self.auth = OkxAuthClient(
            api_key=api_key,
            api_secret=api_secret,
            passphrase=passphrase,
            api_base_url=api_base_url,
            demo_trading=demo_trading,
            transport=transport,
        )

    def get_symbol_constraints(self, symbol: str) -> dict:
        return {}

    def place_order(self, quote: QuoteIntent, book: OrderBookTop) -> dict:
        inst_id = to_okx_inst_id(quote.symbol)
        size = quote.size_usd / max(book.mid_price, 1e-9)
        body = {
            "instId": inst_id,
            "tdMode": "cash",
            "side": "buy" if quote.side.lower() == "buy" else "sell",
            "ordType": "post_only",
            "sz": f"{size:.8f}",
            "px": f"{quote.price:.8f}",
        }
        request_path = "/api/v5/trade/order"
        url = f"{self.auth.api_base_url}{request_path}"
        return self.auth.transport("POST", url, self.auth._headers("POST", request_path, json.dumps(body, separators=(',', ':'))), json.dumps(body, separators=(",", ":")))

    def cancel_order(self, symbol: str, order_id: str) -> dict:
        body = {"instId": to_okx_inst_id(symbol), "ordId": str(order_id)}
        request_path = "/api/v5/trade/cancel-order"
        url = f"{self.auth.api_base_url}{request_path}"
        return self.auth.transport("POST", url, self.auth._headers("POST", request_path, json.dumps(body, separators=(',', ':'))), json.dumps(body, separators=(",", ":")))

    def get_order(self, symbol: str, order_id: str) -> dict:
        path = "/api/v5/trade/order"
        query = urllib.parse.urlencode({"instId": to_okx_inst_id(symbol), "ordId": str(order_id)})
        request_path = f"{path}?{query}"
        url = f"{self.auth.api_base_url}{request_path}"
        return self.auth.transport("GET", url, self.auth._headers("GET", request_path), None)

    def get_position(self, symbol: str) -> PositionState:
        return PositionState(symbol=symbol, base_qty=0.0, quote_value_usd=0.0, open_orders=0)
