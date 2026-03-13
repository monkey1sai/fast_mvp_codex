from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime
import urllib.error
import urllib.request
from typing import Callable


def build_okx_signature(
    timestamp: str,
    method: str,
    request_path: str,
    body: str,
    secret: str,
) -> str:
    payload = f"{timestamp}{method.upper()}{request_path}{body}"
    digest = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")


def _iso8601_millis_now() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


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
        raise RuntimeError(f"OKX API error {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"OKX connection error: {exc.reason}") from exc


class OkxAuthClient:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        passphrase: str,
        api_base_url: str = "https://www.okx.com",
        demo_trading: bool = True,
        transport: Callable[[str, str, dict[str, str], str | None], dict] | None = None,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.api_base_url = api_base_url.rstrip("/")
        self.demo_trading = demo_trading
        self.transport = transport or _default_transport

    def _headers(self, method: str, request_path: str, body: str = "") -> dict[str, str]:
        timestamp = _iso8601_millis_now()
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "SAGA-Brain/2.0",
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": build_okx_signature(timestamp, method, request_path, body, self.api_secret),
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": self.passphrase,
        }
        if self.demo_trading:
            headers["x-simulated-trading"] = "1"
        return headers

    def test_auth(self) -> dict:
        request_path = "/api/v5/account/config"
        url = f"{self.api_base_url}{request_path}"
        try:
            payload = self.transport("GET", url, self._headers("GET", request_path), None)
        except RuntimeError as exc:
            return {"ok": False, "code": "transport_error", "message": str(exc)}
        return {
            "ok": payload.get("code") == "0",
            "code": payload.get("code", ""),
            "message": payload.get("msg", ""),
            "data": payload.get("data", []),
            "mode": "demo" if self.demo_trading else "live",
        }
