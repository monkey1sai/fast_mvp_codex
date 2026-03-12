# Pulse Ingestor MVP

## Language
- 預設使用繁體中文（zh-TW）。
- 程式碼、API 名稱、log 保持原語言。

## Scope
- 這個 repo 專注於接收 ChatGPT 個人 Pro 排程通知 email。
- 第一階段只做被動接收、解析、儲存、查詢與 entropy score。
- 不直接耦合 ChatGPT 網頁 UI，不做自動化操作。

## Working Rules
- 先完成最小可運作閉環，再補排程、推播、權限與觀測。
- 優先保留原始 email 內容，再做結構化欄位抽取。
- 不要把 secrets 寫進 repo；所有帳號與密碼都走環境變數。
- 任何安裝套件或對外連線測試，先說明目的與風險。

## Bootstrap Trigger
- 若缺少 `tasks/`、`prompts/`、或關鍵 workflow 文件，先補齊最小 AI OS 骨架。
