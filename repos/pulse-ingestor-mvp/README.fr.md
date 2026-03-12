# Pulse Ingestor MVP

`pulse-ingestor-mvp` est un prototype minimal qui reçoit passivement les emails planifiés de ChatGPT Personal Pro, les transforme en pulse events structurés, les stocke localement, puis les expose aux LLMs et agents via API et MCP.

## Ce que fait le projet

- Lecture des emails non lus depuis une boîte dédiée
- Transformation en pulse events normalisés
- Conservation du contenu brut et du résumé
- Calcul de `entropy_score` et `decision_signal_score` avec des règles simples
- Exposition des données via API et outils MCP

## Hors périmètre

- Pas de webhook privé ChatGPT
- Pas d’automatisation du navigateur sur l’interface ChatGPT
- Pas d’intégration Compliance API Enterprise
- Pas de couche d’orchestration agent complexe par défaut

## Runtime

- API: FastAPI
- Storage: SQLite
- Ingestion: IMAP polling
- MCP transport: stdio

## Démarrage rapide avec Docker

1. Copier `.env.example` vers `.env`
2. Lancer les services :

```bash
docker compose up --build -d
```

3. Vérifier l’état :

```bash
curl http://127.0.0.1:8000/healthz
```

## API principales

- `GET /healthz`
- `GET /pulses`
- `GET /pulses/{id}`
- `GET /decision/context`
- `GET /scheduler/status`
- `POST /ingest/email`
- `POST /ingest/poll`
- `POST /admin/ingest/backfill`

## Gestion des emails

- Les emails ciblés sont lus depuis `PULSE_IMAP_MAILBOX`
- Après ingestion réussie, ils sont déplacés par défaut vers `AI新聞脈動PLUS`
- Les historiques peuvent être réinjectés ensuite depuis `AI新聞脈動PLUS`
- Le backfill est un appel explicite, pas une tâche automatique au démarrage

## Outils MCP

- `pulse_list`
- `pulse_get`
- `pulse_decision_context`
- `pulse_poll_now`
- `pulse_backfill_history`
- `pulse_scheduler_status`

## Installation MCP

Lancement stdio avec Docker :

```bash
docker compose run --rm -T mcp python -m app.mcp_server
```

Vérification :

```bash
docker compose run --rm -T mcp python -c "import app.mcp_server; print('mcp-import-ok')"
```

## Sponsoring et services

Ce dépôt public peut soutenir deux sources de revenus :

- sponsoring pour la maintenance open source
- services payants d’intégration et de conseil

Services recommandés :

- intégration ChatGPT / email pulse ingestion
- packaging de MCP server
- design de workflow de décision pour LLM
- déploiement FastAPI
- pipelines internes de connaissance et de notification

