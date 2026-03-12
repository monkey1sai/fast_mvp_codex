# Workflow Digest

## 六步流程

1. 先確認需求是否屬於 `pulse-ingestor-mvp`。
2. 先保存原始 email，再做摘要、標籤與 entropy score。
3. 先完成最小閉環，不預設個人版 ChatGPT 有 webhook。
4. 所有新功能都要附最小驗證命令。
5. secrets 只能走環境變數，不進 repo。
6. 若需安裝或對外整合，先說明風險與目的。

## Agent 分工

- Planner：收斂 schema、接收流程與風險。
- Coder：實作 FastAPI、SQLite、IMAP polling 與 parser/scorer。
- Reviewer：檢查資料遺失、去重與安全邊界。
- Tester：驗證 parser、scorer、DB 初始化與可重現命令。

## MCP / Skills

- OpenAI 官方文件 MCP：查產品能力邊界與 API 文件。
- 主要技能：repo-bootstrap-ai-os、writing-plans、python-dev-handbook、fastapi。

## 完成前驗證

- `python -m compileall app tests`
- `python -c "from app.db import init_db; init_db()"`

## Next Suggestion

- 補一個 `requirements.txt` 或 `pyproject.toml`
- 補 `.env.example`
- 決定 IMAP 連線是直接 Gmail/Outlook，或先走 email forwarding inbox
