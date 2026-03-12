# Pulse Ingestor MVP

`pulse-ingestor-mvp` 是一個最小產品原型，用來被動接收 ChatGPT 個人 Pro 的排程 email，將其轉為可查詢、可累積、可供後續 LLM 決策使用的 pulse events。

## MVP Scope

- 從專用信箱讀取未讀 email
- 解析成結構化 pulse event
- 保留原始內容與摘要
- 計算規則式 `entropy_score` 與 `decision_signal_score`
- 透過 API 查詢最新脈動

## Out of Scope

- 直接整合 ChatGPT 私有 webhook
- 操作 ChatGPT UI
- 企業版 Compliance API
- 複雜 agent orchestration

## App Structure

```text
app/
  main.py        FastAPI 入口
  config.py      環境變數設定
  db.py          SQLite 初始化
  schemas.py     API schema
  services/
    ingestor.py  IMAP 輪詢與 email 轉換
    parser.py    email -> pulse event
    scorer.py    entropy / novelty / uncertainty 規則
    storage.py   SQLite 存取
```

## Planned Runtime

- API: FastAPI
- Storage: SQLite
- Ingestion: IMAP polling
- Verification: `python -m compileall`

## Docker Development

1. 複製 `.env.example` 成 `.env`
2. 在 repo 根目錄執行 `docker compose up --build`
3. API 預設暴露在 `http://127.0.0.1:8000`
4. SQLite 會寫到 `runtime/pulse.db`
5. MCP server 會以 `stdio` 方式在 `mcp` service 內啟動

常用命令：

- `docker compose up --build`
- `docker compose down`
- `docker compose logs -f api`
- `docker compose exec -T api python -m unittest tests.test_api tests.test_parser -v`
- `docker compose logs -f mcp`

主要 API：

- `GET /healthz`
- `GET /pulses?limit=20&status=new&min_entropy=0.4`
- `GET /pulses/{id}`
- `GET /decision/context?limit=5&min_decision_signal=0.5`
- `GET /scheduler/status`
- `POST /ingest/email`
- `POST /ingest/poll`
- `POST /admin/ingest/backfill`
- `DELETE /admin/pulses/non-target`
- `POST /admin/pulses/rehydrate`

郵件過濾預設只會收：

- 寄件者包含 `openai` 或 `chatgpt`
- 且主旨或內文包含 task update / 任務更新 / ChatGPT task markers

可透過 `.env` 的 `PULSE_ALLOWED_*` 系列變數調整。

目前 pulse event 會額外正規化：

- 解碼 MIME subject / from
- 抽出第一個 ChatGPT 連結到 `source_url`
- 清掉通知 footer 後再產生 `summary`
- 產出 `decision_signal_score` 供後續 LLM 決策使用

成功 ingest 的目標郵件，預設會自動搬移到 `AI新聞脈動PLUS`。
可透過以下環境變數調整：

- `PULSE_IMAP_MOVE_ON_SUCCESS=true`
- `PULSE_IMAP_PROCESSED_MAILBOX=AI新聞脈動PLUS`

若開啟 `PULSE_AUTO_POLL_ENABLED=true`，服務啟動後會依 `PULSE_AUTO_POLL_INTERVAL_SECONDS` 自動輪詢信箱。

## MCP Tools

`app.mcp_server` 會暴露：

- `pulse_list`
- `pulse_get`
- `pulse_decision_context`
- `pulse_poll_now`
- `pulse_backfill_history`
- `pulse_scheduler_status`

`pulse_backfill_history` 預設會從 `AI新聞脈動PLUS` 讀取歷史信件並回補到 SQLite。
這個動作是明確工具呼叫，不會在 MCP server 啟動時自動執行。

## Connect From Codex

這個 repo 已提供 repo-scoped MCP 設定檔 [`.codex/config.toml`](.codex/config.toml)。

設計方式：

- 由 Codex 以 `docker compose run --rm -T mcp python -m app.mcp_server` 啟動 stdio MCP
- 不依賴本機 Python 直接安裝 `fastmcp`
- 共用 repo 內的 `runtime/pulse.db` 與 `.env`

使用方式：

1. 在 repo 根目錄先執行 `docker compose up -d api`
2. 重新開一個 Codex session，讓 repo-scoped `.codex/config.toml` 生效
3. 下游 agent 即可呼叫：
   - `pulse_list`
   - `pulse_get`
   - `pulse_decision_context`
   - `pulse_poll_now`
   - `pulse_scheduler_status`

最小驗證：

- `docker compose run --rm -T mcp python -c "import app.mcp_server; print('mcp-import-ok')"`
- `docker compose ps`

## Environment Variables

- `PULSE_DB_PATH`
- `PULSE_IMAP_HOST`
- `PULSE_IMAP_PORT`
- `PULSE_IMAP_USERNAME`
- `PULSE_IMAP_PASSWORD`
- `PULSE_IMAP_MAILBOX`
- `PULSE_IMAP_PROCESSED_MAILBOX`
- `PULSE_IMAP_MOVE_ON_SUCCESS`
- `PULSE_POLL_MAX_MESSAGES`

## Next Steps

1. 補 IMAP 連線實測
2. 新增背景排程或外部 scheduler
3. 將 entropy score 串入下游 decision engine
