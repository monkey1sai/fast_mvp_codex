# coingecko-openclaw-mcp

一個給 OpenClaw-compatible agents 使用的 `stdio MCP server`，把 CoinGecko Pro API 轉成 3 個高價值、可直接被 LLM 調用的 crypto 工具：

- `cg_market_snapshot`
- `cg_narrative_scan`
- `cg_grid_strategy_preview`

這個 repo 的目標不是把 CoinGecko endpoint 全部裸露出去，而是提供對 agent 最有價值的三類能力：
- 市場快照
- 題材 / 敘事掃描
- 網格策略預覽

## 為什麼是這 3 個工具

### 1. `cg_market_snapshot`
適合 agent 在決策前快速理解：
- 指定資產籃子的強弱排序
- 大盤風向
- BTC dominance
- 正向 breadth

### 2. `cg_narrative_scan`
適合 agent 做：
- 題材熱度追蹤
- 熱門 category 掃描
- 風險 category 監控
- Trending coin attention check

### 3. `cg_grid_strategy_preview`
適合 agent 做：
- 是否適合開 grid 的前置判斷
- 建議區間上下界
- Grid levels
- Fee edge / capital-per-grid 警示

這一層只做 read-only 分析，不碰下單、不碰交易所私鑰。

## CoinGecko Pro 環境變數

建立 `.env`：

```env
COINGECKO_PRO_API_KEY=replace-me
COINGECKO_API_BASE_URL=https://pro-api.coingecko.com/api/v3
```

官方文件指出 Pro API 應使用：
- base URL: `https://pro-api.coingecko.com/api/v3/`
- header: `x-cg-pro-api-key`

## 本機開發

安裝：

```bash
npm install
```

測試：

```bash
npm test
```

build：

```bash
npm run build
```

以 stdio MCP server 啟動：

```bash
npm run build
node dist/src/cli.js
```

或開發模式：

```bash
npm run dev
```

## OpenClaw 接法

依 OpenClaw 官方文件，ACP bridge 目前不支援在 session metadata 中直接傳 `mcpServers`；MCP 應配置在 `gateway` 或 `agent` 端，而不是每次 ACP request 動態注入。

因此這個 repo 提供的是一個標準 `stdio MCP server`。你在 OpenClaw 側應做的是：

1. 先 build 這個 server
2. 在你的 OpenClaw gateway / agent MCP 設定層，註冊啟動命令：

```bash
node /absolute/path/to/coingecko-openclaw-mcp/dist/src/cli.js
```

3. 透過 OpenClaw 的 gateway / agent 環境變數注入：

```env
COINGECKO_PRO_API_KEY=...
```

重點：
- 不要把 API key 放進 prompt
- 不要依賴 ACP bridge 的 request-level `mcpServers`
- 把這個 MCP 視為 agent 的常駐 read-only 市場資料能力

## 工具摘要

### `cg_market_snapshot`
輸入：
- `coin_ids?`
- `vs_currency`
- `include_global`
- `top_assets?`

輸出重點：
- `global`
- `leaders`
- `assets`
- `agent_notes`

### `cg_narrative_scan`
輸入：
- `vs_currency`
- `top_categories`
- `include_trending`

輸出重點：
- `hot_categories`
- `risk_categories`
- `trending_coins`
- `opportunity_map`
- `agent_notes`

### `cg_grid_strategy_preview`
輸入：
- `coin_id`
- `vs_currency`
- `capital`
- `grid_count`
- `lookback_days`
- `fee_rate`

輸出重點：
- `observed_range`
- `strategy_bounds`
- `capital_plan`
- `levels`
- `warnings`
- `agent_notes`

## 驗證

```bash
npm run build
npm test
```

## 官方參考

- OpenClaw Docs: <https://docs.openclaw.ai>
- OpenClaw ACP bridge caveat on `mcpServers`: <https://docs.openclaw.ai/core-concepts/custom-broker>
- OpenClaw config location / general setup: <https://docs.openclaw.ai/configuration/configuration-reference>
- CoinGecko Auth: <https://docs.coingecko.com/reference/authentication>
- CoinGecko Endpoint Overview: <https://docs.coingecko.com/reference/endpoint-overview>
- CoinGecko MCP beta page: <https://docs.coingecko.com/docs/mcp-server>
