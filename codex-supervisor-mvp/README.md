# Codex Supervisor MVP

這是一套在 Windows 上監督 Codex session 並對固定問題自動回覆的最小可行架構。
正式規則請放在各 repo 自己的監督資料夾，不再依賴 `examples/`。

## 內容

- `supervisor.py`: 啟動子程序、監看 stdout、比對規則、必要時寫入 stdin。
- `scripts/codex-notify.ps1`: 接收 Codex `notify` payload，落盤成 JSONL 事件檔。
- `scripts/default-policy.json`: 測試用白名單規則。
- `scripts/fake_agent.py`: 不依賴真實 Codex 的模擬互動程式，用來測試 supervisor。
- `tests.py`: 本地可重現測試。

## 架構

1. Codex 以互動模式執行，建議搭配 `--no-alt-screen`。
2. `notify` 事件會由 `codex-notify.ps1` 落盤。
3. `supervisor.py` 包住 Codex 程序：
   - 持續讀取 stdout
   - 寫入 `session.log`
   - 用規則比對是否為可自動回覆的問題
   - 對白名單命中項目送回 stdin
   - 對未知問題只記錄，不自動亂答

## 快速開始

1. 把 repo 專屬規則放進 `<repo>/.codex-supervisor/AGENTS.md` 與 `<repo>/.codex-supervisor/policy.json`。
2. 視需要把 `notify` 設定加進 `~/.codex/config.toml`。
3. 在目標 repo 內啟動 supervisor。
4. 測試模擬流程：

```powershell
python .\tests.py
python .\supervisor.py --policy .\scripts\default-policy.json -- python .\scripts\fake_agent.py
```

5. 在 repo 內監督真實 Codex：

```powershell
python C:\.codex_code_project\codex-supervisor-mvp\supervisor.py --policy .\.codex-supervisor\policy.json -- codex --no-alt-screen
```

在 Windows 上若你直接寫 `codex`，supervisor 會自動優先解析成 `codex.cmd`。

## 注意

- 這個 MVP 只會自動回覆白名單規則命中的問題。
- 未知問題不自動回覆，避免誤導 session。
- `notify` 只負責監控與落盤，不是可靠的雙向控制 API。
- 若要降低提問量，優先靠 `AGENTS.md` 與 `approval_policy`，不要期待事後攔截能解所有問題。
