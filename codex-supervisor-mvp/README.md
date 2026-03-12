# Codex Supervisor MVP

`codex-supervisor-mvp` 是 `C:\.codex_code_project` 的 root 層級 supervisor 模組。

它位於管理根目錄，是因為這是跨專案基礎設施，不屬於任何單一受管 repository。

## 職責

- 包住一個類似 Codex 的互動式程序
- 監看 stdout 是否出現白名單規則中的提問模式
- 命中規則時，透過 stdin 回送安全的自動回覆
- 把可重現的 session log 與 audit log 寫入 `state/`
- 支援受管 repo 自己維護的 policy 檔

## 模組結構

```text
codex-supervisor-mvp/
  supervisor.py
  tests.py
  scripts/
    fake_agent.py
    codex-notify.ps1
  state/
```

`state/` 只應視為執行期輸出，不應當成版本化真值。

## Policy 模型

- 不再提供 root 層預設 policy 檔；啟動時需明確傳入 `--policy`
- repo 專屬 policy：`<managed-repo>/.codex-supervisor/policy.json`
- repo 專屬指令：`<managed-repo>/.codex-supervisor/AGENTS.md`

supervisor 只應對狹義、白名單化的提問做自動回覆。未知問題應只記錄，不應自動回答。

## 快速開始

先跑本地 fake-agent 測試：

```powershell
python .\tests.py
python .\supervisor.py --policy <path-to-policy.json> -- python .\scripts\fake_agent.py
```

對受管 repository 啟動：

```powershell
Set-Location C:\.codex_code_project\repos\jacks_happy_bots
python C:\.codex_code_project\codex-supervisor-mvp\supervisor.py --policy .\.codex-supervisor\policy.json -- codex --no-alt-screen
```

在 Windows 上，如果命令是 `codex`，supervisor 會優先嘗試解析成 `codex.cmd`。

## 注意事項

- `scripts/codex-notify.ps1` 主要用於事件落盤，不是可靠的雙向控制 API
- 若要降低提問量，優先改善 workflow 指令與 approval policy，不要先堆更多自動回覆規則
- repo 專屬 policy 應留在該受管 repository 內，不要反向堆回 root 模組
