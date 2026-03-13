# Crypto Arb OpenClaw MVP

以 OpenClaw 為控制平面、以 MCP 為資料/工具層的加密套利 MVP。第一版實作 deterministic 的機會掃描、風控、模擬與決策摘要，不直接做實盤下單。

## Goals

- 用固定規則而非 LLM 直接做套利決策核心。
- 結合既有 `coingecko-openclaw-mcp` 與 `pulse-ingestor-mvp` 的資料能力。
- 對 OpenClaw agent 暴露可控、可重現的策略摘要。
- 先支援回測/模擬，再決定是否需要接入真實 execution MCP。

## Architecture

- `app/strategy.py`: 將市場快照轉成候選套利機會。
- `app/strategy.py`: 用 `淨優勢 bps + 冷卻時間` 做回測門檻決策與候選機會掃描。
- `app/risk.py`: 對費用、滑點、pulse 風險、部位限制做 gating。
- `app/simulator.py`: 用事件序列模擬資金曲線與績效。
- `app/integrations/`: 現有 MCP / OpenClaw 的介面層。
- `app/cli.py`: 本地驗證與 demo 入口。

## Agent Design

- [Sovereign Microstructure Agent](./docs/sovereign-microstructure-agent.md): 高頻交易 agent 的五層架構、世界觀與輸入輸出 schema。
- [Persona Prompt](./prompts/sovereign-microstructure-agent.md): 可直接接到 OpenClaw 的 agent prompt。

## Quick Start

```bash
cd repos/crypto-arb-openclaw-mvp
python -m unittest discover -s tests
python -m app.cli
```

## Live Validation

目前已具備 `Pionex` 與 `OKX` 的 guarded live adapter 與單輪 validation runner。這一層會先走：

- `LIVE_TRADING_ENABLED`
- symbol allowlist
- 單筆 notional cap
- daily loss cap
- explicit confirmation

最小入口：

```bash
python -m app.live_validation_cli --exchange okx --symbol BTC_USDT --price-source coingecko --coingecko-coin-id bitcoin --confirm-live
```

注意：
- 這會走真實交易所 private API
- `Pionex` 需要 `PIONEX_API_KEY` / `PIONEX_API_SECRET`
- `OKX` 需要 `OKX_API_KEY` / `OKX_API_SECRET` / `OKX_API_PASSPHRASE`
- 沒開 `LIVE_TRADING_ENABLED=true` 時，live guard 會拒絕送單
- 這一層已可自動抓 `Pionex` / `OKX` 公開 `ticker`，也可改用 `CoinGecko` 當 reference price
- 預設 `AUTO_CANCEL_AFTER_MS=3000`，也就是 3 秒未成交就撤單
- `BTC_USDT` 目前最小下單金額是 `10 USDT`；若低於交易所門檻，系統會在送單前直接拒絕
- `OKX` live 路徑已驗證可成功下單並查單；若 3 秒內未成交，系統會走查單後撤單

## Continuous Runner

目前已補一個本地可長跑的 `OKX` 連續循環 runner。它會持續：

- 抓取 `OKX` 公開 ticker 或 `CoinGecko` reference price
- 經過現有 live guard
- 走單輪 `place -> wait -> get_order -> cancel`
- 把每輪摘要寫到 `C:\fast_mvp_codex\log\hft-runner.jsonl`
- 把逐步事件寫到 `C:\fast_mvp_codex\log\hft-events.jsonl`

最小入口：

```bash
python -m app.runner_cli --cycles 10 --symbol BTC_USDT --price-source okx --confirm-live
```

改用 `CoinGecko` 當 reference price：

```bash
python -m app.runner_cli --cycles 10 --symbol BTC_USDT --price-source coingecko --coingecko-coin-id bitcoin --confirm-live
```

runner 產出欄位包含：

- `cycle`
- `latency_ms`
- `kill_switch`
- `book`
- `result`

輸出檔預設位置：

- `C:\fast_mvp_codex\log\hft-runner.jsonl`
- `C:\fast_mvp_codex\log\hft-events.jsonl`

事件日誌會包含：

- `market_query`
- `kill_switch`
- `position_snapshot`
- `symbol_constraints`
- `quote_candidates`
- `guard_decision`
- `place_order_request`
- `place_order_result`
- `get_order_result`
- `cancel_order_result`

## Replay / Observability

目前已補最小 replay summary，可直接從 `runtime/hft-runner.jsonl` 讀出執行摘要：

