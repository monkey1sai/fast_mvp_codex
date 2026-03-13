# HFT Agent Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在現有本地 OpenClaw、CoinGecko Pro、Pulse news、單一 CEX 憑證條件下，建立一個適用 30 美元本金的零 DNS、零 Telegram 依賴高頻交易 agent。

**Architecture:** 這不是傳統機房級 HFT，而是零售基礎設施下的「低延遲微結構 agent」。交易核心維持 deterministic，資料面由 CoinGecko MCP、Pulse news、CEX execution adapter 餵入；OpenClaw 只做控制平面、審核、觀測與人工介入。第一階段只允許單交易所、單交易對、maker-first、單日小額風險。

**Tech Stack:** Python 3.10+、本地 OpenClaw gateway、CoinGecko Pro MCP、Pulse news feed、單一 CEX REST/WebSocket adapter、unittest

---

## Runtime Assumptions

- 已有可用的本地 OpenClaw runtime 與 gateway token。
- 已有 CoinGecko Pro API key 可做 reference price / market regime。
- 已有 Pulse news ingestion，可供風險 gating。
- 已有單一 CEX API 憑證可作 execution，但第一階段只開交易權限，不允許提幣。
- 使用者明確要求：不建立 DNS，不建立 Telegram bot。

## Strategy Choice

30 美元本金不適合跨交易所搬磚或高頻三角套利，原因是資金會被分散、手續費佔比過高、最小下單量限制明顯。第一版應該做：

1. `single-venue maker-first microspread strategy`
2. `reference-price deviation gating`
3. `pulse/news risk kill-switch`

也就是：
- 在單一交易所的單一主流交易對上做微結構掛單。
- 用 CoinGecko 作 reference anchor，判斷本地報價是否偏離。
- 用 Pulse news 對交易所事故、極端恐懼、突發風險做停機。

## Deployment Shape

- `crypto-arb-openclaw-mvp` repo 繼續作為主 repo。
- 本地單機部署。
- `openclaw-gateway` 為唯一控制平面入口。
- 不暴露 public webhook，不建立 DNS。
- 不做 Telegram 推播，所有觀測留在本地 CLI / dashboard / logs。

### Task 1: Expand domain model for HFT loop

**Files:**
- Modify: `repos/crypto-arb-openclaw-mvp/app/models.py`
- Create: `repos/crypto-arb-openclaw-mvp/tests/test_models_hft.py`

**Step 1: Write the failing test**

新增測試覆蓋以下資料模型：
- `OrderBookTop`
- `QuoteIntent`
- `PositionState`
- `KillSwitchState`

**Step 2: Run test to verify it fails**

Run: `python -m unittest discover -s tests`
Expected: FAIL with missing dataclasses

**Step 3: Write minimal implementation**

在 `app/models.py` 補上：
- bid/ask/mid/spread_bps
- inventory/base_quote exposure
- quote ttl / side / price / size
- kill-switch reason / triggered_at

**Step 4: Run test to verify it passes**

Run: `python -m unittest discover -s tests`
Expected: PASS

**Step 5: Commit**

```bash
git add repos/crypto-arb-openclaw-mvp/app/models.py repos/crypto-arb-openclaw-mvp/tests/test_models_hft.py
git commit -m "feat: add hft domain models"
```

### Task 2: Add runtime config for 30 USD capital constraints

**Files:**
- Modify: `repos/crypto-arb-openclaw-mvp/app/config.py`
- Modify: `repos/crypto-arb-openclaw-mvp/.env.example`
- Create: `repos/crypto-arb-openclaw-mvp/tests/test_config_hft.py`

**Step 1: Write the failing test**

測試以下設定存在且有合理預設：
- `TRADING_PAIR`
- `MAX_NOTIONAL_PER_ORDER_USD`
- `MAX_OPEN_ORDERS`
- `MAX_NET_POSITION_USD`
- `QUOTE_REFRESH_MS`
- `STOP_ON_PULSE_ENTROPY`

