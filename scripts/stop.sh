#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$ROOT_DIR/logs"

stop_pid() {
  local name="$1"
  local pid_file="$2"
  if [[ -f "$pid_file" ]]; then
    local pid
    pid="$(cat "$pid_file")"
    if kill -0 "$pid" >/dev/null 2>&1; then
      echo "停止 $name (PID $pid)..."
      kill "$pid" || true
    else
      echo "$name 进程不存在 (PID $pid)"
    fi
    rm -f "$pid_file"
  else
    echo "未找到 $name PID 文件"
  fi
}

stop_pid "后端" "$LOG_DIR/backend.pid"
