# Crypto Arb OpenClaw MVP

## Language
- 預設使用繁體中文（zh-TW）。
- 程式碼、API 名稱、log 保持原語言。

## Scope
- 這個 repo 專注於以 OpenClaw 為控制平面、以 MCP 為工具層的加密套利 MVP。
- 第一階段只做 deterministic 策略、模擬、風控與整合介面。
- 不在第一版直接做真實交易所下單。

## Working Rules
- 任何 live execution 相關功能都先以 stub/interface 形式保留。
- 策略判斷與交易執行分層，避免把 LLM 放進即時下單回路。
- 所有新增能力都附最小驗證命令。
- 不要把 secrets 寫進 repo；所有帳號與 API keys 都走環境變數。

## Bootstrap Trigger
- 若缺少 `tasks/`、`prompts/`、或關鍵 workflow 文件，先補齊最小 AI OS 骨架。
