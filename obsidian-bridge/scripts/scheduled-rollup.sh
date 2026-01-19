#!/bin/bash
# Scheduled rollup script for cron
# Runs the knowledge pipeline on a schedule
#
# Add to crontab with: crontab -e
# 0 9,14,21 * * * ~/.claude/skills/obsidian-bridge/scripts/scheduled-rollup.sh
#
# This runs at 9am, 2pm, and 9pm daily

set -e

LOG_DIR="$HOME/.cache/devlog/logs"
LOG_FILE="$LOG_DIR/rollup-$(date +%Y%m%d-%H%M%S).log"

mkdir -p "$LOG_DIR"

# Run pipeline
echo "=== Scheduled Rollup: $(date) ===" >> "$LOG_FILE"

python3 ~/.claude/skills/obsidian-bridge/scripts/run-pipeline.py \
    --since "8 hours ago" \
    >> "$LOG_FILE" 2>&1

# Cleanup old logs (keep last 30 days)
find "$LOG_DIR" -name "rollup-*.log" -mtime +30 -delete

echo "=== Rollup Complete: $(date) ===" >> "$LOG_FILE"

# Optional: Send notification (macOS)
if command -v osascript &> /dev/null; then
    osascript -e 'display notification "Knowledge pipeline complete" with title "DevLog"' 2>/dev/null || true
fi
