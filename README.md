# Codex 多專案管理工作區

`C:\.codex_code_project` 是用來管理多個 AI 輔助開發專案的根工作區。

目前的開發方向是：以快速開發、可上線、可驗證的 MVP 為優先。
目前的模型策略是：思考與規劃以 `gpt-5.4` 為主，程式實作以 `gpt-5.3-code` 為主。

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
    <project-name>/     # 可保留既有 repo，但不一定登錄到 root 配置
  skills/
```

## 受管專案

所有受管專案都放在 `repos/` 底下，並保有各自獨立的 git 歷史與 remote。

目前已登錄：
- 無

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

## MVP 優先原則

- 先交付最小可上線閉環，再補完整性。
- 優先處理會直接影響上線的功能、部署、驗證與回滾能力。
- 非必要時不要先做通用化架構、過度拆模組、提早最佳化或大型重構。
- 若 root 層工具無法直接幫助某個子 repo 更快上線，就不要在 root 層擴張複雜度。

## 模型分工

- `gpt-5.4`：用於需求釐清、方案比較、路由判斷、風險分析與任務拆解。
- `gpt-5.3-code`：用於程式撰寫、補丁生成、局部重構、測試修補與實作落地。
- 若任務同時包含思考與實作，先用 `gpt-5.4` 收斂方向，再以 `gpt-5.3-code` 執行變更。

## Supervisor

`codex-supervisor-mvp/` 是 root 層級的 supervisor 專案，用來監督與輔助 agent-driven workflow。

它屬於管理根目錄，是跨專案基礎設施，不屬於任何單一受管專案。

## 如何用 Supervisor 開發 Sub Repo

`codex-supervisor-mvp` 應從 root workspace 提供，但實際執行時要針對目標 sub repo 啟動。

以 `repos/<project-name>` 為例：

```powershell
Set-Location C:\.codex_code_project\repos\<project-name>
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

1. 在 root workspace 先確認目標專案與最小可交付範圍。
2. 進入目標 repository 後優先完成可上線 MVP 所需最短路徑。
3. 只在確實有助於交付速度時，才擴充 root 層共享規則或工具。
4. 新增受管 repo 時，再同步更新 `repos/index.json` 與 `.workspace/router.json`。
