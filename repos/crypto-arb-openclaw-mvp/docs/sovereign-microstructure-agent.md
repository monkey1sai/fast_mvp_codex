# Sovereign Microstructure Agent

## Positioning

這不是一般的「會喊單」交易 agent，而是一個把貨幣、政治、加密市場結構與微結構執行分層處理的 regime-aware trading system。

它的核心信念是：

- 市場不是只有 K 線，而是權力、流動性、結算規則與敘事的交叉點。
- 加密市場不是獨立宇宙，而是美元流動性邊疆。
- 貨幣不是中性的交換媒介，而是誰有資格記帳、誰能迫使別人接受記帳的制度。
- LLM 可以理解世界，但不應直接控制 live execution。

## Design Goal

在 30 美元本金、單機部署、無 DNS、無 Telegram bot 的前提下，設計一個：

- 大膽
- 有強烈市場觀點
- 對加密、政治、貨幣本質有獨特見解
- 但執行層仍然克制、可驗證、可停止

的高頻交易 agent。

## Five-Layer Architecture

### 1. Civilization Lens Layer

用途：回答市場背後的文明與秩序問題。

主要問題：
- 現在市場把什麼當成錢？
- 全球資本正在追逐收益、避險，還是等待政策定價？
- 主權、監管、戰爭、選舉、央行溝通正在改變哪種風險偏好？

輸出：
- `civilization_regime`
- `macro_bias`
- `fragility_score`
- `narrative_map`

### 2. Political-Monetary Layer

用途：建立對貨幣與政治的核心見解。

核心觀點：
- 法幣的力量來自稅收、法律、清算網路與國家暴力的背書。
- BTC 更像「去主權儲備資產敘事」，不是日常支付貨幣。
- 穩定幣更像美元地下結算網路，而不是獨立主權貨幣。
- 多數 token 並非真正貨幣，而是注意力、敘事與未來現金流的投機容器。

輸出：
- `monetary_thesis`
- `usd_hegemony_mode`
- `state_pressure_score`
- `crypto_legitimacy_score`

### 3. Crypto Market Structure Layer

用途：理解加密市場內部資產階層與流動性邏輯。

主要問題：
- BTC 是風險資產、避險資產，還是美元流動性槓桿鏡像？
- ETH 是科技 beta、鏈上經濟燃料，還是大盤風險代理？
- 山寨輪動是真正資本擴散，還是流動性陷阱？
- ETF、穩定幣供給、交易所存量、鏈上活躍度哪個是主要驅動？

輸出：
- `market_structure_state`
- `asset_hierarchy`
- `rotation_map`
- `liquidity_dependency_score`

### 4. Risk Sovereign Layer

用途：把世界觀轉成可執行限制。

這一層不下單，只做授權。

輸出：
- `mode = normal | caution | halt`
- `allowed_symbols`
- `max_notional_per_order_usd`
- `quote_width_multiplier`
- `inventory_bias`
- `kill_switch_reason`

來源：
- Pulse news
- CoinGecko regime summary
- 本地 drawdown
- inventory stress
- exchange incident tags

### 5. Execution Microstructure Layer

用途：執行真正接近高頻的決策。

職責：
- 讀 order book top
- 算 spread / mid / imbalance
- 設 quote price
- 控 inventory skew
- 做 cancel / replace
- 做短周期微利捕捉

限制：
- 不接受抽象政治觀點直接發單
- 只接受 Risk Sovereign Layer 已授權的 regime 與 risk bounds

## Input / Output Contracts

### Input: Macro / Thesis Context

```json
{
  "civilization_regime": "late-dollar-risk-cycle",
  "macro_bias": "risk-on but fragile",
  "usd_hegemony_mode": "strong",
  "state_pressure_score": 0.62
}
```

### Input: Crypto Structure Context

```json
{
  "market_structure_state": "btc-led",
  "asset_hierarchy": ["BTC", "ETH", "SOL"],
  "rotation_map": {
    "majors": "leading",
    "alts": "lagging"
  },
  "liquidity_dependency_score": 0.71
}
```

### Input: Risk Sovereign Context

```json
{
  "mode": "caution",
  "allowed_symbols": ["BTC_USDT"],
  "max_notional_per_order_usd": 5,
  "quote_width_multiplier": 1.4,
  "inventory_bias": "flat",
  "kill_switch_reason": ""
}
```

### Output: Execution Intent

```json
{
  "symbol": "BTC_USDT",
  "side": "buy",
  "price": 71234.5,
  "size_usd": 5,
  "ttl_ms": 1200,
  "reason": "maker quote under caution regime with widened spread"
}
```

## Why This Agent Is Bold

它的大膽不是來自瘋狂槓桿，而是來自明確世界觀：

- 不把市場看成單純技術圖形。
- 不把加密看成脫離主權體系的烏托邦。
- 不把貨幣看成中性工具。
- 不假裝「中立」，而是承認價格本身就是秩序與權力競逐的結果。

## Why This Agent Is Safe

它的安全不是保守，而是分層：

- 見解層可以激進
- 風控層必須冷靜
- 執行層必須 deterministic

也就是：

- 世界觀可以有稜角
- quote engine 不能有情緒

## Recommended Runtime Shape

在你現有基礎上，這個 agent 應這樣接：

- `coingecko-openclaw-mcp`
  用於 reference price、market snapshot、敘事掃描
- `pulse-ingestor-mvp`
  用於新聞風險、exchange incident、entropy gating
- `openclaw`
  用於控制平面、人工審查、session 記憶與操作入口
- `crypto-arb-openclaw-mvp`
  用於 deterministic strategy、risk、quote engine、dry-run execution

## Recommended First Live Scope

- 單交易所
- 單交易對
- maker-first
- 單筆 5 USD
- 最大淨風險 10 USD
- 單日虧損 5% halt
- 高 entropy pulse 直接 halt

## Non-Goals

- 不追求「30 美元快速變 1000 美元」神話
- 不做政治評論型聊天機器人
- 不讓 LLM 直接下單
- 不把抽象哲學直接轉成市場方向押注
