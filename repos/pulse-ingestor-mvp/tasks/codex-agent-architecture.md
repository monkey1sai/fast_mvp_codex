# Codex Agent Architecture

## Planner
- 定義 pulse event schema、接收流程與風險。

## Coder
- 實作 FastAPI、SQLite、IMAP polling、parser 與 scorer。

## Reviewer
- 檢查資料遺失風險、去重策略與 secrets handling。

## Tester
- 驗證 parser、scorer 與 DB 初始化至少可重現執行。
