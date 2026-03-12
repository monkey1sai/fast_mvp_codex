# Pulse Ingestor MVP

`pulse-ingestor-mvp` هو نموذج أولي صغير يستقبل رسائل ChatGPT Personal Pro المجدولة بشكل سلبي، ويحوّلها إلى pulse events منظّمة، ويخزنها محلياً، ثم يتيحها للـ LLMs والوكلاء اللاحقين عبر API وMCP.

## ما الذي يفعله

- يقرأ الرسائل غير المقروءة من صندوق بريد مخصص
- يحول البريد إلى pulse events منظّمة
- يحتفظ بالمحتوى الخام والملخص
- يحسب `entropy_score` و`decision_signal_score` بطريقة rule-based
- يوفّر API وMCP tools للاستهلاك من قبل الوكلاء

## ما الذي لا يفعله

- لا يدمج webhook خاص بـ ChatGPT
- لا يقوم بأتمتة واجهة ChatGPT
- لا يتضمن Enterprise Compliance API
- لا يضيف طبقة orchestration معقدة بشكل افتراضي

## التشغيل

- API: FastAPI
- Storage: SQLite
- Ingestion: IMAP polling
- MCP transport: stdio

## البدء السريع عبر Docker

1. انسخ `.env.example` إلى `.env`
2. شغّل الخدمات:

```bash
docker compose up --build -d
```

3. افحص الصحة:

```bash
curl http://127.0.0.1:8000/healthz
```

## الواجهات الأساسية

- `GET /healthz`
- `GET /pulses`
- `GET /pulses/{id}`
- `GET /decision/context`
- `GET /scheduler/status`
- `POST /ingest/email`
- `POST /ingest/poll`
- `POST /admin/ingest/backfill`

## التعامل مع البريد

- يتم سحب رسائل pulse المطابقة من `PULSE_IMAP_MAILBOX`
- بعد المعالجة الناجحة يتم نقل الرسائل افتراضياً إلى `AI新聞脈動PLUS`
- يمكن استرجاع التاريخ لاحقاً من `AI新聞脈動PLUS`
- عملية backfill أداة صريحة وليست مهمة تلقائية عند بدء الخادم

## أدوات MCP

- `pulse_list`
- `pulse_get`
- `pulse_decision_context`
- `pulse_poll_now`
- `pulse_backfill_history`
- `pulse_scheduler_status`

## تثبيت MCP

تشغيل MCP عبر Docker وstdio:

```bash
docker compose run --rm -T mcp python -m app.mcp_server
```

التحقق:

```bash
docker compose run --rm -T mcp python -c "import app.mcp_server; print('mcp-import-ok')"
```

## الدعم والخدمات

هذا المستودع العام يدعم مسارين للإيراد:

- الرعاية المستمرة لصيانة المشروع المفتوح
- خدمات التنفيذ والاستشارات المدفوعة

الخدمات المقترحة:

- تكامل ChatGPT والبريد الإلكتروني
- تغليف MCP server
- تصميم مسارات قرار للـ LLM
- نشر FastAPI
- بناء تدفقات معرفة وإشعارات داخلية

