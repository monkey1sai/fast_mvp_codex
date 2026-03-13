#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/mnt/c/fast_mvp_codex"
REPO_DIR="$ROOT_DIR/repos/crypto-arb-openclaw-mvp"
LOG_DIR="$ROOT_DIR/log"

CYCLES="${1:-1}"
SYMBOL="${2:-BTC_USDT}"

cd "$REPO_DIR"
export OKX_DEMO_TRADING=false

./.venv/Scripts/python.exe -m app.runner_cli \
  --cycles "$CYCLES" \
  --symbol "$SYMBOL" \
  --price-source okx \
  --telemetry-path "$LOG_DIR/openclaw-runner.jsonl" \
  --event-log-path "$LOG_DIR/openclaw-events.jsonl" \
  --confirm-live
