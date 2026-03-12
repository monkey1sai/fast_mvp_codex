# Fast MVP Codex

`fast_mvp_codex` 是一個 root workspace，用來管理 AI 輔助開發流程，目標是更快把產品做成可上線的 MVP。

這個 repository 不承載單一產品本體，而是保存 root 層的協作規則、workspace 記憶、共享 agent 提示與跨專案工具。

目前預設策略：
- 開發方向：快速開發、可上線、可驗證的 MVP 優先
- 模型分工：思考與規劃以 `gpt-5.4` 為主，程式實作以 `gpt-5.3-code` 為主

root repo 主要追蹤：
- `.workspace/`：root AI workspace context 與路由資訊
- `agents/`：共享輕量角色提示
- `repos/index.json`：受管專案登錄
- `codex-supervisor-mvp/`：root 層共享工具

真正的產品開發與 git 歷史應保留在 `repos/<project-name>` 內的子 repository。

## 核心原則

- 先交付最小可上線閉環，再補完整性。
- 優先處理直接影響上線的功能、部署、驗證與回滾能力。
- 非必要時不要先做過度抽象、過早最佳化或大型重構。
- 只有在能幫助交付速度時，才擴張 root 層規則或工具。

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

## Model Routing

- `gpt-5.4`：需求釐清、方案比較、風險分析、路由判斷、任務拆解
- `gpt-5.3-code`：程式撰寫、補丁生成、局部重構、測試修補、實作落地
- 同時涉及思考與實作時，先用 `gpt-5.4` 收斂方向，再用 `gpt-5.3-code` 執行

## Managed Repos

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

## Supervisor

`codex-supervisor-mvp/` 是 root 層級的 supervisor 專案，用來監督與輔助 agent-driven workflow。

它屬於管理根目錄，是跨專案基礎設施，不屬於任何單一受管專案。

## Working Style

- 在 root workspace 做方向收斂、路由與共享規則維護
- 進入目標子 repo 後，優先完成最短的可上線路徑
- 只有在確實能加快交付時，才把子 repo 掛回 root registry
- 若使用 supervisor，policy 應由子 repo 顯式提供，而不是依賴 root 預設配置
