#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${FAST_MVP_ROOT_DIR:-/workspace/fast_mvp_codex}"
REPO_DIR="$ROOT_DIR/repos/crypto-arb-openclaw-mvp"
LOG_DIR="$ROOT_DIR/log"
REFRESH_SECONDS="${1:-2}"
ITERATIONS="${2:-0}"

cd "$REPO_DIR"
export PYTHONPATH="$REPO_DIR"

python3 -m app.monitor_cli \
  --telemetry-path "$LOG_DIR/openclaw-runner.jsonl" \
  --event-log-path "$LOG_DIR/openclaw-events.jsonl" \
  --refresh-seconds "$REFRESH_SECONDS" \
  --iterations "$ITERATIONS" \
  --follow
