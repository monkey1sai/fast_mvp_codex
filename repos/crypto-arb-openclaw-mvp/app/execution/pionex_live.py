from __future__ import annotations

import hashlib
import hmac
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Callable

from app.execution.base import ExecutionAdapter
from app.models import OrderBookTop, PositionState, QuoteIntent


def build_rest_signature(
    method: str,
    path: str,
    params: dict[str, str],
    body: str,
    secret: str,
) -> str:
    query = urllib.parse.urlencode(sorted(params.items()))
    path_url = f"{path}?{query}" if query else path
    payload = f"{method.upper()}{path_url}{body}"
    return hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()


def _default_transport(method: str, url: str, headers: dict[str, str], body: str | None) -> dict:
    data = body.encode("utf-8") if body is not None else None
    request = urllib.request.Request(url=url, data=data, headers=headers, method=method.upper())
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8") if exc.fp else ""
        try:
            detail = json.loads(raw) if raw else {"raw": ""}
        except json.JSONDecodeError:
            detail = {"raw": raw}
        raise RuntimeError(f"Pionex API error {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Pionex connection error: {exc.reason}") from exc


class PionexLiveExecution(ExecutionAdapter):
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        api_base_url: str = "https://api.pionex.com",
        transport: Callable[[str, str, dict[str, str], str | None], dict] | None = None,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_base_url = api_base_url.rstrip("/")
        self.transport = transport or _default_transport
        self._symbol_constraints_cache: dict[str, dict] = {}

    def _signed_headers(self, signature: str) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "User-Agent": "SAGA-Brain/2.0",
            "PIONEX-KEY": self.api_key,
            "PIONEX-SIGNATURE": signature,
        }

    def _request(self, method: str, path: str, params: dict[str, str] | None = None, body_dict: dict | None = None) -> dict:
        params = dict(params or {})
        body = json.dumps(body_dict, separators=(",", ":")) if body_dict is not None else None
        signature = build_rest_signature(method, path, params, body or "", self.api_secret)
        url = f"{self.api_base_url}{path}"
        if params:
            url += f"?{urllib.parse.urlencode(params)}"
        return self.transport(method.upper(), url, self._signed_headers(signature), body)

    def _public_request(self, path: str, params: dict[str, str] | None = None) -> dict:
        url = f"{self.api_base_url}{path}"
        query = urllib.parse.urlencode(params or {})
        if query:
            url += f"?{query}"
        return self.transport("GET", url, {"Content-Type": "application/json", "User-Agent": "SAGA-Brain/2.0"}, None)

    def get_symbol_constraints(self, symbol: str) -> dict:
        symbol = symbol.upper()
        if symbol not in self._symbol_constraints_cache:
            payload = self._public_request("/api/v1/common/symbols")
            if not payload.get("result"):
                raise RuntimeError(f"Pionex get_symbol_constraints failed: {payload}")
            for item in payload.get("data", {}).get("symbols", []):
                item_symbol = str(item.get("symbol", "")).upper()
                if not item_symbol:
                    continue
                self._symbol_constraints_cache[item_symbol] = {
                    "basePrecision": int(item.get("basePrecision", 8) or 8),
                    "quotePrecision": int(item.get("quotePrecision", 2) or 2),
                    "minAmount": float(item.get("minAmount", 0) or 0),
                    "minTradeSize": float(item.get("minTradeSize", 0) or 0),
                    "maxTradeSize": float(item.get("maxTradeSize", 0) or 0),
                    "enable": bool(item.get("enable", True)),
                }
        return dict(self._symbol_constraints_cache.get(symbol, {}))

    def place_order(self, quote: QuoteIntent, book: OrderBookTop) -> dict:
        constraints = self.get_symbol_constraints(quote.symbol)
        if constraints and not constraints.get("enable", True):
            raise RuntimeError(f"Pionex symbol disabled: {quote.symbol}")
        size = quote.size_usd / max(book.mid_price, 1e-9)
        base_precision = int(constraints.get("basePrecision", 8) or 8)
        quote_precision = int(constraints.get("quotePrecision", 8) or 8)
        body_dict = {
            "symbol": quote.symbol,
            "side": "BUY" if quote.side.lower() == "buy" else "SELL",
            "type": "LIMIT",
            "size": f"{size:.{base_precision}f}",
            "price": f"{quote.price:.{quote_precision}f}",
        }
        return self._request(
            "POST",
            "/api/v1/trade/order",
            params={"timestamp": str(int(time.time() * 1000))},
            body_dict=body_dict,
        )

    def cancel_order(self, symbol: str, order_id: str) -> dict:
        return self._request(
            "DELETE",
            "/api/v1/trade/order",
            params={"timestamp": str(int(time.time() * 1000))},
            body_dict={"symbol": symbol.upper(), "orderId": int(order_id)},
        )

    def get_position(self, symbol: str) -> PositionState:
        return PositionState(symbol=symbol, base_qty=0.0, quote_value_usd=0.0, open_orders=0)

    def test_auth(self) -> bool:
        try:
            result = self._request(
                "GET",
                "/api/v1/account/balances",
                params={"timestamp": str(int(time.time() * 1000))},
            )
        except RuntimeError:
            return False
        return bool(result.get("result"))