**Step 2: Run test to verify it fails**

Run: `python -m unittest discover -s tests`
Expected: FAIL with missing config fields

**Step 3: Write minimal implementation**

為 30 美元本金定義預設：
- 單筆 notional: `5`
- 最大淨部位: `10`
- 同時掛單數: `2`
- quote refresh: `750-1500ms`
- 風險事件閾值: `0.75`

**Step 4: Run test to verify it passes**

Run: `python -m unittest discover -s tests`
Expected: PASS

**Step 5: Commit**

```bash
git add repos/crypto-arb-openclaw-mvp/app/config.py repos/crypto-arb-openclaw-mvp/.env.example repos/crypto-arb-openclaw-mvp/tests/test_config_hft.py
git commit -m "feat: add hft runtime config"
```

### Task 3: Implement CEX adapter contract and dry-run Pionex execution layer

**Files:**
- Create: `repos/crypto-arb-openclaw-mvp/app/execution/__init__.py`
- Create: `repos/crypto-arb-openclaw-mvp/app/execution/base.py`
- Create: `repos/crypto-arb-openclaw-mvp/app/execution/pionex_dryrun.py`
- Create: `repos/crypto-arb-openclaw-mvp/tests/test_pionex_dryrun.py`

**Step 1: Write the failing test**

測試 dry-run adapter 能：
- 接收 quote intent
- 回傳 accepted/rejected
- 更新模擬 inventory

**Step 2: Run test to verify it fails**

Run: `python -m unittest discover -s tests`
Expected: FAIL with missing execution adapter

**Step 3: Write minimal implementation**

在 `base.py` 定義：
- `place_order`
- `cancel_order`
- `get_position`

在 `pionex_dryrun.py` 實作：
- 不打真 API
- 依當前 best bid/ask 模擬成交
- 寫入本地 in-memory order state

**Step 4: Run test to verify it passes**

Run: `python -m unittest discover -s tests`
Expected: PASS

**Step 5: Commit**

```bash
git add repos/crypto-arb-openclaw-mvp/app/execution repos/crypto-arb-openclaw-mvp/tests/test_pionex_dryrun.py
git commit -m "feat: add dry-run execution adapter"
```

### Task 4: Build reference-price deviation engine

**Files:**
- Create: `repos/crypto-arb-openclaw-mvp/app/signals.py`
- Create: `repos/crypto-arb-openclaw-mvp/tests/test_signals.py`
- Modify: `repos/crypto-arb-openclaw-mvp/app/integrations/coingecko_mcp.py`

**Step 1: Write the failing test**

測試：
- CoinGecko reference mid 與本地 mid 差值超過閾值時產生 `quote_widen`
- 差值過小時允許正常 quoting

**Step 2: Run test to verify it fails**

Run: `python -m unittest discover -s tests`
Expected: FAIL with missing signal logic

**Step 3: Write minimal implementation**

加入：
- `reference_deviation_bps`
- `spread_mode`
- `inventory_skew`
- `no_trade_zone`

**Step 4: Run test to verify it passes**

Run: `python -m unittest discover -s tests`
Expected: PASS

**Step 5: Commit**

```bash
git add repos/crypto-arb-openclaw-mvp/app/signals.py repos/crypto-arb-openclaw-mvp/app/integrations/coingecko_mcp.py repos/crypto-arb-openclaw-mvp/tests/test_signals.py
git commit -m "feat: add reference price deviation engine"
```

### Task 5: Build pulse/news kill-switch

**Files:**
- Modify: `repos/crypto-arb-openclaw-mvp/app/risk.py`
- Create: `repos/crypto-arb-openclaw-mvp/tests/test_killswitch.py`
- Modify: `repos/crypto-arb-openclaw-mvp/app/integrations/pulse_mcp.py`

**Step 1: Write the failing test**

