# Pulse Ingestor MVP

`pulse-ingestor-mvp` adalah prototipe produk minimal yang menerima email terjadwal dari ChatGPT Personal Pro secara pasif, mengubahnya menjadi pulse events terstruktur, menyimpannya secara lokal, lalu menyediakannya ke LLM/agent downstream melalui API dan MCP.

## Fungsi Utama

- Membaca email yang belum dibaca dari mailbox khusus
- Mengubah email menjadi pulse event yang ternormalisasi
- Menyimpan konten mentah dan ringkasan
- Menghitung `entropy_score` dan `decision_signal_score` berbasis aturan
- Menyediakan API dan MCP tools untuk agent downstream

## Di Luar Cakupan

- Tidak terhubung ke webhook privat ChatGPT
- Tidak melakukan automasi browser untuk UI ChatGPT
- Tidak mencakup Enterprise Compliance API
- Tidak menambahkan lapisan orkestrasi agent yang kompleks secara default

## Runtime

- API: FastAPI
- Storage: SQLite
- Ingestion: IMAP polling
- MCP transport: stdio

## Quick Start dengan Docker

1. Salin `.env.example` menjadi `.env`
2. Jalankan layanan:

```bash
docker compose up --build -d
```

3. Cek health:

```bash
curl http://127.0.0.1:8000/healthz
```

## API Utama

- `GET /healthz`
- `GET /pulses`
- `GET /pulses/{id}`
- `GET /decision/context`
- `GET /scheduler/status`
- `POST /ingest/email`
- `POST /ingest/poll`
- `POST /admin/ingest/backfill`

## Penanganan Email

- Email pulse yang cocok dibaca dari `PULSE_IMAP_MAILBOX`
- Setelah berhasil di-ingest, email akan dipindah ke `AI新聞脈動PLUS` secara default
- Riwayat lama bisa di-backfill dari `AI新聞脈動PLUS`
- Backfill adalah tool eksplisit, bukan proses otomatis saat startup

## MCP Tools

- `pulse_list`
- `pulse_get`
- `pulse_decision_context`
- `pulse_poll_now`
- `pulse_backfill_history`
- `pulse_scheduler_status`

## Instalasi MCP

Menjalankan MCP dengan Docker dan stdio:

```bash
docker compose run --rm -T mcp python -m app.mcp_server
```

Validasi:

```bash
docker compose run --rm -T mcp python -c "import app.mcp_server; print('mcp-import-ok')"
```

## Sponsor dan Layanan

Repo publik ini cocok untuk dua jalur monetisasi:

- sponsor untuk pemeliharaan open-source
- layanan implementasi dan konsultasi berbayar

Layanan yang direkomendasikan:

- integrasi ChatGPT/email pulse ingestion
- packaging MCP server
- desain workflow keputusan untuk LLM
- deployment FastAPI
- pipeline knowledge dan notification internal

