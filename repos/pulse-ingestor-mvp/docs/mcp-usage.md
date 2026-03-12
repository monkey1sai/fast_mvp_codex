# Pulse Ingestor MCP Usage

## Purpose

`pulse-ingestor-mvp` 現在同時提供：

- FastAPI 查詢介面
- stdio MCP tools

MCP 的角色是讓下游 agent / LLM 用工具方式讀取 pulse，而不是直接綁 REST API 細節。

## Repo-Scoped Codex Config

設定檔位置：

- [`.codex/config.toml`](../.codex/config.toml)

目前設定會讓 Codex 在此 repo 內自動註冊：

- `pulseIngestor`

啟動指令：

```bash
docker compose run --rm -T mcp python -m app.mcp_server
```

這樣的好處：

- 用既有 Docker image 啟動，不依賴本機 Python 套件
- 可以直接共用 `.env`
- 使用相同的 `runtime/pulse.db`

## Available Tools

- `pulse_list`
  列出 pulse，支援 `limit`、`status`、`source_type`、`min_entropy`、`min_decision_signal`
- `pulse_get`
  讀取單筆 pulse
- `pulse_decision_context`
  取高訊號 pulse 摘要
- `pulse_poll_now`
  立即輪詢信箱
- `pulse_scheduler_status`
  讀取背景排程狀態

## Recommended Flow

1. 先確保 API 與資料庫存在：

```bash
docker compose up -d api
```

2. 重新開啟 Codex session，讓 repo-scoped MCP 設定生效

3. 由下游 agent 依需求呼叫：

```text
pulse_list(limit=10, min_decision_signal=0.45)
pulse_decision_context(limit=5, min_decision_signal=0.5)
pulse_get(pulse_id=13)
```

## Verification

確認 MCP 模組可被容器正常載入：

```bash
docker compose run --rm -T mcp python -c "import app.mcp_server; print('mcp-import-ok')"
```

確認服務狀態：

```bash
docker compose ps
curl http://127.0.0.1:8000/healthz
```