```bash
python -m app.replay_cli --telemetry-path runtime/hft-runner.jsonl
```

輸出欄位包含：

- `cycles`
- `placed_orders`
- `cancelled_orders`
- `halt_cycles`
- `guard_reject_cycles`
- `avg_latency_ms`
- `max_latency_ms`
- `price_sources`
- `symbols`

## OKX Auth Smoke Test

如果你要先切到 `OKX`，先只驗證 API key / secret / passphrase 是否可用，不碰下單。

先在 root `.env` 或你自己的 shell 補上：

```env
OKX_API_KEY=
OKX_API_SECRET=
OKX_API_PASSPHRASE=
OKX_API_BASE_URL=https://www.okx.com
OKX_DEMO_TRADING=true
```

然後執行：

```bash
python -m app.okx_auth_smoke
```

成功時會回傳類似：

```json
{"ok":true,"code":"0","mode":"demo"}
```

若要直接跑 `OKX live validation`：

```bash
python -m app.live_validation_cli --exchange okx --symbol BTC_USDT --price-source coingecko --coingecko-coin-id bitcoin --confirm-live
```

## Backtest Gate

目前不再使用「單筆固定 3%」這種不實際門檻，而是改成：

- `BACKTEST_PROFIT_TARGET_BPS`: 過去視窗內要求的最低淨優勢
- `BACKTEST_WINDOW_SECONDS`: 回看視窗，預設 `300` 秒
- `COOLDOWN_SECONDS`: 若未達門檻，等待多久再重新評估，預設 `150` 秒

這代表策略循環現在是：

- 回看最近 `5` 分鐘
- 扣掉 fee/slippage 後估算 `net edge`
- 若高於目標 `bps`，才允許進一步交易
- 若低於門檻，就進入 `2.5` 分鐘冷卻

## Live Market Monitor

目前已補好 CoinGecko WebSocket 監控骨架，但仍是 `monitor-only`，不下單。用途是先抓真實即時價格、寫成本地 JSONL，再供後續 quote engine 驗證。

相關檔案：
- `app/live_market.py`
- `tests/test_live_market.py`

後續若要真連線，需要安裝 WebSocket client 套件並使用 `COINGECKO_PRO_API_KEY`。

### Docker Runtime Mapping

這個 repo 現在有自己的 Docker Compose。`runtime/*.jsonl` 會直接 bind mount 到 workspace 的同一個目錄：

- host: `repos/crypto-arb-openclaw-mvp/runtime`
- container: `/app/runtime`

也就是說，你在容器裡跑出的：

- `/app/runtime/coingecko-live.jsonl`

會直接出現在：

- `repos/crypto-arb-openclaw-mvp/runtime/coingecko-live.jsonl`

啟動方式：

```bash
cd repos/crypto-arb-openclaw-mvp
docker compose --env-file ../../.env --env-file ../../.env.runtime up --build
```

只跑一次 monitor：

```bash
cd repos/crypto-arb-openclaw-mvp
docker compose --env-file ../../.env --env-file ../../.env.runtime run --rm live-monitor
```

直接看輸出檔：

```bash
type runtime\\coingecko-live.jsonl
```

## Environment

複製 `.env.example` 到你自己的 `.env` 或 shell 環境後再接 live services：

```env
COINGECKO_PRO_API_KEY=
OPENCLAW_AGENT_ID=saga-trader-codex
OPENCLAW_GATEWAY_CMD=openclaw agent --agent saga-trader-codex --json
PULSE_CONTEXT_ENDPOINT=http://127.0.0.1:8000/decision/context?limit=5
MAX_POSITION_USD=50
MAX_DAILY_DRAWDOWN_PCT=0.1
```

## Current Status

- 已提供 deterministic arbitrage simulation MVP。
- 已提供 `淨優勢 bps + 冷卻時間` 的回測門檻決策。
- 已提供 CoinGecko MCP / Pulse MCP / OpenClaw 的 adapter contract。
- 已提供 `Pionex` live trading 基礎層：簽名、live adapter、live guard。
- execution 仍預設為 dry-run；未開啟 `LIVE_TRADING_ENABLED` 前不得真實下單。
- 已定義具世界觀與風控分層的 `Sovereign Microstructure Agent`。

## Verification

```bash
python -m unittest discover -s tests
python -m app.cli
python -m app.runner_cli --help
python -m app.replay_cli --telemetry-path runtime/hft-runner.jsonl
```
