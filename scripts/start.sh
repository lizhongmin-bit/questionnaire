#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$ROOT_DIR/logs"
MODE="${1:-dev}"

mkdir -p "$LOG_DIR"

if [[ -f "$LOG_DIR/backend.pid" ]]; then
  echo "已有进程记录，请先运行 ./scripts/stop.sh"
  exit 1
fi

echo "启动后端..."
nohup bash -lc "cd '$ROOT_DIR/backend' && \
  if [[ -f .venv/bin/activate ]]; then source .venv/bin/activate; fi; \
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8008" \
  > "$LOG_DIR/backend.log" 2>&1 &
echo $! > "$LOG_DIR/backend.pid"

echo "后端日志: $LOG_DIR/backend.log"
echo "模式: $MODE"
echo "按 Ctrl+C 停止日志查看（不会停止服务）"

tail -n 50 -f "$LOG_DIR/backend.log"
