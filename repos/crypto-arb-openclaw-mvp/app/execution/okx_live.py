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
        base_ccy, quote_ccy = symbol.split("_", 1)

        balance_path = f"/api/v5/account/balance?{urllib.parse.urlencode({'ccy': f'{base_ccy},{quote_ccy}'})}"
        balance_url = f"{self.auth.api_base_url}{balance_path}"
        balance_payload = self.auth.transport("GET", balance_url, self.auth._headers("GET", balance_path), None)

        detail_rows: list[dict] = []
        for account_row in balance_payload.get("data", []):
            detail_rows.extend(account_row.get("details", []))

        base_qty = 0.0
        quote_value_usd = 0.0
        available_quote_usd = 0.0
        for row in detail_rows:
            ccy = str(row.get("ccy", "")).upper()
            if ccy == base_ccy.upper():
                base_qty = float(row.get("eq", row.get("cashBal", 0.0)) or 0.0)
                quote_value_usd = float(row.get("eqUsd", 0.0) or 0.0)
            if ccy == quote_ccy.upper():
                available_quote_usd = float(row.get("availBal", 0.0) or 0.0)

        pending_path = f"/api/v5/trade/orders-pending?{urllib.parse.urlencode({'instId': to_okx_inst_id(symbol)})}"
        pending_url = f"{self.auth.api_base_url}{pending_path}"
        pending_payload = self.auth.transport("GET", pending_url, self.auth._headers("GET", pending_path), None)
        open_orders = len(pending_payload.get("data", []))

        return PositionState(
            symbol=symbol,
            base_qty=base_qty,
            quote_value_usd=quote_value_usd,
            open_orders=open_orders,
            available_quote_usd=available_quote_usd,
        )