測試：
- 高 entropy pulse 觸發 kill-switch
- 包含 exchange incident / withdrawal halt / exploit tags 時停止 quoting

**Step 2: Run test to verify it fails**

Run: `python -m unittest discover -s tests`
Expected: FAIL with missing kill-switch behavior

**Step 3: Write minimal implementation**

補上：
- `should_halt_trading()`
- `should_widen_quotes()`
- `risk mode: normal / caution / halt`

**Step 4: Run test to verify it passes**

Run: `python -m unittest discover -s tests`
Expected: PASS

**Step 5: Commit**

```bash
git add repos/crypto-arb-openclaw-mvp/app/risk.py repos/crypto-arb-openclaw-mvp/app/integrations/pulse_mcp.py repos/crypto-arb-openclaw-mvp/tests/test_killswitch.py
git commit -m "feat: add pulse driven kill switch"
```

### Task 6: Add quote engine and inventory controls

**Files:**
- Create: `repos/crypto-arb-openclaw-mvp/app/quote_engine.py`
- Create: `repos/crypto-arb-openclaw-mvp/tests/test_quote_engine.py`
- Modify: `repos/crypto-arb-openclaw-mvp/app/strategy.py`

**Step 1: Write the failing test**

測試：
- 正常狀態下生成雙邊 quote
- inventory 偏多時只保留 sell bias
- risk caution 時自動擴 spread

**Step 2: Run test to verify it fails**

Run: `python -m unittest discover -s tests`
Expected: FAIL with missing quote engine

**Step 3: Write minimal implementation**

讓 quote engine 輸出：
- buy quote
- sell quote
- ttl
- cancel/replace decision

**Step 4: Run test to verify it passes**

Run: `python -m unittest discover -s tests`
Expected: PASS

**Step 5: Commit**

```bash
git add repos/crypto-arb-openclaw-mvp/app/quote_engine.py repos/crypto-arb-openclaw-mvp/app/strategy.py repos/crypto-arb-openclaw-mvp/tests/test_quote_engine.py
git commit -m "feat: add quote engine"
```

### Task 7: Add event loop runner for local HFT cycle

**Files:**
- Create: `repos/crypto-arb-openclaw-mvp/app/runner.py`
- Create: `repos/crypto-arb-openclaw-mvp/tests/test_runner.py`
- Modify: `repos/crypto-arb-openclaw-mvp/app/cli.py`

**Step 1: Write the failing test**

測試 runner 每次循環能：
- 讀 market snapshot
- 讀 pulse signals
- 產生 quote intents
- 經 risk 過濾
- 送到 dry-run adapter

**Step 2: Run test to verify it fails**

Run: `python -m unittest discover -s tests`
Expected: FAIL with missing loop runner

**Step 3: Write minimal implementation**

實作：
- `run_once()`
- `run_cycles(n)`
- quote refresh cadence
- local metrics aggregation

**Step 4: Run test to verify it passes**

Run: `python -m unittest discover -s tests`
Expected: PASS

**Step 5: Commit**

```bash
git add repos/crypto-arb-openclaw-mvp/app/runner.py repos/crypto-arb-openclaw-mvp/app/cli.py repos/crypto-arb-openclaw-mvp/tests/test_runner.py
git commit -m "feat: add local hft cycle runner"
```

### Task 8: Add OpenClaw control-plane summaries without order authority

**Files:**
- Modify: `repos/crypto-arb-openclaw-mvp/app/integrations/openclaw.py`
- Create: `repos/crypto-arb-openclaw-mvp/tests/test_openclaw_summary.py`

**Step 1: Write the failing test**

測試輸出的 OpenClaw message 會包含：
- current mode
- approved/blocked quotes
- inventory
- kill-switch reason
- next human action

**Step 2: Run test to verify it fails**

Run: `python -m unittest discover -s tests`
Expected: FAIL with missing fields

