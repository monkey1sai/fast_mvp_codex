# Repos 管理清單

`repos/` 是 `C:\.codex_code_project` 底下所有受管專案的正式容器。

此目錄的使用原則以「盡快把子專案做成可上線 MVP」為優先。

## 規則
- 每個受管 repository 都應是 `repos/` 的直接子目錄。
- 每個專案都要登錄到 `repos/index.json`。
- root 層級的 `.workspace/router.json` 應與 `repos/index.json` 保持一致。
- 實際程式開發應在目標 repository 內進行，而不是在管理根目錄進行。
- 只有當 root 層配置能幫助更快交付時，才把專案掛回 root registry。

## 目前專案
- 無已登錄專案

## 更新檢查清單
1. 把新的 repository 放到 `repos/<project-name>`。
2. 在 `repos/index.json` 新增一筆專案資料。
3. 如果該專案需要由 root workspace 路由，更新 `.workspace/router.json`。
4. 只有在需要新增 root 層共用索引時，才更新 `.workspace/index.json`。
