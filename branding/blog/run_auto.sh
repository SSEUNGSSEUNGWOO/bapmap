#!/bin/bash
set -e

PROJECT_DIR="/Users/sseung/Documents/business/Bapmap"
PYTHON="$PROJECT_DIR/.venv/bin/python"
LOG_DIR="$PROJECT_DIR/branding/blog/logs"

mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/$(date +%Y-%m-%d).log"

echo "=== $(date '+%Y-%m-%d %H:%M:%S') 시작 ===" >> "$LOG_FILE"

cd "$PROJECT_DIR"
"$PYTHON" -m branding.blog.auto --max-spots 5 >> "$LOG_FILE" 2>&1

echo "=== $(date '+%Y-%m-%d %H:%M:%S') 완료 ===" >> "$LOG_FILE"
