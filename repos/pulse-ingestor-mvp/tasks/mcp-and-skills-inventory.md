# MCP And Skills Inventory

## MCP
- OpenAI 官方文件 MCP：用於查官方 API / 產品邊界。
- `pulseIngestor`：repo-scoped MCP，透過 [`.codex/config.toml`](../.codex/config.toml) 以 `docker compose run --rm -T mcp python -m app.mcp_server` 啟動。
  Enabled: `true`
  Required: `false`
  用途：讓下游 agent 以工具方式呼叫 `pulse_list`、`pulse_get`、`pulse_decision_context`、`pulse_poll_now`、`pulse_scheduler_status`
  關閉條件：Docker 不可用，或該 turn 不需要 pulse tools 時

## Skills
- repo-bootstrap-ai-os
- writing-plans
- python-dev-handbook
- fastapi
