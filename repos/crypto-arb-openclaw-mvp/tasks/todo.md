# TODO

## Progress
- [x] 建立 repo 與最小 AI OS 骨架。
- [x] 實作 deterministic arbitrage strategy / risk / simulation MVP。
- [x] 建立 CoinGecko MCP、Pulse MCP、OpenClaw 整合介面。
- [x] 依現有本地 env 條件完成 30 美元 HFT agent 規劃。
- [x] 定義 `Sovereign Microstructure Agent` 的架構與 persona。
- [x] 補 `Pionex` live adapter 與 live guard 基礎層。
- [x] 補 `Pionex` 單輪 guarded live validation runner/CLI。
- [x] 把固定 3% 想法改成 `淨優勢 bps + 冷卻時間` 的回測門檻。
- [x] 補 OKX 連續循環 runner 與 JSONL telemetry。
- [x] 補 replay loader 與最小 observability summary。
- [ ] 補 execution MCP contract 與 paper-trading OMS。
- [ ] 補單交易所 maker-first HFT quote engine。
- [ ] 補更完整的 observability 指標與 replay 分析。
- [ ] 補更真實的多交易所/三角套利資料模型。
- [ ] 補 `Pionex` 原生市場資料 feed，取代手動 bid/ask 注入。

## Review
- 第一版不做真實下單，避免把 live execution 與 LLM 耦合。
- 下一階段應補回測資料載入器與事件回放，而不是直接接 exchange key。
- 30 美元本金不適合先做跨所套利，第一個 live 路徑應改成單交易所微結構策略。
- 真實交易路徑先以 `Pionex` 為第一站，但必須保留 `LIVE_TRADING_ENABLED` 與 symbol/notional guard。
- `BTC_USDT` 在 `Pionex` 的最小下單金額目前是 `10 USDT`，30 美元本金下不能假設 `5 USD` 測試單可成交。
- 目前已具備 `OKX public ticker -> guard -> place/cancel -> JSONL telemetry` 的可連續執行路徑，但還未接 WebSocket order book。
- replay 目前先提供 JSONL 匯總，不含逐筆 fills/position 對帳與事件重播。
