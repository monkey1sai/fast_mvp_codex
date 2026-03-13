#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${FAST_MVP_ROOT_DIR:-/workspace/fast_mvp_codex}"
REPO_DIR="$ROOT_DIR/repos/crypto-arb-openclaw-mvp"
LOG_DIR="$ROOT_DIR/log"
CYCLES="${1:-1}"
SYMBOL="${2:-BTC_USDT}"

mkdir -p "$LOG_DIR"
cd "$REPO_DIR"

export PYTHONPATH="$REPO_DIR"
export OKX_DEMO_TRADING="${OKX_DEMO_TRADING:-false}"

python3 -m app.runner_cli \
  --cycles "$CYCLES" \
  --symbol "$SYMBOL" \
  --price-source okx \
  --telemetry-path "$LOG_DIR/openclaw-runner.jsonl" \
  --event-log-path "$LOG_DIR/openclaw-events.jsonl" \
  --confirm-live
