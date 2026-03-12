# Pulse Ingestor MVP

`pulse-ingestor-mvp` เป็นต้นแบบผลิตภัณฑ์ขนาดเล็กที่รับอีเมลตามกำหนดเวลาจาก ChatGPT Personal Pro แบบ passive แปลงเป็น pulse events แบบมีโครงสร้าง จัดเก็บในเครื่อง และเปิดให้ LLM/agent ชั้นถัดไปเรียกใช้ผ่าน API และ MCP

## ความสามารถหลัก

- อ่านอีเมลที่ยังไม่อ่านจากกล่องจดหมายเฉพาะ
- แปลงอีเมลเป็น pulse event แบบ normalized
- เก็บทั้งข้อมูลดิบและ summary
- คำนวณ `entropy_score` และ `decision_signal_score` แบบ rule-based
- เปิด API และ MCP tools ให้ agent ภายนอกเรียกใช้

## ขอบเขตที่ไม่ทำ

- ไม่เชื่อม private webhook ของ ChatGPT
- ไม่ทำ browser automation กับ UI ของ ChatGPT
- ไม่รวม Enterprise Compliance API
- ไม่ทำ orchestration agent แบบซับซ้อนในตัว

## Runtime

- API: FastAPI
- Storage: SQLite
- Ingestion: IMAP polling
- MCP transport: stdio

## เริ่มต้นด้วย Docker

1. คัดลอก `.env.example` เป็น `.env`
2. เริ่มบริการ:

```bash
docker compose up --build -d
```

3. ตรวจสอบสถานะ:

```bash
curl http://127.0.0.1:8000/healthz
```

## API หลัก

- `GET /healthz`
- `GET /pulses`
- `GET /pulses/{id}`
- `GET /decision/context`
- `GET /scheduler/status`
- `POST /ingest/email`
- `POST /ingest/poll`
- `POST /admin/ingest/backfill`

## การจัดการอีเมล

- ระบบจะอ่านอีเมลเป้าหมายจาก `PULSE_IMAP_MAILBOX`
- เมื่อ ingest สำเร็จ อีเมลจะถูกย้ายไป `AI新聞脈動PLUS` โดยค่าเริ่มต้น
- ประวัติอีเมลเก่าสามารถ backfill ภายหลังได้จาก `AI新聞脈動PLUS`
- การ backfill เป็นการเรียกใช้แบบ explicit ไม่ได้รันอัตโนมัติตอนเริ่ม server

## MCP Tools

- `pulse_list`
- `pulse_get`
- `pulse_decision_context`
- `pulse_poll_now`
- `pulse_backfill_history`
- `pulse_scheduler_status`

## การติดตั้ง MCP

เริ่ม MCP แบบ stdio ผ่าน Docker:

```bash
docker compose run --rm -T mcp python -m app.mcp_server
```

ตรวจสอบ:

```bash
docker compose run --rm -T mcp python -c "import app.mcp_server; print('mcp-import-ok')"
```

## การสนับสนุนและบริการ

repo นี้เหมาะกับ 2 รูปแบบรายได้:

- การสนับสนุนโครงการโอเพนซอร์ส
- บริการติดตั้งและให้คำปรึกษาแบบชำระเงิน

บริการที่แนะนำ:

- การเชื่อมต่อ ChatGPT/email pulse ingestion
- การสร้าง MCP server
- การออกแบบ workflow สำหรับ LLM decision
- การ deploy FastAPI
- ระบบ notification และ knowledge pipeline ภายในองค์กร

