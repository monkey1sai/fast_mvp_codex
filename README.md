# Codex 多專案管理工作區

`C:\.codex_code_project` 是用來管理多個 AI 輔助開發專案的根工作區。

這個 root repo 主要追蹤共享的管理層內容：
- `.workspace/` 內的 root AI workspace 檔案
- `agents/` 內的共用輕量角色提示
- `repos/index.json` 內的受管專案清單
- `codex-supervisor-mvp/` 這類 root 層級的 supervisor 工具

實際專案開發應在對應的受管 repo 內進行。

## 目錄結構

```text
C:\.codex_code_project
  .workspace/
  agents/
  codex-supervisor-mvp/
  repos/
    index.json
    README.md
    jacks_happy_bots/   # 獨立 git repository
  skills/
```

## 受管專案

所有受管專案都放在 `repos/` 底下，並保有各自獨立的 git 歷史與 remote。

目前已登錄：
- `repos/jacks_happy_bots`

參考檔案：
- `repos/index.json`
- `repos/README.md`

## Git 管理模型

root repository 與每一個受管 repository 是刻意分開管理的。

規則：
- root git 只追蹤管理層與 root 工具
- `repos/` 底下的子 repo 保有自己的 `.git` 目錄
- root `.gitignore` 預設排除 nested repo 的內容
- 專案程式碼的 `pull`、`merge`、`push` 應在子 repo 內執行

## Supervisor

`codex-supervisor-mvp/` 是 root 層級的 supervisor 專案，用來監督與輔助 agent-driven workflow。

它屬於管理根目錄，是跨專案基礎設施，不屬於 `jacks_happy_bots` 單一專案。

## 如何用 Supervisor 開發 Sub Repo

`codex-supervisor-mvp` 應從 root workspace 提供，但實際執行時要針對目標 sub repo 啟動。

以 `repos/jacks_happy_bots` 為例：

```powershell
Set-Location C:\.codex_code_project\repos\jacks_happy_bots
python C:\.codex_code_project\codex-supervisor-mvp\supervisor.py --policy .\.codex-supervisor\policy.json -- codex --no-alt-screen
```

建議每個受管 repo 都遵守以下配置：
- 在 `.codex-supervisor/policy.json` 放 repo 專屬規則
- 在 `.codex-supervisor/AGENTS.md` 放 repo 專屬指令
- 實作、測試與 git 操作都留在 sub repo 內執行
- 跨專案的監督邏輯與共用自動化則保留在 root 模組

運作模型：
- supervisor 程式碼由 root workspace 管理
- policy 與指令由 sub repo 自己負責
- supervisor 執行時的 log 預設寫到 `codex-supervisor-mvp/state/`，除非你另外指定 `--state-dir`
- 專案程式碼的 `git pull`、`commit`、`push` 仍應在 sub repo 內執行

## 建議工作流程

1. 在 root workspace 進行多專案路由與管理。
2. 進入目標 repository 後再做實作。
3. 新增受管 repo 時，同步更新 `repos/index.json`。
4. 保持 `.workspace/router.json` 與目前有效的受管專案一致。
