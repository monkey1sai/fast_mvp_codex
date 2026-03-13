from __future__ import annotations

import asyncio
import json
import urllib.parse
import urllib.request
from typing import Callable

from app.models import OrderBookTop


def _default_transport(method: str, url: str, headers: dict[str, str]) -> dict:
    request = urllib.request.Request(url=url, headers=headers, method=method.upper())
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


class CoinGeckoReferenceMarketData:
    def __init__(
        self,
        api_key: str,
        api_base_url: str = "https://pro-api.coingecko.com/api/v3",
        transport: Callable[[str, str, dict[str, str]], dict] | None = None,
    ) -> None:
        self.api_key = api_key
        self.api_base_url = api_base_url.rstrip("/")
        self.transport = transport or _default_transport

    def get_reference_book(self, symbol: str, coin_id: str, vs_currency: str = "usd") -> OrderBookTop:
        path = "/simple/price"
        query = urllib.parse.urlencode(
            {
                "ids": coin_id,
                "vs_currencies": vs_currency,
                "include_last_updated_at": "true",
            }
        )
        url = f"{self.api_base_url}{path}?{query}"
        headers = {"x-cg-pro-api-key": self.api_key}
        payload = self.transport("GET", url, headers)
        asset = payload.get(coin_id)
        if not asset:
            raise RuntimeError(f"no CoinGecko price returned for {coin_id}")
        price = float(asset[vs_currency])
        spread_proxy = max(price * 0.001, 0.01)
        return OrderBookTop(
            symbol=symbol,
            bid=round(price - (spread_proxy / 2), 8),
            ask=round(price + (spread_proxy / 2), 8),
            timestamp=str(asset.get("last_updated_at", "")),
        )

    async def get_reference_book_via_websocket(
        self,
        symbol: str,
        coin_id: str,
        ws_url: str = "wss://stream.coingecko.com/v1",
        channel: str = "CGSimplePrice",
    ) -> OrderBookTop:
        import websockets

        connection_url = f"{ws_url}?{urllib.parse.urlencode({'x_cg_pro_api_key': self.api_key})}"
        subscribe_message = {
            "command": "subscribe",
            "identifier": json.dumps({"channel": channel}),
        }
        set_tokens_message = {
            "command": "message",
            "identifier": json.dumps({"channel": channel}),
            "data": json.dumps({"coin_id": [coin_id], "action": "set_tokens"}),
        }

        async with websockets.connect(connection_url, ping_interval=20, ping_timeout=20) as websocket:
            await websocket.send(json.dumps(subscribe_message))
            await asyncio.sleep(1)
            await websocket.send(json.dumps(set_tokens_message))
            while True:
                raw = await asyncio.wait_for(websocket.recv(), timeout=15)
                payload = json.loads(raw)
                data = payload.get("message", payload)
                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                if not isinstance(data, dict):
                    continue
                if data.get("type"):
                    continue
                incoming_coin = str(data.get("coin_id", data.get("id", data.get("i", ""))))
                price = float(data.get("price", data.get("usd_price", data.get("p", 0.0))))
                if incoming_coin != coin_id or price <= 0:
                    continue
                spread_proxy = max(price * 0.001, 0.01)
                return OrderBookTop(
                    symbol=symbol,
                    bid=round(price - (spread_proxy / 2), 8),
                    ask=round(price + (spread_proxy / 2), 8),
                    timestamp=str(data.get("t", "")),
                )
