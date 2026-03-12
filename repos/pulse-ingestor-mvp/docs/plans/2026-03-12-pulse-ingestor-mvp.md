# Pulse Ingestor MVP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 建立一個可被動接收 ChatGPT email 脈動資訊、儲存並提供查詢的最小系統。

**Architecture:** 使用 FastAPI 暴露查詢與手動 ingest API，使用 SQLite 儲存原始 email 與結構化 pulse events，使用標準庫 `imaplib` 進行 mailbox 輪詢。第一版 entropy score 採規則法，避免過早引入第二個 LLM。

**Tech Stack:** Python, FastAPI, SQLite, imaplib, unittest

---

### Task 1: 建立資料骨架

**Files:**
- Create: `app/config.py`
- Create: `app/db.py`
- Create: `app/models.py`
- Create: `app/schemas.py`

**Step 1: Write the failing test**
- 建立 parser / scorer 基礎測試，確保輸入能被轉成 pulse event。

**Step 2: Run test to verify it fails**
- 待安裝測試環境後執行：`python -m unittest`

**Step 3: Write minimal implementation**
- 加入設定、SQLite 初始化與 schema。

**Step 4: Run test to verify it passes**
- `python -m compileall app tests`

**Step 5: Commit**
- `git add .`
- `git commit -m "feat: scaffold pulse ingestor domain models"`

### Task 2: 建立 ingestion pipeline

**Files:**
- Create: `app/services/ingestor.py`
- Create: `app/services/parser.py`
- Create: `app/services/scorer.py`
- Create: `app/services/storage.py`

**Step 1: Write the failing test**
- 驗證 email subject/body 會被解析為預期欄位。

**Step 2: Run test to verify it fails**
- `python -m unittest tests.test_parser`

**Step 3: Write minimal implementation**
- 加入 email -> pulse event 轉換、規則式 entropy score、SQLite 儲存。

**Step 4: Run test to verify it passes**
- `python -m unittest tests.test_parser`

**Step 5: Commit**
- `git add .`
- `git commit -m "feat: add pulse ingestion pipeline"`

### Task 3: 建立 API 入口

**Files:**
- Create: `app/main.py`

**Step 1: Write the failing test**
- 驗證健康檢查與最新 pulse 查詢可呼叫。

**Step 2: Run test to verify it fails**
- `python -m unittest`

**Step 3: Write minimal implementation**
- 建立 `/healthz`、`/pulses`、`/ingest/email`、`/ingest/poll`。

**Step 4: Run test to verify it passes**
- `python -m compileall app tests`

**Step 5: Commit**
- `git add .`
- `git commit -m "feat: add pulse ingestor API"`
