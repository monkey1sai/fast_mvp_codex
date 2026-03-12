# TODO

## Objective
- 建立第一個 MVP：被動接收 ChatGPT email 脈動資訊，轉成可儲存與查詢的 pulse events。

## Progress
- [x] 建立 repo 骨架
- [x] 建立最小 workflow / architecture 文件
- [x] 建立 FastAPI + SQLite + IMAP ingestor 程式骨架
- [x] 建立 repo 級 Docker 開發環境
- [ ] 補上真實 mailbox 整合驗證
- [ ] 補上排程執行器

## Review
- 第一版以可運行閉環優先，entropy score 採規則式而非模型式。
- 個人 Pro 沒有官方 webhook，因此以 email ingestion 為正式輸入面。

## Verification
- `python -m compileall app tests`
- `python -c "from app.db import init_db; init_db()"`
- `docker compose up --build`
