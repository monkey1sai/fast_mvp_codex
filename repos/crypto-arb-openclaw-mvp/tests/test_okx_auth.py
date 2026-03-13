import unittest

from app.execution.okx_auth import OkxAuthClient, build_okx_signature


class OkxAuthTests(unittest.TestCase):
    def test_build_okx_signature_matches_expected(self) -> None:
        signature = build_okx_signature(
            timestamp="2026-03-13T10:00:00.000Z",
            method="GET",
            request_path="/api/v5/account/config",
            body="",
            secret="demo-secret",
        )
        self.assertEqual(signature, "cAoCW93HwEt9+4/Fv2X+NUypmRuB2XWkJYJGcDfVB0E=")

    def test_test_auth_uses_account_config_with_demo_header(self) -> None:
        calls: list[dict] = []

        def fake_transport(method: str, url: str, headers: dict[str, str], body: str | None) -> dict:
            calls.append({"method": method, "url": url, "headers": headers, "body": body})
            return {"code": "0", "data": [{"uid": "12345"}]}

        client = OkxAuthClient(
            api_key="demo-key",
            api_secret="demo-secret",
            passphrase="demo-passphrase",
            transport=fake_transport,
        )

        result = client.test_auth()

        self.assertTrue(result["ok"])
        self.assertEqual(calls[0]["method"], "GET")
        self.assertTrue(calls[0]["url"].endswith("/api/v5/account/config"))
        self.assertEqual(calls[0]["headers"]["OK-ACCESS-KEY"], "demo-key")
        self.assertEqual(calls[0]["headers"]["OK-ACCESS-PASSPHRASE"], "demo-passphrase")
        self.assertEqual(calls[0]["headers"]["x-simulated-trading"], "1")
        self.assertEqual(calls[0]["body"], None)

    def test_test_auth_returns_error_payload(self) -> None:
        def fake_transport(method: str, url: str, headers: dict[str, str], body: str | None) -> dict:
            return {"code": "50113", "msg": "Invalid signature", "data": []}

        client = OkxAuthClient(
            api_key="demo-key",
            api_secret="demo-secret",
            passphrase="demo-passphrase",
            transport=fake_transport,
        )

        result = client.test_auth()

        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "50113")


if __name__ == "__main__":
    unittest.main()
