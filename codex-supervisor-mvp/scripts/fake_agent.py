from __future__ import annotations

import sys
import time


def ask(prompt: str) -> str:
    print(prompt, flush=True)
    answer = sys.stdin.readline().strip()
    print(f"收到回覆: {answer}", flush=True)
    return answer


def main() -> int:
    print("Fake agent started", flush=True)
    time.sleep(0.1)
    ask("是否要執行測試？")
    time.sleep(0.1)
    ask("要不要連網查資料？")
    print("Fake agent finished", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
