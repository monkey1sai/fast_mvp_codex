# 2026-03-13 Crypto Arb OpenClaw MVP

## Objective

根據 `deep-research-report (5).md` 建立新的 child repo，落地成第一版可執行的加密套利 MVP 骨架。

## Scope

- 建立 deterministic 的套利機會掃描、風控、模擬。
- 串接既有 `coingecko-openclaw-mcp` 與 `pulse-ingestor-mvp` 的資料 contract。
- 產出可供 OpenClaw agent 讀取的摘要格式。
- 明確保留 execution MCP 為下一階段。

## Non-Goals

- 真實交易所下單
- 金鑰管理與提幣流程
- 高頻 orderbook 回放

## Validation

```bash
python -m unittest
python -m app.cli
```
