#!/bin/bash
# Record an orchestration event
set -e

EVENT="${1:-}"
PROJECT_DIR="${2:-.}"
ORCH_DIR="$PROJECT_DIR/.claude/orchestration"
STATE_FILE="$ORCH_DIR/state.json"

if [ -z "$EVENT" ]; then
    echo "Usage: record-event.sh <event-name> [project-dir]"
    echo ""
    echo "Examples:"
    echo "   record-event.sh design:complete"
    echo "   record-event.sh tests:fail"
    echo "   record-event.sh gate:typecheck:pass"
    exit 1
fi

if [ ! -f "$STATE_FILE" ]; then
    echo "❌ No state file found."
    exit 1
fi

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

if command -v jq &> /dev/null; then
    TMP_FILE=$(mktemp)
    cat "$STATE_FILE" | jq \
        --arg event "$EVENT" \
        --arg ts "$TIMESTAMP" \
        '.events += [{"event": $event, "timestamp": $ts}]' \
        > "$TMP_FILE"
    mv "$TMP_FILE" "$STATE_FILE"
    echo "📡 Event recorded: $EVENT"
else
    echo "⚠️  jq not installed - event not recorded"
fi
