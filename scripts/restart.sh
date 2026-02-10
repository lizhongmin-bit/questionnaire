#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

bash "$ROOT_DIR/scripts/stop.sh"
sleep 1
bash "$ROOT_DIR/scripts/start.sh" "${1:-dev}"
