from __future__ import annotations

import json
import os
from pathlib import Path

from app.execution.okx_auth import OkxAuthClient


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if not os.getenv(key):
            os.environ[key] = value


def main() -> None:
    workspace_env = Path(__file__).resolve().parents[3] / ".env"
    load_env_file(workspace_env)

    api_key = os.getenv("OKX_API_KEY", "")
    api_secret = os.getenv("OKX_API_SECRET", "")
    passphrase = os.getenv("OKX_API_PASSPHRASE", "")
    api_base_url = os.getenv("OKX_API_BASE_URL", "https://www.okx.com")
    demo_trading = os.getenv("OKX_DEMO_TRADING", "true").lower() in {"1", "true", "yes", "on"}

    if not api_key or not api_secret or not passphrase:
        raise SystemExit("OKX_API_KEY, OKX_API_SECRET, OKX_API_PASSPHRASE are required")

    client = OkxAuthClient(
        api_key=api_key,
        api_secret=api_secret,
        passphrase=passphrase,
        api_base_url=api_base_url,
        demo_trading=demo_trading,
    )
    print(json.dumps(client.test_auth(), ensure_ascii=False))


if __name__ == "__main__":
    main()
