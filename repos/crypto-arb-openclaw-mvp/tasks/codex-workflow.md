# Codex Workflow

1. 先確認需求是否屬於加密套利、OpenClaw、MCP 或模擬/風控範圍。
2. 所有 live execution 能力先以 deterministic 介面與 stub 實作。
3. 每次新增策略能力都要附帶最小測試與可重現 CLI 驗證。
4. 優先維持控制平面與資料平面的分層，避免把 LLM 放進下單主回路。
