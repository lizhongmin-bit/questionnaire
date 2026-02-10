#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$ROOT_DIR/logs"

stop_pid() {
  local name="$1"
  local pid_file="$2"
  local pgid_file="$3"
  if [[ -f "$pid_file" ]]; then
    local pid
    pid="$(cat "$pid_file")"
    local pgid=""
    if [[ -f "$pgid_file" ]]; then
      pgid="$(cat "$pgid_file")"
    fi
    if [[ -n "$pgid" ]] && kill -0 "$pgid" >/dev/null 2>&1; then
      echo "停止 $name (PGID $pgid)..."
      kill -TERM "-$pgid" || true
    elif kill -0 "$pid" >/dev/null 2>&1; then
      echo "停止 $name (PID $pid)..."
      kill "$pid" || true
    else
      echo "$name 进程不存在 (PID $pid)"
    fi
    rm -f "$pid_file"
    [[ -f "$pgid_file" ]] && rm -f "$pgid_file"
  else
    echo "未找到 $name PID 文件"
  fi
}

stop_pid "后端" "$LOG_DIR/backend.pid" "$LOG_DIR/backend.pgid"