**Step 3: Write minimal implementation**

擴充 summary schema，但保留規則：
- 不生成 live order 指令
- 只輸出觀測與建議

**Step 4: Run test to verify it passes**

Run: `python -m unittest discover -s tests`
Expected: PASS

**Step 5: Commit**

```bash
git add repos/crypto-arb-openclaw-mvp/app/integrations/openclaw.py repos/crypto-arb-openclaw-mvp/tests/test_openclaw_summary.py
git commit -m "feat: enrich openclaw control plane summary"
```

### Task 9: Add local observability and replay files

**Files:**
- Create: `repos/crypto-arb-openclaw-mvp/runtime/.gitkeep`
- Create: `repos/crypto-arb-openclaw-mvp/app/telemetry.py`
- Create: `repos/crypto-arb-openclaw-mvp/tests/test_telemetry.py`
- Modify: `repos/crypto-arb-openclaw-mvp/.gitignore`

**Step 1: Write the failing test**

測試每輪事件能寫出：
- quotes log
- fills log
- risk events log
- pnl snapshots

**Step 2: Run test to verify it fails**

Run: `python -m unittest discover -s tests`
Expected: FAIL with missing telemetry writer

**Step 3: Write minimal implementation**

採 JSONL 輸出到本地 `runtime/`，不依賴任何雲服務。

**Step 4: Run test to verify it passes**

Run: `python -m unittest discover -s tests`
Expected: PASS

**Step 5: Commit**

```bash
git add repos/crypto-arb-openclaw-mvp/app/telemetry.py repos/crypto-arb-openclaw-mvp/runtime/.gitkeep repos/crypto-arb-openclaw-mvp/.gitignore repos/crypto-arb-openclaw-mvp/tests/test_telemetry.py
git commit -m "feat: add local telemetry and replay logs"
```

### Task 10: Gate live trading behind explicit manual switch

**Files:**
- Create: `repos/crypto-arb-openclaw-mvp/app/live_guard.py`
- Create: `repos/crypto-arb-openclaw-mvp/tests/test_live_guard.py`
- Modify: `repos/crypto-arb-openclaw-mvp/app/runner.py`
- Modify: `repos/crypto-arb-openclaw-mvp/README.md`

**Step 1: Write the failing test**

測試：
- 預設一律 `DRY_RUN=true`
- 未設定 `LIVE_TRADING_ENABLED=true` 時，不得呼叫真實 execution adapter

**Step 2: Run test to verify it fails**

Run: `python -m unittest discover -s tests`
Expected: FAIL with missing live guard

**Step 3: Write minimal implementation**

加入：
- explicit env gate
- startup confirmation
- max loss kill-switch

**Step 4: Run test to verify it passes**

Run: `python -m unittest discover -s tests`
Expected: PASS

**Step 5: Commit**

```bash
git add repos/crypto-arb-openclaw-mvp/app/live_guard.py repos/crypto-arb-openclaw-mvp/app/runner.py repos/crypto-arb-openclaw-mvp/README.md repos/crypto-arb-openclaw-mvp/tests/test_live_guard.py
git commit -m "feat: add live trading safety gate"
```

## Rollout Stages

1. `Stage 0`: 純模擬，使用固定 market payload + pulse payload。
2. `Stage 1`: dry-run，接真實 CoinGecko / Pulse，execution 仍為模擬。
3. `Stage 2`: paper trading，接 CEX 真實 market data，但下單仍走最小額度。
4. `Stage 3`: 只有在 14 天內最大回撤、成交率、fill slippage 都符合門檻後，才允許小額 live。

## Guardrails

- 不使用 DNS。
- 不使用 Telegram bot。
- 不做跨交易所資金拆分。
- 初期只做一個交易對。
- 單日虧損超過 `5%` 即 halt。
- 任一 Pulse 高風險事件命中即 halt。
- LLM 只讀 summary，不直接發單。
